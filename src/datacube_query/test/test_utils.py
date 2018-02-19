import pytest
from unittest.mock import Mock, patch
from .fixtures import data_path

import tempfile
import shutil
from pathlib import Path

import datacube
import numpy
import rasterio
import xarray

from datacube_query.exceptions import NoDataError
import datacube_query.utils


def test_build_overviews():
    without_ovr = Path(data_path(),'test_without_ovr.tif')
    with_ovr = Path(data_path(), 'test_with_ovr.tif')

    with tempfile.TemporaryDirectory() as tempdir:
        tmp_raster = Path(tempdir, without_ovr.name)
        shutil.copy(without_ovr, tmp_raster)
        datacube_query.utils.build_overviews(str(tmp_raster))

        with rasterio.open(str(tmp_raster)) as test_raster, rasterio.open(str(with_ovr)) as known_raster:
            test_checksums = [test_raster.checksum(i) for i in test_raster.indexes]
            known_checksums = [known_raster.checksum(i) for i in known_raster.indexes]
            assert test_checksums == known_checksums # [14157, 14592, 14233]

def test_build_query():
    pass

@patch('datacube.Datacube')
def test_run_query_no_datasets(mock_datacube):

    mock_datacube().index.datasets.search_eager.return_value =  None

    with pytest.raises(NoDataError):
        datacube_query.utils.run_query(None, None, [0, 1], [0, 1, 2, 3], 'EPSG:4326')


@patch('datacube.Datacube')
def test_run_query_no_data(mock_datacube):

    mock_datacube().load.return_value =  xarray.Dataset({})

    with pytest.raises(NoDataError):
        datacube_query.utils.run_query(None, None, [0, 1], [0, 1, 2, 3], 'EPSG:4326')


@patch('datacube.Datacube')
def test_run_query_with_data(mock_datacube):
    nobs, nrows, ncols = 4, 300, 400
    data_array = xarray.DataArray(
        data=numpy.ones((nobs, nrows, ncols)),
        coords={
            'time': numpy.linspace(1, 5, nobs),
            'x': numpy.linspace(1450000.0, 1460000.0, ncols),
            'y': numpy.linspace(-4000000.0, -3992500, nrows)},
        dims=['time', 'y', 'x'])

    mock_dataset = xarray.Dataset({'blue': data_array, 'green': data_array, 'red': data_array})
    mock_datacube().load.return_value =  mock_dataset

    assert mock_dataset.identical(datacube_query.utils.run_query(None, None, [0, 1], [0, 1, 2, 3], 'EPSG:3577'))



@patch('datacube.Datacube')
def test_run_query_with_dodgy_crs(mock_datacube):

    with pytest.raises(Exception):
        datacube_query.utils.run_query(None, None, [0, 1], [0, 1, 2, 3], 'EPSG:1234')
