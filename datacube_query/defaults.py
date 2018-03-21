from collections import OrderedDict
from rasterio.enums import Resampling, Compression
from datacube.helpers import ga_pq_fuser


HELP_URL = 'http://datacube-qgis.readthedocs.io/en/latest'
SETTINGS_GROUP = 'Open Data Cube'

GTIFF_COMPRESSION = [c.value for c in Compression]
GTIFF_OVR_RESAMPLING = {r.name: r for r in Resampling}


GTIFF_DEFAULTS = {"driver": "GTiff",
                  "interleave": "band", "tiled": True,
                  "blockxsize": 256, "blockysize": 256,
                  "compress": "lzw", "predictor": 1,
                  "tfw": False, "jpeg_quality": 75,
                  "profile": "GDALGeoTIFF",
                  "bigtiff": "IF_NEEDED",
                  "geotiff_keys_flavor": "STANDARD",
                  'photometric': 'RGBA',
                  }

GTIFF_OVR_DEFAULTS = {'resampling': 'average',
                      'factors': [2, 4, 8, 16, 32],
                      'internal_storage': True}

GROUP_BY_FUSE_FUNC = OrderedDict(
    [
        ('Solar Day', ('solar_day', None)), #default in datacube-qgis
        ('Time', (None, None)),  #defaults to 'time' in datacube-core
        ('Solar Day (GA PQ Fuser)', ('solar_day', ga_pq_fuser)),
    ])