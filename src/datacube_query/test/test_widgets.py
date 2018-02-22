import pytest

import json
from datacube_query import widgets
from qgis.PyQt.QtWidgets import QApplication

# TODO user interaction with pytest-qt qtbot fixture??? http://pytest-qt.readthedocs.io


def test_daterange():

    app = QApplication([])

    test_data = ['2001-01-01', '2001-12-31']

    w = widgets.WidgetDateRange()
    w.set_value(test_data)

    assert json.loads(w.value()) == test_data
    app.exit(0)


def test_products():
    from collections import OrderedDict
    import json

    app = QApplication([])

    test_data = OrderedDict([['ls5_nbar_albers', ['blue', 'green', 'red', 'nir', 'swir1', 'swir2']],
                            ['ls7_nbar_albers', ['blue', 'green', 'red', 'nir', 'swir1', 'swir2']],
                            ['ls8_nbar_albers', ['coastal_aerosol', 'blue', 'green', 'red', 'nir', 'swir1', 'swir2']]])

    w = widgets.WidgetProducts(test_data)

    test_selected = OrderedDict([['ls5_nbar_albers', ['red']],
                            ['ls7_nbar_albers', ['green']],
                            ['ls8_nbar_albers', ['blue', 'green', 'red']]])
    w.set_value(test_selected)

    assert json.loads(w.value()) == test_selected
    app.exit(0)
