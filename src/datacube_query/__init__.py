# -*- coding: utf-8 -*-
"""
 This script initializes the plugin, making it known to QGIS.
"""

__author__ = 'Geoscience Australia'
__date__ = '2017-11-09'
__copyright__ = '(C) 2017 by Geoscience Australia'


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load DataCubeQuery class from file DataCubeQuery.

        :param iface: A QGIS interface instance.
        :type iface: QgsInterface
    """
    from .plugin import DataCubeQueryPlugin
    return DataCubeQueryPlugin()
