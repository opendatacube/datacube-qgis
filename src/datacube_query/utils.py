from collections import defaultdict
from datetime import datetime

import dask.array
import numpy as np
import pandas as pd
from pathlib import Path
import rasterio as rio
from rasterio.dtypes import check_dtype

import datacube
from datacube.api.query import Query
from datacube.storage.storage import write_dataset_to_netcdf as _write_dataset_to_netcdf

from .defaults import (GTIFF_OVR_DEFAULTS,
                       GTIFF_DEFAULTS,
                       GTIFF_OVR_RESAMPLING)
from .exceptions import NoDataError

# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'


def build_overviews(filename, overview_options=None):
    """
    Build reduced resolution overviews/pyramids for a raster

    :param filename: The raster to build overviews for.
    :type filename: str

    :param overview_options: Overview options.
    :type overview_options: dict.
        Example:

            {"resampling": "average", "factors": [2, 4, 8, 16, 32], "internal_storage": True}

    """

    options = GTIFF_OVR_DEFAULTS.copy()
    if overview_options is not None:
        options.update(overview_options)
    if options['internal_storage']:
        mode = 'r+'
    else:
        mode = 'r'

    resampling = GTIFF_OVR_RESAMPLING[options['resampling']]

    # TODO check if enum.Enum or rasterio enums still segfault QGIS3 after release
    # TODO this is a kludge to mock an Enum as rasterio.io.build_overviews requires an Enum
    from collections import namedtuple
    resampling = namedtuple('Enum', 'value')(resampling)

    with rio.open(filename, mode) as raster:
        raster.build_overviews(options['factors'], resampling)
        raster.update_tags(ns='rio_overview', resampling=options['resampling'])


def build_query(
        product, measurements, date_range, extent,
        query_crs, output_crs=None, output_res=None,
        dask_chunks=None, group_by=None, fuse_func=None):
    """
    Build a datacube query

    :param str product: Product name.
    :param measurements: List of measurements.
    :type measurements: Union(list[str], tuple[str])
    :param date_range: Start and end dates.
    :type date_range: Union(list[str], tuple[str])
    :param extent: Query extent (xmin, ymin, xmax, ymax).
    :type extent: Union(list[float], tuple[float])
    :param str query_crs: Query CRS.
    :param str output_crs: Output CRS or None.
    :param float output_res: Output resolution or None.
    :param dict dask_chunks: Dask chunks.
    :param str group_by: Group data by (time/solar_day).
    :param callable fuse_func: Fuser function for grouped data.

    :return: Query.
    :rtype: dict
    """

    xmin, ymin, xmax, ymax = extent
    query = dict(product=product, measurements=measurements,
                 x=(xmin, xmax), y=(ymin, ymax),
                 time=date_range, crs=str(query_crs))

    if dask_chunks is not None:
        query['dask_chunks'] = dask_chunks
    if group_by is not None:
        query['group_by'] = group_by
    if fuse_func is not None:
        query['fuse_func'] = fuse_func
    if output_crs is not None:
        query['output_crs'] = str(output_crs)
    if output_res is not None:
        query['resolution'] = output_res

    return query


def datetime_to_str(datetime64, str_format='%Y-%m-%d'):
    """
    Convert a numpy.datetime64 to a string

    :param numpy.datetime64 datetime64: The datetime object.
    :param str str_format:              String format code.

    :rtype: str

    """

    # datetime64 has nanosecond resolution so convert to millisecs
    dt = datetime64.astype(np.int64) // 1000000000

    dt = datetime.utcfromtimestamp(dt)
    return dt.strftime(str_format)


def get_products_and_measurements(config=None):
    """
    Get a dict of products and measurements.

    :param str config: The raster to build overviews for.
    :type config: str or None.

    :return: A dict of products and measurements.
    :rtype: dict


        {product_description: 'product': product_name,
                              'measurements': {measurement_description, measurement_name]}

        e.g.
            {'Landsat 8 NBART 25 metre':
                'product': 'ls8_nbart_scene',
                'measurements': {
                    '1/band_1/coastal_aerosol': '1',
                    '2/band_2/blue': '2',
                    '3/band_3/green': '3',
                    '4/band_4/red': '4',
                    '5/band_5/nir': '5',
                    '6/band_6/swir1': '6',
                    '7/band_7/swir2': '7'}
            }
        where: measurement_description is derived from measurement name and alias attributes
    """

    proddict = defaultdict(lambda: defaultdict(dict))

    dc = datacube.Datacube(config=config)
    products = dc.list_products()
    # products = products[~products['name'].str.contains("archived")]  # TODO this is a kludge/workaround
    measurements = dc.list_measurements()
    measurements.reset_index(inplace=True)
    display_columns = ['name', 'description']
    products = products[display_columns]
    display_columns = ['measurement', 'aliases', 'product']
    measurements = measurements[display_columns]
    # measurements = measurements[~measurements['product'].str.contains('archived')] # TODO this is a kludge/workaround

    products.set_index(['name'], inplace=True, drop=False)
    measurements.set_index(['product'], inplace=True, drop=False)

    prodmeas = measurements.join(products, how='left')
    prodmeas['meas_desc'] = prodmeas[['measurement', 'aliases']].apply(lambda x: measurement_desc(*x), axis=1)

    for row in prodmeas.itertuples():
        # TODO - what if description is NA
        description = '{} ({})'.format(row.description, row.name)
        proddict[description]['product'] = row.product
        proddict[description]['measurements'][row.meas_desc] = row.measurement

    return proddict


def lcase_dict(adict):
    """
    Convert the keys in a dict to lowercase (if they're strings).

    :param dict adict: The dict.

    :rtype: dict
    """
    ret_dict = {}
    for k, v in adict.items():
        try:
            ret_dict[k.lower()] = v
        except TypeError:
            ret_dict[k] = v

    return ret_dict


def measurement_desc(measurement, aliases):
    """
    Generate measurement descriptions from measurement name and aliases.

    :param str measurement: Measurement name.
    :param list aliases: List of aliases or NaN.

    :rtype: str
    """
    try:
        if pd.isnull(aliases):
            return measurement
    except ValueError:  # Got a list
        pass

    if measurement in aliases:  # Assumes a list...
        del aliases[aliases.index(measurement)]

    # return '/'.join([measurement]+aliases) #Assumes a list...
    return '{} ({})'.format(measurement, '/'.join(aliases))


def run_query(query, config=None):
    """
    Load and return the data.

    :param dict query: Query.
    :param str config: Datacube config filepath or None.

    :return: Data.
    :rtype: xarray.Dataset

    :raise NoDataError: No data found for query

    """

    # noinspection PyTypeChecker
    dc = datacube.Datacube(config=config, app='QGIS Plugin')

    test_query = {k: query[k] for k in ('product', 'time', 'x', 'y', 'crs')}
    test_query = Query(**test_query)
    datasets = dc.index.datasets.search_eager(**test_query.search_terms)

    if not datasets:
        raise NoDataError('No datasets found for query:\n{}'.format(str(query)))

    data = dc.load(**query)

    if not data.variables:
        raise NoDataError('No data found for query:\n{}'.format(str(query)))

    return data


def str_snip(str_to_snip, max_len, suffix='...'):
    """
    Shorten a string to a certain length and add a suffix.

    :param str str_to_snip: String to snip.
    :param int max_len: Maximum length of returned string.
    :param suffix: Suffix to append to returned string after it has been snipped.
    :return:  Snipped string
    :rtype: str
    """
    snip_len = max_len - len(suffix)
    snipped = str_to_snip if len(str_to_snip) <= max_len else str_to_snip[:snip_len]+suffix
    return snipped


def upcast(dataset, old_dtype):
    """
    Upcast to next dtype of same kind, i.e. from int to int16

    :param xarray.Dataset dataset: Dataset to cast.
    :param old_dtype: Data type object or string.
    :type old_dtype: Union(numpy.dtype, str)
    :return: Tuple of upcast Dataset and new dtype
    :rtype: tuple(xarray.Dataset, numpy.dtype)
    """

    old_dtype = np.dtype(old_dtype)  # Ensure old dtype is an np.dtype instance (i.e. not a string)
    dtype = np.dtype(old_dtype.kind + str(old_dtype.itemsize * 2))

    # dataset.astype strips attrs, so save them
    dataset_attrs = dataset.attrs
    datavar_attrs = {var: val.attrs for var, val in dataset.data_vars.items()}

    # Upcast
    dataset = dataset.astype(dtype)  # loses attrs

    # Re-add attrs
    dataset.attrs.update(**dataset_attrs)
    for var, val in dataset.data_vars.items():
        val.attrs.update(**datavar_attrs[var])

    return dataset, dtype


def update_tags(filename, bidx=0, ns=None, **tags):
    """
    Update raster metadata tags.

    :param str filename: Raster to update.
    :param bidx: Index of band to be updated.
    :param str ns: Namespace
    :param dict tags: tags to update
    """
    with rio.open(filename, 'r+') as raster:
        raster.update_tags(bidx=bidx, ns=ns, **tags)


def write_geotiff(filename, dataset, time_index=None, profile_override=None, overwrite=False):
    """
    Write an xarray dataset to a geotiff
        Modified from datacube.helpers.write_geotiff to support:
            - dask lazy arrays,
            - arrays with no time dimension
            - Nodata values
            - Small rasters (row or cols < blocksize)
            - Nodata values
            - dtype checks and upcasting
            - existing output checks
        https://github.com/opendatacube/datacube-core/blob/develop/datacube/helpers.py
        Original code licensed under the Apache License, Version 2.0 (the "License");

    :param str filename: Output filename
    :param xarray.Dataset dataset: xarray dataset containing multiple bands to write to file
    :param int time_index: time index to write to file
    :param dict profile_override: option dict, overrides rasterio file creation options.
    :param bool overwrite: Allow overwriting existing files.

    """

    filepath = Path(filename)
    if filepath.exists() and not overwrite:
        raise RuntimeError('Output file exists "{}"'.format(filename))

    profile_override = profile_override or {}

    dtypes = {val.dtype for val in dataset.data_vars.values()}
    assert len(dtypes) == 1  # Check for multiple dtypes
    dtype = dtypes.pop()

    if not check_dtype(dtype):  # Check for invalid dtypes
        dataset, dtype = upcast(dataset, dtype)

    dimx = dataset.dims[dataset.crs.dimensions[1]]
    dimy = dataset.dims[dataset.crs.dimensions[0]]

    profile = GTIFF_DEFAULTS.copy()
    profile.update({
        'width': dimx,
        'height': dimy,
        'transform': dataset.affine,
        'crs': dataset.crs.crs_str,
        'count': len(dataset.data_vars),
        'dtype': str(dtype)
    })
    profile.update(profile_override)
    profile = lcase_dict(profile)

    blockx = profile.get('blockxsize')
    blocky = profile.get('blockysize')
    if (blockx and blockx > dimx) or (blocky and blocky > dimy):
        del profile['blockxsize']
        del profile['blockysize']
        profile['tiled'] = False

    with rio.open(str(filename), 'w', **profile) as dest:
        for bandnum, data in enumerate(dataset.data_vars.values(), start=1):
            try:
                nodata = data.nodata
                profile.update({'nodata': nodata})
            except AttributeError:
                pass

            if time_index is None:
                data = data.data
            else:
                data = data.isel(time=time_index).data

            if isinstance(data, dask.array.Array):
                data = data.compute()

            dest.write(data, bandnum)


def write_netcdf(dataset, filename, overwrite=False, *args, **kwargs):
    """
    Write an xarray dataset to a NetCDF

    :param str filename: Output filename
    :param xarray.Dataset dataset: xarray dataset containing multiple bands to write to file
    :param bool overwrite: Allow overwriting existing files.
    :param args: Positional arguments to pass to datacube.storage.storage.write_dataset_to_netcdf.
    :param kwargs: Keyword arguments to pass to datacube.storage.storage.write_dataset_to_netcdf.
    """
    filepath = Path(filename)

    if filepath.exists() and overwrite:
        filepath.unlink()

    _write_dataset_to_netcdf(dataset, filename, *args, **kwargs)
