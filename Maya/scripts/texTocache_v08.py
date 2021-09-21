# ##################################################################################
#                               shader transfer for Alembic caches
#                 Concept & Design: Derek Flood, Python scripting: ShanShan He 2017
#            See https://docs.sharktacos.com/pipeline/abcTexPy.html for detailed description
#				
#		Usage: To call the script, copy the text here and paste it into the 
#		Maya Script Editor in a Python tab. Hit "play" in the Script Editor to launch the GUI.
#		You can also make a shelf button for it by selecting the text in the Python tab 
#		and MMB-draging it into the Maya shelf.
#
# 
# ##################################################################################

import maya.cmds as mc
import os, sys

if mc.window('TransferTex', ex = True):
    mc.deleteUI ('TransferTex')


window = mc.window( "TransferTex",widthHeight=(250,155))
mainLayout = mc.columnLayout( adjustableColumn=True )
routeLayout11 = mc.rowLayout(nc = 4, w = 390, cw4 = (5,90,28,5), p = mainLayout )
routeRow44 = mc.text(label = '', p = routeLayout11)
routeRow11 = mc.button( label='Select Source',command = 'sSource()' ,p = routeLayout11 ) 
routeRow22 = mc.textScrollList( 'sourcegroup', numberOfRows=6, allowMultiSelection=True, a = [], w = 150, h = 22, p = routeLayout11,
            showIndexedItem=1 )
mc.separator( height=40, w = 430, style='out', p = mainLayout )

routeLayout1 = mc.rowLayout(nc = 4, w = 390, cw4 = (5,90,28,5), p = mainLayout )
routeRow4 = mc.text(label = '', p = routeLayout1)
routeRow1 = mc.button( label='Select Target',command = 'sTarget()'  ,p = routeLayout1)
routeRow33 = mc.textScrollList( 'targetgroup', numberOfRows=6, allowMultiSelection=True, a = [], w = 150, h = 22, p = routeLayout1,
            showIndexedItem=1 )
mc.separator( height=40, w = 430, style='out', p = mainLayout )

mc.button( label='Transfer Materials',w = 150,command = 'tMaterials()' ,p =mainLayout)
mc.separator( height=30, w = 430, p = mainLayout )
mc.button( label='Close', command=('cmds.deleteUI(\"' + window + '\", window=True)') ,p =mainLayout)

mc.separator( height=20, w = 430, style='out', p = mainLayout )
mc.window('TransferTex', edit=True, widthHeight=(300, 300) ) 
mc.setParent( '..' )
mc.showWindow( window )



def sSource():
    global shadingGrps
    global sourceSel
    global sameName
    global sourceName
    global shapesInSel
    sameName = []
    sourceName = []
    transforms =  mc.ls(type='transform')
    deleteList = []
    for tran in transforms:
        if mc.nodeType(tran) == 'transform':
            children = cmds.listRelatives(tran, c=True) 
            if children == None:
                deleteList.append(tran)
    if deleteList == []:
        pass
    else:
        mc.delete(deleteList)
    # get list of selection:
    shapesInSel = mc.ls(dag=1,o=1,l=1,sl=1,g=True)
    consrain = mc.ls(type='constraint')

#    if len(consrain) > 0:
#        mc.select(consrain)
#        mc.parentConstraint(n= 'consrain', remove = True )
#    else:
#        pass
    

    
    sourceSel = mc.ls(sl=True)


    for sourceNames in shapesInSel:
        sourceName.append(sourceNames)
        oldnNames = sourceNames.split('|',2)
        for oldName in oldnNames[2:]:
            sameName.append(oldName.encode("utf-8"))

    mc.textScrollList('sourcegroup',e = True, ai = True, append = sourceSel,removeAll = True)


def sTarget():
    global shapesOutSel
    global targetSel
    global neName
    neName = []
    transforms =  mc.ls(type='transform')

    deleteList = []
    for tran in transforms:
        if mc.nodeType(tran) == 'transform':
            children = cmds.listRelatives(tran, c=True) 
            if children == None:
                deleteList.append(tran)
    
    if deleteList == []:
        pass
    else:
        mc.delete(deleteList)
    consrain = mc.ls(type='constraint')
#    if len(consrain) > 0:
#        mc.select(consrain)
#        mc.parentConstraint(n= 'consrain', remove = True )
#    else:
#        pass
    # get samename of selection:
    shapesOutSel = mc.ls(dag=1,o=1,l=1,sl=1,g=True)
    targetSel = mc.ls(sl=True)
    for targetNames in shapesOutSel:
        neNames = targetNames.rsplit('|',5)
        neName.append(neNames)

    mc.textScrollList('targetgroup',e = True, ai = True, append = targetSel,removeAll = True)



def tMaterials():
    global shadingGrps
    global sourceSel
    global shapesOutSel
    global targetSel
    global sameName
    global neName
    global sourceName
    global shapesInSel
    fullName = []
    errorList = []


    for comb in sameName:
        fullName.append(str(targetSel[0] + '|' + comb))

        
    for ii in shapesInSel:
        snames = ii.rsplit('|',2)
        shadingGrps = mc.listConnections(ii,type='shadingEngine')
        if shadingGrps == None:
            pass
        else:
            names = mc.listConnections(shadingGrps, type="mesh")
            #print shadingGrps, "->", ", ".join(names)  
            CacheGroup = mc.ls(snames[-2], l=True)
            if len(CacheGroup) < 2:
                errorfinds = "# Warning: Can't find Geo" "%s"%(snames[-2])
                errorfind = errorfinds + " in the target group"
                errorList.append(errorfind)
                someList = cmds.textScrollList('ErrorWarning', exists=True)
                if someList == False:
                    Error = mc.textScrollList( 'ErrorWarning', numberOfRows=6, allowMultiSelection=True, a = [], w = 150, h = 62, p = mainLayout,
                    showIndexedItem=1 ) 
                else:
                    pass
                mc.textScrollList('ErrorWarning',e = True, ai = True, append = "%s"%(errorfind))

    
            else:
                mc.sets(CacheGroup, edit=True, forceElement="%s"%(shadingGrps[0]))
                Geos = CacheGroup[0].split('|')
                print shadingGrps[0], "assigned to object", Geos[-1]
    for eacherror in errorList:
        print eacherror

