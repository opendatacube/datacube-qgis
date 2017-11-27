import os
from datetime import date

import numpy as np
import pandas as pd
import rasterio as rio
from rasterio.enums import Resampling, Compression

from qgis.core import QgsMessageLog
from qgis.PyQt.QtGui import QIcon

import datacube
import datacube.api
from datacube.helpers import write_geotiff as _write_geotiff
# from datacube.helpers import DEFAULT_PROFILE

# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

# TODO Refactor and move qgis specific code to a separate module?
# TODO GeoTIFF options and overviews

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


def get_icon(basename):
    filepath = os.path.join(
        os.path.dirname(__file__),
        'icons',
        basename
    )
    return QIcon(filepath)


def get_products(config=None):
    # TODO
    dc = datacube.Datacube(config=config)
    products = dc.list_products()
    products = products[['name', 'description']]
    products.set_index('name', inplace=True)
    return products.to_dict('index')


def get_products_and_measurements(product=None, config=None):
    dc = datacube.Datacube(config=config)
    products = dc.list_products()
    measurements = dc.list_measurements()
    products = products.rename(columns={'name': 'product'})
    measurements.reset_index(inplace=True)
    display_columns = ['product_type', 'product', 'description']
    products = products[display_columns]
    display_columns = ['measurement', 'aliases', 'dtype', 'units', 'product']
    measurements = measurements[display_columns]
    prodmeas = pd.merge(products, measurements, how='left', on=['product'])
    if product is not None:
        prodmeas = prodmeas[prodmeas['product'] == product]
    prodmeas.set_index(['product_type', 'product', 'description'], inplace=True)  # , drop=False)
    return prodmeas


def log_message(message, title=None,
                level=QgsMessageLog.INFO,
                translator=None):

    if translator is not None:
        message = translator(message, message)
        if title is not None:
            title = translator(title, title)

    QgsMessageLog.logMessage(message, title, level)


def run_query(product, measurements, date_range, extent, query_crs, output_crs, output_res, config=None):

    # TODO Use dask
    dc = datacube.Datacube(config=config, app='QGIS Plugin')

    xmin, ymin, xmax, ymax = extent
    query = {'product': product,
             'x': (xmin, xmax),
             'y': (ymin, ymax),
             'time':date_range,
             'crs': str(query_crs)
            }
    if output_crs is not None:
        query['output_crs'] = str(output_crs)
    if output_res is not None:
        query['output_res'] = output_res

    query = datacube.api.query.Query(**query)
    datasets = dc.index.datasets.search_eager(**query.search_terms)

    if not datasets:
        # raise RuntimeError('No datasets found')
        return

    # TODO Masking
    # - test for PQ product
    # - apply default mask

    data = dc.load(group_by='solar_day',
                   measurements=measurements,
                   **query.search_terms)

    # TODO report upstream (datacube-core)
    # rasterio.dtypes doesn't support'int8'
    # so datacube.helpers.write_geotiff fails with FC datasets
    for val in data.data_vars:
        if data[val].dtype == 'int8':
            data[val] = data[val].astype('uint8')
    # /TODO

    return data


def datetime_to_str(datetime64, str_format='%Y-%m-%d'):

    # datetime64 has nanosecond resolution so convert to millisecs
    dt = datetime64.astype(np.int64) // 1000000000

    dt = date.fromtimestamp(dt)
    return dt.strftime(str_format)


def build_overviews(filename, overview_options):
    options = DEFAULT_OVERVIEWS.copy()
    if overview_options is not None:
        options.update(overview_options)
    if options['internal_storage']:
        mode = 'r+'
    else:
        mode = 'r'

    resampling = RESAMPLING[options['resampling']]
    with rio.open(filename, mode) as raster:
        raster.build_overviews(options['factors'], resampling)
        raster.update_tags(ns='rio_overview', resampling=options['resampling'])


def update_tags(filename, bidx=0, ns=None, **kwargs):
    with rio.open(filename, 'r+') as raster:
        raster.update_tags(bidx=bidx, ns=ns, **kwargs)


def write_geotiff(filename, dataset, time_index=None,
                  profile_override=None, overviews=False, overview_options=None):

    _write_geotiff(filename, dataset, time_index, profile_override)
    if overviews:
        build_overviews(filename, overview_options)
