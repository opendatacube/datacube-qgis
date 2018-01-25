from qgis.core import (QgsProcessingParameterString,)

class ParameterDateRange(QgsProcessingParameterString):
    """ Date range parameter that returns a '|' separated date range string in 'yyyy-MM-dd|yyy-MM-dd' format.
        e.g. 2017-01-01|2017-12-31

        Null values are represented as empty strings,
        e.g. '|', '2017-01-01|' or '|2017-12-31'
    """
    # TODO - validate start <= end
    def __init__(self, name, description, *args, **kwargs):
        wrapper = {'widget_wrapper': 'datacube_query.widgets.WrapperDateRange'}
        QgsProcessingParameterString.__init__(self, name, description, *args, **kwargs)
        self.setMetadata(wrapper)

    def type(self):
        return 'date_range'


class ParameterProduct(QgsProcessingParameterString):
    """  """
    # TODO
    def __init__(self, name, description, *args, **kwargs):
        wrapper = {'widget_wrapper': 'datacube_query.widgets.WrapperProducts'}
        QgsProcessingParameterString.__init__(self, name, description, *args, ** kwargs)
        self.setMetadata(wrapper)

    # noinspection PyMethodMayBeStatic
    # pylint: disable=no-self-use
    def type(self):
        return 'product_measurements'

