import pytest

from contextlib import contextmanager
from osgeo import gdal
from pathlib import Path
from datetime import datetime
import numpy as np

@pytest.fixture
def data_path():
    return Path(Path(__file__).parent, 'data').absolute()


@pytest.fixture
@contextmanager
def shut_gdal_up():
    """ Turn off stderr spam """
    gdal.PushErrorHandler('CPLQuietErrorHandler')
    yield
    gdal.PopErrorHandler()


@pytest.fixture
def fake_data_2x2x2():
    from datacube.utils.geometry import CRS

    fake_data = {
        'attrs': {'crs': CRS('EPSG:3577')},
        'coords': {
            'time': {
                'attrs': {'units': 'seconds since 1970-01-01 00:00:00'},
                'data': [datetime(2001, 1, 31, 23, 59, 59), datetime(2001, 12, 30, 23, 59, 59)],
                'dims': ('time',)},
            'x': {'attrs': {'units': 'metre'}, 'data': [1456789.5, 1456790.5], 'dims': ('x',)},
            'y': {'attrs': {'units': 'metre'}, 'data': [-4098765.5, -4098766.5], 'dims': ('y',)}},
        'data_vars': {
            'FOO': {'attrs': {'crs': CRS('EPSG:3577'), 'nodata': -1, 'units': 'percent'},
                    'data': np.ones((2,2,2), dtype=np.int8), 'dims': ('time', 'y', 'x')}, },
        'dims': {'time': 2, 'x': 2, 'y': 2}
    }
    return fake_data

