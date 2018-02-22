from collections import defaultdict
from pathlib import Path

from processing.core.ProcessingConfig import ProcessingConfig

from qgis.PyQt.QtGui import QIcon


def get_help(alg_class):
    """
    Get an icon bitmap as a QIcon

    :param str basename: file name without path
    :return: Icon
    :rtype: qgis.PyQt.QtGui.QIcon
    """
    filepath = Path(Path(__file__).parent, 'help', '{}.txt'.format(alg_class))
    if filepath.exists():
        return open(filepath).read()

    return str(filepath)



def get_icon(basename):
    """
    Get an icon bitmap as a QIcon

    :param str basename: file name without path
    :return: Icon
    :rtype: qgis.PyQt.QtGui.QIcon
    """
    filepath = Path(Path(__file__).parent, 'icons', basename)
    return QIcon(str(filepath))


def get_settings(key=None):
    """
    Get a dict of QGIS settings for a specific key or all

    :param str key: Settings key to get or None
    :return: A setting value or the settings dict
    :rtype: Union(str, bool, int, float, dict)
    """
    settings = defaultdict(dict)
    for setting in ProcessingConfig.settings.values():
        settings[setting.group][setting.name] = setting.value

    if key:
        return settings[key]
    else:
        return settings
