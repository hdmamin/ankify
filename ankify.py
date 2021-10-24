import fire
import pandas as pd
from pathlib import Path
from tqdm.auto import tqdm

# from htools.cli import fire, module_docstring
from htools.core import load, save


def main(path, out_dir='/tmp', sep='\t', chunksize=1):
    def process_one(path):
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
        print(f'Found {len(pairs)} questions.')

        df = pd.DataFrame(pairs, columns=['q', 'a'])
        out_path = Path(out_dir)/f'anki_{path.stem}.csv'
        df.to_csv(out_path, sep=sep, index=False, header=False)
        print(f'File saved to {out_path}.')

    path = Path(path)
    if path.is_file():
        process_one(path)
    else:
        for p in tqdm(path.iterdir()):
            if p.suffix == '.txt':
                process_one(p)


if __name__ == '__main__':
    fire.Fire(main)
