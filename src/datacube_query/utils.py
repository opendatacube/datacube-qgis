import os
from datetime import date
import tempfile

import numpy as np

from qgis.core import QgsMessageLog
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import QCoreApplication

import datacube
import datacube.api
from datacube.helpers import write_geotiff

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

#def datacube_connection(config=None):
#    dc = datacube.Datacube(config=config)

def get_icon(basename):
    filepath = os.path.join(
        os.path.dirname(__file__),
        'icons',
        basename
    )
    return QIcon(filepath)


def get_products_and_measurements(platform=None, instrument=None):
    pass #TODO - use to populate parameters dynamically
    # products = dc.list_products()
    # display_columns = ['name', 'description', 'platform', 'instrument', 'crs', 'resolution']
    # nbar_products = products[products['product_type'] == 'nbar'][display_columns].dropna()


def log_message(message, title=None,
                level=QgsMessageLog.INFO,
                translator=QCoreApplication.translate):

    message = translator(message, message)

    if title is not None:
        title = translator(title,title)

    QgsMessageLog.logMessage(message, title, level)


def run_query(output_directory, product, measurements, date_range, extent, config=None):

    dc = datacube.Datacube(config=config, app='QGIS Plugin')

    #TODO folder for temp output (vsimem/temp dir).
    #  - Check mem avail and check/estimate xarray size (inc. lazy via dask?)
    output_directory = '/vsimem' #tempfile.mkdtemp()
    xmin, ymin, xmax, ymax = extent
    query = {'product':product,
             'lon':(xmin, xmax),
             'lat':(ymin, ymax),
             'time':date_range,
            }

    query = datacube.api.query.Query(**query)
    datasets = dc.index.datasets.search_eager(**query.search_terms)

    if not datasets:
        #raise RuntimeError('No datasets found')
        return

    #TODO Masking
    # - test for PQ product
    # - apply default mask

    data = dc.load(group_by='solar_day',
                   measurements=measurements,
                   **query.search_terms)

    return data


def datetime_to_str(datetime64, format='%Y-%m-%d'):

    # datetime64 has nanosecond resolution so convert to millisecs
    dt = datetime64.astype(np.int64) // 1000000000

    dt = date.fromtimestamp(dt)
    return dt.strftime(format)
