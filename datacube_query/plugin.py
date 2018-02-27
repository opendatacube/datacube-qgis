# -*- coding: utf-8 -*-

"""
/***************************************************************************
 DataCubeQuery
                                 A QGIS plugin
 Query and view data stored in an Open Data Cube (https://www.opendatacube.org)
                              -------------------
        begin                : 2017-11-09
        copyright            : (C) 2017 by Geoscience Australia
        email                : luke dot pinner at ga .gov.au
 ***************************************************************************/


"""

__author__ = 'Geoscience Australia'
__date__ = '2017-11-09'
__copyright__ = '(C) 2017 by Geoscience Australia'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from qgis.core import QgsApplication
from .provider import DataCubeQueryProvider
from .qgisutils import get_icon


class DataCubeQueryPlugin:

    def __init__(self, iface):
        self.iface = iface
        # TODO figure out why a duplicate provider is registered
        self.provider = DataCubeQueryProvider()

    def initGui(self):
        # noinspection PyArgumentList
        QgsApplication.processingRegistry().addProvider(self.provider)

    def unload(self):
        # noinspection PyArgumentList
        QgsApplication.processingRegistry().removeProvider(self.provider)

    def getIcon(self):
        return get_icon('opendatacube.png')

