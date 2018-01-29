from qgis.core import (QgsProcessingParameterString,)

class ParameterDateRange(QgsProcessingParameterString):
    """ Date range parameter that returns a json encoded list of two date strings,
        [start_date, end_date] in  in 'yyyy-MM-dd' format.

            e.g. ['2017-01-01', '2017-12-31']

        Null values are represented as empty strings,

            e.g. ['', ''], ['2017-01-01', ''] or ['', '2017-12-31']
    """
    # TODO - validate start <= end
    def __init__(self, name, description, *args, **kwargs):
        wrapper = {'widget_wrapper': 'datacube_query.widgets.WrapperDateRange'}
        QgsProcessingParameterString.__init__(self, name, description, *args, **kwargs)
        self.setMetadata(wrapper)

    def type(self):
        return 'date_range'


class ParameterProduct(QgsProcessingParameterString):
    """ Product and measurements parameter that returns a json encoded list of
        product string and measurements list of strings:
            [product, ['list', 'of', 'measurements']]

        e.g.
            ['ls8_nbar_albers', ['red', 'green', 'blue']]
            ['ls8_fc_albers', []]


    """

    def __init__(self, name, description, *args, **kwargs):
        wrapper = {'widget_wrapper': 'datacube_query.widgets.WrapperProducts'}
        QgsProcessingParameterString.__init__(self, name, description, *args, ** kwargs)
        self.setMetadata(wrapper)

        self._products = []
        self._measurements = {}

    # noinspection PyMethodMayBeStatic
    # pylint: disable=no-self-use
    def type(self):
        return 'product_measurements'

    def set_values(self, products, measurements):

        for wrapper in list(self.wrappers.values()):
            w = wrapper.widget
            #self.connectWidgetChangedSignals(w)
            for c in w.findChildren(QWidget):
                print(c.value)
