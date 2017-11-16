# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DataCubeQuery
                                 A QGIS plugin
 Query and view data stored in an Open Data Cube (https://www.opendatacube.org)
                              -------------------
        begin                : 2017-11-09
        copyright            : (C) 2017 by Geoscience Australia
        email                : luke.pinner@ga.gov.au
 ***************************************************************************/

 This script initializes the plugin, making it known to QGIS.
"""

__author__ = 'Geoscience Australia'
__date__ = '2017-11-09'
__copyright__ = '(C) 2017 by Geoscience Australia'

import qgis.utils

QGIS_VERSION = qgis.utils.QGis.QGIS_VERSION
QGIS_VERSION_INT = qgis.utils.QGis.QGIS_VERSION_INT

# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load DataCubeQuery class from file DataCubeQuery.

        :param iface: A QGIS interface instance.
        :type iface: QgsInterface
        """
    #
    #Monkey patch QGIS2 to mock QGIS 3 API
    if QGIS_VERSION_INT < 30000: #TODO or not TODO - This won't work for dev/preview
                                 #i.e QGIS 2.99...
        if QGIS_VERSION_INT >= 21400:
            try:
                import qgis2compat.apicompat
            except ImportError:
                message = ('The DataCubeQuery Plugin uses the QGIS2compat plugin. '
                           'Please install it with the plugin manager and '
                           'restart QGIS.')
                raise ImportError(message)
        else:
            message = ('The DataCubeQuery Plugin requires QGIS >=2.14')
            raise RuntimeError(message)


    from .plugin import DataCubeQueryPlugin
    return DataCubeQueryPlugin()
