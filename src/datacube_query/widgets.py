import os

from processing.gui.wrappers import WidgetWrapper
from qgis.PyQt import uic

_ui_path = os.path.join(os.path.dirname(__file__), 'ui')


WIDGET, BASE = uic.loadUiType(
    os.path.join(_ui_path, 'widget_daterange.ui'))


class WidgetDateRange(BASE, WIDGET):

    def __init__(self, options):
        super(DateRangeWidget, self).__init__(None)
        self.setupUi(self)

    def value(self):
        return self.date_start.toPlainText(), self.date_end.toPlainText()


class WrapperDateRange(WidgetWrapper):
    def _panel(self, options):
        return WidgetDateRange(options)
