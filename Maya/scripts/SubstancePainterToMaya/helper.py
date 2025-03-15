import maya.cmds as mc
import mtoa.core as core 
import os
import re





try:
    import PySide2 as PySide
except:
    import PySide6 as PySide
    

    
try:
    import PySide2.QtWidgets as QtWidgets
except ImportError:
    import PySide6.QtWidgets as QtWidgets
    

from PySide6.QtGui import QImage




class foundMap:

    def __init__(self):

        filePath = ''
        textureName = ''
        mapName = ''
        mapOutput = ''
        shader = ''

def splitTextureName(delimiters, textureName):

    return re.split(delimiters, textureName)

def before(value, a):
    # Find first part and return slice before it.
    pos_a = value.find(a)
    if pos_a == -1: return ""
    return value[0:pos_a]

def splitNamingConvention(ui, textures):

    construction = []
    textureSetSeparator = '_'
    mapSeparator = '_'
    textureSet = ui.textureSet.text()
    map = ui.map.text()
    

    for texture in textures:

        if textureSet in texture and map in texture:

            beforeTextureSet = re.split(ui.DELIMITERS, before(texture, textureSet))
            beforeMapSet = re.split(ui.DELIMITERS, before(texture, map))

            extension = texture.split('.')[-1]

            if extension in ui.PAINTER_IMAGE_EXTENSIONS:
                textureSplit = re.split(ui.DELIMITERS, texture)

                textureSetSplit = re.split(ui.DELIMITERS, textureSet)
                textureSetSeparator = re.sub('[abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789]', '', textureSet)

                mapSplit = re.split(ui.DELIMITERS, map)
                mapSeparator = re.sub('[abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789]', '', map)



                for i in range(0, len(textureSplit)):
                    if len(beforeTextureSet) <= i+1 <= (len(beforeTextureSet) + len(textureSetSplit))-1:
                        construction.append('textureSet')
                        continue

                    if len(beforeMapSet) <= i+1 <= (len(beforeMapSet) + len(mapSplit))-1:
                        construction.append('map')
                        continue

                    construction.append('part')

                break

    return construction, textureSetSeparator, mapSeparator

def getMapFromName(mapName, renderer):
    """
    Check if the map name correspond to a known attribute
    :param mapName: The name of the map
    :return: Index of the associated attribute
    """

    for key, value in renderer.renderParameters.MAPS_INDICES.items():
        if mapName in value[0]:
            return value[1]

    return 0


def listTextures(ui, renderer, foundFiles, allTextureSets):

    foundTextures = []
    mapsFound = []

    # Get the texture path
    texturePath = ui.texturePath.text()

    # Get naming convention elements
    construction, textureSetSeparator, mapSeparator = splitNamingConvention(ui, foundFiles)

    for texture in foundFiles:

        if not allTextureSets:
            if not ui.textureSet.text() in texture:
                continue

        # Create the texture path
        filePath = os.path.join(texturePath, texture)

        # If item is a file
        if os.path.isfile(filePath):
            # Get item's extension
            extension = texture.split('.')[-1]

            # If its a valid texture file
            if extension in ui.PAINTER_IMAGE_EXTENSIONS:

                textureSet = ''
                name = ''

                textureSetStart = 0
                nameStart = 0

                textureSplit = re.split(ui.DELIMITERS, texture)

                if len(construction) == len(textureSplit):

                    for i in range(0, len(construction)):

                        if construction[i] == 'textureSet':
                            if textureSetStart > 0:
                                textureSet += textureSetSeparator[textureSetStart - 1]
                            textureSet += textureSplit[i]
                            textureSetStart += 1

                        if construction[i] == 'map':
                            if nameStart > 0:
                                name += mapSeparator[nameStart - 1]
                            name += textureSplit[i]
                            nameStart += 1

                mapName = name
                textureSetName = textureSet

                if mapName and textureSetName:

                        # If the map name is not already listed (e.g.: baseColor)
                        if mapName not in mapsFound:

                            # Create map object
                            map = foundMap()
                            map.textureName = texture
                            map.filePath = filePath
                            map.extension = extension
                            map.textureSet = textureSetName

                            # Get associated attribute name
                            map.indice = getMapFromName(mapName, renderer)
                            map.mapName = mapName
                            map.mapInList = renderer.renderParameters.MAP_LIST[map.indice]

                            # Add map to foundTextures
                            foundTextures.append(map)

    return foundTextures

def populateFoundMaps(ui, renderer, foundTextures):

    layoutPosition = 0
    foundMapsName = []
    uiElements = []

    if foundTextures:

        for foundTexture in foundTextures:

            if foundTexture.mapName not in foundMapsName:

                # Create the layout
                foundMapsSubLayout2 = PySide.QtWidgets.QHBoxLayout()
                ui.foundMapsLayout.insertLayout(-1, foundMapsSubLayout2, stretch=1)

                # Create the widgets
                map1 = PySide.QtWidgets.QLineEdit(foundTexture.mapName)
                foundMapsSubLayout2.addWidget(map1)

                map1Menu = PySide.QtWidgets.QComboBox()
                map1Menu.addItems(renderer.renderParameters.MAP_LIST)
                map1Menu.setCurrentIndex(foundTexture.indice)
                foundMapsSubLayout2.addWidget(map1Menu)

                # Add ui element to uiElements
                uiElements.append([map1, map1Menu])

                foundMapsName.append(foundTexture.mapName)

                # Increment layout position
                layoutPosition += 1

    else:
        # Create the layout
        foundMapsSubLayout2 = PySide.QtWidgets.QHBoxLayout()
        ui.foundMapsLayout.insertLayout(layoutPosition, foundMapsSubLayout2, stretch=1)

        # Create the widgets
        map1 = PySide.QtWidgets.QLineEdit('No texture found, \ncheck Texture Folder and Naming Convention')
        foundMapsSubLayout2.addWidget(map1)

    return foundTextures, uiElements


def displaySecondPartOfUI(ui, renderer):

    # Display second part of the interface
    ui.grpFoundMaps.setVisible(True)
    ui.grpOptions.setVisible(True)
    ui.scroll.setVisible(True)

    ui.grpProceed.setVisible(True)
    ui.launchButton.setText('Re-launch')

    return ui

def clearLayout(layout):
    """
    Empty specified PySide layout
    :param layout: Layout to clear
    :return: None
    """

    if layout is not None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                clearLayout(item.layout())



def createFileNode_Ai(texture, UDIMS):
    """
    Creates an Arnold file node, set the texture of the file node and connect both of them
    :param material: The name of the material
    :param mapFound: The name of the texture map
    :param itemPath: The path of the texture map
    :return: Name of the file node
    """

    material = texture.textureSet
    textureName = texture.mapName
    itemPath = re.sub(r"\d{4}\.", '<UDIM>.', texture.filePath)
    
    # Create a file node
    fileNode = core.createArnoldNode("aiImage", name=material + '_' + textureName + '_file')
    mc.setAttr(fileNode + '.ignoreMissingTextures', 1)
    mc.setAttr(fileNode + '.missingTextureColor', 0.5, 0.5, 0.5, type='double3') 

    # Set the file path of the file node
    mc.setAttr(fileNode + '.filename', itemPath, type='string')

    return fileNode

def createFileNode(texture, UDIMS):
    """
    Creates a file node and a place2d node, set the texture of the file node and connect both of them
    :param material: The name of the material
    :param mapFound: The name of the texture map
    :param itemPath: The path of the texture map
    :return: Name of the file node
    """

    material = texture.textureSet
    textureName = texture.mapName
    itemPath = texture.filePath

    # Create a file node
    fileNode = mc.shadingNode('file', asTexture=True, isColorManaged=True, name=material + '_' + textureName + '_file')

    # Create a place2d node
    place2d = mc.shadingNode('place2dTexture', asUtility=True, name=material + '_' + textureName + '_place2d')

    # Set the file path of the file node
    mc.setAttr(fileNode + '.fileTextureName', itemPath, type='string')

    # Set alpha is luminance
    mc.setAttr(fileNode + '.alphaIsLuminance', True)

    if UDIMS:
        mc.setAttr(fileNode + '.uvTilingMode', 3)

    # Connect the file and the place2d nodes
    connectPlace2dTexture(place2d, fileNode)

    return fileNode


def connectPlace2dTexture(place2d, fileNode):
    """
    Connect the place2d to the file node
    :param place2d: The name of the place2d node
    :param fileNode: The name of the file node
    :return: None
    """

    # Connections to make
    connections = ['rotateUV', 'offset', 'noiseUV', 'vertexCameraOne', 'vertexUvThree', 'vertexUvTwo',
                   'vertexUvOne', 'repeatUV', 'wrapV', 'wrapU', 'stagger', 'mirrorU', 'mirrorV', 'rotateFrame',
                   'translateFrame', 'coverage']

    # Basic connections
    mc.connectAttr(place2d + '.outUV', fileNode + '.uvCoord')
    mc.connectAttr(place2d + '.outUvFilterSize', fileNode + '.uvFilterSize')

    # Other connections
    for attribute in connections:
        mc.connectAttr(place2d + '.' + attribute, fileNode + '.' + attribute)

'''
def checkCreateMaterialX(ui, texture, renderer):
    """
    Based on the interface options, create or use existing materials
    :param material: The material's name
    :return: The material's name, if the material was found
    """

    materialNotFound = False
    materialName = texture.textureSet
    materialType = renderer.renderParameters.SHADER

    # If option: "use existing Materials. Convert if wrong material type."
    if ui.grpRadioMaterials.checkedId() == -4:

        # If the material doesn't exist
        if not mc.objExists(materialName):

            # Specify that the material was not found
            materialNotFound = True
            
        # If the material is not of the right type
        elif not mc.objectType(materialName) == materialType:

            SG = mc.listConnections (materialName + '.outColor', d=True, s=False)[0] or []
#            shaderGroups = mc.listConnections (materialName + '.outColor', d=True, s=False)
            print ("Material wrong type:")
            print (materialName)
            # check if material already exists
            if mc.objectType(SG) == 'shadingEngine':

                # Delete the material and replace with material of correct type
#                mc.delete(materialName) 
#                material = mc.shadingNode(materialType, asShader=True, name=materialName)

                # Connect the material to the original shading group        
                for shaderGroup in shaderGroups:
                    mc.connectAttr(material + '.outColor', shaderGroup + '.surfaceShader', force=True)

    return materialName, materialNotFound
'''   

def checkCreateMaterial(ui, texture, renderer):
    """
    Based on the interface options, create or use existing materials
    :param material: The material's name
    :return: The material's name, if the material was found
    """

    materialNotFound = False
    materialName = texture.textureSet
    materialType = renderer.renderParameters.SHADER

    # option: "Create new materials if they don't exist, or else use existing ones"
    if ui.grpRadioMaterials.checkedId() == -2:

        # If the material doesn't exist or if it's not of the right type
        if not mc.objExists(materialName) or not mc.objectType(materialName) == materialType:

            # If a '_shd' version of the material doesn't exist
            if not mc.objExists(materialName + '_shd'):

                # Create the material
                createMaterialAndShadingGroup(materialName, materialType)

            materialName += '_shd'

    # If option: "create new ones"
    elif ui.grpRadioMaterials.checkedId() == -3:

        # If the '_shd' version of the material doesn't exist
        if not mc.objExists(materialName + '_shd'):

            # Create the material
            createMaterialAndShadingGroup(materialName, materialType)

        materialName += '_shd'

    # If option: "use existing Materials. Convert if wrong material type."
    elif ui.grpRadioMaterials.checkedId() == -4:

        # If the material doesn't exist
        if not mc.objExists(materialName):

            # Specify that the material was not found
            materialNotFound = True

        # If the material is not of the right type
        elif not mc.objectType(materialName) == materialType:

            SG = mc.listConnections (materialName + '.outColor', d=True, s=False)[0] or []
            shaderGroups = mc.listConnections (materialName + '.outColor', d=True, s=False)

            # check if material already exists
            if mc.objectType(SG) == 'shadingEngine':

                # Delete the material and replace with material of correct type
                mc.delete(materialName) 
                material = mc.shadingNode(materialType, asShader=True, name=materialName)

                # Connect the material to the original shading group        
                for shaderGroup in shaderGroups:
                    mc.connectAttr(material + '.outColor', shaderGroup + '.surfaceShader', force=True)

    return materialName, materialNotFound

def swapMaterialAndShadingGroupUE(texture, renderer):
    """
    Swap  material and it's shading group for Unreal Alembic
    :param material: The material's name
    :return: The material's name
    """

    materialName = texture.textureSet
    materialType = renderer.renderParameters.SHADER
    shaderGroups = mc.listConnections (texture.textureSet + '.outColor', d=True, s=False)

    # Rename the material.
    materialName_orig = materialName
    mc.rename(materialName, materialName +'_shd')

    # Rename shader group to original material name.
    for shaderGroup in shaderGroups:
        shaderGroup = mc.rename(shaderGroup, materialName_orig)

    return materialName


def createMaterialAndShadingGroup(materialName, materialType):
    """
    Create a material and it's shading group
    :param material: The material's name
    :return: The material's name
    """

    # Create the material
    material = createMaterial(materialName, materialType)

    # Create the shading group
    shadingEngine = createShadingGroup(materialName)

    # Connect the material to the shading group
    mc.connectAttr(material + '.outColor', shadingEngine + '.surfaceShader')

    return materialName

def createMaterial(materialName, materialType):

    # Create the material
    material = mc.shadingNode(materialType, asShader=True, name=materialName + '_shd')

    return material

def createShadingGroup( materialName):

    shadingEngineName = materialName.replace('_shd', '_SG')
    shadingEngine = mc.sets(renderable=True, noSurfaceShader=True, empty=True, name=shadingEngineName)

    return shadingEngine

def getTexturesToUse(renderer, foundTextures, uiElements):

    texturesToUse = []

    # Create and connect the textures
    for foundTexture in foundTextures:

        # Connect file node to material
        for uiElement in uiElements:

            if foundTexture.mapName == uiElement[0].text():
                foundTexture.attribute = uiElement[1].currentText()
                foundTexture.indice = uiElement[1].currentIndex()

        if foundTexture.indice in renderer.renderParameters.DONT_USE_IDS:

            continue

        else:

            if foundTexture.indice in renderer.renderParameters.MAP_LIST_COLOR_ATTRIBUTES_INDICES:

                foundTexture.output = 'outColor'
            else:
                foundTexture.output = 'outColorR'

            texturesToUse.append(foundTexture)

    return texturesToUse


def connectTexture(textureNode, textureOutput, targetNode, targetInput, colorCorrect=False, forceTexture=True):
    """
    Connect the file node to the material
    :param textureNode: Name of the file node
    :param textureOutput: Output attribute of the file node we need to use
    :param targetNode: Name of the material node
    :param targetInput: Input attribute of the material node we need to use
    :return: None
    """

    # If use colorCorrect
    if colorCorrect == True:

        # Create a colorCorrect node
        colorCorrect = mc.shadingNode('colorCorrect', asUtility=True, isColorManaged=True, )

        textureInput = textureOutput.replace('out', 'in')

        # Connect the file node to the color correct
        mc.connectAttr(textureNode + '.' + textureOutput, colorCorrect + '.' + textureInput, force=forceTexture)

        # Connect the color correct to the material
        mc.connectAttr(colorCorrect + '.' + textureOutput, targetNode + '.' + targetInput, force=forceTexture)

    # Connect the file node output to material input, except for mix2
    elif targetInput != 'mix2' and targetInput != 'displacementShader':
        mc.connectAttr(textureNode + '.' + textureOutput, targetNode + '.' + targetInput, force=forceTexture)


def createDisplacementMap(texture, fileNode, colorCorrect=False, forceTexture=True):
    """
    Connect displacement to the right shading engine(s)
    :param material: The name of the material
    :param forceTexture: Specify if the texture connection is forced
    :param imageNode: The file node to connect
    :return: None
    """

    shadingGroups = None

    # Create a displacement node
    displaceNode = mc.shadingNode('displacementShader', asShader=True)

    # Connect the texture to the displacement node
    connectTexture(fileNode, 'outColorR', displaceNode, 'displacement', colorCorrect)

    # Get the shading engine associated with given material
    shadingGroups = mc.listConnections(texture.textureSet + '.outColor')

    for shadingGroup in shadingGroups:

        if mc.objectType(shadingGroup) == 'shadingEngine':
            # Connect the displacement node to all the found shading engines
            mc.connectAttr(displaceNode + '.displacement',
                           shadingGroup + '.displacementShader', force=forceTexture)


    
def is_black_constant(path):
    img = PySide.QtGui.QImage(path)

    if img.isNull():
        return False 

    if not img.format() == img.Format.Format_Grayscale8:
        img.convertTo(img.Format.Format_Grayscale8)

    return not any(img.constBits())



"""
def is_flat_colorRGB(path):
    img = PySide.QtGui.QImage(path)

    # sample pixel color
    pix = img.pixel(5,5)
    r = round(PySide.QtGui.qRed(pix) / 255, 4)
    g = round(PySide.QtGui.qGreen(pix) / 255, 4)
    b = round(PySide.QtGui.qBlue(pix) / 255, 4)
    
    # Fail-safe for invalid image formats (EXR)
    null = False
    if img.isNull():
        file = path.rsplit('/', 1)[1]
        # print ('Unable to do flat texture detection for 16/32 bit float image: ' + file)
        flat = False
        return flat, r, g, b 

    # convert to grayscale
    if not img.format() == img.Format.Format_Grayscale8:
        img.convertTo(img.Format.Format_Grayscale8)

    #iterate through bits to see if they are all the same
    bits = img.constBits()
    first = bits[0]
    flat = all(first == next for next in bits)
    return flat, r, g, b
"""

def is_black_EXR(path):
    black = False
    # try to import imgeio and numpy
    try:
        import imageio.v3 as iio
        import numpy as np
     #   import imageio_freeimage

    except ImportError:
        print ('Required imageio module not found. See docs for installation. Cannot parse EXR: ' + path)

    else:
        # read in the exr with freeimage plugin
        img = iio.imread(path, plugin="EXR-FI")
        #detect for zero pixel value with numpy
        zero = np.count_nonzero(img)
        if zero==0:
            black = True

    return black


def is_flat_color(path):
    img = PySide.QtGui.QImage(path)
    
    # Fail-safe for invalid image formats (EXR 16/32b float)
    null = False
    if img.isNull():
        print('Invalid 16/32b image format. Try OpenEXR instead. Cannot parse: ' + path)
        return False

    # convert to grayscale
    if not img.format() == img.Format.Format_Grayscale8:
        img.convertTo(img.Format.Format_Grayscale8)

    # iterate through bits to see if they are all the same
    bits = img.constBits()
    first = bits[0]   
    return all(first == next for next in bits)
    

 



def cleanFiles(texture, fileNode):

    if os.path.exists(texture.filePath):
        mc.delete(fileNode)

        os.remove(texture.filePath)
        print('    Deleting file: ' + texture.textureName)
    else:
        print('    '+ texture.filePath + " does not exist")


def cleanNodes(texture, fileNode):

    if os.path.exists(texture.filePath):
        mc.delete(fileNode)
 
    else:
        print('    '+ texture.filePath + " does not exist")

def cleanFiles2(texture, fileNode):

    if os.path.exists(texture.filePath):
        place2d = mc.listConnections(fileNode, t='place2dTexture')[0]
        mc.delete(place2d)
        mc.delete(fileNode)

        os.remove(texture.filePath)
        print('    Deleting file: ' + texture.textureName)
    else:
        print('    '+ texture.filePath + " does not exist")


        
def cleanNodes2(texture, fileNode):

    if os.path.exists(texture.filePath):
        place2d = mc.listConnections(fileNode, t='place2dTexture')[0]
        mc.delete(place2d)
        mc.delete(fileNode)
 
    else:
        print('    '+ texture.filePath + " does not exist")
        


def createSpecMap(texture, fileNode, clean, colorCorrect=False, forceTexture=True):
    """
    Connect the specRoughness map with the mix nodes
    :param material: The name of the material
    :param attributeName: The name of the material attribute to use
    :param forceTexture: Specify if the texture connection is forced
    :param imageNode: The file node to connect
    :return: None
    """

    #blendNode = 'blendColors'
    material = texture.textureSet
    attributeName = texture.materialAttribute
    
    # check for EXR texture
    if texture.extension=='exr':
        flat = is_black_EXR(texture.filePath)
    else:
        flat = is_black_constant(texture.filePath)

    # if texture is flat (all pixels the same value) skip
    if flat: 
        print('Spec Roughness: Found flat texture map. Skipping: ' + texture.textureName)

        # if delete option is set, delete flat texture files, else delete unused nodes
        if clean:
            cleanFiles(texture, fileNode)
        else:
            cleanNodes(texture, fileNode)

    if not flat:

        # Create the range and two roughness sliders
        
        #blendNode = mc.shadingNode(blendNode, asUtility=True, name='blendRoughness')
        #mc.setAttr (blendNode + ".color1", 0.2, 0.2, 0.2, type='double3')
        #mc.setAttr (blendNode + ".color2", 0.5, 0.5, 0.5, type='double3')
        blendNode = core.createArnoldNode("aiRange", name='lerp')
        RufA = core.createArnoldNode("aiFlat", name='roughness_A')
        RufB = core.createArnoldNode("aiFlat", name='roughness_B')
        mc.setAttr (RufA + ".color", 0.2, 0.2, 0.2, type='double3')
        mc.setAttr (RufB + ".color", 0.5, 0.5, 0.5, type='double3')

        # connect roughness sliders to range
        mc.connectAttr ( RufA + '.outColorR', blendNode + '.outputMin', force=True )
        mc.connectAttr ( RufB + '.outColorR', blendNode + '.outputMax', force=True )

        # delete unused SGs
        RufA_sg = mc.listConnections(RufA,type='shadingEngine')
        RufB_sg = mc.listConnections(RufB,type='shadingEngine')
        mc.delete(RufA_sg)
        mc.delete(RufB_sg)

        # Connect the file to range
        connectTexture(fileNode, 'outColor', blendNode, 'input', colorCorrect)
        # Old for blendColors
        #connectTexture(fileNode, 'outColorR', blendNode, 'blender', colorCorrect)

        # List all the connection in the material attribute
        connectedNodes = mc.listConnections(material + '.' + attributeName)

        # If there's connections
        if connectedNodes:

            for node in connectedNodes:

                # Replace the connection by the spec node tree if the force texture is true
                #mc.connectAttr(blendNode + '.outputR', material + '.' + attributeName, force=forceTexture)
                mc.connectAttr(blendNode + '.outColorR', material + '.' + attributeName, force=forceTexture)
                

        # If there's not connections
        else:

            # Connect the spec node tree to the material attribute
            mc.connectAttr(blendNode + '.outColorR', material + '.' + attributeName, force=forceTexture)

