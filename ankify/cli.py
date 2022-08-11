"""
Examples
--------
Note to self: recommended usage at the moment is to run these two commands.

```
ankify ~/notes/00_ml
ankify ~/notes/01_books
```

You should also be able to run this on a single file and/or use relative paths:

```
# From ~/notes/01_books dir:
ankify language_instinct.txt
"""

import fire
from functools import partial
import json
import pandas as pd
from pathlib import Path
import requests

from htools.core import load, parallelize


URL = 'http://localhost:8765'


def create_deck(deck_name):
    """Create an anki deck if it does not exist. Does not delete existing
    cards. Note that we can use a format like "parent::child" to create nested
    decks.
    """
    payload = {
        'action': 'createDeck',
        'version': 6,
        'params': {'deck': deck_name}
    }
    res = requests.get(URL, data=json.dumps(payload))
    return res


def process_one_file(path, q_char='#Q:', a_char='#A:',
                     broken_q_chars=('#Q.', 'Q:', 'Q.')):
    """Extract q/a pairs from a single txt file and generate a list of dicts.
    These can be passed directly to `add_cards`.

    Returns
    -------
    list[dict]
    """
    path = Path(path).absolute()
    deck_name = path.parent.name + '::' + path.stem
    options = {
            "allowDuplicate": False,
            "duplicateScope": "deck",
            "duplicateScopeOptions": {
                "deckName": deck_name,
                "checkChildren": False,
                "checkAllModels": False
            }
    }
    text = load(path)
    cards = []
    msg_fmt = 'Found malformed Q/A in {path}: {chunk}'
    for chunk in text.split('\n\n'):
        if chunk.startswith(q_char):
            pair = chunk[3:].strip().replace('\n', '<br/>')\
                .split(f'<br/>{a_char}')
            assert len(pair) == 2, msg_fmt.format(path=path, chunk=chunk)
            # Include deck name in question in case we're practicing a larger
            # deck. Otherwise we have to manually specify the context in every
            # question.
            card = {
                "deckName": deck_name,
                "modelName": "Basic",
                "fields": {
                    "Front": f'[{deck_name}] {pair[0]}',
                    "Back": pair[1]
                },
                "tags": [],
                "options": options
            }
            cards.append(card)
        elif chunk.startswith(broken_q_chars):
            raise RuntimeError(msg_fmt.format(path=path, chunk=chunk))

    # Indent files with no Q/A pairs to make output easier to read.
    length = len(cards)
    prefix = '\t' * (1 - bool(length))
    print(f'{prefix}Found {length} questions in {path}.')
    if length:
        create_deck(deck_name)
    return cards


def add_cards(cards):
    """Add cards to anki deck. Technically uses the addNotes action but this
    seems to do what I want.

    Returns
    -------
    int: Number of new cards added. We avoid adding duplicates to the same
    deck.
    """
    payload = {
        "action": "addNotes",
        "version": 6,
        "params": {
            "notes": cards
        }
    }
    res = requests.get(URL, data=json.dumps(payload))
    n_added = len([row for row in res.json()['result'] if row])
    return n_added


def main(path, chunksize=1, q_char='#Q:',
         a_char='#A:', broken_q_chars=('#Q.', 'Q:', 'Q.')):
    """Convert notes (in the form of 1 or more txt files) to csv's that can be
    imported into anki.

    Parameters
    ----------
    path: str or Path
        Text file or directory containing multiple text files. Any file
        containing Q/A pairs must use my standard Anki formatting
        (see data/sample_notes.txt).
    chunksize: int
        When passing in a directory for `path`, this is a parameter that
        controls how many items multiprocessing sends to each process. Usually
        1 should be fine but if you have a directory with thousands of files
        you might try a larger number.
    """
    path = Path(path)
    func = partial(process_one_file, q_char=q_char,
                   a_char=a_char, broken_q_chars=broken_q_chars)
    if path.is_file():
        cards = func(path)
    else:
        paths = [p for p in path.iterdir() if p.suffix == '.txt']
        nested = parallelize(func, paths, chunksize=chunksize)
        cards = sum(nested, [])
    n_added = add_cards(cards)
    print(f'\nDONE: Added {n_added} new cards.')


def cli():
    fire.Fire(main)


if __name__ == '__main__':
    cli()
