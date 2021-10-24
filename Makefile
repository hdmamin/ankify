clean:
		rm -rf dist/*

lib: clean
		python setup.py sdist

pypi: lib
		twine upload dist/*

reinstall:
		pip uninstall -y ankify && pip install -e ~/ankify
