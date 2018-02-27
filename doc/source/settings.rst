Settings
--------
The plugin can be configured through the QGIS Settings | Options... menu in the
Processing | Providers | Open Data Cube section.

.. image:: images/settings_dialog.png

Open Data Cube database config file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
:Type:  File path
:Notes:
    Path to an Open Data Cube
    `config file <http://datacube-core.readthedocs.io/en/stable/ops/db_setup.html#create-configuration-file>`_.
    If not set, the Open Data Cube library will look for a config file in some
    `default locations <http://datacube-core.readthedocs.io/en/stable/ops/config.html#runtime-config-doc>`_.

Maximum datasets to load in a query
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
:Type: Integer
:Notes:
    The plugin can and will load every available dataset that matches your query.
    This can cause memory issues and will certainly be slow for large numbers of datasets.
    If a query will return data from more than the maximum specified in this settings,
    the query will not execute and a message will be displayed.
:Default: 500

Build GeoTiff Overviews
~~~~~~~~~~~~~~~~~~~~~~~
:Type: Checkbox
:Notes:
    If checked, the plugin will build overviews/pyramids for the returned data to speed up rendering.
:Default: checked

GeoTiff Creation Options
~~~~~~~~~~~~~~~~~~~~~~~~
:Type: JSON
:Notes:
    A valid JSON string that contains ``rasterio``
    `creation options <https://mapbox.github.io/rasterio/topics/image_options.html#creation-options>`_.
:Default:
    ``{"driver": "GTiff", "interleave": "band", "tiled": true, "blockxsize": 256, "blockysize": 256, "compress": "lzw", "predictor": 1, "tfw": false, "jpeg_quality": 75, "profile": "GDALGeoTIFF", "bigtiff": "IF_NEEDED", "geotiff_keys_flavor": "STANDARD", "photometric": "RGBA"}``

GeoTiff Overview Options
~~~~~~~~~~~~~~~~~~~~~~~~
:Type: JSON
:Notes:
    A valid JSON string to configure ``rasterio``
    `overviews <https://mapbox.github.io/rasterio/topics/overviews.html>`_.
:Default:
    ``{"resampling": "average", "factors": [2, 4, 8, 16, 32], "internal_storage": true}``
