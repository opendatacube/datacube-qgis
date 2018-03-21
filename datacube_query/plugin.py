from qgis.core import QgsApplication
from .provider import DataCubeQueryProvider
from .qgisutils import get_icon


class DataCubeQueryPlugin:

    def __init__(self, iface):
        self.iface = iface
        self.provider = DataCubeQueryProvider()

    def initGui(self):
        # noinspection PyArgumentList
        QgsApplication.processingRegistry().addProvider(self.provider)

    def unload(self):
        # noinspection PyArgumentList
        QgsApplication.processingRegistry().removeProvider(self.provider)

    def getIcon(self):
        return get_icon('opendatacube.png')

