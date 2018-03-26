.PHONY: build clean doc test

build: doc
	python3 setup.py build_plugin

clean:
	find . -type d -name '.cache' -exec rm -rf {} +
	find . -type d -name '.eggs' -exec rm -rf {} +
	find . -type d -name 'build' -exec rm -rf {} +
	find . -type d -name 'dist' -exec rm -rf {} +
	find . -type d -name 'doctrees' -exec rm -rf {} +
	find . -type d -name '__pycache__' -exec rm -rf {} +
	find . -type d -name '*.egg-info' -exec rm -rf {} +

	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f  {} +

	rm -rf datacube_query/help/html
	rm -f datacube_query/metadata.txt
	rm -f datacube_query/LICENSE


doc: clean
	python3 setup.py build_sphinx


test: clean
	python3 setup.py pytest
