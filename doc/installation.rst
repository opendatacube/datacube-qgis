Installation
------------

Australian NCI users
~~~~~~~~~~~~~~~~~~~~
The plugin is installed in a QGIS environment on the NCI. See the `DEA documentation`_ for more details


Prerequisites
~~~~~~~~~~~~~
- `QGIS`_ 3
- A populated and running local `Open Data Cube`_
  instance [1]_

Linux
.....
Installation with `pip`_:

- Install `QGIS`_ 3 via your distribution package manager
- Install the datacube-core package which will also install the required dependencies

    .. code-block:: bash

        $ pip3 install datacube

Installation with `conda`_:

- Install `miniconda`_ if you haven't already
- Create a QGIS + Data Cube environment

    .. code-block:: bash

        $ conda create  -c conda-forge -n qgiscube python=3.6 qgis=3 datacube
        $ source activate qgiscube
        $ qgis

Windows
.......

Installation with `OSGeo4W`_

- Run `osgeo4w-setup-x86_64.exe` and select Advanced install
- Install QGIS 3.x from the Desktop section.
- Download the appropriate `rasterio` wheel from the
  `Unofficial Windows Binaries for Python Extension Packages <https://www.lfd.uci.edu/~gohlke/pythonlibs/#rasterio>`_
  site
- Open an OSGeo4W shell and

    .. code-block:: batch

        C:\> pip3 install <path to download folder>\rasterio-1.0a12-cp36-cp36m-win_amd64.whl
        C:\> pip3 install datacube

    Note: You *may* need to install updated GDAL, numpy and pandas from the above site.


Plugin
~~~~~~

- Download the latest `release`_ of the plugin
- Install the plugin in QGIS using `Plugins | Manage and Install Plugins... | Install from ZIP`


----

.. [1] You can connect to a remote Data Cube with an SSH port forward and sshfs, but this is not covered here.

.. References
.. _conda: https://conda.io
.. _miniconda: https://conda.io/miniconda.html
.. _Open Data Cube: http://datacube-core.readthedocs.io/en/latest
.. _OSGeo4W:  https://trac.osgeo.org/osgeo4w
.. _pip: https://packaging.python.org/tutorials/installing-packages
.. _QGIS: https://qgis.org/en/site/forusers/alldownloads.html#linux
.. _release: https://github.com/lpinner/datacube-qgis/releases
.. _DEA documentation: https://github.com/lpinner/dea-datacube-qgis