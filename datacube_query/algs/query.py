""""""
__author__ = 'Geoscience Australia'
__date__ = '2017-11-09'
__copyright__ = '(C) 2017 by Geoscience Australia'

# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

from collections import defaultdict
import json
from pathlib import Path

from sqlalchemy.exc import SQLAlchemyError

from processing.core.parameters import (
    QgsProcessingParameterBoolean as ParameterBoolean,
    QgsProcessingParameterCrs as ParameterCrs,
    QgsProcessingParameterEnum as ParameterEnum,
    QgsProcessingParameterExtent as ParameterExtent,
    QgsProcessingParameterNumber as ParameterNumber,
    QgsProcessingParameterFolderDestination as ParameterFolderDestination)

from processing.core.outputs import (
    QgsProcessingOutputMultipleLayers as OutputMultipleLayers)

from qgis.core import (
    QgsLogger,
    QgsProcessingContext,
    QgsProcessingException)

from .__base__ import BaseAlgorithm
from ..defaults import GROUP_BY_FUSE_FUNC
from ..exceptions import (NoDataError, TooManyDatasetsError)
from ..parameters import (ParameterDateRange, ParameterProducts)
from ..qgisutils import (get_icon)
from ..utils import (
    build_overviews,
    build_query,
    datetime_to_str,
    get_products_and_measurements,
    run_query,
    update_tags,
    write_geotiff,
    write_netcdf
)


class DataCubeQueryAlgorithm(BaseAlgorithm):
    """
    Class that represent a "tool" in the processing toolbox.
    """

    OUTPUT_FOLDER = 'Output Directory'
    OUTPUT_LAYERS = 'Output Layers'

    # TODO ??? Add more input params.
    # PARAM_PRODUCT_TYPE   # Would need to build a signal/slot filter for PARAM_PRODUCTS widget
    # PARAM_PLATFORM
    # PARAM_INSTRUMENT
    # /TODO ???
    PARAM_PRODUCTS = 'Products and measurements'
    PARAM_DATE_RANGE = 'Date range (yyyy-mm-dd)'
    PARAM_EXTENT = 'Query extent'

    # Advanced params
    PARAM_OVERVIEWS = 'Build overviews for output GeoTIFFs?'
    PARAM_FORMAT = 'Write NetCDF instead of GeoTIFF?'
    PARAM_OUTPUT_CRS = 'Output CRS (required for products with no CRS defined)'
    PARAM_OUTPUT_RESOLUTION = ('Output pixel resolution '
                               '(required for products with no resolution defined)')
    PARAM_GROUP_BY = 'Group data by'

    # TODO error handling with QgsProcessingException

    def __init__(self, products=None):
        """
        Initialise the algorithm

        :param dict products: A dict of products as returned by
            :func:`datacube_query.utils.get_products_and_measurements`
        """
        super().__init__()

        self._icon = get_icon('opendatacube.png')
        self.products = {} if products is None else products
        self.outputs = {}

    def checkParameterValues(self, parameters, context):
        msgs = []

        if self.parameterAsString(parameters, self.PARAM_PRODUCTS, context) == '{}':
            msgs += ['Please select at least one product']

        output_crs = self.parameterAsCrs(parameters, self.PARAM_OUTPUT_CRS, context).isValid()
        output_res = self.parameterAsDouble(parameters, self.PARAM_OUTPUT_RESOLUTION, context)
        if output_crs and not output_res:
            msgs += ['Please specify "Output Resolution" when specifying "Output CRS"']

        if msgs:
            return False, self.tr('\n'.join(msgs))

        return super().checkParameterValues(parameters, context)

    def createInstance(self, config=None):
        try:
            products = self.get_products_and_measurements()
        except SQLAlchemyError:  # TODO add custom exception classes?
            msg = 'Unable to connect to a running Data Cube instance'
            QgsLogger().warning(msg)
            products = {msg: {'measurements': {}}}

        return type(self)(products)

    def displayName(self, *args, **kwargs):
        return self.tr('Data Cube Query')

    def get_products_and_measurements(self):
        config_file = self.get_settings()['datacube_config_file'] or None
        return get_products_and_measurements(config=config_file)

    def group(self):
        """
        The folder the tool is shown in
        """
        return self.tr('Data Cube Query')

    def groupId(self):
        return 'datacubequery'

    def initAlgorithm(self, config=None):
        """
        Define the parameters and output of the algorithm.
        """

        # Basic Params
        items = defaultdict(list)
        for k, v in self.products.items():
            items[k] += v['measurements'].keys()

        self.addParameter(ParameterProducts(self.PARAM_PRODUCTS,
                                            self.tr(self.PARAM_PRODUCTS),
                                            items=items))

        self.addParameter(ParameterDateRange(self.PARAM_DATE_RANGE,
                                             self.tr(self.PARAM_DATE_RANGE),
                                             optional=True))
        self.addParameter(ParameterExtent(self.PARAM_EXTENT,
                                          self.tr(self.PARAM_EXTENT)))

        # FIXME - Temporarily disable NetCDF - https://gis.stackexchange.com/q/271525/2856
        # param = ParameterBoolean(self.PARAM_FORMAT,
        #                          self.tr(self.PARAM_FORMAT), defaultValue=False)
        # self.addParameter(param)

        param = ParameterCrs(self.PARAM_OUTPUT_CRS, self.tr(self.PARAM_OUTPUT_CRS), optional=True)
        self.addParameter(param)

        param = ParameterNumber(self.PARAM_OUTPUT_RESOLUTION, self.tr(self.PARAM_OUTPUT_RESOLUTION),
                                type=ParameterNumber.Double, optional=True, defaultValue=None)
        self.addParameter(param)

        param = ParameterEnum(self.PARAM_GROUP_BY, self.tr(self.PARAM_GROUP_BY), allowMultiple=False,
                              options=GROUP_BY_FUSE_FUNC.keys(), defaultValue=0)
        self.addParameter(param)

        # Output/s
        self.addParameter(ParameterFolderDestination(self.OUTPUT_FOLDER,
                                                     self.tr(self.OUTPUT_FOLDER)),
                          createOutput=True)

        self.addOutput(OutputMultipleLayers(self.OUTPUT_LAYERS, self.tr(self.OUTPUT_LAYERS)))

    def prepareAlgorithm(self, parameters, context, feedback):
        return True

    def postProcessAlgorithm(self, context, feedback):
        """
        Add resulting layers to map

        :param qgis.core.QgsProcessingContext context:  Threadsafe context in which a processing algorithm is executed
        :param qgis.core.QgsProcessingFeedback feedback: For providing feedback from a processing algorithm
        """
        output_layers = self.outputs if self.outputs else {}

        for layer, layer_name in output_layers.items():
            context.addLayerToLoadOnCompletion(
                layer, QgsProcessingContext.LayerDetails(layer_name, context.project()))
        return {} #Avoid NoneType can not be converted to a QMap instance

    # noinspection PyMethodOverriding
    def processAlgorithm(self, parameters, context, feedback):
        """
        Collect parameters and execute the query

        :param parameters: Input parameters supplied by the processing framework
        :param qgis.core.QgsProcessingContext context:  Threadsafe context in which a processing algorithm is executed
        :param qgis.core.QgsProcessingFeedback feedback: For providing feedback from a processing algorithm
        :return:
        """

        # General options
        settings = self.get_settings()
        config_file = settings['datacube_config_file'] or None
        try:
            max_datasets = int(settings['datacube_max_datasets'])
        except (TypeError, ValueError):
            max_datasets = None
        gtiff_options = json.loads(settings['datacube_gtiff_options'])
        gtiff_ovr_options = json.loads(settings['datacube_gtiff_ovr_options'])
        overviews = settings['datacube_build_overviews']

        # Parameters
        product_descs = self.parameterAsString(parameters, self.PARAM_PRODUCTS, context)
        product_descs = json.loads(product_descs)
        products = defaultdict(list)
        for k, v in product_descs.items():
            for m in v:
                products[self.products[k]['product']] += [self.products[k]['measurements'][m]]

        date_range = self.parameterAsString(parameters, self.PARAM_DATE_RANGE, context)
        date_range = json.loads(date_range)

        extent = self.parameterAsExtent(parameters, self.PARAM_EXTENT, context)  # QgsRectangle
        extent = [extent.xMinimum(), extent.yMinimum(), extent.xMaximum(), extent.yMaximum()]
        extent_crs = self.parameterAsExtentCrs(parameters, self.PARAM_EXTENT, context)  # QgsCoordinateReferenceSystem
        extent_crs = extent_crs.authid()

        # FIXME - Temporarily disable NetCDF - https://gis.stackexchange.com/q/271525/2856
        # output_netcdf = self.parameterAsBool(parameters, self.PARAM_FORMAT, context)
        output_netcdf = False

        output_crs = self.parameterAsCrs(parameters, self.PARAM_OUTPUT_CRS, context).authid()
        output_crs = None if not output_crs else output_crs

        output_res = self.parameterAsDouble(parameters, self.PARAM_OUTPUT_RESOLUTION, context)
        output_res = None if not output_res else [output_res, output_res]

        group_by = self.parameterAsEnum(parameters, self.PARAM_GROUP_BY, context)
        group_by, fuse_func = GROUP_BY_FUSE_FUNC[list(GROUP_BY_FUSE_FUNC.keys())[group_by]]

        output_folder = self.parameterAsString(parameters, self.OUTPUT_FOLDER, context)

        dask_chunks = {'time': 1} if date_range is not None else None

        output_layers = self.execute(
            products, date_range, extent, extent_crs,
            output_crs, output_res, output_netcdf, output_folder,
            config_file, dask_chunks, overviews, gtiff_options, gtiff_ovr_options,
            group_by, fuse_func, max_datasets, feedback)

        results = {self.OUTPUT_FOLDER: output_folder, self.OUTPUT_LAYERS: output_layers.keys()}
        self.outputs = output_layers # This is used in postProcessAlgorithm
        return results

    # noinspection PyTypeChecker
    def execute(self,
                products, date_range, extent, extent_crs,
                output_crs, output_res, output_netcdf, output_folder,
                config_file, dask_chunks, overviews, gtiff_options, gtiff_ovr_options,
                group_by, fuse_func, max_datasets, feedback):

        output_layers = {}
        progress_total = 100 / (10*len(products))
        feedback.setProgress(0)

        for idx, (product, measurements) in enumerate(products.items()):

            if feedback.isCanceled():
                return output_layers

            feedback.setProgressText('Processing {}'.format(product))

            try:
                query = build_query(
                    product, measurements,
                    date_range, extent,
                    extent_crs, output_crs,
                    output_res, dask_chunks=dask_chunks,
                    group_by=group_by, fuse_func=fuse_func)

                feedback.setProgressText('Query {}'.format(repr(query)))

                data = run_query(query, config_file, max_datasets=max_datasets)

            except (NoDataError, TooManyDatasetsError) as err:
                # feedback.pushInfo('{}'.format(err))
                feedback.reportError('Error encountered processing {}: {}'.format(product, err))
                feedback.setProgress(int((idx + 1) * 10 * progress_total))
                continue

            basename = '{}_{}'.format(product, '{}')
            basepath = str(Path(output_folder, basename))

            feedback.setProgressText('Saving outputs for {}'.format(product))
            if output_netcdf:
                start_date = datetime_to_str(data.time[0].data)
                end_date = datetime_to_str(data.time[-1].data)
                dt = '{}_{}'.format(start_date, end_date)
                raster_path = basepath.format(dt) + '.nc'
                write_netcdf(data, raster_path, overwrite=True)

                for i, measurement in enumerate(measurements):
                    nc_path = 'NETCDF:"{}":{}'.format(raster_path, measurement)
                    layer_name = 'NETCDF:"{}":{}'.format(Path(raster_path).stem, measurement)
                    output_layers[nc_path] = layer_name

                    feedback.setProgress(int((idx * 10 + i + 1) * progress_total))

            else:
                for i, dt in enumerate(data.time):
                    if group_by is None:
                        ds = datetime_to_str(dt.data, '%Y-%m-%d_%H-%M-%S')
                        tag = datetime_to_str(dt.data, '%Y:%m:%d %H:%M:%S')
                    else:
                        ds = datetime_to_str(dt.data)
                        tag = datetime_to_str(dt.data, '%Y:%m:%d')

                    raster_path = basepath.format(ds) + '.tif'

                    write_geotiff(data, raster_path, time_index=i,
                                  profile_override=gtiff_options, overwrite=True)

                    update_tags(raster_path, TIFFTAG_DATETIME=tag)

                    if overviews:
                        build_overviews(raster_path, gtiff_ovr_options)

                    lyr_name = basename.format(ds)
                    output_layers[raster_path] = lyr_name

                    feedback.setProgress(int((idx * 10 + i + 1) * progress_total))

                    if feedback.isCanceled():
                        return output_layers

            feedback.setProgress(int((idx + 1) * 10 * progress_total))

        return output_layers
