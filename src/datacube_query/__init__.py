# -*- coding: utf-8 -*-
"""
 This script initializes the plugin, making it known to QGIS.
"""

__author__ = 'Geoscience Australia'
__date__ = '2017-11-09'
__copyright__ = '(C) 2017 by Geoscience Australia'

import qgis.core

QGIS_VERSION = qgis.core.Qgis.QGIS_VERSION
QGIS_VERSION_INT = qgis.core.Qgis.QGIS_VERSION_INT


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load DataCubeQuery class from file DataCubeQuery.

        :param iface: A QGIS interface instance.
        :type iface: QgsInterface
    """
    #
    # Monkey patch QGIS2 to mock QGIS 3 API
    if QGIS_VERSION_INT < 29900:  #29900 = QGIS 3 Dev build, 30000 will be 3.0
        if QGIS_VERSION_INT >= 21400:
            try:
                import qgis2compat.apicompat
            except ImportError:
                message = ('The DataCubeQuery Plugin uses the QGIS2compat plugin. '
                           'Please install it with the plugin manager and '
                           'restart QGIS.')
                raise ImportError(message)
        else:
            message = 'The DataCubeQuery Plugin requires QGIS >=2.14'
            raise RuntimeError(message)

    from .plugin import DataCubeQueryPlugin
    return DataCubeQueryPlugin()
