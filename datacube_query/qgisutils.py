from collections import defaultdict
from pathlib import Path

from processing.core.ProcessingConfig import ProcessingConfig

from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import QUrl

from .defaults import HELP_URL


def get_help(alg_class):
    """
    Get help URL

    :param str alg_class: Algorithm class name
    :return: help URL
    :rtype: str
    """
    helppath = Path(__file__).parent / 'help/html'
    filepath = helppath / 'algs/{}.html'.format(alg_class.lower())
    url = '{}/algs/{}.html'.format(HELP_URL, alg_class.lower())

    if filepath.exists():
        return QUrl.fromLocalFile(str(filepath)).toString()
    else:
        return url


def get_short_help(alg_class):
    """
    Get help string

    :param str alg_class: Algorithm class name
    :return: help string
    :rtype: str
    """
    filepath = Path(Path(__file__).parent, 'help', '{}.txt'.format(alg_class))
    if filepath.exists():
        with open(filepath) as fp:
            return fp.read()


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
