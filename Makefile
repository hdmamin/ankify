clean:
		rm -rf dist/*

lib: clean
		python setup.py sdist

pypi: lib
		twine upload -r gg-pypi dist/*

reinstall:
		pip uninstall -y ankify && pip install -e ~/ankify
