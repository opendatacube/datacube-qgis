""""""
__author__ = 'Geoscience Australia'
__date__ = '2017-11-09'
__copyright__ = '(C) 2017 by Geoscience Australia'

# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

import os
from collections import defaultdict
from datetime import date
import json

import pandas as pd
from sqlalchemy.exc import SQLAlchemyError

from processing.core.parameters import (QgsProcessingParameterBoolean as ParameterBoolean,
                                        QgsProcessingParameterCrs as ParameterCrs,
                                        QgsProcessingParameterExtent as ParameterExtent,
                                        QgsProcessingParameterEnum as ParameterEnum,
                                        QgsProcessingParameterString as ParameterString,
                                        QgsProcessingParameterNumber as ParameterNumber,
                                        QgsProcessingParameterFolderDestination as ParameterFolderDestination)

from processing.core.ProcessingConfig import ProcessingConfig
from processing.core.outputs import QgsProcessingOutputFolder as OutputFolder

from datacube.storage.storage import write_dataset_to_netcdf as write_netcdf

from .base import BaseAlgorithm
from ..parameters import ParameterDateRange, ParameterProducts
from ..qgisutils import (get_icon, log_message, LOGLEVEL)
from ..utils import (
    build_overviews,
    calc_stats,
    datetime_to_str,
    get_products_and_measurements,
    run_query,
    str_snip,
    update_tags,
    write_geotiff,
)


class DataCubeQueryAlgorithm(BaseAlgorithm):
    """This is TODO

    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    OUTPUT_FOLDER = 'Output Directory'

    # TODO ?
    # PARAM_PRODUCT_TYPE = 'Input Product Type'
    # platform
    # instrument
    # /TODO
    PARAM_PRODUCTS = 'Product and measurements'
    PARAM_DATE_RANGE = 'Date range (yyyy-mm-dd)'
    PARAM_EXTENT = 'Query extent'

    # Advanced params
    PARAM_OVERVIEWS = 'Build overviews for output GeoTIFFs?'
    PARAM_FORMAT = 'Write NetCDF instead of GeoTIFF?'
    PARAM_OUTPUT_CRS = 'Output CRS (required for products with no CRS defined)'
    PARAM_OUTPUT_RESOLUTION = ('Output resolution  (N or N,N, '
                               'required for products with no resolution defined)')

    # TODO PARAM_ADD_TO_MAP = 'Add query results to map' #Bool

    # TODO error handling with GeoAlgorithmExecutionException

    def __init__(self, products=None):
        super().__init__()

        self._icon = get_icon('opendatacube.png')
        self.config_file = None
        self.products = {} if products is None else products

    def checkParameterValues(self, parameters, context):
        if self.parameterAsString(parameters, self.PARAM_PRODUCTS, context) == '{}':
            return False, self.tr('Please select at least one product')
        return super().checkParameterValues(parameters, context)

    # def create(self):
    #     pass
    #
    def createInstance(self):
        try:products = self.get_products_and_measurements()
        except SQLAlchemyError as e:
            log_message('Unable to connect to a running Data Cube instance',
                        LOGLEVEL.WARNING)
            products = None

        return self.__class__(products)

    def displayName(self, *args, **kwargs):
        return self.tr('Data Cube Query')

    def get_products_and_measurements(self):
        config_file = ProcessingConfig.getSetting('datacube_config_file')
        self.config_file = config_file or None
        return get_products_and_measurements(config=self.config_file)

    def group(self):
        return self.tr('Data Cube Query')

    def groupId(self):
        return 'datacubequery'

    def initAlgorithm(self, config=None):
        """
            Define the inputs and output of the algorithm.
        """

        # Basic Params
        items = defaultdict(list)
        for k, v in self.products.items():
            items[k] += v['measurements'].keys()

        self.addParameter(ParameterProducts(self.PARAM_PRODUCTS,
                                            self.tr(self.PARAM_PRODUCTS),
                                            items=items
                                           ))

        self.addParameter(ParameterDateRange(self.PARAM_DATE_RANGE,
                                             self.tr(self.PARAM_DATE_RANGE),
                                             optional=True))
        self.addParameter(ParameterExtent(self.PARAM_EXTENT,
                                          self.tr(self.PARAM_EXTENT)))

        # "Advanced" Params (just to reduce interface clutter)
        param = ParameterBoolean(self.PARAM_FORMAT,
                                 self.tr(self.PARAM_FORMAT), defaultValue=False)
        param.isAdvanced = True
        self.addParameter(param)

        param = ParameterCrs(self.PARAM_OUTPUT_CRS, self.tr(self.PARAM_OUTPUT_CRS), optional=True)
        param.isAdvanced = True
        self.addParameter(param)

        param = ParameterNumber(self.PARAM_OUTPUT_RESOLUTION, self.tr(self.PARAM_OUTPUT_RESOLUTION),
                               optional=True, defaultValue=None)
        param.isAdvanced = True
        self.addParameter(param)

        # Output/s
        # self.addParameter(ParameterFolderDestination(self.OUTPUT_FOLDER,
        #                                             self.tr(self.OUTPUT_FOLDER)))
        self.addOutput(OutputFolder(self.OUTPUT_FOLDER, self.tr(self.OUTPUT_FOLDER)))

    def prepareAlgorithm(self, parameters, context, feedback):
        """TODO docstring"""
        return True

    def processAlgorithm(self, parameters, context, feedback):
        """TODO docstring"""

        # General options
        config_file = ProcessingConfig.getSetting('datacube_config_file')
        config_file = config_file if config_file else None
        gtiff_options = json.loads(ProcessingConfig.getSetting('gtiff_options'))
        gtiff_ovr_options = json.loads(ProcessingConfig.getSetting('gtiff_ovr_options'))
        overviews = ProcessingConfig.getSetting('build_overviews')

        # Parameters
        product_descs = self.parameterAsString(parameters, self.PARAM_PRODUCTS, context)
        product_descs = json.loads(product_descs)
        products = defaultdict(list)
        for k, v in product_descs.items():
            for m in v:
                products[self.products[k]['product']] += [self.products[k]['measurements'][m]]

        date_range = self.parameterAsString(parameters, self.PARAM_DATE_RANGE, context)
        date_range = json.loads(date_range)

        extent = self.parameterAsExtent(parameters, self.PARAM_EXTENT, context) #QgsRectangle
        extent = [extent.xMinimum(), extent.yMinimum(), extent.xMaximum(), extent.yMaximum()]
        extent_crs = self.parameterAsExtentCrs(parameters, self.PARAM_EXTENT, context) # QgsCoordinateReferenceSystem
        extent_crs = extent_crs.authid()

        # TODO add_results = self.parameterAsBool(parameters, self.PARAM_ADD_TO_MAP, context)
        add_results = True

        output_netcdf = self.parameterAsBool(parameters, self.PARAM_FORMAT, context)

        output_crs = self.parameterAsCrs(parameters, self.PARAM_OUTPUT_CRS, context).authid()
        output_crs = None if not output_crs else output_crs

        output_res = self.parameterAsDouble(parameters, self.PARAM_OUTPUT_RESOLUTION, context)
        output_res = None if not output_res else [output_res, output_res]

        output_folder = self.parameterAsString(parameters, self.OUTPUT_FOLDER, context)

        dask_chunks = {'time': 1}

        stats = False # TODO from Settings

        # TODO remove debug prints
        for product, measurements in products.items():
            print(product)
            print(measurements)

        # TODO Progress (QProgressBar+iface.messageBar/iface.mainWindow().showMessage)
        # TODO Debug Logging
        # TODO Error handling

        # TODO Check mem avail and check/estimate xarray size (inc. lazy via dask?)
        # data = run_query(product,
        #                  measurements,
        #                  date_range,
        #                  extent,
        #                  extent_crs,
        #                  output_crs,
        #                  output_res,
        #                  config_file,
        #                  dask_chunks=dask_chunks
        #                  )
        #
        # if data is None:
        #     raise RuntimeError('No data found')
        #
        # basename = '{}_{}'.format(product, '{}')
        # basepath = os.path.join(OUTPUT_FOLDER, basename)
        #
        # if output_netcdf:
        #     ext = '.nc'
        #     start_date = datetime_to_str(data.time[0])
        #     end_date = datetime_to_str(data.time[-1])
        #     dt = '{}_{}'.format(start_date, end_date)
        #     raster_path = basepath.format(dt) + ext
        #     write_netcdf(data, raster_path)
        #
        #     if add_results:
        #         for measurement in measurements:
        #             layer_name = '{}_{}_{}'.format(product, measurement, dt)
        #             nc_path = 'NETCDF:"{}":{}'.format(raster_path, measurement)
        #             raster_lyr = QgsRasterLayer(nc_path, layer_name)
        #             QgsProject.instance().addMapLayer(raster_lyr)
        # else:
        #     ext = '.tif'
        #     for i, dt in enumerate(data.time):
        #         ds = datetime_to_str(dt)
        #         raster_path = basepath.format(ds) + ext
        #         # TODO add advanced param/s for overview stuff
        #         write_geotiff(raster_path, data, time_index=i,
        #                       profile_override=gtiff_options)
        #
        #         update_tags(raster_path, TIFFTAG_DATETIME=datetime_to_str(dt, '%Y:%m:%d %H:%M:%S'))
        #
        #         if overviews:
        #             build_overviews(raster_path, gtiff_ovr_options)
        #
        #         if stats:
        #             calc_stats(gtiff_ovr_options, stats_options)
        #
        #         if add_results:
        #             raster_lyr = QgsRasterLayer(raster_path, basename.format(ds))
        #             QgsProject.instance().addMapLayer(raster_lyr)
        #
        #         # TODO return rasters

        return {self.OUTPUT_FOLDER: output_folder}
