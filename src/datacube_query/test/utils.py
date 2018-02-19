from contextlib import contextmanager
from osgeo import gdal
from pathlib import Path


def data_path():
    return Path(Path(__file__).parent, 'data').absolute()


@contextmanager
def shut_gdal_up():  # Turn off stderr spam
    gdal.PushErrorHandler('CPLQuietErrorHandler')
    yield
    gdal.PopErrorHandler()
