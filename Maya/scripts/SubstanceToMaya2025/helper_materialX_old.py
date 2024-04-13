import os
import re
import maya.cmds as mc
from SubstanceToMaya2025 import helper
from importlib import reload
reload(helper)


# change config to not use bmp for nor (but should it then make value ""?)

#	new loop, replace SPC.jpg with ""
# do i want to keep docs? Can always export them

# update SP mtlX template
# make compound for lerp?    
# test UDIMs    


import ufe
import mayaUsd
import maya.mel as mel
import maya.cmds as mc


imgAttrs = ufe.Attributes.attributes(imgNode)
AttrType = imgAttrs.attributeType("inputs:file")
AttrFile = imgAttrs.attribute("inputs:file")
filename = "bob.jpg"

print(ufeFullPath)
cmds.setAttr(ufeFullPath, filename)

def assignFilename(ufeAttr, filename, fileType):
    ufeFullPath = '%s.%s' % (ufe.PathString.string(ufeAttr.sceneItem().path()), "file")
    cmds.setAttr(ufeFullPath, filename)
    currentDir = cmds.workspace(q=True, dir=True)
    mel.eval("""retainWorkingDirectory("%s")""" % currentDir)
    self.updateUi(ufeAttr, self.controlName)
    return True
    
##########

def createTiledImage ():
    #create tileimg (in doc)
    #set filename
    
def createMtlxShader ():

    #create doc
    #create SG
    #create material
    #connect mat>SG
    
    #create normalmap
    #create CC
    #create lerp
    
def connectMtlx_dif ():
    #create tileimg
    # create CC
    #set filename
    #connect img>CC>mat
    
def connectMtlx_nor ():
    # IF NOT FLAT
    #create tileimg
    # create norMap
    #set filename
    #connect img > nor > mat
    
def connectMtlx_met ():
    #create tileimg
    #set filename
    #connect img > mat
    
def connectMtlx_spc ():
    # IF NOT FLAT
    #create tileimg
    # create lerp
    #set filename
    #connect img > lerp > mat    
    


# how to find None in map? getInfo? Slack

# maybe make all textures "" in doc.mtlx and only replace material name.
# then read in and replace filenames with ufe (matName_met, file value). def for each file type (dif,met,nor,spc)
### don't know how to replace file name with UFE
# then disconnect where it's ""

### can I get the value to know to disconnect it? 

# or I could build enture shader network in ufe. 
#  create nodes
#  set values   (how do I set to a string filename?)
#  connect nodes

# can I use connect to insert filepath string?

def MtlxDisconnectNormal (texture, stackShapePath, stackShapeItem):
    
    materialName = texture.textureSet
    DAGin = stackShapePath + ",%" + materialName + "%" + materialName
    DAGout = DAGin + "_normalmap"
    AttrOut = 'outputs:out'
    AttrIn = 'inputs:normal'
    
    "|materialXStack1|materialXStackShape1,%hubcaps%hubcaps_maps%hubcaps_nor"
    = stackShapePath + ",%" + materialName + "%" + materialName + "_maps%" + materialName + "_nor"
    DAGmap = DAGin +  "_maps%" + materialName + "_nor"
    "|materialXStack1|materialXStackShape1,%hubcaps%hubcaps_maps%hubcaps_spc"
             
    mtlxSurfacePath = stackShapePath + ",%" + materialName + "%" + materialName + "_normalmap"

    # Get the document SceneItem (since it is the parent to use when adding nodes)
    doc = ufe.Hierarchy.hierarchy(stackShapeItem).children()[-1]
    connectionHandler = ufe.RunTimeMgr.instance().connectionHandler(doc.runTimeId())

    # create ufe nodes/items
    ufeMapNode = createUfeSceneItem(DAGmap) 
    ufeOutNode = createUfeSceneItem(DAGout) 
    ufeInNode = createUfeSceneItem(DAGin)  

    # attr info
    OutInfo = ufe.AttributeInfo(ufeImg.path(), AttrOut)
    InInfo = ufe.AttributeInfo(ufeSurf.path(), AttrIn)
    
    # disconnect
    connectionHandler.disconnect(OutInfo, InInfo)
    
    # get attr info (testing)
    ''' 
    surfaceAttrs = ufe.Attributes.attributes(ufeImg)
    print(surfaceAttrs.attributeNames)
    '''

def MtlxDisconnectSpc (texture, stackShapePath, stackShapeItem):
    
    materialName = texture.textureSet
    DAGin = stackShapePath + ",%" + materialName + "%" + materialName
    DAGoutSpc = DAGin + "_roughness_lerp"
    AttrOut = 'outputs:out'
    AttrIn = 'inputs:specular_roughness'
             
    # Get the document SceneItem (since it is the parent to use when adding nodes)
    doc = ufe.Hierarchy.hierarchy(stackShapeItem).children()[-1]
    connectionHandler = ufe.RunTimeMgr.instance().connectionHandler(doc.runTimeId())

    # create ufe nodes/items
    ufeOutNode = createUfeSceneItem(DAGout) # 'outputs:out'
    ufeInNode = createUfeSceneItem(DAGin)  # 'inputs:base_color'

    # attr info
    OutInfo = ufe.AttributeInfo(ufeImg.path(), AttrOut)
    InInfo = ufe.AttributeInfo(ufeSurf.path(), AttrIn)
    
    # disconnect
    connectionHandler.disconnect(OutInfo, InInfo)
    
    
    
# stack
#stackShapeName = mc.createNode( 'materialxStack' )
#stackShapePath = mel.eval('ls -l {}'.format(stackShapeName))[0]
#stackShapeItem = ufe.Hierarchy.createItem(ufe.PathString.path(stackShapePath))
#contextOps = ufe.ContextOps.contextOps(stackShapeItem)

# Get the document SceneItem (since it is the parent to use when adding nodes)
doc = ufe.Hierarchy.hierarchy(stackShapeItem).children()[-1]
connectionHandler = ufe.RunTimeMgr.instance().connectionHandler(doc.runTimeId())

# node dag paths
Surf = "|materialXStack1|materialXStackShape1,%document1%standard_surface1"
img = "|materialXStack1|materialXStackShape1,%document1%tiledimage1"

def createUfeSceneItem(dagPath):
    """
    Make ufe item out of dag path
    """
    ufePath = ufe.PathString.path('{}'.format(dagPath))
    ufeItem = ufe.Hierarchy.createItem(ufePath)
    
    return ufeItem

# ufeSceneItem = createUfeSceneItem(dagPath)

# create ufe nodes/items
ufeSurf = createUfeSceneItem(Surf)  # 'inputs:base_color'
ufeImg = createUfeSceneItem(img) # 'outputs:out'

print(ufeSurf)
# attr info
OutInfo = ufe.AttributeInfo(ufeImg.path(), 'outputs:out')
InInfo = ufe.AttributeInfo(ufeSurf.path(), 'inputs:base_color')

# connect
connectionHandler.connect(OutInfo, InInfo)

# disconnect
connectionHandler.disconnect(OutInfo, InInfo)



#find flat maps
# exclude from replace

# inspect imported doc for temp.jpg
# disconnect 





                        
'''


######################### 

# how to select?

# (dis)Connect the surface to the material:
surfaceAttrs = ufe.Attributes.attributes(surfaceNode)
surfaceOutput = surfaceAttrs.attribute("outputs:out")

matAttrs = ufe.Attributes.attributes(matNode)
matInput = matAttrs.attribute("inputs:surfaceshader")

connectionHandler = ufe.RunTimeMgr.instance().connectionHandler(doc.runTimeId())
connectionHandler.disconnect(surfaceOutput, matInput)

                           
######## 
contextOps = ufe.ContextOps.contextOps(stackShapeItem)
contextOps.doOp(['MxDeleteItems'])

DeleteItems


            
#########

        # 1. get mtlX SG path
        mtlxSurfacePath = stackShapePath + ",%" + texture.textureSet + "%" + texture.textureSet + "_SG"
        print (mtlxSurfacePath)
        
        # 2. select geo

        SG = mc.listConnections(texture.textureSet + '.outColor', d=True)[0]
        print (SG)
        
        for texture in texturesToUse:
            if mc.objExists(texture.textureSet)
        
                geoName = mc.listConnections(SG, type='mesh')
                print (geoName)
        mc.select (geoName, r=True)

        # 3. assign materialX SG to geo
        mc.materialxAssign (edit=True, assign=True, sourcePath=mtlxSurfacePath)
        
        
############      
        



# assign mtlx to geo...
# 1. get mtlX SG path
SG_path = stackShapePath + ",%" + shaderName + "%" + shaderName + "_SG"

# 2. select geo
MayaMaterial = "surf" # textureSet name

shader = mc.listConnections(MayaMaterial + '.outColor', d=True)[0]
geoName = mc.listConnections(shader, type='mesh')
mc.select (geoName, r=True)

# 3. assign materialX SG to geo
mc.materialxAssign (edit=True, assign=True, sourcePath=SG_path)
    
##########################


def connectMtlX(ui, texture, renderer, fileNode):

    clean = ui.checkboxRem.isChecked()
    attributeName = texture.materialAttribute
    

##################


'''




