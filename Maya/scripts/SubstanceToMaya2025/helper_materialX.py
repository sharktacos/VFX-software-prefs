import os
import re
import maya.cmds as mc
from SubstanceToMaya2025 import helper
from importlib import reload
reload(helper)

    
def mtlxCreateDoc (texture, mtlxBasic, mtlxPath):

    """
    Creates a materialX document based on shader template for all existing materials
    :param material: The material's name
    :return: The material's name, if the material was found
    """
    
    materialNotFound = False
    materialName = texture.textureSet # the shader name
    
    # If the material doesn't exist, tag as not found
    if not mc.objExists(materialName):
        materialNotFound = True
    
    else:  

        # mtlx doc pathname
        mtlxTmp = mtlxPath + "/" + materialName + ".mtlx"
    
        # if doesn't exist, create materialX doc with shader name
        if not os.path.exists(mtlxTmp):
            replacements = { 'MatName':materialName }
            with open(mtlxBasic) as infile, open(mtlxTmp, 'w') as outfile:
                for line in infile:
                    for src, target in replacements.items():
                        line = line.replace(src, target)
                    outfile.write(line)
                    
    return materialName, materialNotFound



def cleanFilesMtlx(texture):

    if os.path.exists(texture.filePath):
        os.remove(texture.filePath)
        print('    Deleting file: ' + texture.textureName)
        
    else:
        print('    '+ texture.filePath + " does not exist")


def mtlxConnect (texture, mtlxPath, clean):

    """
    For each map type replace place-holder with the filepath in the MaterialX document
    :param materialName: The name of the material
    :param attributeName: The name of the material attribute to use
    """

    materialName = texture.textureSet 
    attributeName = texture.materialAttribute 
    mtlxDoc = mtlxPath + "/" + materialName + ".mtlx"
    flat = helper.is_flat_color(texture.filePath)
       
    # If normalMap
    if attributeName == 'normalCamera' and texture.output == 'outColor':
        
        # if texture is flat (all pixels the same value) skip
        if flat:
            print('Normal map: Found flat texture map. Skipping: ' + texture.textureName)

            # if delete option is set, delete flat texture files.
            if clean:
                cleanFilesMtlx(texture)

        if not flat:
            mapType = 'MAP_nor.jpg'
            mtlxAddMaps (texture, mapType, mtlxDoc)
        
    # If spec roughness create a mask network
    elif attributeName == 'specularRoughness':
        # if texture is flat (all pixels the same value) skip
        if flat:
            print('Spec Roughness: Found flat texture map. Skipping: ' + texture.textureName)

            # if delete option is set, delete flat texture files.
            if clean:
                cleanFilesMtlx(texture)

        if not flat:
            mapType = 'MAP_spc.jpg'
            mtlxAddMaps (texture, mapType, mtlxDoc)

    # If base color connect to base and sss
    elif attributeName == 'baseColor':
        mapType = 'MAP_dif.jpg'
        mtlxAddMaps (texture, mapType, mtlxDoc)

    # If metalness 
    elif attributeName == 'metalness':
        mapType = 'MAP_met.jpg'
        mtlxAddMaps (texture, mapType, mtlxDoc)        
              
       
def mtlxAddMaps (texture, mapType, mtlxDoc):

    filePath = texture.filePath # texture file path
    itemPath = re.sub(r"\d{4}\.", '<UDIM>.', texture.filePath) #not sure if needed for UDIMS
    
    # Read in the file
    with open(mtlxDoc, 'r') as file:
        filedata = file.read()

    # Replace the target string
    filedata = filedata.replace(mapType, itemPath)

    # Write the file out again
    with open(mtlxDoc, 'w') as file:
        file.write(filedata)
        
def mtlxCleanMaps (mapType, texture, mtlxPath):
    
    materialName = texture.textureSet 
    mtlxDoc = mtlxPath + "/" + materialName + ".mtlx"
    
    # Read in the file
    with open(mtlxDoc, 'r') as file:
        filedata = file.read()

    # Replace the target string
    filedata = filedata.replace(mapType, '')

    # Write the file out again
    with open(mtlxDoc, 'w') as file:
        file.write(filedata)


def mtlxAssignMaterial(texture, stackShapePath):

    materialName = texture.textureSet
    mtlxSurfacePath = stackShapePath + ",%" + materialName + "%" + materialName + "_SG"
    ShaderGroups = mc.listConnections(materialName + '.outColor', d=True, s=False)

    # Assign materialX to mesh
    for SG in ShaderGroups:
        meshes = mc.listConnections(SG, type='mesh')
        if meshes:
            for mesh in meshes:
                mc.select (mesh, r=True)
                mc.materialxAssign (edit=True, assign=True, sourcePath=mtlxSurfacePath)        



def createUfeSceneItem(dagPath):
    """
    Make ufe item out of dag path
    """
    ufePath = ufe.PathString.path('{}'.format(dagPath))
    ufeItem = ufe.Hierarchy.createItem(ufePath)
    
    return ufeItem
    
