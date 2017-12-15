import os

from qgis.core import QgsMessageLog
from qgis.PyQt.QtGui import QIcon


def get_icon(basename):
    filepath = os.path.join(
        os.path.dirname(__file__),
        'icons',
        basename
    )
    return QIcon(filepath)


def log_message(message, title=None,
                level=QgsMessageLog.INFO,
                translator=None):

    if translator is not None:
        message = translator(message, message)
        if title is not None:
            title = translator(title, title)

    QgsMessageLog.logMessage(message, title, level)


