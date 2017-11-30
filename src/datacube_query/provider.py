# -*- coding: utf-8 -*-

"""
/***************************************************************************
 DataCubeQuery
                                 A QGIS plugin
 Query and view data stored in an Open Data Cube (https://www.opendatacube.org)
                              -------------------
        begin                : 2017-11-09
        copyright            : (C) 2017 by Geoscience Australia
        email                : luke.pinner@ga.gov.au
 ***************************************************************************/


"""

__author__ = 'Geoscience Australia'
__date__ = '2017-11-09'
__copyright__ = '(C) 2017 by Geoscience Australia'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import json

from processing.core.AlgorithmProvider import AlgorithmProvider
from processing.core.ProcessingConfig import Setting, ProcessingConfig

from .algs.query import DataCubeQueryAlgorithm
from .algs.list_products import DataCubeListAlgorithm

from .utils import get_icon
from .defaults import (GTIFF_OVR_DEFAULTS, GTIFF_DEFAULTS)


class DataCubeQueryProvider(AlgorithmProvider):

    NAME = 'Open Data Cube'
    DESCRIPTION = 'Open Data Cube Algorithms'

    def __init__(self):
        # TODO - add GDAL/rio format and overview creation options as settings
        self.settings = [
            Setting(DataCubeQueryProvider.DESCRIPTION,
                    'datacube_config_file',
                    self.tr("Open Data Cube database config file"),
                    '',
                    valuetype=Setting.FILE),
            Setting(DataCubeQueryProvider.DESCRIPTION,
                    'build_overviews',
                    self.tr("Build GeoTiff Overviews"),
                    default=True,
                    valuetype=None),
            Setting(DataCubeQueryProvider.DESCRIPTION,
                    'gtiff_options',
                    self.tr("GeoTiff Creation Options"),
                    default=json.dumps(GTIFF_DEFAULTS),
                    valuetype=Setting.STRING),
            Setting(DataCubeQueryProvider.DESCRIPTION,
                    'gtiff_ovr_options',
                    self.tr("GeoTiff Overview Options"),
                    default=json.dumps(GTIFF_OVR_DEFAULTS),
                    valuetype=Setting.STRING),
        ]

        AlgorithmProvider.__init__(self)

        # Deactivate provider by default
        self.activate = False

        # Load algorithms
        self.alglist = [DataCubeQueryAlgorithm(),
                        DataCubeListAlgorithm()]
        for alg in self.alglist:
            alg.provider = self

    def initializeSettings(self):
        """In this method we add settings needed to configure our
        provider.

        Do not forget to call the parent method, since it takes care
        or automatically adding a setting for activating or
        deactivating the algorithms in the provider.
        """

        AlgorithmProvider.initializeSettings(self)
        for setting in self.settings:
            ProcessingConfig.addSetting(setting)

    def unload(self):
        """Setting should be removed here, so they do not appear anymore
        when the plugin is unloaded.
        """
        AlgorithmProvider.unload(self)
        for setting in self.settings:
            ProcessingConfig.removeSetting(setting.name)

    def getName(self):
        """This is the name that will appear on the toolbox group.

        It is also used to create the command line name of all the
        algorithms from this provider.
        """
        return DataCubeQueryProvider.NAME

    def getDescription(self):
        """This is the provided full name.
        """
        return DataCubeQueryProvider.DESCRIPTION

    def getIcon(self):
        return get_icon('opendatacube.png')

    def _loadAlgorithms(self):
        """Here we fill the list of algorithms in self.algs.

        This method is called whenever the list of algorithms should
        be updated. If the list of algorithms can change (for instance,
        if it contains algorithms from user-defined scripts and a new
        script might have been added), you should create the list again
        here.

        In this case, since the list is always the same, we assign from
        the pre-made list. This assignment has to be done in this method
        even if the list does not change, since the self.algs list is
        cleared before calling this method.
        """
        self.algs = self.alglist
