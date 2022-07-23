##############################################
#
# SUBSTANCE PAINTER TO MAYA
#
# This tool is used to automatically connect Substance Painter textures to Arnold, VRay and Renderman for Maya.
#
# Created by Tristan Le Granche
# tristan.legranche@gmail.com
#
# Tool under licence CC-BY-NC
# Contact me for commercial use
#
# INSTALL
# Put the SubstancePainterToMaya folder in a PYTHONPATH folder (I.e: C:\Users\user\Documents\maya\scripts on Windows)
# Create a shelf button in Maya with the following Python command
# import SubstancePainterToMaya
# SubstancePainterToMaya.main.PainterToMaya()
#
# HOW TO USE
# 1. Click on the shelf button
# 2. Define the texture folder
# 3. Define the Naming Convention
# 4. Choose the renderer
# 5. Choose a materials option
# 6. Click on Launch
# 7. Specify where to plug each found maps
# 8. Choose some options
# 9. Click on Proceed
# 10. Enjoy !
#
# LIMITATIONS
# This version 0.1 only works with Arnold and uses aiStandardSurface shaders
#
# FOR MORE DETAILS
# Read the README.md file provided with the script
#
# call script with the following python code:
'''

from SubstancePainterToMaya import main
from importlib import reload
reload(main)
main.SPtoM()

'''
##############################################

# Libraries
import os
import maya.cmds as mc
import maya.OpenMaya as om
from SubstancePainterToMaya import UI as ui
from SubstancePainterToMaya import helper
from importlib import reload
reload(ui)
reload(helper)

# Variables
toolUI = ui.PainterToMayaUI()
toolUI.createUI()

# Add action to launch button
toolUI.launchButton.clicked.connect(lambda: launch(toolUI))

###################################
#
# Needed objects
#
# UI - ok
# Texture
# Renderer - ok
#
###################################

class rendererObject:

    def __init__(self):
        self.name = 'Arnold'

    def define(self):

        # Check for the render engine and load config file
        if self.ui.grpRadioRenderer.checkedId() == -2:
            from SubstancePainterToMaya import config_mtoa as config
            reload(config)
            self.name = 'Arnold'
#            print ('Arnold')

        elif self.ui.grpRadioRenderer.checkedId() == -3:
            from SubstancePainterToMaya import config_vray as config
            reload(config)
            self.name = 'Vray'
            print (Vray)

        elif self.ui.grpRadioRenderer.checkedId() == -4:
            from SubstancePainterToMaya import config_renderman_pxrdisney as config
            reload(config)
            self.name = 'PxrDisney'
            print (Renderman - PxrDisney)

        elif self.ui.grpRadioRenderer.checkedId() == -5:
            from SubstancePainterToMaya import config_renderman_pxrsurface as config
            reload(config)
            self.name = 'PxrSurface'
            print (Renderman - PxrSurface)

        elif self.ui.grpRadioRenderer.checkedId() == -6:
            from SubstancePainterToMaya import config_redshift as config
            reload(config)
            self.name = 'Redshift'
            print (Redshift)
        elif self.ui.grpRadioRenderer.checkedId() == -7:
            from SubstancePainterToMaya import config_stingray as config
            reload(config)
            self.name = 'Stingray'
            print (Stingray)

        self.renderParameters = config.config()


def SPtoM():

    # Create the UI
    toolUI = ui.PainterToMayaUI()
    toolUI.createUI()
    toolUI.launchButton.clicked.connect(lambda: launch(toolUI))

def launch(ui):

    print('\n LAUNCH \n')

    allTextures = []

    # Create the renderer
    renderer = rendererObject()
    renderer.ui = ui
    renderer.define()

    # Get all the texture files
    texturePath = ui.texturePath.text()

    allTextureSets = False

    if ui.textureSetRadio1.isChecked():
        allTextureSets = True

    foundFiles = os.listdir(texturePath)

    # Create all the map objects
    foundTextures = helper.listTextures(ui, renderer, foundFiles, allTextureSets)

    # Remove elements from FoundMaps
    helper.clearLayout(ui.foundMapsLayout)
    helper.clearLayout(ui.optionsSubLayout2)

    # Populate the UI with the maps
    foundTextures, uiElements = helper.populateFoundMaps(ui, renderer, foundTextures)

    # Display second part of the UI
    ui = helper.displaySecondPartOfUI(ui, renderer)

    # Add connect to the proceed button
    ui.proceedButton.clicked.connect(lambda: proceed(ui, foundTextures, renderer, uiElements))

def proceed(ui, foundTextures, renderer, uiElements):

    print('\n PROCEED \n')

    # Import render definitions
    if renderer.name == 'Arnold':
        from SubstancePainterToMaya import helper_arnold as render_helper
        reload(render_helper)
        subdivisions = ui.checkbox5.isChecked()

    elif renderer.name == 'Vray':
        import helper_vray as render_helper
        reload(render_helper)
        subdivisions = ui.checkbox6.isChecked()

    elif renderer.name == 'PxrDisney':
        import helper_renderman as render_helper
        reload(render_helper)
        subdivisions = ui.checkbox7.isChecked()

    elif renderer.name == 'PxrSurface':
        import helper_renderman as render_helper
        reload(render_helper)
        subdivisions = ui.checkbox7.isChecked()

    elif renderer.name == 'Redshift':
        import helper_redshift as render_helper
        reload(render_helper)
        subdivisions = ui.checkbox8.isChecked()

    elif renderer.name == 'Stingray':
        import helper_stingray as render_helper
        reload(render_helper)
        subdivisions = False

    UDIMs = False

    if ui.checkboxUDIMs.isChecked():
        UDIMs = True

    # Get the textures to use
    texturesToUse = helper.getTexturesToUse(renderer, foundTextures, uiElements)

    # Connect main textures
    for texture in texturesToUse:

        texture.materialAttribute = renderer.renderParameters.MAP_LIST_REAL_ATTRIBUTES[texture.indice]

        # Defer creation of layer texture maps
        mixNode = renderer.renderParameters.MIX_NODE
        if texture.materialAttribute != mixNode:

            # Create file node and 2dPlacer
            fileNode = helper.createFileNode(texture, UDIMs)

        # Create material
        material, materialNotFound = helper.checkCreateMaterial(ui, texture, renderer)

        if materialNotFound:
            continue

        texture.textureSet = material
        render_helper.connect(ui, texture, renderer, fileNode)

        # Add subdivisions
        if subdivisions == True:
            render_helper.addSubdivisions(ui, texture)

    # Connect optional layer network
    useLyr = ui.checkbox4.isChecked()

    for texture in texturesToUse:
        if useLyr and texture.materialAttribute == mixNode:
            
            # create the layer file node
            fileNode = helper.createFileNode(texture, UDIMs)
            # assemble the layer network
            render_helper.createLayerNetwork(texture, renderer, fileNode)


    print('\n FINISHED \n')











