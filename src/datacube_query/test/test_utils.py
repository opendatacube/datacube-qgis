import pytest
from unittest.mock import patch

from datetime import datetime
import tempfile
import shutil
from pathlib import Path

import datacube
import numpy as np
import pandas as pd
import rasterio as rio
import xarray as xr

import datacube_query.utils


def test_build_overviews(data_path):
    without_ovr = Path(data_path,'test_without_ovr.tif')
    with_ovr = Path(data_path, 'test_with_ovr.tif')

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
    # Nanosec res
    dtns = np.datetime64('2001-12-31T01:23:45.000000000')
    assert datacube_query.utils.datetime_to_str(dtns) == '2001-12-31'
    assert datacube_query.utils.datetime_to_str(dtns, '%Y-%m-%d_%H-%M-%S') == '2001-12-31_01-23-45'

    # Microsec res
    dtus = np.datetime64('2001-12-31T01:23:45.0000')
    assert datacube_query.utils.datetime_to_str(dtus) == '2001-12-31'
    assert datacube_query.utils.datetime_to_str(dtus, '%Y-%m-%d_%H-%M-%S') == '2001-12-31_01-23-45'

    # Millisec res
    dtms = np.datetime64('2001-12-31T01:23:45.0')
    assert datacube_query.utils.datetime_to_str(dtms) == '2001-12-31'
    assert datacube_query.utils.datetime_to_str(dtms, '%Y-%m-%d_%H-%M-%S') == '2001-12-31_01-23-45'

    # Sec res
    dtms = np.datetime64('2001-12-31T01:23:45')
    assert datacube_query.utils.datetime_to_str(dtms) == '2001-12-31'
    assert datacube_query.utils.datetime_to_str(dtms, '%Y-%m-%d_%H-%M-%S') == '2001-12-31_01-23-45'

    # Must be >= 1970
    with pytest.raises(OverflowError):
        bad_dt64 = np.datetime64('1969-12-31T11:59:59')
        datacube_query.utils.datetime_to_str(bad_dt64)

    # Doesn't accept a DataArray
    with pytest.raises(OSError):  # OSError: [Errno 75] Value too large for defined data type
        xrns = xr.DataArray(dtns, coords={'time': dtns})
        datacube_query.utils.datetime_to_str(xrns)

    with pytest.raises(OSError):  # OSError: [Errno 75] Value too large for defined data type
        xrus = xr.DataArray(dtus, coords={'time': dtus})
        datacube_query.utils.datetime_to_str(xrus)

    with pytest.raises(OSError):  # OSError: [Errno 75] Value too large for defined data type
        xrms = xr.DataArray(dtms, coords={'time': dtms})
        datacube_query.utils.datetime_to_str(xrms)


@patch('datacube.Datacube')
def test_get_products_and_measurements(mock_datacube):
    from datacube.utils.geometry import CRS

    products = {
        'id': 42,
        'name': {42: 'some_dataset'}, 'description': {42: 'Some Dataset'}, 'format': {42: 'NETCDF'},
        'orbit': {42: np.nan}, 'time': {42: None}, 'lat': {42: np.nan}, 'platform': {42: 'HHG2U'},
        'instrument': {42: 'a towel'}, 'product_type': {42: 'stuff'}, 'crs': {42: CRS('EPSG:4326')},
        'resolution': {42: [-0.05, 0.05]}, 'tile_size': {42: None},
        'spatial_dimensions': {42: ('latitude', 'longitude')}}

    df_products = pd.DataFrame(products)
    df_products.set_index(['id'])

    measurements = {
        'product': 'some_dataset', 'measurement': 'some_data',
        'dtype': {('some_dataset', 'some_data'): 'float32'},
        'name': {('some_dataset', 'some_data'): 'some_data'},
        'nodata': {('some_dataset', 'some_data'): -999},
        'spectral_definition': {('some_dataset', 'some_data'): np.nan},
        'units': {('some_dataset', 'some_data'): 'fm'}}

    expected_with_aliases = {'Some Dataset (some_dataset)': {
        'product': 'some_dataset',
        'measurements': {'some_data/foo/bar': 'some_data'}}}
    expected_without_aliases = {'Some Dataset (some_dataset)': {
        'product': 'some_dataset',
        'measurements': {'some_data': 'some_data'}}}

    measurements_with_aliases = measurements.copy()
    measurements_with_aliases['aliases'] = {('some_dataset', 'some_data'): ['foo','bar']}
    df_measurements_with_aliases = pd.DataFrame(measurements_with_aliases)
    df_measurements_with_aliases.set_index(['product','measurement'])

    measurements_without_aliases = measurements.copy()
    measurements_without_aliases['aliases'] = {('some_dataset', 'some_data'): np.nan}
    df_measurements_without_aliases = pd.DataFrame(measurements_without_aliases)
    df_measurements_without_aliases.set_index(['product','measurement'])

    mock_datacube().list_products.return_value = pd.DataFrame(df_products)

    mock_datacube().list_measurements.return_value = pd.DataFrame(df_measurements_with_aliases)
    test_with_aliases = datacube_query.utils.get_products_and_measurements()
    assert test_with_aliases == expected_with_aliases

    mock_datacube().list_measurements.return_value = pd.DataFrame(df_measurements_without_aliases)
    test_without_aliases = datacube_query.utils.get_products_and_measurements()
    assert test_without_aliases == expected_without_aliases


def test_lcase_dict():
    test_dict = {'A': 0, 'B': 0, 'c': 0, 'DeFg': 0, (1,2,3): 0, 4: 0}
    expected__dict = {'a': 0, 'b': 0, 'c': 0, 'defg': 0, (1,2,3): 0, 4: 0}
    assert datacube_query.utils.lcase_dict(test_dict) == expected__dict


def test_measurement_desc():
    measurement = 'abc'
    nan_aliases = np.nan
    list_aliases = ['def', 'ghi']

    assert datacube_query.utils.measurement_desc(measurement, nan_aliases) == 'abc'
    assert datacube_query.utils.measurement_desc(measurement, list_aliases) == 'abc/def/ghi'
    assert datacube_query.utils.measurement_desc(measurement, nan_aliases, True) == 'abc'
    assert datacube_query.utils.measurement_desc(measurement, list_aliases, True) == 'abc (def/ghi)'


@patch('datacube.Datacube')
def test_run_query_no_datasets(mock_datacube):
    from datacube_query.exceptions import NoDataError

    mock_datacube().index.datasets.search_eager.return_value = None

    query = {'product': 'tma', 'measurements': ['1', '4', '9'],
             'x': (19680402.0, 19680205.0), 'y': (-19680205.0, -19680402.0),
             'time': ['2001-01-01', '2001-12-31'], 'crs': 'EPSG:4283'}

    with pytest.raises(NoDataError):
        datacube_query.utils.run_query(query)


@patch('datacube.Datacube')
def test_run_query_no_data(mock_datacube):
    from datacube_query.exceptions import NoDataError

    mock_datacube().load.return_value = xr.Dataset({})

    query = {'product': 'tma', 'measurements': ['1', '4', '9'],
             'x': (19680402.0, 19680205.0), 'y': (-19680205.0, -19680402.0),
             'time': ['2001-01-01', '2001-12-31'], 'crs': 'EPSG:4283'}

    with pytest.raises(NoDataError):
        datacube_query.utils.run_query(query)


@patch('datacube.Datacube')
def test_run_query_with_data(mock_datacube):
    nobs, nrows, ncols = 4, 300, 400
    data_array = xr.DataArray(
        data=np.ones((nobs, nrows, ncols)),
        coords={
            'time': np.linspace(1, 5, nobs),
            'x': np.linspace(1450000.0, 1460000.0, ncols),
            'y': np.linspace(-4000000.0, -3992500, nrows)},
        dims=['time', 'y', 'x'])

    mock_dataset = xr.Dataset({'blue': data_array, 'green': data_array, 'red': data_array})
    mock_datacube().load.return_value = mock_dataset

    query = {'product': 'tma', 'measurements': ['1', '4', '9'],
             'x': (19680402.0, 19680205.0), 'y': (-19680205.0, -19680402.0),
             'time': ['2001-01-01', '2001-12-31'], 'crs': 'EPSG:4283'}

    assert mock_dataset.identical(datacube_query.utils.run_query(query))


@patch('datacube.Datacube')
def test_run_query_with_dodgy_crs(mock_datacube, shut_gdal_up):
    query = {'product': 'tma', 'measurements': ['1', '4', '9'],
             'x': (19680402.0, 19680205.0), 'y': (-19680205.0, -19680402.0),
             'time': ['2001-01-01', '2001-12-31'], 'crs': 'EPSG:9000'}

    with pytest.raises(datacube.utils.geometry.InvalidCRSError), shut_gdal_up:
        datacube_query.utils.run_query(query)


def test_upcast(fake_data_2x2x2):

    data = xr.Dataset.from_dict(fake_data_2x2x2)
    test_data, test_dtype = datacube_query.utils.upcast(data, np.int8)

    # Check cast
    assert test_data.data_vars['FOO'].dtype == test_dtype == np.int16
    # Check attrs retained
    assert test_data.crs


def test_update_tags():
    pass  # tested implicitly in test_build_overviews


def test_write_geotiff(fake_data_2x2x2):

    data = xr.Dataset.from_dict(fake_data_2x2x2)
    with tempfile.TemporaryDirectory() as tempdir:
        path = Path(tempdir, 'test.tif')
        datacube_query.utils.write_geotiff(path, data, time_index=0)

        assert path.exists()


def test_write_netcdf():
    pass
