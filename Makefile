.RECIPEPREFIX +=
.PHONY: test build doc

clean:
    find . -name '.cache' -exec rm -rf {} +
    find . -name '.eggs' -exec rm -rf {} +
    find . -name 'build' -exec rm -rf {} +
    find . -name 'dist' -exec rm -rf {} +
    find . -name 'doctrees' -exec rm -rf {} +
    find . -name '__pycache__' -exec rm -rf {} +
    find . -name '*.egg-info' -exec rm -rf {} +

    find . -name '*.pyc' -exec rm -f {} +
    find . -name '*.pyo' -exec rm -f {} +
    find . -name '*~' -exec rm -f  {} +

    rm -rf datacube_query/help/html
    rm -f datacube_query/metadata.txt
    rm -rf datacube_query/LICENSE


test:
    # py.test-3 --verbose --color=yes
    python3 setup.py pytest


doc:
    # make -C doc
    python3 setup.py build_sphinx


build: clean doc
    python3 setup.py build_plugin
