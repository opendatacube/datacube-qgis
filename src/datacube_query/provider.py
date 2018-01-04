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

from qgis.core import QgsApplication, QgsProcessingProvider
from processing.core.ProcessingConfig import ProcessingConfig, Setting

from .algs.query import DataCubeQueryAlgorithm
from .algs.list_products import DataCubeListAlgorithm

from .qgisutils import get_icon
from .defaults import (GTIFF_OVR_DEFAULTS, GTIFF_DEFAULTS)


class DataCubeQueryProvider(QgsProcessingProvider):

    ID = 'opendatacube'
    NAME = 'Open Data Cube'
    DESCRIPTION = 'Open Data Cube Algorithms'

    def __init__(self):

        QgsProcessingProvider.__init__(self)

        self._icon = get_icon('opendatacube.png')

        # TODO - add GDAL/rio format and overview creation options as settings
        self.settings = [
            Setting(DataCubeQueryProvider.DESCRIPTION,
                    'Activate',
                    self.tr('Activate provider'),
                    default=True,
                    valuetype=Setting.FILE),
            Setting(DataCubeQueryProvider.DESCRIPTION,
                    'datacube_config_file',
                    self.tr("Open Data Cube database config file"),
                    default='',
                    valuetype=Setting.FILE),
            Setting(DataCubeQueryProvider.DESCRIPTION,
                    'build_overviews',
                    self.tr("Build GeoTiff Overviews"),
                    default=True,
                    valuetype=None),
            Setting(DataCubeQueryProvider.DESCRIPTION,
                    'gtiff_options',
                    self.tr("GeoTiff Creation Options"),
                    default=json.dumps(GTIFF_DEFAULTS),
                    valuetype=Setting.STRING),
            Setting(DataCubeQueryProvider.DESCRIPTION,
                    'gtiff_ovr_options',
                    self.tr("GeoTiff Overview Options"),
                    default=json.dumps(GTIFF_OVR_DEFAULTS),
                    valuetype=Setting.STRING),
        ]

        # Activate provider by default
        self.activate = True

        # Load algorithms
        self.algs = [DataCubeQueryAlgorithm(),
                     DataCubeListAlgorithm()]
        for alg in self.algs:
            alg.provider = self

    def load(self):
        ProcessingConfig.settingIcons[DataCubeQueryProvider.NAME] = self._icon
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
            self.addAlgorithm(alg)
