from collections import defaultdict
import os
import json

from processing.gui.wrappers import WidgetWrapper

from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt, QDate
from qgis.PyQt.QtWidgets import QTreeWidgetItem, QTreeWidgetItemIterator

_ui_path = os.path.join(os.path.dirname(__file__), 'ui')

WIDGET_DATE_RANGE, BASE_DATE_RANGE = uic.loadUiType(
    os.path.join(_ui_path, 'widget_daterange.ui'))

WIDGET_PRODUCT, BASE_PRODUCT = uic.loadUiType(
    os.path.join(_ui_path, 'widget_product.ui'))

class WrapperBase(WidgetWrapper):

    def setValue(self, data):
        self.widget.set_data(data)

    def value(self):
        return self.widget.value()


class WrapperDateRange(WrapperBase):

    def createWidget(self, *args, **kwargs):
        return WidgetDateRange(*args, **kwargs)


class WrapperProducts(WrapperBase):

    def createWidget(self, *args, **kwargs):
        return WidgetProducts(*args, **kwargs)


class WidgetDateRange(BASE_DATE_RANGE, WIDGET_DATE_RANGE):

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.setupUi(self)

        self._dateformat = 'yyyy-MM-dd'

        self._start = self.date_start.dateTime().toString(self._dateformat)
        self._end = self.date_end.dateTime().toString(self._dateformat)

        self.date_start.valueChanged.connect(self.update_start)
        self.date_end.valueChanged.connect(self.update_end)

    def set_data(self, data):
        data = data if data else {}
        data = json.loads(data) if isinstance(data, str) else data

        self.date_start.date = QDate.fromString(data[0], self._dateformat)
        self.date_end.date = QDate.fromString(data[1], self._dateformat)

    def update_start(self, qdatetime):
        self._start = qdatetime.toString(self._dateformat)

    def update_end(self, qdatetime):
        self._end = qdatetime.toString(self._dateformat)

    def value(self):
        return json.dumps([self._start, self._end])


class WidgetProducts(BASE_PRODUCT, WIDGET_PRODUCT):

    def __init__(self, data=None, *args, **kwargs):
        super().__init__()
        self.setupUi(self)

        self._data = None
        self.set_data(data)

        # In case we need to implement single product selections only
        # self.tree_products.itemClicked.connect(self.check_item)

    def check_item(self, item, column=0):

        """ Stub for implementing single product selections only"""
        # Get items, check item != clicked item, uncheck non-clicked parents
        pass

    def get_checked(self):
        return self.get_items(flags=QTreeWidgetItemIterator.Checked)

    def get_items(self, item=None, flags=QTreeWidgetItemIterator.All):
        """ Returns an iterator over the tree items. """

        if item is None:
            item = self.tree_products

        twit = QTreeWidgetItemIterator(item, flags)

        while twit.value() is not None: #This 'orrible iteration style offends me greatly
            yield twit.value()
            twit += 1

    def set_selected(self, selected=None): #TODO make sure running alg from history loads all products and selects orig
        pass

    def set_data(self, data=None):
        self.tree_products.clear()

        data = data if data else {}
        self._data = json.loads(data) if isinstance(data, str) else data

        for product, measurements in self._data.items():
            parent = QTreeWidgetItem(self.tree_products)
            parent.setText(0, product)
            parent.setFlags(parent.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)

            for measurement in measurements:
                child = QTreeWidgetItem(parent)
                child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
                child.setText(0, measurement)
                child.setCheckState(0, Qt.Unchecked)

    def get_data(self):
        """ Return checked """
        data = defaultdict(list)

        for item in self.get_checked():
            value = item.text(0)
            parent = item.parent()
            if parent is None:
                _ =data[value]
            else:
                data[parent.text(0)].append(value)

        return data

    def value(self):
        return json.dumps(self.get_data())


# # Stub for alternative TreeView widget using Model-View-Controller (MVC) design pattern
# WIDGET_PRODUCTS, BASE_PRODUCTS = uic.loadUiType(
#     os.path.join(_ui_path, 'widget_products.ui')) # This is a QTreeView, not a QTreeWidget
#
# class WidgetProducts(BASE_PRODUCTS, WIDGET_PRODUCTS):
#
#     def __init__(self, data=None, *args, **kwargs):
#         super().__init__()
#         self.setupUi(self)
#
#         self._data = None

#         self._model = QStandardItemModel()
#
#         self.set_data(data)
#
#     def set_data(self, data=None):
#         self._data = data if data else {}
#         self._model = QStandardItemModel()
#         self.tree_products.setModel(self._model)
#         root = self._model.invisibleRootItem()
#
#         for product, measurements in self._data.items():
#             parent = QStandardItem(product)
#             parent.setFlags(parent.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
#             parent.setCheckState(Qt.Unchecked)
#             root.appendRow(parent)
#
#             for measurement in measurements:
#                 child = QStandardItem(measurement)
#                 child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
#                 #child.setText(0, measurement)
#                 child.setCheckState(Qt.Unchecked)
#                 parent.appendRow(child)
