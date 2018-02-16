""""""
__author__ = 'Geoscience Australia'
__date__ = '2018-01-04'
__copyright__ = '(C) 2018 by Geoscience Australia'

# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

from qgis.core import QgsProcessingAlgorithm
from qgis.PyQt.QtCore import QCoreApplication

from ..defaults import SETTINGS_GROUP
from ..qgisutils import get_icon, get_settings


class BaseAlgorithm(QgsProcessingAlgorithm):
    """Super class for multiple Data Cube algorithms"""

    def __init__(self):
        super().__init__()

    def get_settings(self):
        return get_settings(SETTINGS_GROUP)

    def icon(self):
        return get_icon('opendatacube.png')

    def name(self):
        return self.__class__.__name__

    def tr(self, string, context=None):
        if context is None:
            context = self.name()
        return QCoreApplication.translate(context, string)
