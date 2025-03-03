# -*- coding: utf-8 -*-

"""
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

from pcraster import (
    readmap,
    setclone,
    scalar,
    lddcreate,
    accuflux,
    cellarea,
    slope,
    atan,
    ln,
    tan,
    report
)

from math import pi

from qgis import processing
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingParameterRasterLayer,
    QgsProcessingParameterNumber,
    QgsProcessingParameterCrs,
    QgsProcessingParameterRasterDestination)

#from pcraster_tools.processing.algorithm import PCRasterAlgorithm

class spiAlgorithm(QgsProcessingAlgorithm):
    INPUT_RASTER = 'INPUT'
    OUTPUT_RASTER = 'OUTPUT'

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return spiAlgorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'streampowerindex'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Stream Power Index (SPI)')

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr('PCRaster User Scripts')

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'pcrasteruser'

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        return self.tr(
            """Calculates the Stream Power Index
          
          
            Parameters:
            
            * <b>Input DEM raster</b> (required) - scalar raster layer
            * <b>Output SPI raster</b> (required) - Scalar raster with result
            """
        )

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT_RASTER,
                self.tr('DEM layer')
            )
        )


        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT_RASTER,
                self.tr("Output SPI raster layer")
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        input_raster = self.parameterAsRasterLayer(parameters, self.INPUT_RASTER, context)
        output_raster = self.parameterAsRasterLayer(parameters, self.OUTPUT_RASTER, context)
        setclone(input_raster.dataProvider().dataSourceUri())
        DEM = readmap(input_raster.dataProvider().dataSourceUri())
        feedback.pushInfo('Calculate flowdirection')
        LDD = lddcreate(DEM,1e31,1e31,1e31,1e31)
        feedback.pushInfo('Calculate Specific Catchment Area')
        SCA = accuflux(LDD,1) * cellarea()
        feedback.pushInfo('Calculate slope')
        slopefraction = slope(DEM)
        slopedegrees = atan(slopefraction)
        sloperadians = scalar(slopedegrees) * (pi/180)
        feedback.pushInfo('Calculate SPI')
        SPI = ln(SCA * tan(sloperadians))
        outputFilePath = self.parameterAsOutputLayer(parameters, self.OUTPUT_RASTER, context)

        report(SPI,outputFilePath)
        
#        self.set_output_crs(output_file=outputFilePath, crs=input_raster.crs(), feedback=feedback, context=context)

        return {self.OUTPUT_RASTER: outputFilePath}
