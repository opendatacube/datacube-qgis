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


class ParameterProducts(QgsProcessingParameterString):
    """ Products and measurements parameter that returns a json encoded dict of
        product strings and measurements list of strings:
            {'product': ['list', 'of', 'measurements']}

        e.g.
            {'ls8_nbar_albers', ['red', 'green', 'blue'],
             'ls8_fc_albers', ['nir']}

    """

    def __init__(self, name, description, *args, **kwargs):
        wrapper = {'widget_wrapper': 'datacube_query.widgets.WrapperProducts'}
        QgsProcessingParameterString.__init__(self, name, description, *args, ** kwargs)
        self.setMetadata(wrapper)

    def type(self):
        return 'product_measurements'

    def set_data(self, data):
        for wrapper in list(self.wrappers.values()):
            wrapper.setValue(data)