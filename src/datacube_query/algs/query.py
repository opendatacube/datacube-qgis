""""""
__author__ = 'Geoscience Australia'
__date__ = '2017-11-09'
__copyright__ = '(C) 2017 by Geoscience Australia'

# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

import os
from datetime import date

from qgis.core import QgsRasterLayer, QgsMapLayerRegistry

from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.parameters import ParameterCrs, ParameterExtent
# from processing.core.parameters import ParameterString # TODO in QGIS 3
from processing.core.parameters import ParameterBoolean, ParameterString
from processing.core.ProcessingConfig import ProcessingConfig
from processing.core.outputs import OutputDirectory

from datacube.storage.storage import write_dataset_to_netcdf as write_netcdf

from ..utils import (get_icon, run_query, log_message, datetime_to_str, write_geotiff)

# from ..parameters import ParameterDateRange # TODO in QGIS 3


class DataCubeQueryAlgorithm(GeoAlgorithm):
    """This is TODO

    All Processing algorithms should extend the GeoAlgorithm class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    OUTPUT_DIRECTORY = 'Output Directory'

    # TODO PARAM_PRODUCT is for proof of concept only
    PARAM_PRODUCT = 'Product'
    PARAM_MEASUREMENTS = 'Measurements'
    # PARAM_PRODUCT_TYPE = 'Input Product Type'
    # platform
    # instrument
    # PARAM_ADD_TO_MAP = 'Add query results to map' #Bool
    # /TODO

    # TODO QGIS3
    PARAM_DATE_RANGE = 'Date range (Y-M-D, Y-M-D)'
    # PARAM_DATE_RANGE = 'Date range'
    # / TODO
    PARAM_EXTENT = 'Query extent'
    PARAM_CRS = 'Query extent CRS (if not WGS84/EPSG:4326)'
    PARAM_FORMAT = 'Write NetCDF instead of GeoTIFF?'

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
        self.group = 'Data Cube Query'  # TODO can there be a top level alg, not under a folder?

        self.addParameter(ParameterString(self.PARAM_PRODUCT,
                                          self.tr(self.PARAM_PRODUCT)))
        self.addParameter(ParameterString(self.PARAM_MEASUREMENTS,
                                          self.tr(self.PARAM_MEASUREMENTS)))
        # TODO QGIS 3
        # self.addParameter(ParameterDateRange(self.PARAM_DATE_RANGE, self.tr(self.PARAM_DATE_RANGE)))
        qgis2_date_default = '{ymd},{ymd}'.format(ymd=date.today().strftime('%Y-%m-%d'))
        self.addParameter(ParameterString(self.PARAM_DATE_RANGE,
                                          self.tr(self.PARAM_DATE_RANGE),
                                          default=qgis2_date_default))
        # / TODO
        self.addParameter(ParameterExtent(self.PARAM_EXTENT,
                                          self.tr(self.PARAM_EXTENT)))
        self.addParameter(ParameterCrs(self.PARAM_CRS,  # TODO Can this be updated from the canvas/selected layer
                                       self.tr(self.PARAM_CRS), default='EPSG:4326'))
        param = ParameterBoolean(self.PARAM_FORMAT,
                                 self.tr(self.PARAM_FORMAT), default=False)
        param.isAdvanced = True
        self.addParameter(param)
        self.addOutput(OutputDirectory(self.OUTPUT_DIRECTORY, self.tr(self.OUTPUT_DIRECTORY)))

    def processAlgorithm(self, progress):
        """Here is where the processing itself takes place."""
        config_file = ProcessingConfig.getSetting('datacube_config_file')
        config_file = config_file if config_file else None

        product = self.getParameterValue(self.PARAM_PRODUCT)
        measurements = self.getParameterValue(self.PARAM_MEASUREMENTS)
        date_range = self.getParameterValue(self.PARAM_DATE_RANGE)
        extent = self.getParameterValue(self.PARAM_EXTENT)
        crs = self.getParameterValue(self.PARAM_CRS)
        # TODO add_results = self.getParameterValue(self.PARAM_ADD_TO_MAP)
        add_results = True
        output_netcdf = self.getParameterValue(self.PARAM_FORMAT)
        output_directory = self.getOutputValue(self.OUTPUT_DIRECTORY)

        date_range = [s.strip() for s in date_range.split(',')]
        xmin, xmax, ymin, ymax = [float(f) for f in extent.split(',')]
        extent = xmin, ymin, xmax, ymax
        measurements = [s.strip() for s in measurements.split(',')]

        # TODO Progress (QProgressBar+iface.messageBar/iface.mainWindow().showMessage)
        # TODO Debug Logging
        # TODO Error handling

        data = run_query(product,
                         measurements,
                         date_range,
                         extent,
                         str(crs),
                         config=config_file)

        if data is None:
            raise RuntimeError('No data found')

        # TODO folder for temp output (vsimem/temp dir).
        #  - Check mem avail and check/estimate xarray size (inc. lazy via dask?)
        # output_directory = '/vsimem'  # tempfile.mkdtemp()
        # TODO Refactor this outta here.
        basename = '{}_{}_{}'.format(product, '_'.join(measurements),'{}')
        basepath = os.path.join(output_directory, basename)

        if output_netcdf:
            ext = '.nc'
            start_date = datetime_to_str(data.time[0])
            end_date = datetime_to_str(data.time[-1])
            dt = '{}_{}'.format(start_date, end_date)
            raster_path = basepath.format(dt) + ext
            write_netcdf(data, raster_path)

            if add_results:
                for measurement in measurements:
                    layer_name = '{}_{}_{}'.format(product, measurement, dt)
                    nc_path = 'NETCDF:"{}":{}'.format(raster_path, measurement)
                    raster_lyr = QgsRasterLayer(nc_path, layer_name)
                    QgsMapLayerRegistry.instance().addMapLayer(raster_lyr)
        else:
            ext = '.tif'
            rasters = []
            for i, dt in enumerate(data.time):
                dt = datetime_to_str(dt)
                raster_path = basepath.format(dt) + ext
                # TODO add advanced param/s for overview stuff
                write_geotiff(raster_path, data, time_index=i, overviews=True)

                if add_results:
                    raster_lyr = QgsRasterLayer(raster_path, basename.format(dt))
                    QgsMapLayerRegistry.instance().addMapLayer(raster_lyr)

        # TODO return rasters