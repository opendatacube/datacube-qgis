import os

from processing.gui.wrappers import WidgetWrapper
from qgis.PyQt import uic

_ui_path = os.path.join(os.path.dirname(__file__), 'ui')


WIDGET_DATE_RANGE, BASE_DATE_RANGE = uic.loadUiType(
    os.path.join(_ui_path, 'widget_daterange.ui'))

WIDGET_PRODUCTS, BASE_PRODUCTS = uic.loadUiType(
    os.path.join(_ui_path, 'widget_product.ui'))


class WidgetDateRange(BASE_DATE_RANGE, WIDGET_DATE_RANGE):

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.setupUi(self)

        self._dateformat = 'yyyy-MM-dd'

        self._start = self.date_start.dateTime().toString(self._dateformat)
        self._end = self.date_end.dateTime().toString(self._dateformat)

        self.date_start.valueChanged.connect(self.update_start)
        self.date_end.valueChanged.connect(self.update_end)

    def update_start(self, qdatetime):
        self._start = qdatetime.toString(self._dateformat)

    def update_end(self, qdatetime):
        self._end = qdatetime.toString(self._dateformat)

    def value(self):
        return '|'.join([self._start, self._end])


class WrapperDateRange(WidgetWrapper):

    def _panel(self, *args, **kwargs):
        return WidgetDateRange(*args, **kwargs)

    def createWidget(self, *args, **kwargs):
        return self._panel(*args, **kwargs)

    def value(self):
        return self.widget.value()



class WidgetProducts(BASE_PRODUCTS, WIDGET_PRODUCTS):

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.setupUi(self)

    def value(self):
        return "PRODUCT", "MEASUREMENTS"


class WrapperProducts(WidgetWrapper):

    def _panel(self, *args, **kwargs):
        print(self.__class__)
        return WidgetProducts(*args, **kwargs)

    def createWidget(self, *args, **kwargs):
        return self._panel(*args, **kwargs)