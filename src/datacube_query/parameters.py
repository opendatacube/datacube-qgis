from processing.core.parameters import Parameter

# noinspection PyUnresolvedReferences
# pylint: disable=unused-import
from .widgets import WrapperDateRange


class ParameterDateRange(Parameter):
    """  """
    # TODO
    def __init__(self, name, description, default=None, optional=False):
        wrapper = {'widget_wrapper': 'widgets.WrapperDateRange'}
        Parameter.__init__(name, description, default, optional) # Q3+, metadata=wrapper)
        self.setMetadata(wrapper)

    # noinspection PyMethodMayBeStatic
    # pylint: disable=no-self-use
    def type(self):
        return 'date_range'


class ParameterProducts(Parameter):
    """  """
    # TODO
    def __init__(self, name, description, default=None, optional=False):
        wrapper = {'widget_wrapper': 'widgets.WrapperDateRange'}
        Parameter.__init__(name, description, default, optional) # Q3+, metadata=wrapper)
        self.setMetadata(wrapper)

    # noinspection PyMethodMayBeStatic
    # pylint: disable=no-self-use
    def type(self):
        return 'products_measurements'

