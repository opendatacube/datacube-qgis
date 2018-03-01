from processing.gui.wrappers import WidgetWrapper
from .widgets import (
    WidgetDateRange,
    WidgetProducts)

class WrapperBase(WidgetWrapper):

    def setValue(self, data):
        self.widget.set_value(data)

    def value(self):
        return self.widget.value()


class WrapperDateRange(WrapperBase):

    def createWidget(self, *args, **kwargs):
        return WidgetDateRange(*args, **kwargs)


class WrapperProducts(WrapperBase):

    def createWidget(self, items=None, *args, **kwargs):
        return WidgetProducts(items, *args, **kwargs)


