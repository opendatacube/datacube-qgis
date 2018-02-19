from collections import OrderedDict
from datacube.helpers import ga_pq_fuser

# TODO Disabling rasterio enums (for now).
# Having this enabled segfaults QGIS 2.99dev (3.0) when the "Select CRS" button
# in _any_ processing alg. dialog (even core) is clicked.
# Might be related to rasterio 0.36. Upgrading to 1.0a(n) fixes the segfault
# However, could be rasterio's use of enum.Enum which I've separately found to segfault QGIS...

# from rasterio.enums import Resampling, Compression
#
# GTIFF_COMPRESSION = [c.value for c in Compression]
# GTIFF_OVR_RESAMPLING = {r.name: r for r in Resampling}

SETTINGS_GROUP = 'Open Data Cube'

GTIFF_COMPRESSION = [
    'JPEG',
    'LZW',
    'PACKBITS',
    'DEFLATE',
    'LZMA',
    'NONE'
]

GTIFF_OVR_RESAMPLING = {
    'nearest': 0,
    'bilinear': 1,
    'cubic': 2,
    'cubic_spline': 3,
    'lanczos': 4,
    'average': 5,
    'mode': 6,
    'gauss': 7,
    'max': 8,
    'min': 9,
    'med': 10,
    'q1': 11,
    'q3': 12}

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

GROUP_BY_FUSE_FUNC = OrderedDict([
    ('Solar Day', ('solar_day', None)),
    ('Solar Day (GA PQ Fuser)', ('solar_day', ga_pq_fuser)),
    ('Don\'t group', (None, None))])  #defaults to 'time' in datacube-core