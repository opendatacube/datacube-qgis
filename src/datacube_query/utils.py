import os
from datetime import date

import numpy as np
import pandas as pd

from qgis.core import QgsMessageLog
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import QCoreApplication

import datacube
import datacube.api

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

# TODO Refactor and move qgis specific code to a separate module?

def get_icon(basename):
    filepath = os.path.join(
        os.path.dirname(__file__),
        'icons',
        basename
    )
    return QIcon(filepath)


def get_products_and_measurements(config=None):
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
    prodmeas.set_index(['product_type', 'product', 'description'], inplace=True)  # , drop=False)
    return prodmeas

def log_message(message, title=None,
                level=QgsMessageLog.INFO,
                translator=QCoreApplication.translate):

    message = translator(message, message)

    if title is not None:
        title = translator(title,title)

    QgsMessageLog.logMessage(message, title, level)


def run_query(product, measurements, date_range, extent, crs, config=None):

    # TODO Use dask
    dc = datacube.Datacube(config=config, app='QGIS Plugin')

    xmin, ymin, xmax, ymax = extent
    query = {'product': product,
             'x': (xmin, xmax),
             'y': (ymin, ymax),
             'time':date_range,
             'crs': crs
            }

    query = datacube.api.query.Query(**query)
    datasets = dc.index.datasets.search_eager(**query.search_terms)

    if not datasets:
        # raise RuntimeError('No datasets found')
        return

    #TODO Masking
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


def datetime_to_str(datetime64, format='%Y-%m-%d'):

    # datetime64 has nanosecond resolution so convert to millisecs
    dt = datetime64.astype(np.int64) // 1000000000

    dt = date.fromtimestamp(dt)
    return dt.strftime(format)

