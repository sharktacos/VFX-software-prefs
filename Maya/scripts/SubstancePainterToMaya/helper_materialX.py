'''
v02 fix flats
'''

import os
import re
import numpy as np
try:
    from PySide6.QtGui import QImage
except ImportError:
    from PySide6.QtGui import QImage

from pathlib import Path
import ufe
import maya.cmds as mc

from SubstancePainterToMaya import helper
from importlib import reload
reload(helper)

def is_flat_colorMtlx(path):
    img = QImage(path)
    
    # Fail-safe for invalid image formats (EXR 16/32b float)
    if img.isNull():
        print('Invalid 16/32b image format. Try OpenEXR instead. Cannot parse: ' + path)
        return False

    # Convert to grayscale if not already
    if img.format() != QImage.Format_Grayscale8:
        img = img.convertToFormat(QImage.Format_Grayscale8)

    # Efficient pixel comparison using numpy
    bits = img.bits().tobytes()
    np_bits = np.frombuffer(bits, dtype=np.uint8)
    
    return np.all(np_bits == np_bits[0])

    
def is_black_constant_Mtlx(path):
    img = QImage(path)

    if img.isNull():
        return False 

    if img.format() != QImage.Format_Grayscale8:
        img = img.convertToFormat(QImage.Format_Grayscale8)

    img_bits = np.frombuffer(img.constBits(), dtype=np.uint8).reshape((img.height(), img.width()))
    return not np.any(img_bits)
    

def mtlxImportDoc (material, stackShapePath):

    materialName = material 
    script_path: Path = Path(__file__).parent.resolve()
    templateName = "MaterialX_basicGrp"
    templatePath = str(script_path) + "/" + templateName + ".mtlx"
    stackShapeItem = ufe.Hierarchy.createItem(ufe.PathString.path(stackShapePath))
    contextOps = ufe.ContextOps.contextOps(stackShapeItem)
    
    # import materialX document
    contextOps.doOp(['MxImportDocument', templatePath])
    mc.select( stackShapePath + ",%" + templateName , r=True )
    docPath = mc.rename( materialName ) # |materialXStack1|materialXStackShape1,%wassupDoc
    
    # rename nodes 
    mc.rename(docPath + "%MatName_SG",  materialName + "_SG" )
    mc.rename(docPath + "%MatName_mtl", materialName + "_mtl")
    
    grpPath = mc.rename(docPath + "%MatName_nodes", materialName + "_nodes")
    mc.rename(grpPath + "%MatName_dif", materialName + "_dif")
    mc.rename(grpPath + "%MatName_nor", materialName + "_nor")
    mc.rename(grpPath + "%MatName_spc", materialName + "_spc")
    mc.rename(grpPath + "%MatName_met", materialName + "_met")
    mc.rename(grpPath + "%MatName_roughness_lerp", materialName + "_roughness_lerp")
    mc.rename(grpPath + "%MatName_normalmap", materialName + "_normalmap")
    #mc.rename(grpPath + "%MatName_UV_dif", materialName + "_UV_dif")
    #mc.rename(grpPath + "%MatName_UV_nor", materialName + "_UV_nor")
    #mc.rename(grpPath + "%MatName_UV_spc", materialName + "_UV_spc")
    #mc.rename(grpPath + "%MatName_UV_met", materialName + "_UV_met")
    

def mtlxAddMaps (texture, mapType, stackShapePath):
    
    """
    For each map type replace place-holder with the filepath in the file attribute
    :param attributeName: The name of the material attribute to use
    """
    
    # replace with UDIM tag as needed
    #file_path = texture.filePath
    texture.filePath = texture.filePath.replace('\\', '/')
    filePath = re.sub(r"\d{4}\.", '<UDIM>.', texture.filePath) #not sure if needed for UDIMS
    materialName = texture.textureSet
    mapDagPath = stackShapePath + ",%" + materialName + "%" + materialName + "_nodes%" + materialName + mapType
    mapNode = createUfeSceneItem(mapDagPath)      # Call utility to make ufe item out of dag path
    mapAttrs = ufe.Attributes.attributes(mapNode)
    attrDagPath = '%s.%s' % (ufe.PathString.string(mapAttrs.sceneItem().path()), "file")
    mc.setAttr(attrDagPath, filePath)



def mtlxConnect (texture, clean, flatX, stackShapePath):

    """
    For each map type replace place-holder with the filepath in the MaterialX document
    :param attributeName: The name of the material attribute to use
    """
    attributeName = texture.materialAttribute 
    #flat = is_flat_colorMtlx(texture.filePath)
    materialName = texture.textureSet
    
    nodegraph_string = stackShapePath + ",%" + materialName + "%" + materialName + "_nodes%"
    nodegraph_item = ufe.Hierarchy.createItem(ufe.PathString.path(nodegraph_string)) 
    mtl_string = stackShapePath + ",%" + materialName + "%" + materialName + "_mtl"
    mtl_item = ufe.Hierarchy.createItem(ufe.PathString.path(mtl_string)) # string to item
    
    doc_string = stackShapePath + ",%" + materialName
    doc_item = ufe.Hierarchy.createItem(ufe.PathString.path(doc_string)) # string to item
    #mxRuntimeId = doc_item.runTimeId() # UFE runtime ID of the MaterialX runtime.
    #connectionHandler = ufe.RunTimeMgr.instance().connectionHandler(mxRuntimeId)
       
    # If normalMap
    if attributeName == 'normalCamera' and texture.output == 'outColor':

        mapType = '_nor'
        mtlxAddMaps (texture, mapType, stackShapePath)
            
        
    # If spec roughness create a mask network
    if attributeName == 'specularRoughness':

        if flatX:
        
            flat = is_black_constant_Mtlx(texture.filePath)
            if not flat:
                mapType = '_spc'
                mtlxAddMaps (texture, mapType, stackShapePath)
        
            else:
                print('Spec Roughness: Found flat texture map. Skipping: ' + texture.textureName)
            
                # Get the attribute info of the 'out' output of the shader.
                ruf_output = ufe.AttributeInfo(nodegraph_item.path(), 'outputs:outRoughness')
                ruf_input = ufe.AttributeInfo(mtl_item.path(), 'inputs:specular_roughness')

                # Disconnect the image to shader.
                mxRuntimeId = doc_item.runTimeId()
                connectionHandler_ruf = ufe.RunTimeMgr.instance().connectionHandler(mxRuntimeId)
                connectionHandler_ruf.disconnect(ruf_output, ruf_input)
            
                # delete the map nodes
                map_ruf = stackShapePath + ",%" + materialName + "%" + materialName + "_nodes%" + materialName + "_spc"
                map_lerp = stackShapePath + ",%" + materialName + "%" + materialName + "_nodes%" + materialName + "_roughness_lerp"

                mc.delete(map_ruf)
                mc.delete(map_lerp)

                # if delete option is set, delete flat texture files.
                if clean:
                    cleanFilesMtlx(texture)
        
        else:
            mapType = '_spc'
            mtlxAddMaps (texture, mapType, stackShapePath)









    # If base color connect to base and sss
    if attributeName == 'baseColor':
        mapType = '_dif'
        
        mtlxAddMaps (texture, mapType, stackShapePath)

    # If metalness 
    if attributeName == 'metalness':
        mapType = '_met'
        mtlxAddMaps (texture, mapType, stackShapePath)     



def cleanFilesMtlx(texture):

    '''
    If delete option is set, delete flat texture files on disc.
    '''
    
    if os.path.exists(texture.filePath):
        os.remove(texture.filePath)
        print('    Deleting file: ' + texture.textureName)
        
    else:
        print('    '+ texture.filePath + " does not exist")
        

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





# write to temp file (legacy)...


def mtlxCreateDocFile (texture, mtlxBasic, mtlxPath):

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




def mtlxConnectToFile (texture, mtlxPath, clean):

    """
    For each map type replace place-holder with the filepath in the MaterialX document
    :param materialName: The name of the material
    :param attributeName: The name of the material attribute to use
    """

    materialName = texture.textureSet 
    attributeName = texture.materialAttribute 
    mtlxDoc = mtlxPath + "/" + materialName + ".mtlx"
    flat = is_flat_colorMtlx(texture.filePath)
       
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
              
       
        
def mtlxCleanMapsInFile (mapType, texture, mtlxPath):
    
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

def mtlxAddMapsToFile (texture, mapType, mtlxDoc):

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
        

   

# UFE Helpers -----------

def createUfeSceneItem(dagPath):
    """
    Make ufe item out of dag path
    """
    ufePath = ufe.PathString.path('{}'.format(dagPath))
    ufeItem = ufe.Hierarchy.createItem(ufePath)
    
    return ufeItem
    
    
    
def createItem(ufePathOrPathString):
    '''
    Create a UFE scene item from a UFE path or path string.
    '''
    path = ufe.PathString.path(ufePathOrPathString) \
           if isinstance(ufePathOrPathString, str) else ufePathOrPathString
           
    return ufe.Hierarchy.createItem(path)
    


def createUfePathSegment(mayaPath):
    """
        Create a UFE path from a given maya path and return the first segment.
        Args:
            mayaPath (str): The maya path to use
        Returns :
            PathSegment of the given mayaPath
    """
    return ufe.PathString.path(mayaPath).segments[0]

###############
# selecting...

def selectUfeItems(selectItems):
    """
    Add given UFE item or list of items to a UFE global selection list
    """
    ufeSelectionList = ufe.Selection()
    
    realListToSelect = selectItems if type(selectItems) is list else [selectItems]
    for item in realListToSelect:
        ufeSelectionList.append(item)
    
    ufe.GlobalSelection.get().replaceWith(ufeSelectionList)

def getMayaSelectionList():
    """ 
        Returns the current Maya selection in a list
        Returns:
            A list(str) containing all selected Maya items
    """
    # Remove the unicode of cmds.ls

    # TODO: HS, June 10, 2020 investigate why x needs to be encoded
    if sys.version_info[0] == 2:
        return [x.encode('UTF8') for x in cmds.ls(sl=True)]
    else:
        return [x for x in cmds.ls(sl=True)]
        
def stripPrefix(input_str, prefix):
    if input_str.startswith(prefix):
        return input_str[len(prefix):]
    return input_str
    
