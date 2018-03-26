#wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh;
#bash miniconda.sh -b -p $HOME/miniconda
export PATH="$HOME/conda/bin:$PATH"
hash -r
conda config --set always_yes yes --set changeps1 yes
conda update -q conda
conda env create -q --force -f .travis/environment.yml
source activate datacube-qgis
export PYTHONPATH=$CONDA_PREFIX/share/qgis/python/plugins/processing:$CONDA_PREFIX/share/qgis/python
conda info -a
make test