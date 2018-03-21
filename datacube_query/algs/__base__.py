from qgis.core import QgsProcessingAlgorithm
from qgis.PyQt.QtCore import QCoreApplication

from ..defaults import SETTINGS_GROUP
from ..qgisutils import (get_help, get_icon, get_settings, get_short_help)


class BaseAlgorithm(QgsProcessingAlgorithm):
    """Super class for multiple Data Cube algorithms"""

    def __init__(self):
        super().__init__()

    def get_settings(self):
        return get_settings(SETTINGS_GROUP)

    def helpUrl(self):
        return get_help(self.__class__.__name__)

    def icon(self):
        return get_icon('opendatacube.png')

    def name(self):
        return self.__class__.__name__

    def shortHelpString(self):
        return get_short_help(self.__class__.__name__)

    def tr(self, string, context=None):
        if context is None:
            context = self.name()
        return QCoreApplication.translate(context, string)
