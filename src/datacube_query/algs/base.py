""""""
__author__ = 'Geoscience Australia'
__date__ = '2018-01-04'
__copyright__ = '(C) 2018 by Geoscience Australia'

# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

from qgis.core import QgsProcessingAlgorithm
from qgis.PyQt.QtCore import QCoreApplication

from ..qgisutils import get_icon, log_message


class BaseAlgorithm(QgsProcessingAlgorithm):

    def __init__(self):
        QgsProcessingAlgorithm.__init__(self)

    def icon(self):
        return get_icon('opendatacube.png')

    def createInstance(self, config=None):
        return self.__class__(config)

    def name(self):
        return self.__class__.__name__

    def tr(self, string, context=None):
        if context is None:
            context = self.name()
        return QCoreApplication.translate(context, string)
