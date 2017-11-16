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

import os
import sys
import inspect

from processing.core.Processing import Processing
from .provider import DataCubeQueryProvider

cmd_folder = os.path.split(inspect.getfile(inspect.currentframe()))[0]

if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)


class DataCubeQueryPlugin:

    def __init__(self):
        self.provider = DataCubeQueryProvider()

    def initGui(self):
        Processing.addProvider(self.provider)

    def unload(self):
        Processing.removeProvider(self.provider)
