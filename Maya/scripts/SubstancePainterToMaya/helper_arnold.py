import os
import re
import maya.cmds as mc
from SubstancePainterToMaya import helper
from importlib import reload
reload(helper)

def addSubdivisions(ui, texture):
    """
    Add render subdivisions of a certain type
    :param material: The material used to find which shapes to subdivide
    :return: None
    """

    material = texture.textureSet

    # Get values from interface
    subdivType = ui.subdivType.currentIndex() + 1
    iterations = ui.subdivIter.text()

    # Find the shapes connected to the material
    shader = mc.listConnections(material + '.outColor', d=True)[0]
    meshes = mc.listConnections(shader, type='mesh')

    if meshes:

        # For all shapes add the render subdivisions
        for mesh in meshes:
            mc.setAttr(mesh + '.aiSubdivType', subdivType)
            mc.setAttr(mesh + '.aiSubdivIterations', int(iterations))

def createNormalMap(texture, renderer, fileNode, clean, colorCorrect, forceTexture=True):
    """
    Connect the normal map with the right nodes, even if a bump already exists
    :param material: The name of the material
    :param attributeName: The name of the material attribute to use
    :param forceTexture: Specify if the texture connection is forced
    :param imageNode: The file node to connect
    :return: None
    """

    normalNode = renderer.renderParameters.NORMAL_NODE
    bumpNode = renderer.renderParameters.BUMP_NODE
    material = texture.textureSet
    attributeName = texture.materialAttribute

    # if texture is flat (all pixels the same value) skip
    flat = helper.is_flat_color(texture.filePath)
    
    if flat:
        print('Normal map: Found flat texture map. Skipping: ' + texture.textureName)

        # if delete option is set, delete flat texture files, else delete unused nodes
        if clean:
            helper.cleanFiles(texture, fileNode)
        else:
            helper.cleanNodes(texture, fileNode)

    if not flat:
        # Create the normal utility
        normalNode = mc.shadingNode(normalNode, asUtility=True)

        # Connect the file node to the normal utility node
        helper.connectTexture(fileNode, 'outColor', normalNode, 'input', colorCorrect)

        # List the connections in the material input attribute
        connectedNodes = mc.listConnections(material + '.' + attributeName)

        # If there's connected nodes
        if connectedNodes:

            for node in connectedNodes:

                # If this is already a normal utility node
                if mc.objectType(node) == normalNode:

                    # Connect the new utility instead if forceTexture is true
                    mc.connectAttr(normalNode + '.outValue', material + '.' + attributeName, force=forceTexture)

                # If it's a bump node
                elif mc.objectType(node) == bumpNode:

                    # Get the input file of the bump node
                    connectedBumpNodes = mc.listConnections(node + '.bumpMap')
                    for connectedBumpNode in connectedBumpNodes:

                        # If it's a colorCorrect or a file node with '_file' in it's name
                        if '_file' in connectedBumpNode or 'colorCorrect' in connectedBumpNode:

                            # Connect the utility node in the bump node
                            mc.connectAttr(normalNode + '.outValue', node + '.normal', force=forceTexture)

                        else:
                            # Instead replace the bump node by the normal utility node
                            mc.connectAttr(normalNode + '.outValue', material + '.' + attributeName, force=forceTexture)

        # If there's no connections in the material attribute
        else:
            # Connect the normal utility to the material attribute
            mc.connectAttr(normalNode + '.outValue', material + '.' + attributeName, force=forceTexture)


def createMetalMap(texture, fileNode, clean, colorCorrect=False, forceTexture=True):

    """
    Connect the metalness map
    :param material: The name of the material
    :param attributeName: The name of the material attribute to use
    :param forceTexture: Specify if the texture connection is forced
    :param imageNode: The file node to connect
    :return: None
    """

    material = texture.textureSet
    attributeName = texture.materialAttribute
    metalness = '.metalness'

    # List all the connection in the material attribute
    connectedNodes = mc.listConnections(material + '.' + attributeName)

    # If there's connections
    if connectedNodes:

        for node in connectedNodes:

            # Replace the connection if the force texture is true
            mc.connectAttr(fileNode + '.outColorR', material + metalness, force=forceTexture)

    # If there's not connections
    else:

        # Connect the color texture map to the SSS
        mc.connectAttr(fileNode + '.outColorR', material + metalness, force=forceTexture)


def createBumpMap(texture, renderer, fileNode, clean, colorCorrect, forceTexture=True):
    """
    Connect the bump map with the right nodes, even if a normal map already exists
    :param material: The name of the material
    :param attributeName: The name of the material attribute to use
    :param forceTexture: Specify if the texture connection is forced
    :param imageNode: The file node to connect
    :return: None
    """

    normalNode = renderer.renderParameters.NORMAL_NODE
    bumpNode = renderer.renderParameters.BUMP_NODE
    material = texture.textureSet
    attributeName = texture.materialAttribute

    # check for EXR texture
    if texture.extension=='exr':
        flat = helper.is_black_EXR(texture.filePath)
    else:
        flat = helper.is_flat_color(texture.filePath)
        
    # if texture is flat (all pixels the same value) skip
    if flat: 
        print('Bump map: Found flat texture map. Skipping: ' + texture.textureName)

        # if delete option is set, delete flat texture files, else delete unused nodes
        if clean:
            helper.cleanFiles(texture, fileNode)
        else:
            helper.cleanNodes(texture, fileNode)

    if not flat:
        # Create the bump utility node
        bumpNode = mc.shadingNode(bumpNode, asUtility=True)
        if texture.extension=='exr':
            mc.setAttr (bumpNode + ".bumpHeight", 1)
        else:
            mc.setAttr (bumpNode + ".bumpHeight", 2)

        # Connect the file node to the bump utility node
        helper.connectTexture(fileNode, 'outColorR', bumpNode, 'bumpMap', colorCorrect)

        # List all the connection in the material attribute
        connectedNodes = mc.listConnections(material + '.' + attributeName)

        # If there's connections
        if connectedNodes:

            for node in connectedNodes:

                # If it's a normal utility node
                if mc.objectType(node) == normalNode:

                    # Connect the normal utility to the material attribute
                    mc.connectAttr(node + '.outValue', material + '.' + attributeName, force=forceTexture)
                    mc.connectAttr(node + '.outValue', material + '.coatNormal', force=forceTexture)

                    # Connect the bump node to the material attribute
                    #mc.connectAttr(bumpNode + '.outValue', material + '.' + '.normalCamera', force=forceTexture)
                    #mc.connectAttr(bumpNode + '.outValue', material + '.' + '.coatNormal', force=forceTexture)

                # If it's not a normal utility node
                else:

                    # Replace the connection by the bump node if the force texture is true
                    mc.connectAttr(bumpNode + '.outValue', material + '.' + attributeName, force=forceTexture)
                    mc.connectAttr(bumpNode + '.outValue', material + '.coatNormal', force=forceTexture)

        # If there's not connections
        else:

            # Connect the bump utility to the material attribute
            mc.connectAttr(bumpNode + '.outValue', material + '.' + attributeName, force=forceTexture)
            mc.connectAttr(bumpNode + '.outValue', material + '.coatNormal', force=forceTexture)


def createLayerNetwork(texture, renderer, fileNode):
    """
    Convert standard shader into layer network.
    :param material: The name of the material
    :param materialTypleLyr: The default layer shader type
    :param mixNode: The layer shader mix input
    :return: None
    """

    materialName = texture.textureSet
    materialTypeLyr = renderer.renderParameters.SHADER_LYR
    mixNode = renderer.renderParameters.MIX_NODE
    attributeName = texture.materialAttribute

    # Get shader group connection
    SG = mc.listConnections (materialName + '.outColor', d=True, s=False)[0] or []
    shaderGroups = mc.listConnections (materialName + '.outColor', d=True, s=False)

    # check if layer network already exists
    if mc.objectType(SG) == 'shadingEngine':

        # duplicate material with inputs
        materialName_top = mc.duplicate(materialName, un=True, name=materialName + '_top')[0] or []

        # create layer shader and connect mix
        layer_material = mc.shadingNode(materialTypeLyr, asShader=True, name=materialName + '_lyr')
        mc.setAttr( layer_material+'.enable2', 1)
        mc.connectAttr(fileNode + '.outAlpha', layer_material + '.' + mixNode, force=True)

        # Connect the shading network
        mc.connectAttr (materialName + '.outColor', layer_material + '.input1')
        mc.connectAttr (materialName_top + '.outColor', layer_material + '.input2')

        # Connect the lyr material to the original shading group
        #mc.connectAttr(layer_material + '.outColor', SG + '.surfaceShader', force=True)
        
        for shaderGroup in shaderGroups:
            mc.connectAttr(layer_material + '.outColor', shaderGroup + '.surfaceShader', force=True)

        # Connect displacement map
        if attributeName == 'displacementShader':
            helper.createDisplacementMap(texture, fileNode)

    else:
        print('The shader \"' + materialName + '\" has already been assigned a layer shader network. Skipping.')

#    return materialName
    
def materialSettings(material):

    # set default values
    mc.setAttr ( material+'.transmitAovs', 1)
    mc.setAttr ( material+'.specular', 0.5)
    mc.setAttr ( material+'.subsurfaceScale', 0.1)
    mc.setAttr ( material+'.subsurfaceAnisotropy', 0.8)
    mc.setAttr ( material+'.subsurfaceRadius', 0.15, 0.0075, 0.0075, type='double3' )

def createSSSMap(texture, fileNode, colorCorrect=False, forceTexture=True):
    """
    Connect the specRoughness map with the mix nodes
    :param material: The name of the material
    :param attributeName: The name of the material attribute to use
    :param forceTexture: Specify if the texture connection is forced
    :param imageNode: The file node to connect
    :return: None
    """

    material = texture.textureSet
    attributeName = texture.materialAttribute
    sssColor = '.subsurfaceColor'
    baseColor = '.baseColor'

    # List all the connection in the material attribute
    connectedNodes = mc.listConnections(material + '.' + attributeName)

    # If there's connections
    if connectedNodes:

        for node in connectedNodes:

            # Replace the connection if the force texture is true
            mc.connectAttr(fileNode + '.outColor', material + sssColor, force=forceTexture)
            mc.connectAttr(fileNode + '.outColor', material + baseColor, force=forceTexture)

    # If there's not connections
    else:

        # Connect the color texture map to the SSS
        mc.connectAttr(fileNode + '.outColor', material + sssColor, force=forceTexture)
        mc.connectAttr(fileNode + '.outColor', material + baseColor, force=forceTexture)



def connect(ui, texture, renderer, fileNode):

    colorCorrect = False
    useBump = ui.checkbox1.isChecked()
    clean = ui.checkboxRem.isChecked()
    attributeName = texture.materialAttribute
    
    # Set default shader values
    if mc.objectType(texture.textureSet) == renderer.renderParameters.SHADER:
        materialSettings(texture.textureSet)

    # If displacement
    if attributeName == 'displacementShader':
        helper.createDisplacementMap(texture, fileNode)

    # If height or normalMap
    if attributeName == 'normalCamera':

        # If height
        if texture.output == 'outColorR':

            # If bump
            if useBump:
               createBumpMap(texture, renderer, fileNode, clean, colorCorrect)

        # If normalMap
        elif texture.output == 'outColor':
            createNormalMap(texture, renderer, fileNode, clean, colorCorrect)

    # If spec roughness create a mask network
    elif attributeName == 'specularRoughness':
        helper.createSpecMap(texture, fileNode, clean, colorCorrect)

    # If base color connect to base and sss
    elif attributeName == 'baseColor':
        createSSSMap(texture, fileNode, colorCorrect)

    # If metalness 
    elif attributeName == 'metalness':
        createMetalMap(texture, fileNode, clean, colorCorrect)

    # If it's another type of map
    else:
        helper.connectTexture(fileNode, texture.output, texture.textureSet, attributeName, colorCorrect)


