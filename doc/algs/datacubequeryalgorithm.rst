Data Cube Query
===============
A QGIS 3 processing plugin to query and return data in GeoTIFF format from an Open Data Cube.

Parameters
..........

``Products and measurements`` [selection]
    Select one or more products and/or individual product measurements.

    If the algorithm can't connect to a running Data Cube instance, this list will be empty and the
    warning message "Unable to connect to a running Data Cube instance" will be displayed.


``Date range`` [date] (Optional)
    Restrict query by start and end date.


``Query extent (xmin, xmax, ymin, ymax)`` [extent]
    Restrict query to specified extent.

    Click the `[...]` button to the right of the parameter to select the extent
    from a layer/map canvas extent or by drawing a rectangle.

``Output CRS`` [crs] (Optional)
  Coordinate reference system for outputs

  Default: *Input Product CRS*

    Note: This parameter is *required* for products that do not have a CRS defined.

``Output pixel resolution`` [number] (Optional)
  Output pixel resolution

  Default: *Input Product resolution*

    Note: This parameter is *required* for products that do not have a defined resolution.

``Group data by`` [combobox]
  Observation grouping method. One of Solar Day or Time.

  For EO-specific datasets that are based around scenes, the time dimension can be reduced to the day level,
  using solar day to keep scenes together.


  Default: *Solar Day*


Outputs
.......

``Output directory`` [directory]
    The output directory.


Notes
.....

If a selected product does not have a CRS or pixel resolution defined and you do not specify
either, that product will be skipped when the algorithm is run and a warning message will be shown in
the log.

If you specify an output CRS or resolution, this will be applied to all products you select, not
just those that do not have a CRS or resolution defined.
