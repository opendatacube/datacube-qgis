import os
from collections import defaultdict

from processing.core.ProcessingConfig import ProcessingConfig

from qgis.core import QgsMessageLog
from qgis.PyQt.QtGui import QIcon


class LOGLEVEL(object): #TODO for some reason using an Enum here segfaults QGIS?!?!?
    INFO = QgsMessageLog.INFO
    WARNING = QgsMessageLog.WARNING
    CRITICAL = QgsMessageLog.CRITICAL


def get_icon(basename):
    filepath = os.path.join(
        os.path.dirname(__file__),
        'icons',
        basename
    )
    return QIcon(filepath)


def get_settings(key=None):
    '''Return a dict of QGIS settings for a specific key or all'''
    settings = defaultdict(dict)
    for setting in ProcessingConfig.settings.values():
        settings[setting.group][setting.name] = setting.value

    if key:
        return settings[key]
    else:
        return settings


def log_message(message,
                level=QgsMessageLog.INFO,
                translator=None):

    title = "Open Data Cube Query"
    if translator is not None:
        message = translator(message, message)

    QgsMessageLog.logMessage(message, title, level)


