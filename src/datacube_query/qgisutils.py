import os

from qgis.core import QgsMessageLog
from qgis.PyQt.QtGui import QIcon

class LOGLEVEL(object): #for some reason an Enum segfaults QGIS?!?!?
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


def log_message(message,
                level=QgsMessageLog.INFO,
                translator=None):

    title = "Open Data Cube Query"
    if translator is not None:
        message = translator(message, message)

    QgsMessageLog.logMessage(message, title, level)


