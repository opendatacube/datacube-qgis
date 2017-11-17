""""""
__author__ = 'Geoscience Australia'
__date__ = '2017-11-09'
__copyright__ = '(C) 2017 by Geoscience Australia'

# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

import os

from qgis.core import QgsRasterLayer, QgsProject, QgsMapLayerRegistry

from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.parameters import ParameterCrs, ParameterExtent
from processing.core.parameters import ParameterRange, ParameterString
from processing.core.ProcessingConfig import Setting, ProcessingConfig
from processing.core.outputs import OutputDirectory

from ..utils import (get_icon, run_query,
                     log_message, write_geotiff,
                     datetime_to_str)


class DataCubeQueryAlgorithm(GeoAlgorithm):
    """This is TODO

    All Processing algorithms should extend the GeoAlgorithm class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    OUTPUT_DIRECTORY = 'Output Directory'

    #TODO INPUT_PRODUCT is for proof of concept only
    INPUT_PRODUCT = 'Product'
    INPUT_MEASUREMENTS = 'Measurements'
    #INPUT_PRODUCT_TYPE = 'Input Product Type'
    #platform
    #instrument
    #INPUT_ADD_TO_MAP = 'Add query results to map' #Bool
    #/TODO

    INPUT_DATE_RANGE = 'Date range'
    INPUT_EXTENT = 'Query extent'
    INPUT_CRS = 'Query extent CRS (if not WGS84/EPSG:4326)'

    # TODO Bool "Add outputs to TOC?
    # TODO error handling with GeoAlgorithmExecutionException

    def __init__(self):
        GeoAlgorithm.__init__(self)

        self._icon = get_icon('opendatacube.png')

    def defineCharacteristics(self):
        """Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # The name that the user will see in the toolbox
        self.name = 'Data Cube Query'

        # The branch of the toolbox under which the algorithm will appear
        self.group = 'Data Cube Query' #TODO can there be a top level alg, not under a folder?

        self.addParameter(ParameterString(self.INPUT_PRODUCT,
            self.tr(self.INPUT_PRODUCT)))
        self.addParameter(ParameterString(self.INPUT_MEASUREMENTS,
            self.tr(self.INPUT_MEASUREMENTS)))
        self.addParameter(ParameterString(self.INPUT_DATE_RANGE,
            self.tr(self.INPUT_DATE_RANGE)))
        self.addParameter(ParameterExtent(self.INPUT_EXTENT,
            self.tr(self.INPUT_EXTENT)))
        self.addParameter(ParameterCrs(self.INPUT_CRS,
            self.tr(self.INPUT_CRS), default='EPSG:4326'))

        self.addOutput(OutputDirectory(self.OUTPUT_DIRECTORY,
            self.tr(self.OUTPUT_DIRECTORY)))

    def processAlgorithm(self, progress):
        """Here is where the processing itself takes place."""

        config_file = ProcessingConfig.getSetting('datacube_config_file')
        config_file = config_file if config_file else None

        product = self.getParameterValue(self.INPUT_PRODUCT)
        measurements = self.getParameterValue(self.INPUT_MEASUREMENTS)
        date_range = self.getParameterValue(self.INPUT_DATE_RANGE)
        extent = self.getParameterValue(self.INPUT_EXTENT)
        crs = self.getParameterValue(self.INPUT_CRS)
        #TODO add_results = self.getParameterValue(self.INPUT_ADD_TO_MAP)
        add_results = True
        output_directory = self.getOutputValue(self.OUTPUT_DIRECTORY)

        # log_message(extent,
        #             'extent',
        #             translator=self.tr)

        date_range = [s.strip() for s in date_range.split(',')]
        xmin, xmax, ymin, ymax = [float(f) for f in extent.split(',')]
        extent = xmin, ymin, xmax, ymax
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
                         str(crs),
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

