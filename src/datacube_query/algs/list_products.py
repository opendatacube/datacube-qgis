""""""
__author__ = 'Geoscience Australia'
__date__ = '2017-11-09'
__copyright__ = '(C) 2017 by Geoscience Australia'

# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

import os

from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.ProcessingConfig import ProcessingConfig
from processing.core.outputs import OutputHTML
from processing.tools.system import getTempFilename

from ..utils import (get_icon, get_products_and_measurements, log_message)

class DataCubeListAlgorithm(GeoAlgorithm):
    """This is TODO

    All Processing algorithms should extend the GeoAlgorithm class.
    """
    OUTPUT_HTML = 'OUTPUT_HTML'

    def __init__(self):
        GeoAlgorithm.__init__(self)

        self._icon = get_icon('opendatacube.png')

    def defineCharacteristics(self):
        """Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # The name that the user will see in the toolbox
        self.name = 'Data Cube List Products'
        #self.addOutput(OutputHTML(self.OUTPUT_HTML, hidden=True))
        self.addOutput(OutputHTML(self.OUTPUT_HTML))

        # The branch of the toolbox under which the algorithm will appear
        self.group = 'Data Cube Helpers'  # TODO can there be a top level alg, not under a folder?

    def processAlgorithm(self, progress):
        """Here is where the processing itself takes place."""
        config_file = ProcessingConfig.getSetting('datacube_config_file')
        config_file = config_file if config_file else None
        output_html = getTempFilename('.html')  #self.getOutputValue('HTML')
        table = get_products_and_measurements(config_file)
        with open(output_html, 'w') as html:
            html.write(table.to_html())
            # html.write(table.style.render())
            # html.write(table.style.set_table_styles(styles).render())

        self.setOutputValue(self.OUTPUT_HTML, output_html)
        #import webbrowser
        #webbrowser.open_new(os.path.join('file://', output_html))
        return {self.OUTPUT_HTML: output_html}
