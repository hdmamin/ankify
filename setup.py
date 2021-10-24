import os
import setuptools


def requirements(path='requirements.txt'):
    with open(path, 'r') as f:
        deps = [line.strip() for line in f]
    return deps


def version():
    path = os.path.join('ankify', '__init__.py')
    with open(path, 'r') as f:
        for row in f:
            if not row.startswith('__version__'):
                continue
            return row.split(' = ')[-1].strip('\n').strip("'")


setuptools.setup(name='ankify',
                 version=version(),
                 author='Harrison Mamin',
                 author_email='hmamin55@gmail.com',
                 description='Tiny CLI to convert my personal notes to '
                             'Anki-importable CSVs.',
                 packages=setuptools.find_packages(),
                 install_requires=requirements(),
                 entry_points={'console_scripts': ['ankify=ankify.cli:cli']})
