"""
 This script initializes the plugin, making it known to QGIS.
"""

# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load DataCubeQuery class from file DataCubeQuery.

        :param iface: A QGIS interface instance.
        :type iface: QgsInterface
    """
    from .plugin import DataCubeQueryPlugin
    return DataCubeQueryPlugin(iface)

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
