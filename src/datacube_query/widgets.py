import os
import json

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
        return json.dumps([self._start, self._end])


class WrapperDateRange(WidgetWrapper):

    def createWidget(self, *args, **kwargs):
        return WidgetDateRange(*args, **kwargs)

    def value(self):
        return self.widget.value()


class WidgetProducts(BASE_PRODUCTS, WIDGET_PRODUCTS):

    def __init__(self, data=None, *args, **kwargs):
        super().__init__()
        self.setupUi(self)

        self._data = None
        self._product = ''
        self._measurements = []

        self.set_data(data)

        self.cbx_products.currentTextChanged.connect(self.update_measurements)

    def value(self):
        return json.dumps([self._product, self._measurements])

    def set_data(self, data):
        self.cbx_products.clear()
        self.cbx_measurements.clear()

        self._data = data if data else {}

        for product in self._data:
            self.cbx_product.addItem(product)

        self.update_measurements()

    def update_measurements(self):
        self.cbx_measurements.clear()
        self._product = self.cbx_products.currentText()

        measurements = self._data.get(self._product, [])
        for measurement in measurements:
            self.cbx_measurements.addItem(measurement)



class WrapperProducts(WidgetWrapper):

    def createWidget(self, *args, **kwargs):
        return WidgetProducts(*args, **kwargs)

    def value(self):
        return self.widget.value()

    def set_data(self, data):
        self.widget.set_data(data)