"""
Examples
--------
ankify ~/notes/dl/gans.txt
ankify ~/notes/dl
"""

import fire
from functools import partial
import pandas as pd
from pathlib import Path

from htools.core import load, parallelize


def process_one_file(path, out_dir, sep):
    """Extract q/a pairs from a single txt file and save it as a csv. Args are
    the same as the ones documented in `main`.
    """
    path = Path(path)
    text = load(path)
    pairs = []
    msg_fmt = 'Found malformed Q/A: {chunk}'
    for chunk in text.split('\n\n'):
        if chunk.startswith('_Q:'):
            pair = chunk[3:].strip().replace('\n',
                                                '<br/>').split('<br/>_A:')
            assert len(pair) == 2, msg_fmt.format(chunk)
            pairs.append(pair)
        elif chunk.startswith(('_Q.', 'Q:', 'Q.')):
            raise RuntimeError(msg_fmt.format(chunk))
    length = len(pairs)
    print(f'Found {length} questions in {path}.')
    if not length:
        return

    df = pd.DataFrame(pairs)
    out_path = Path(out_dir)/f'anki_{path.stem}.csv'
    df.to_csv(out_path, sep=sep, index=False, header=False)
    print(f'File saved to {out_path}.')


def main(path, out_dir='/tmp', sep='\t', chunksize=1):
    """Convert notes (in the form of 1 or more txt files) to csv's that can be
    imported into anki.

    Parameters
    ----------
    path: str or Path
        Text file or directory containing multiple text files. Any file
        containing Q/A pairs must use my standard Anki formatting
        (see data/sample_notes.txt).
    sep: str
        Used to separate fields in resulting csv/tsv. I rarely (never?) use
        tabs in my notes since vim converts them to spaces. Haven't tested
        behavior if this char appears in your text file naturally.
    chunksize: int
        When passing in a directory for `path`, this is a parameter that
        controls how many items multiprocessing sends to each process. Usually
        1 should be fine but if you have a directory with thousands of files
        you might try a larger number.
    """
    path = Path(path)
    func = partial(process_one_file, out_dir=out_dir, sep=sep)
    if path.is_file():
        func(path)
    else:
        paths = [p for p in path.iterdir() if p.suffix == '.txt']
        parallelize(func, paths, chunksize=chunksize)


def cli():
    fire.Fire(main)


if __name__ == '__main__':
    cli()
