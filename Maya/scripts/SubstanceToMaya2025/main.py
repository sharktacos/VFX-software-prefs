##############################################
#
# SUBSTANCE PAINTER TO MAYA
#
# This tool is used to automatically connect Substance Painter textures to Arnold, VRay and Renderman for Maya.
#
# Originally created by Tristan Le Granche
# tristan.legranche@gmail.com
# updated for Python3 with modified options by Derek Flood
# sharktacos.github,io
#
# Tool under licence CC-BY-NC
# Contact me for commercial use
#
# INSTALL
# Put the SubstanceToMaya2025 folder in a PYTHONPATH folder (I.e: C:\Users\user\Documents\maya\scripts on Windows)
# Create a shelf button in Maya with the following Python command
# import SubstanceToMaya2025
# SubstanceToMaya2025.main.PainterToMaya()
#
# HOW TO USE
# 1. Click on the shelf button
# 2. Define the texture folder
# 3. Define the Naming Convention
# 5. Choose a materials option
# 6. Click on Launch
# 7. Specify where to plug each of the found maps
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

from SubstanceToMaya2025 import main
from importlib import reload
reload(main)
main.SPtoM()

'''
##############################################

# Libraries
import os
from pathlib import Path
import shutil
import ufe
import maya.cmds as mc
import maya.OpenMaya as om
import maya.mel as mel
from SubstanceToMaya2025 import UI as ui
from SubstanceToMaya2025 import helper
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
            from SubstanceToMaya2025 import config_mtoa as config
            reload(config)
            self.name = 'Arnold'
            print ('Arnold')

        elif self.ui.grpRadioRenderer.checkedId() == -3:
            from SubstanceToMaya2025 import config_ue as config
            reload(config)
            self.name = 'Unreal_FBX'
            print ('Unreal_FBX')

        elif self.ui.grpRadioRenderer.checkedId() == -4:
            from SubstanceToMaya2025 import config_mtoa as config
            reload(config)
            self.name = 'MaterialX'
            print ('MaterialX')

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
        from SubstanceToMaya2025 import helper_arnold as render_helper
        reload(render_helper)
#        subdivisions = ui.checkbox5.isChecked()
        subdivisions = False
        
    elif renderer.name == 'MaterialX':
        from SubstanceToMaya2025 import helper_materialX as render_helper
        reload(render_helper)
        subdivisions = False
        
    elif renderer.name == 'Unreal_FBX' or 'Unreal_ABC':
        from SubstanceToMaya2025 import helper_unreal as render_helper
        reload(render_helper)
        subdivisions = False
        


    UDIMs = False

    if ui.checkboxUDIMs.isChecked():
        UDIMs = True

    # Get the textures to use
    texturesToUse = helper.getTexturesToUse(renderer, foundTextures, uiElements)

    # materialX option selected
    if renderer.name == 'MaterialX':
    
        # Location of materialX template doc (in parent script directory)
        script_path: Path = Path(__file__).parent.resolve()
        mtlxBasic = script_path / "MaterialX_basic.mtlx"

        # Create temp directory in User HOME 
        homeDir = os.getenv ("HOME")
        mtlxDir = "materialX_docs"   
        #tmpPath = os.path.join(homeDir, mtlxDir) 
        mtlxPath = homeDir + "/" + mtlxDir
        
        # make tmp directory if it doesn't already exist
        try:
            os.mkdir(mtlxPath)
        except FileExistsError:
            pass
            
        # create materialX stack for scene
        stackShapeName = mc.createNode( 'materialxStack' )
        stackShapePath = mel.eval('ls -l {}'.format(stackShapeName))[0]
        stackShapeItem = ufe.Hierarchy.createItem(ufe.PathString.path(stackShapePath))
        contextOps = ufe.ContextOps.contextOps(stackShapeItem)

        
        # Create MaterialX shader networks
        for texture in texturesToUse:

            texture.materialAttribute = renderer.renderParameters.MAP_LIST_REAL_ATTRIBUTES[texture.indice]

            # Create materialX docs
            material, materialNotFound = render_helper.mtlxCreateDoc(texture, mtlxBasic, mtlxPath)
        
            if materialNotFound:
                continue

            texture.textureSet = material
            
            # Add maps
            clean = ui.checkboxRem.isChecked()
            render_helper.mtlxConnect (texture, mtlxPath, clean)
            
            #clean unused maps
            render_helper.mtlxCleanMaps ('MAP_dif.jpg', texture, mtlxPath)
            render_helper.mtlxCleanMaps ('MAP_met.jpg', texture, mtlxPath)
            render_helper.mtlxCleanMaps ('MAP_spc.jpg', texture, mtlxPath)
            render_helper.mtlxCleanMaps ('MAP_nor.jpg', texture, mtlxPath)            
            #	new loop, replace SPC.jpg with ""
            # do i disconnect map from material?

            
        # import the materialx documents (shaders) to the stack
        for mtlxDoc in os.listdir(mtlxPath):
            
            # import materialX document
            contextOps.doOp(['MxImportDocument', mtlxPath + "/" + mtlxDoc])

        # remove the materialX documents
        if os.path.exists(mtlxPath):
            shutil.rmtree(mtlxPath)
            
        # Assign MaterialX shaders
        for texture in texturesToUse:
            render_helper.mtlxAssignMaterial (texture, stackShapePath)
 
        
    else:
    
         # Connect main textures
        for texture in texturesToUse:

            texture.materialAttribute = renderer.renderParameters.MAP_LIST_REAL_ATTRIBUTES[texture.indice]
   
            # Defer creation of layer texture maps
            mixNode = renderer.renderParameters.MIX_NODE
            if texture.materialAttribute != mixNode:

                # Create file node and 2dPlacer
                if renderer.name == 'Unreal_FBX':
                    fileNode = helper.createFileNode(texture, UDIMs)
                else:
                    fileNode = helper.createFileNode_Ai(texture, UDIMs)

                # Create material
                material, materialNotFound = helper.checkCreateMaterial(ui, texture, renderer)

                if materialNotFound:
                    continue

                texture.textureSet = material
                render_helper.connect(ui, texture, renderer, fileNode)

            # Add subdivisions
            if subdivisions == True:
                render_helper.addSubdivisions(ui, texture)

        #ABC option:
        if renderer.name == 'Unreal_ABC':

            shaderGroups = mc.listConnections (texture.textureSet + '.outColor', d=True, s=False)

            for texture in texturesToUse:

                if mc.objExists(texture.textureSet) and not mc.objExists(texture.textureSet + '_mtl'):

                    # Rename the material.
                    materialName_orig = texture.textureSet
                    materialName_new = mc.rename(texture.textureSet, texture.textureSet + '_mtl')

                    SG = mc.listConnections (materialName_new + '.outColor', d=True, s=False)
                    if SG != materialName_orig:
                        SG_new = mc.rename(SG, materialName_orig)

        # Connect optional layer network
        useLyr = ui.checkbox4.isChecked()

        for texture in texturesToUse:
            if useLyr and texture.materialAttribute == mixNode:

                # create the layer file node
                fileNode = helper.createFileNode(texture, UDIMs)
                # assemble the layer network
                render_helper.createLayerNetwork(texture, renderer, fileNode)

        #delete unused nodes
#           if ui.grpRadioMaterials.checkedId() == -4:
#               mel.eval('hyperShadePanelMenuCommand("hyperShadePanel1", "deleteUnusedNodes");')


    print('\n FINISHED \n')


