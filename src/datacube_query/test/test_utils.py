import pytest
from unittest.mock import patch
from .fixtures import data_path

import tempfile
import shutil
from pathlib import Path

import datacube
import numpy as np
import rasterio as rio
import xarray

from datacube_query.exceptions import NoDataError
import datacube_query.utils


def test_build_overviews():
    without_ovr = Path(data_path(),'test_without_ovr.tif')
    with_ovr = Path(data_path(), 'test_with_ovr.tif')

    with tempfile.TemporaryDirectory() as tempdir:
        tmp_raster = Path(tempdir, without_ovr.name)
        # noinspection PyTypeChecker
        shutil.copy(without_ovr, tmp_raster)
        datacube_query.utils.build_overviews(str(tmp_raster))

        with rio.open(str(tmp_raster)) as test_raster, rio.open(str(with_ovr)) as known_raster:
            test_checksums = [test_raster.checksum(i) for i in test_raster.indexes]
            known_checksums = [known_raster.checksum(i) for i in known_raster.indexes]
            assert test_checksums == known_checksums # [14157, 14592, 14233]


def test_build_query():
    known_query = {'product': 'tma', 'measurements': ['1', '4', '9'],
                   'x': (19680402.0, 19680205.0), 'y': (-19680205.0, -19680402.0),
                   'time': ['2001-01-01', '2001-12-31'], 'crs': 'EPSG:9000'}
    extent = [c for xy in zip(known_query['x'],known_query['y']) for c in xy]
    test_query = datacube_query.utils.build_query(known_query['product'], known_query['measurements'],
                                                  known_query['time'], extent, known_query['crs'])

    assert known_query == test_query


def test_datetime_to_str():
    dt64 = np.datetime64('2001-12-31T01:23:45.0000000')
    assert datacube_query.utils.datetime_to_str(dt64) == '2001-12-31'
    assert datacube_query.utils.datetime_to_str(dt64, '%Y-%m-%d_%H-%M-%S') == '2001-12-31_01-23-45'
    assert datacube_query.utils.datetime_to_str(dt64, '%Y:%m:%d %H:%M:%S') == '2001:12:31 01:23:45'


@patch('datacube.Datacube')
def test_run_query_no_datasets(mock_datacube):

    mock_datacube().index.datasets.search_eager.return_value =  None

    query = {'product': 'tma', 'measurements': ['1', '4', '9'],
             'x': (19680402.0, 19680205.0), 'y': (-19680205.0, -19680402.0),
             'time': ['2001-01-01', '2001-12-31'], 'crs': 'EPSG:4283'}

    with pytest.raises(NoDataError):
        datacube_query.utils.run_query(query)


@patch('datacube.Datacube')
def test_run_query_no_data(mock_datacube):

    mock_datacube().load.return_value = xarray.Dataset({})

    query = {'product': 'tma', 'measurements': ['1', '4', '9'],
             'x': (19680402.0, 19680205.0), 'y': (-19680205.0, -19680402.0),
             'time': ['2001-01-01', '2001-12-31'], 'crs': 'EPSG:4283'}

    with pytest.raises(NoDataError):
        datacube_query.utils.run_query(query)


@patch('datacube.Datacube')
def test_run_query_with_data(mock_datacube):
    nobs, nrows, ncols = 4, 300, 400
    data_array = xarray.DataArray(
        data=np.ones((nobs, nrows, ncols)),
        coords={
            'time': np.linspace(1, 5, nobs),
            'x': np.linspace(1450000.0, 1460000.0, ncols),
            'y': np.linspace(-4000000.0, -3992500, nrows)},
        dims=['time', 'y', 'x'])

    mock_dataset = xarray.Dataset({'blue': data_array, 'green': data_array, 'red': data_array})
    mock_datacube().load.return_value = mock_dataset

    query = {'product': 'tma', 'measurements': ['1', '4', '9'],
             'x': (19680402.0, 19680205.0), 'y': (-19680205.0, -19680402.0),
             'time': ['2001-01-01', '2001-12-31'], 'crs': 'EPSG:4283'}


    assert mock_dataset.identical(datacube_query.utils.run_query(query))


@patch('datacube.Datacube')
def test_run_query_with_dodgy_crs(mock_datacube):
    query = {'product': 'tma', 'measurements': ['1', '4', '9'],
             'x': (19680402.0, 19680205.0), 'y': (-19680205.0, -19680402.0),
             'time': ['2001-01-01', '2001-12-31'], 'crs': 'EPSG:9000'}

    with pytest.raises(datacube.utils.geometry.InvalidCRSError):
        datacube_query.utils.run_query(query)
