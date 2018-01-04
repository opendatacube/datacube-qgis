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

from processing.core.parameters import (QgsProcessingParameterBoolean as ParameterBoolean,
                                        QgsProcessingParameterCrs as ParameterCrs,
                                        QgsProcessingParameterExtent as ParameterExtent,
                                        QgsProcessingParameterEnum as ParameterEnum,
                                        QgsProcessingParameterString as ParameterString)

# from processing.core.parameters import ParameterString # TODO in QGIS 3
from processing.core.ProcessingConfig import ProcessingConfig
from processing.core.outputs import QgsProcessingOutputFolder as OutputFolder

from datacube.storage.storage import write_dataset_to_netcdf as write_netcdf

from .base import BaseAlgorithm

from ..qgisutils import get_icon, log_message

from ..utils import (
    build_overviews,
    calc_stats,
    datetime_to_str,
    get_products,
    get_products_and_measurements,
    run_query,
    str_snip,
    update_tags,
    write_geotiff,
)


# from ..parameters import ParameterDateRange # TODO in QGIS 3


class DataCubeQueryAlgorithm(BaseAlgorithm):
    """This is TODO

    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    OUTPUT_FOLDER = 'Output Directory'

    # TODO PARAM_PRODUCT is for proof of concept only
    PARAM_PRODUCT = 'Product'
    PARAM_MEASUREMENTS = 'Measurements (comma separated list)'
    # PARAM_PRODUCT_TYPE = 'Input Product Type'
    # platform
    # instrument
    # PARAM_ADD_TO_MAP = 'Add query results to map' #Bool
    # /TODO

    # TODO QGIS3
    PARAM_DATE_RANGE = 'Date range (YYY-MM-DD, YYY-MM-DD)'
    # PARAM_DATE_RANGE = 'Date range'
    # / TODO
    PARAM_EXTENT = 'Query extent'
    PARAM_EXTENT_CRS = 'Query extent CRS (if not WGS84/EPSG:4326)'

    # Advanced params
    PARAM_OVERVIEWS = 'Build overviews for output GeoTIFFs?'
    PARAM_FORMAT = 'Write NetCDF instead of GeoTIFF?'
    PARAM_OUTPUT_CRS = 'Output CRS (required for products with no CRS defined)'
    PARAM_OUTPUT_RESOLUTION = ('Output resolution  (N or N,N, '
                               'required for products with no resolution defined)')

    # TODO Bool "Add outputs to TOC?
    # TODO error handling with GeoAlgorithmExecutionException

    def __init__(self):
        BaseAlgorithm.__init__(self)

        self._icon = get_icon('opendatacube.png')
        self.products = {}
        self.product_opts = []
        self.measurements = defaultdict(list)
        self.config_file = None

    def checkParameterValuesBeforeExecuting(self, *args, **kwargs):
        self.update_products_measurements()
        # TODO make PARAM_FORMAT==True and PARAM_OVERVIEWS==True mutually exclusive?

    def checkBeforeOpeningParametersDialog(self):
        self.update_products_measurements()

    def initAlgorithm(self, config=None):
        """Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # Basic Params
        self.addParameter(ParameterEnum(self.PARAM_PRODUCT,
                                        self.tr(self.PARAM_PRODUCT)))
        self.addParameter(ParameterString(self.PARAM_MEASUREMENTS,
                                          self.tr(self.PARAM_MEASUREMENTS),
                                          optional=True, multiLine=True))
        # TODO QGIS 3
        # self.addParameter(ParameterDateRange(self.PARAM_DATE_RANGE, self.tr(self.PARAM_DATE_RANGE)))
        qgis2_date_default = '{ymd},{ymd}'.format(ymd=date.today().strftime('%Y-%m-%d'))
        self.addParameter(ParameterString(self.PARAM_DATE_RANGE,
                                          self.tr(self.PARAM_DATE_RANGE),
                                          defaultValue=qgis2_date_default))
        # / TODO
        self.addParameter(ParameterExtent(self.PARAM_EXTENT,
                                          self.tr(self.PARAM_EXTENT)))
        self.addParameter(ParameterCrs(self.PARAM_EXTENT_CRS,  # TODO Can this be updated from the canvas/selected layer
                                       self.tr(self.PARAM_EXTENT_CRS), defaultValue='EPSG:4326'))

        # "Advanced" Params (just to reduce interface clutter)
        param = ParameterBoolean(self.PARAM_FORMAT,
                                 self.tr(self.PARAM_FORMAT), defaultValue=False)
        param.isAdvanced = True
        self.addParameter(param)

        param = ParameterCrs(self.PARAM_OUTPUT_CRS, self.tr(self.PARAM_OUTPUT_CRS), optional=True)
        param.isAdvanced = True
        self.addParameter(param)

        # param = ParameterRange(self.PARAM_OUTPUT_RESOLUTION, self.tr(self.PARAM_OUTPUT_RESOLUTION),
        #                        optional=True, defaultValue='0,0')
        param = ParameterString(self.PARAM_OUTPUT_RESOLUTION, self.tr(self.PARAM_OUTPUT_RESOLUTION),
                               optional=True, defaultValue=None)
        param.isAdvanced = True
        self.addParameter(param)

        # Output/s
        self.addOutput(OutputFolder(self.OUTPUT_FOLDER, self.tr(self.OUTPUT_FOLDER)))

    def group(self):
        return self.tr('Data Cube Query')

    def groupId(self):
        return 'datacubequery'

    def displayName(self, *args, **kwargs):
        return self.tr('Data Cube Query')

    def processAlgorithm(self, progress):
        """Here is where the processing itself takes place."""

        # General options
        config_file = ProcessingConfig.getSetting('datacube_config_file')
        config_file = config_file if config_file else None
        gtiff_options = json.loads(ProcessingConfig.getSetting('gtiff_options'))
        gtiff_ovr_options = json.loads(ProcessingConfig.getSetting('gtiff_ovr_options'))
        overviews = ProcessingConfig.getSetting('build_overviews')

        # Parameters
        product_idx = self.getParameterValue(self.PARAM_PRODUCT) # nu
        try:
            product_opt = self.product_opts[product_idx]
            product = self.products[product_opt]
        except TypeError: # If a name is passed directly as a string
            product = product_idx

        measurements = self.getParameterValue(self.PARAM_MEASUREMENTS)
        date_range = self.getParameterValue(self.PARAM_DATE_RANGE)
        extent = self.getParameterValue(self.PARAM_EXTENT)
        crs = self.getParameterValue(self.PARAM_EXTENT_CRS)
        # TODO add_results = self.getParameterValue(self.PARAM_ADD_TO_MAP)
        add_results = True
        output_netcdf = self.getParameterValue(self.PARAM_FORMAT)
        output_crs = self.getParameterValue(self.PARAM_OUTPUT_CRS)
        output_crs = None if not output_crs else output_crs
        output_res = self.getParameterValue(self.PARAM_OUTPUT_RESOLUTION)
        output_res = None if not output_res else [float(r) for r in output_res.split(',')]
        if output_res is not None and len(output_res) != 2:
            output_res = [output_res[0], output_res[0]]

        OUTPUT_FOLDER = self.getOutputValue(self.OUTPUT_FOLDER)

        date_range = [s.strip() for s in date_range.split(',')]
        xmin, xmax, ymin, ymax = [float(f) for f in extent.split(',')]
        extent = xmin, ymin, xmax, ymax
        measurements = [s.strip() for s in measurements.split(',')] if measurements else None
        dask_chunks = {'time': 1}

        stats = False # TODO from Settings

        # TODO Progress (QProgressBar+iface.messageBar/iface.mainWindow().showMessage)
        # TODO Debug Logging
        # TODO Error handling

        # TODO Check mem avail and check/estimate xarray size (inc. lazy via dask?)
        data = run_query(product,
                         measurements,
                         date_range,
                         extent,
                         crs,
                         output_crs,
                         output_res,
                         config_file,
                         dask_chunks=dask_chunks
                         )

        if data is None:
            raise RuntimeError('No data found')

        basename = '{}_{}'.format(product, '{}')
        basepath = os.path.join(OUTPUT_FOLDER, basename)

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
            for i, dt in enumerate(data.time):
                ds = datetime_to_str(dt)
                raster_path = basepath.format(ds) + ext
                # TODO add advanced param/s for overview stuff
                write_geotiff(raster_path, data, time_index=i,
                              profile_override=gtiff_options)

                update_tags(raster_path, TIFFTAG_DATETIME=datetime_to_str(dt, '%Y:%m:%d %H:%M:%S'))

                if overviews:
                    build_overviews(raster_path, gtiff_ovr_options)

                if stats:
                    calc_stats(gtiff_ovr_options, stats_options)

                #if add_results:
                #    raster_lyr = QgsRasterLayer(raster_path, basename.format(ds))
                #    QgsMapLayerRegistry.instance().addMapLayer(raster_lyr)

                # TODO return rasters

    def update_products_measurements(self):
        config_file = ProcessingConfig.getSetting('datacube_config_file')
        self.config_file = config_file or None

        measurements = get_products_and_measurements(config=self.config_file)
        measurements = measurements.reset_index()[['product', 'measurement', 'aliases']]
        for r in measurements.itertuples(False):
            meas = None
            try:
                meas = [r.measurement] + r.aliases
            except TypeError:
                if pd.notna(r.measurement):
                    meas = [r.measurement]
            if meas:
                self.measurements[r.product] += meas

        prods = get_products(config=self.config_file).items()
        self.products = {'{} ({})'.format(k, str_snip(v['description'], 75)):
                         k for k, v in prods if k in self.measurements}

        param = self.getParameterFromName(self.PARAM_PRODUCT)
        param.options = self.product_opts = sorted(self.products.keys())
