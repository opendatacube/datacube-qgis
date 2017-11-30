from rasterio.enums import Resampling, Compression


GTIFF_COMPRESSION = [c.value for c in Compression]

GTIFF_DEFAULTS = {"interleave": "band", "tiled": True,
                  "blockxsize": 256, "blockysize": 256,
                  "compress": "lzw", "predictor": 1,
                  "tfw": False, "jpeg_quality": 75,
                  "profile": "GDALGeoTIFF",
                  "bigtiff": "IF_NEEDED", "geotiff_keys_flavor": "STANDARD"}

GTIFF_OVR_RESAMPLING = {r.name: r for r in Resampling
                        if r.name in ['nearest', 'cubic', 'average', 'mode', 'gauss']}

GTIFF_OVR_DEFAULTS = {'resampling': 'average',
                      'factors': [2, 4, 8, 16, 32],
                      'internal_storage': True}

