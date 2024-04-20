import os
import maya.cmds as mc
from SubstancePainterToMaya import helper
from importlib import reload
reload(helper)



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
    material = texture.textureSet
    attributeName = texture.materialAttribute

    # if texture is flat (all pixels the same value) skip
    flat = helper.is_flat_color(texture.filePath)
    
    if flat:
        print('Normal map: Found flat texture map. Skipping: ' + texture.textureName)

        # if delete option is set, delete flat texture files, else delete unused nodes
        if clean:
            helper.cleanFiles2(texture, fileNode)
        else:
            helper.cleanNodes2(texture, fileNode)

    if not flat:
        # Create the normal utility
        normalNode = mc.shadingNode(normalNode, asUtility=True)
        mc.setAttr(normalNode + '.bumpInterp', 1)

        # Connect the file node to the normal utility node
        helper.connectTexture(fileNode, 'outAlpha', normalNode, 'bumpValue', colorCorrect)
                
        # List the connections in the material input attribute
        connectedNodes = mc.listConnections(material + '.' + attributeName)

        # If there's connected nodes
        if connectedNodes:

            for node in connectedNodes:

                # If this is already a normal utility node
                if mc.objectType(node) == normalNode:

                    # Connect the new utility instead if forceTexture is true
                    mc.connectAttr(normalNode + '.outNormal', material + '.' + attributeName, force=forceTexture)

        # If there's no connections in the material attribute
        else:
            # Connect the normal utility to the material attribute
            mc.connectAttr(normalNode + '.outNormal', material + '.' + attributeName, force=forceTexture)

def createORM(texture, fileNode, clean, colorCorrecSubstancePainterToMayase, forceTexture=True):

    """
    Connect the ORM map
    :param material: The name of the material
    :param attributeName: The name of the material attribute to use
    :param forceTexture: Specify if the texture connection is forced
    :param imageNode: The file node to connect
    :return: None
    """

    material = texture.textureSet
    attributeName = texture.materialAttribute

    # List all the connection in the material attribute
    connectedNodes = mc.listConnections(material + '.' + attributeName)

    # If there's connections
    if connectedNodes:

        for node in connectedNodes:

            # Replace the connection if the force texture is true
            mc.connectAttr(fileNode + '.outColor', material + '.specularColor', force=forceTexture)

    # If there's not connections
    else:

        # Connect the color texture map to the SSS
        mc.connectAttr(fileNode + '.outColor', material + '.specularColor', force=forceTexture)


def createColorMap(texture, fileNode, colorCorrect=False, forceTexture=True):
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
    baseColor = '.color'

    # List all the connection in the material attribute
    connectedNodes = mc.listConnections(material + '.' + attributeName)

    # If there's connections
    if connectedNodes:

        for node in connectedNodes:

            # Replace the connection if the force texture is true
            mc.connectAttr(fileNode + '.outColor', material + baseColor, force=forceTexture)

    # If there's not connections
    else:

        # Connect the color texture map
        mc.connectAttr(fileNode + '.outColor', material + baseColor, force=forceTexture)


def connect(ui, texture, renderer, fileNode):

    colorCorrect = False
    useBump = ui.checkbox1.isChecked()
    clean = ui.checkboxRem.isChecked()
    attributeName = texture.materialAttribute

    # If height or normalMap
    if attributeName == 'normalCamera':
        createNormalMap(texture, renderer, fileNode, clean, colorCorrect)

    # If ORM 
    elif attributeName == 'specularColor':
        createORM(texture, fileNode, clean, colorCorrect)

    # If base color connect to base and sss
    elif attributeName == 'color':
        createColorMap(texture, fileNode, colorCorrect)


