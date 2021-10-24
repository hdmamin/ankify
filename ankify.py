import fire
from functools import partial
import pandas as pd
from pathlib import Path
from tqdm.auto import tqdm

# from htools.cli import fire, module_docstring
from htools.core import load, parallelize


def process_one_file(path, out_dir, sep):
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
    path = Path(path)
    func = partial(process_one_file, out_dir=out_dir, sep=sep)
    if path.is_file():
        func(path)
    else:
        paths = [p for p in path.iterdir() if p.suffix == '.txt']
        parallelize(func, paths, chunksize=chunksize)


if __name__ == '__main__':
    fire.Fire(main)
