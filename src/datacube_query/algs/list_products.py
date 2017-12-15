""""""
__author__ = 'Geoscience Australia'
__date__ = '2017-11-09'
__copyright__ = '(C) 2017 by Geoscience Australia'

# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.ProcessingConfig import ProcessingConfig
from processing.core.outputs import OutputHTML
from processing.core.parameters import ParameterSelection
from processing.tools.system import getTempFilename

from ..qgisutils import (get_icon, log_message)
from ..utils import (get_products_and_measurements, get_products)


class DataCubeListAlgorithm(GeoAlgorithm):
    """This is TODO

    All Processing algorithms should extend the GeoAlgorithm class.
    """
    PARAM_PRODUCT = 'Product type'
    OUTPUT_HTML = 'Output report'
    ALL = 'All'

    def __init__(self):
        GeoAlgorithm.__init__(self)

        self._icon = get_icon('opendatacube.png')
        self.products = {}
        self.param_options = ["All"]
        self.config_file = None

    def defineCharacteristics(self):
        """Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # The name that the user will see in the toolbox
        self.name = 'Data Cube List Products'

        self.addParameter(ParameterSelection(
            self.PARAM_PRODUCT,
            self.tr(self.PARAM_PRODUCT),
            options=["All"], default="All"
        ))

        self.addOutput(OutputHTML(self.OUTPUT_HTML, self.tr(self.OUTPUT_HTML)))

        # The branch of the toolbox under which the algorithm will appear
        self.group = 'Data Cube Helpers'  # TODO can there be a top level alg, not under a folder?

    def checkBeforeOpeningParametersDialog(self):
        config_file = ProcessingConfig.getSetting('datacube_config_file')
        self.config_file = config_file if config_file else None

        # invert dict mapping
        products = get_products(config=self.config_file)
        self.products = {v['description']: k for k, v in products.items()}
        product_desc = sorted(self.products.keys())
        for param in self.parameters:
            if isinstance(param, ParameterSelection) and param.name == self.PARAM_PRODUCT:
                param.options = ['All']+product_desc
                self.param_options = param.options

    def processAlgorithm(self, progress):
        """Here is where the processing itself takes place."""
        output_html = getTempFilename('.html')
        param_opt = self.getParameterValue(self.PARAM_PRODUCT)
        product = self.param_options[param_opt]
        product = self.products.get(product, None)
        table = get_products_and_measurements(product, self.config_file)

        with open(output_html, 'w') as html:
            html.write(table.to_html())
            # html.write(table.style.render())
            # html.write(table.style.set_table_styles(styles).render())

        self.setOutputValue(self.OUTPUT_HTML, output_html)
        return {self.OUTPUT_HTML: output_html}
