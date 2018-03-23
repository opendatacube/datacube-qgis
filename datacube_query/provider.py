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

        # TODO??? Plugin system to dynamically load algs,
        # maybe with setuptools entry_points & pkg_resources.iter_entry_points
        self.algs = [DataCubeQueryAlgorithm]
        self.settings = []

    def load(self):
        # Setting descs prefixed with number as processing framework sorts alphabetically by desc
        self.settings = [
            Setting(SETTINGS_GROUP,
                    'datacube_config_file',
                    self.tr("1. Open Data Cube database config file"),
                    default='',
                    valuetype=Setting.FILE),
            Setting(SETTINGS_GROUP,
                    'datacube_max_datasets',
                    self.tr("2. Maximum datasets to load in a query"),
                    default=500,
                    valuetype=Setting.INT),
            Setting(SETTINGS_GROUP,
                    'datacube_gtiff_options',
                    self.tr("3. GeoTiff Creation Options"),
                    default=json.dumps(GTIFF_DEFAULTS),
                    valuetype=Setting.STRING),
            Setting(SETTINGS_GROUP,
                    'datacube_build_overviews',
                    self.tr("4. Build GeoTiff Overviews"),
                    default=True,
                    valuetype=None),
            Setting(SETTINGS_GROUP,
                    'datacube_gtiff_ovr_options',
                    self.tr("5. GeoTiff Overview Options"),
                    default=json.dumps(GTIFF_OVR_DEFAULTS),
                    valuetype=Setting.STRING),
            Setting(SETTINGS_GROUP,
                    'datacube_calculate_statistics',
                    self.tr("6. Calculate GeoTiff statistics"),
                    default=True,
                    valuetype=None),
            Setting(SETTINGS_GROUP,
                    'datacube_approx_statistics',
                    self.tr("7. Statistics will be calculated approximately (faster)"),
                    default=True,
                    valuetype=None),
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
