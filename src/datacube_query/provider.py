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


"""

__author__ = 'Geoscience Australia'
__date__ = '2017-11-09'
__copyright__ = '(C) 2017 by Geoscience Australia'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import json

from qgis.core import QgsProcessingProvider
from processing.core.ProcessingConfig import ProcessingConfig, Setting

from .algs.query import DataCubeQueryAlgorithm

from .qgisutils import get_icon
from .defaults import (GTIFF_OVR_DEFAULTS, GTIFF_DEFAULTS, SETTINGS_GROUP)


class DataCubeQueryProvider(QgsProcessingProvider):

    ID = 'opendatacube'
    NAME = 'Open Data Cube'
    DESCRIPTION = 'Open Data Cube Algorithms'

    def __init__(self):
        super().__init__()

        # Activate provider by default
        self.activate = True

        self.algs = [DataCubeQueryAlgorithm]
        self.settings = []

    def load(self):

        self.settings = [
            Setting(SETTINGS_GROUP,
                    'datacube_config_file',
                    self.tr("Open Data Cube database config file"),
                    default='',
                    valuetype=Setting.FILE),
            Setting(SETTINGS_GROUP,
                    'datacube_build_overviews',
                    self.tr("Build GeoTiff Overviews"),
                    default=True,
                    valuetype=None),
            Setting(SETTINGS_GROUP,
                    'datacube_gtiff_options',
                    self.tr("GeoTiff Creation Options"),
                    default=json.dumps(GTIFF_DEFAULTS),
                    valuetype=Setting.STRING),
            Setting(SETTINGS_GROUP,
                    'datacube_gtiff_ovr_options',
                    self.tr("GeoTiff Overview Options"),
                    default=json.dumps(GTIFF_OVR_DEFAULTS),
                    valuetype=Setting.STRING),
        ]


        ProcessingConfig.settingIcons[DataCubeQueryProvider.NAME] = self.icon()
        for setting in self.settings:
            ProcessingConfig.addSetting(setting)

        ProcessingConfig.readSettings()
        self.refreshAlgorithms()

        return True

    def unload(self):
        for setting in self.settings:
            ProcessingConfig.removeSetting(setting.name)

    def name(self):
        return DataCubeQueryProvider.NAME

    def getDescription(self):
        return DataCubeQueryProvider.DESCRIPTION

    def icon(self):
        return get_icon('opendatacube.png')

    def id(self):
        return DataCubeQueryProvider.ID

    def loadAlgorithms(self):
        for alg in self.algs:
            self.addAlgorithm(alg())
