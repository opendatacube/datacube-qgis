""""""
__author__ = 'Geoscience Australia'
__date__ = '2017-11-09'
__copyright__ = '(C) 2017 by Geoscience Australia'

# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

import os

from qgis.PyQt.QtCore import QSettings, qVersion
try:
    import qgis2compat.apicompat #Monkey patch QGIS2 to mock QGIS 3 API
except ImportError:
    pass
    #TODO check QGIS version and fail gracefully if we can't run Q3
from qgis.core import QgsRasterLayer, QgsProject, QgsMapLayerRegistry

from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.parameters import ParameterCrs, ParameterExtent
from processing.core.parameters import ParameterRange, ParameterString
from processing.core.ProcessingConfig import Setting, ProcessingConfig
from processing.core.outputs import OutputDirectory

from ..utils import (get_icon, run_query,
                     log_message, write_geotiff,
                     datetime_to_str)


class SimpleDataCubeQueryAlgorithm(GeoAlgorithm):
    """This is TODO

    All Processing algorithms should extend the GeoAlgorithm class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    OUTPUT_DIRECTORY = 'Output Directory'

    #TODO INPUT_PRODUCT is for proof of concept only
    INPUT_PRODUCT = 'Input Product'
    INPUT_MEASUREMENTS = 'Input Measurements'
    #INPUT_PRODUCT_TYPE = 'Input Product Type'
    #platform
    #instrument
    #INPUT_ADD_TO_MAP = 'Add query results to map' #Bool
    #/TODO

    INPUT_DATE_RANGE = 'INPUT_DATE_RANGE'
    INPUT_EXTENT = 'INPUT_EXTENT'

    #TODO Bool Add to TOC?

    def __init__(self):
        GeoAlgorithm.__init__(self)

        self._icon = get_icon('opendatacube.png')

    def defineCharacteristics(self):
        """Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # The name that the user will see in the toolbox
        self.name = 'Simple Data Cube Query'

        # The branch of the toolbox under which the algorithm will appear
        self.group = 'Demo Data Cube Query' #TODO can there be a top level alg, not under a folder?

        self.addParameter(ParameterString(self.INPUT_PRODUCT,
            self.tr('Input product')))
        self.addParameter(ParameterString(self.INPUT_MEASUREMENTS,
            self.tr('Input measurements')))
        self.addParameter(ParameterString(self.INPUT_DATE_RANGE,
            self.tr('Input date range')))
        self.addParameter(ParameterString(self.INPUT_EXTENT,
            self.tr('Input extent')))

        self.addOutput(OutputDirectory(self.OUTPUT_DIRECTORY,
            self.tr('Output location')))

    def processAlgorithm(self, progress):
        """Here is where the processing itself takes place."""

        config_file = ProcessingConfig.getSetting('datacube_config_file')
        config_file = config_file if config_file else None

        product = self.getParameterValue(self.INPUT_PRODUCT)
        date_range = self.getParameterValue(self.INPUT_DATE_RANGE)
        extent = self.getParameterValue(self.INPUT_EXTENT)
        measurements = self.getParameterValue(self.INPUT_MEASUREMENTS)
        #TODO add_results = self.getParameterValue(self.INPUT_ADD_TO_MAP)
        add_results = True
        output_directory = self.getOutputValue(self.OUTPUT_DIRECTORY)

        # log_message(str(config_file),
        #             'config_file',
        #             translator=self.tr)
        # log_message(extent,
        #             'extent',
        #             translator=self.tr)
        date_range = [s.strip() for s in date_range.split(',')]
        extent = [float(f) for f in extent.split(',')]
        measurements = [s.strip() for s in measurements.split(',')]

        #TODO Progress (QProgressBar+iface.messageBar/iface.mainWindow().showMessage)
        #TODO Debug Logging
        #TODO Error handling
        #
        data = run_query(output_directory,
                         product,
                         measurements,
                         date_range,
                         extent,
                         config=config_file)

        if data is None:
            raise RuntimeError('No data found')

        basename = '{}_{}_{}.tif'.format(product, '_'.join(measurements),'{}')
        for i, dt in enumerate(data.time):
            raster = basename.format(datetime_to_str(dt))
            raster_path = os.path.join(output_directory, raster)
            write_geotiff(raster_path, data, time_index=i)
            if add_results:
                raster_lyr = QgsRasterLayer(raster_path, raster)
                #toc_tree = QgsProject.instance().layerTreeRoot()
                #toc_tree.insertLayer(i, raster_lyr)
                QgsMapLayerRegistry.instance().addMapLayer(raster_lyr)

