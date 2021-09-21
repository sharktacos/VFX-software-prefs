# ##################################################################################
#                                        dfMakeTx
#                 Concept & Design: Derek Flood, Python scripting: ShanShan He 2017
#            See http://docs.sharktacos.com/texture/mipmap.html for detailed description
#
#             A modified version of the awesome nMakeTx by Luca Fiorentini 2013
#                               luca.fiorentini@gmail.com
# ##################################################################################
#                                     USAGE:
#
# To call the script type in a python tab:
# import dfMakeTx
# dfMakeTx.Main()
# 
# ##################################################################################
#                                    ChangeLog
# ##################################################################################
# > dfMakeTx 2.0.0
#
# * Major update of GUI of nMakeTx
# * Added converstion to linear option with DWA compression based on string in file name
# * Added optional conversion of all .EXR and .HDR files using DWA compression
# * Removed all options checkboxes in old GUI, and replaced with single editable text field
#
# ##################################################################################

import maya.cmds as mc
import os
import maya.mel 
import time
import datetime
import re
import fnmatch

from subprocess import call
from maya.OpenMaya import MGlobal

class Main():
    def __init__(self):
        self.name = 'nMakeTxMainUi'
        self.title = 'dfMakeTx'
        self.mayaVersion = maya.mel.eval('getApplicationVersionAsFloat')
        self.widgetHeight = 24
        self.fieldLenght = 80
        self.checkBoxLenght = 20
        self.simpleCheckBoxes = []
        self.intCheckBoxes = []
        self.doubleIntCheckBoxes = []
        self.floatCheckBoxes = []
        self.enumCheckBoxes = []
        self.doubleEnumCheckBoxes = []
        self.stringCheckBoxes = []
        self.simpleAdditionlCheckBox = []
        
        if not mc.optionVar(q='nMakeTx_makeTxPath'):
            mc.optionVar(sv=['nMakeTx_makeTxPath',    'c:/solidangle/mtoadeploy/%s/bin' % self.mayaVersion])
        if not mc.optionVar(q='nMakeTx_convertOption'):
            mc.optionVar(iv=['nMakeTx_convertOption', 0])
        
        
        self.makeTxPath = mc.optionVar(q='nMakeTx_makeTxPath')
        self.convertBehavior = mc.optionVar(q='nMakeTx_convertOption')
                
        # Begin creating the UI
        if (mc.window(self.name, q=1, exists=1)):
            mc.deleteUI(self.name)
        
        self.window = mc.window(self.name, title=self.title, menuBar=False, s=True, resizeToFitChildren=True) ###turn on sizeable, I also add autofit UI

        self.mainWindowLayout = mc.columnLayout(adj=1)

        self.optionLayout = mc.columnLayout(adj=1, p=self.mainWindowLayout,h=348)
        mc.text(l='Convert any texture file to .tx', h=35, bgc=[.125,.125,.125], p=self.optionLayout)
        mc.text(l='', p=self.optionLayout)
        
        self.pathTextField = mc.textFieldButtonGrp('myPathTextField', label='makeTx.exe path:', text = "C:/solidangle/mtoadeploy/2017/bin", buttonLabel='Browse',  buttonCommand=Callback(self.browse, 'myPathTextField'), changeCommand=self.saveOptions, cw=[2, 350], w=600, p=self.optionLayout)
        self.textureFrom = mc.radioButtonGrp(label='Use textures from:', labelArray2=['Current scene', 'Folder'], numberOfRadioButtons=2, onc=Callback(self.switchManage, 'myTextureFolderField'), sl=2, vr=False, p=self.optionLayout)
        self.texturePathTextField = mc.textFieldButtonGrp('myTextureFolderField', label='Texture folder', buttonLabel='Browse', fileName='', cw=[2, 350], w=600, buttonCommand=Callback(self.browse, 'myTextureFolderField'), manage=True, p=self.optionLayout)
        self.convertBehaviorRadioButton = mc.radioButtonGrp(label='Convert options:', labelArray3=['Only not existing', 'Overwrite older', 'Overwrite all'], numberOfRadioButtons=3, vr=True, sl=1, cc=self.saveOptions, p=self.optionLayout)
        mc.text(l='', p=self.optionLayout)
        
        #EXTRA FLAGS

        #self.simpleCheckWidget('verbose', '-v')
        self.simpleCheckStringFieldWidget('linearize_if_matching_string', '--colorconvert ')
        self.simpleOptionMenuWidget('linear_compression_type', '-d', 'DWAB', 'DWAA')
        self.simpleCheckIntFieldWidget('linear_compression_level', '--compression')
        self.simpleCheckWidget('convert_EXR_to_mipmap', '-exr')
        self.simpleHDRCheckWidget('convert_HDR_to_mipmap', '-hdr')
        self.simpleAdditionlWidget('Additional Options:', '--fixnan')

       
        # PROGRESS BAR LAYOUT
        self.progressLayout = mc.columnLayout(adj=True, manage=False, p=self.mainWindowLayout)
        self.progressControl = mc.progressBar(h=30, p=self.progressLayout)
        mc.rowLayout(nc=2, p=self.progressLayout, adj=1, cw1=140)
        self.currentNumberText = mc.text(l='Loading files', align='left')
        self.currentFileText = mc.text(l='', align='right')
        
        # CONVERT LAYOUT
        self.buttonLayout = mc.columnLayout(adj=True, p=self.mainWindowLayout, h = 25)
        okButton = mc.button(l='Convert', c=self.convert, p=self.buttonLayout, w=100)
        
        mc.showWindow(self.window)
        mc.refresh(self.window)

            
    def simpleCheckWidget(self, myLabel, flag):
        global convertEXRcheckbox
        convertEXRcheckbox = []
        self.tempLayout = mc.rowLayout(nc=3, columnWidth3=(162, 75, 50), h=self.widgetHeight, p=self.optionLayout)
        self.checkLayout = mc.columnLayout( adjustableColumn=True, columnAttach=('both', 140) )
        myCheckBox = mc.checkBox('%sCheckBox' % myLabel, ann=flag, l='', value = 1, w=self.checkBoxLenght, p=self.checkLayout)
        convertEXRcheckbox.append('%sCheckBox' % myLabel) 
        mc.text('%sText' % myLabel, l=' '.join(myLabel.split('_')), p=self.tempLayout)        
       
    def simpleHDRCheckWidget(self, myLabel, flag):
        global convertHDRcheckbox
        convertHDRcheckbox = []
        self.tempLayout = mc.rowLayout(nc=3, columnWidth3=(162, 75, 50), h=self.widgetHeight, p=self.optionLayout)
        self.checkLayout = mc.columnLayout( adjustableColumn=True, columnAttach=('both', 140) )
        myCheckBox = mc.checkBox('%sCheckBox' % myLabel, ann=flag, l='',  value = 0, w=self.checkBoxLenght, p=self.checkLayout)
        convertHDRcheckbox.append('%sCheckBox' % myLabel)
        mc.text('%sText' % myLabel, l=' '.join(myLabel.split('_')), p=self.tempLayout)        
        


    def simpleCheckIntFieldWidget(self, myLabel, flag):
        global cLevelvalue
        self.tempLayout = mc.rowLayout(nc=3, columnWidth3=(162, 75, 50), h=self.widgetHeight, p=self.optionLayout)
        myCheckBox = mc.checkBox('%sCheckBox' % myLabel,vis = False, l='', w=self.checkBoxLenght, ann=flag, value = 1, cc=Callback(self.activateWidget, '%sIntField' % myLabel), p=self.tempLayout)
        mc.text('%sText' % myLabel, l=' '.join(myLabel.split('_')), w=150, align='left', p=self.tempLayout)
        cLevelvalues = mc.intField('%sIntField' % myLabel, w=self.fieldLenght, v=45, p=self.tempLayout, enable=True)
        cLevelvalue = cLevelvalues.split('|')[4]
        self.intCheckBoxes.append(myLabel)
        

    def simpleCheckStringFieldWidget(self, myLabel, flag, *args):
        global StringValue
        global controlCheckbox
        self.tempLayout = mc.rowLayout(nc=3, columnWidth3=(162, 75, 50), h=self.widgetHeight, p=self.optionLayout)
        self.checkLayout = mc.columnLayout( adjustableColumn=True, columnAttach=('both', 140) )
        myCheckBox = mc.checkBox('%sCheckBox' % myLabel, l='', w=self.checkBoxLenght, ann=flag, value = 1, cc=Callback(self.activateWidget, '%sStringField' % myLabel,'linear_compression_typeOptionMenu','linear_compression_levelIntField'), p=self.checkLayout)
        myStatus = mc.checkBox('%sCheckBox' % myLabel, q=True, value=True)
        controlCheckbox = '%sCheckBox' %myLabel
        mc.text('%sText' % myLabel, l=' '.join(myLabel.split('_')), w=150, align='left', p=self.tempLayout)
        StringValues = mc.textField('%sStringField' % myLabel, w=self.fieldLenght, p=self.tempLayout, enable=myStatus, insertText = '_dif_')
        StringValue = StringValues.split('|')[4]
        self.stringCheckBoxes.append(myLabel)



    def simpleAdditionlWidget(self, myLabel, flag):
        global AddOptions
        self.tempLayout = mc.rowLayout(nc=3, columnWidth3=(140, 75, 50), h=self.widgetHeight, p=self.optionLayout)
        self.checkLayout = mc.columnLayout( adjustableColumn=True, columnAttach=('both', 36) )
        #self.tempLayout = mc.columnLayout(h=48, p=self.optionLayout)
        mc.text('%sText' % myLabel, l=' '.join(myLabel.split('_')), w=150, align='left', p=self.checkLayout)
        mc.textField('AdditionOptions', w=530, p=self.tempLayout, enable=True, insertText = '--fixnan box3 --monochrome-detect --constant-color-detect --opaque-detect --unpremult --oiio')
        self.simpleAdditionlCheckBox.append(myLabel)


    def simpleOptionMenuWidget(self, myLabel, flag, *attrs):
        global cTypevalue
        global controlCheckbox
        myString = []
        self.tempLayout = mc.rowLayout(nc=3, columnWidth3=(162, 75, 50), h=self.widgetHeight, p=self.optionLayout)
        myCheckBox = mc.checkBox('%sCheckBox' % myLabel, vis = False ,l='', w=20, ann=flag, value=1, cc=Callback(self.activateWidget, '%sOptionMenu' % myLabel), p=self.tempLayout) #set value to 1 as default
        myStatus = mc.checkBox(controlCheckbox, q=True, value=True)
        mc.text('%sText' % myLabel, l=' '.join(myLabel.split('_')), w=150, align='left', p=self.tempLayout)
        cTypevalues = mc.optionMenu('%sOptionMenu' % myLabel, l='', enable=myStatus, w=80, p=self.tempLayout) ###update option manue based on checkbox value
        cTypevalue = cTypevalues.split('|')[4]
        for attr in attrs:
            mc.menuItem(attr)
        self.enumCheckBoxes.append(myLabel)


    def activateWidget(self, *args):
        for myWidget in args:
            wState = mc.control(myWidget, q=True, enable=True)
            mc.control(myWidget, e=True, enable=(1 - wState))
        
    def browse(self, widget, *args):
        myFolder = mc.fileDialog2(fileFilter='*.*', dialogStyle=2, fm=3)
        if myFolder:
            mc.textFieldButtonGrp(widget, e=True, fileName=myFolder[0])
            self.saveOptions()
        
    def saveOptions(self, *args):
        myValue = mc.textFieldButtonGrp(self.pathTextField, q=True, fileName=True)
        mc.optionVar(sv=['nMakeTx_makeTxPath', myValue])
        myValue = mc.radioButtonGrp(self.convertBehaviorRadioButton, q=True, sl=True)
        mc.optionVar(iv=['nMakeTx_convertOption', myValue - 1])
        
    def switchManage(self, widget, *args):
        currState = mc.control(widget, q=True, manage=True)
        mc.control(widget, e=True, manage=1 - currState)
        
    def convert(self, *args):
        global AddOptions
        global cTypevalue
        global cLevelvalue
        global AdditionOptions
        global StringValue
        global controlCheckbox
        global convertEXRcheckbox
        global convertHDRcheckbox
        # 0: 'Only not existing'
        # 1: 'Overwrite older'
        # 2: 'Overwrite all'
        
        # 0: from scene
        # 1: from folder

        lErrors = []

        makeTxPath = mc.textFieldButtonGrp(self.pathTextField, q=True, fileName=True)
        convertType = mc.radioButtonGrp(self.convertBehaviorRadioButton, q=True, sl=True) - 1
        sourceType = mc.radioButtonGrp(self.textureFrom, q=True, sl=True) - 1
        #showTerminal = mc.checkBox('verboseCheckBox', q=True, v=True)
     
        
        
        if not os.path.isfile('%s/maketx.exe' % makeTxPath):
            MGlobal.displayInfo('[ERROR] Unable to find makeTx.exe. Exit!')
            return
            
        if not len(mc.ls(type='file')) and not sourceType:
            MGlobal.displayInfo('[WARNING] No textures in current scene. Nothing to convert.')
            return
        
        myFileList = []
        myHDRFileList = []
        FileLists = []
        if sourceType:
            myTextureFolder = mc.textFieldButtonGrp(self.texturePathTextField, q=True, fileName=True)
            imageFormats = [  '.bmp', '.cin', '.dds', '.dpx', '.f3d', '.fits', '.hdri', '.ico', '.iff', '.jpg', '.jpeg',
                                        '.jif', '.jfif', '.jfi', '.jp2', '.j2k', '.png', '.pbm', '.pgm', '.ppm', '.ptex', '.rla',
                                        '.sgi', '.rgb', '.rgba', '.pic', '.tga', '.tif', '.tiff'  ]
           
                            
            for (fileFolder, folders, files) in os.walk(myTextureFolder): 
                for file in files:
                    if os.path.splitext(file)[-1] in imageFormats:
                        myFileList.append(os.path.join(fileFolder, file))
                if convertType != 3:
                   break
             
            if(mc.checkBox('%s'%convertHDRcheckbox[0], q = True, v = True)):
                imageFormatHDR =  ['.hdr',]
                for (fileFolder, folders, files) in os.walk(myTextureFolder): 
                   for file in files:
                       if os.path.splitext(file)[-1] in imageFormatHDR:
                            myFileList.append(os.path.join(fileFolder, file))
                   if convertType != 3:
                      break                   
            if(mc.checkBox('%s'%convertEXRcheckbox[0], q = True, v = True)):
                imageFormatEXR =  ['.exr',]
                for (fileFolder, folders, files) in os.walk(myTextureFolder):
                    for file in files:
                       if os.path.splitext(file)[-1] in imageFormatEXR:
                            myFileList.append(os.path.join(fileFolder, file))
                    if convertType != 3:
                      break               
 
           
        else:
            imageFormats = [  '.bmp', '.cin', '.dds', '.dpx', '.f3d', '.fits', '.hdri', '.ico', '.iff', '.jpg', '.jpeg',
                                        '.jif', '.jfif', '.jfi', '.jp2', '.j2k', '.png', '.pbm', '.pgm', '.ppm', '.ptex', '.rla',
                                        '.sgi', '.rgb', '.rgba', '.pic', '.tga', '.tif', '.tiff'  ]            
            for fileNode in mc.ls(type='file'):
                
                if os.path.splitext(mc.getAttr('%s.fileTextureName' % fileNode))[-1] in imageFormats:
                    myFileList.append(mc.getAttr('%s.fileTextureName' % fileNode))
               
                if(mc.checkBox('%s'%convertHDRcheckbox[0], q = True, v = True)):
                    imageFormatHDR =  ['.hdr',]
 
                    if os.path.splitext(mc.getAttr('%s.fileTextureName' % fileNode))[-1] in imageFormatHDR:
                        myFileList.append(mc.getAttr('%s.fileTextureName' % fileNode))
                        print myFileList                           
                         
                 

                if(mc.checkBox('%s'%convertEXRcheckbox[0], q = True, v = True)):
                    imageFormatEXR =  ['.exr',]
                    if os.path.splitext(mc.getAttr('%s.fileTextureName' % fileNode))[-1] in imageFormatEXR:
                        myFileList.append(mc.getAttr('%s.fileTextureName' % fileNode))
                        print myFileList                           
                         
                    
                        #myFileList.append(os.path.join(fileFolder, file))

            
        #Setting up the progress bar.
  
        x = len(myFileList)
        counter = 0
        mc.progressBar(self.progressControl, e=True, maxValue=x)

        mc.columnLayout(self.progressLayout, e=True, manage=True)
        mc.refresh(f=True)
        
        for i, texFileIn in enumerate(myFileList):
            
            allfiles = '%s'%myFileList
            StringMatch = mc.textField('%s' % StringValue, q = True, text= True)

            AddOptions = mc.textField('AdditionOptions', q = True, text= True)
 
            cType= mc.optionMenu('%s' % cTypevalue, q =True, v = True)

            cLevel = mc.intField('%s' % cLevelvalue, q =True, v = True)
 
            myPath, myFile = os.path.split(texFileIn)
            myFile, myExt = os.path.splitext(myFile)
            texFileOut = '%s/%s.tx' % (myPath, myFile)
            
            if sourceType:
                if convertType != 3:
                    if myPath != myTextureFolder:
                        break
            


            progressInc = mc.progressBar(self.progressControl, edit=True, pr=counter)
            ###check linear match and checkbox statue to print the process
            if (mc.checkBox('%s'%controlCheckbox, q = True, v = True)):
                if fnmatch.fnmatch(texFileIn, '*%s*'%StringMatch):
                    mc.text(self.currentNumberText, e=True, l='Processing file %i / %i in linear mode' % (i+1, x)) 
                else:
                    mc.text(self.currentNumberText, e=True, l='Processing file %i / %i' % (i+1, x)) 
            else:
                mc.text(self.currentNumberText, e=True, l='Processing file %i / %i' % (i+1, x))   
            mc.text(self.currentFileText, e=True, l='%s%s' % (myFile, myExt))
            mc.refresh(f=True)
            

            LinearOption ='%s' % AddOptions
            
            if (mc.checkBox('%s'%controlCheckbox, q = True, v = True)):
                LinearOption ='%s' '%s:' '%s ' '%s ' '%s' %('--compression ', cType,cLevel, '--colorconvert sRGB linear --format exr -d half', AddOptions )

            
            if not os.path.isfile(texFileOut) or convertType == 2:
                allfiles = '%s'%myFileList 
  
                 ##does it match string?
                if fnmatch.fnmatch(texFileIn, '*%s*'%'.hdr'):
                    hdrOption ='%s' '%s:' '%s ' '%s ' '%s' %('--compression ', cType,cLevel, '--format exr -d half', AddOptions )
                    call('%s/maketx.exe %s "%s"' % (makeTxPath, hdrOption, texFileIn), shell=True)
                    myPath, HDRmyFile = os.path.split(texFileIn)
                    MGlobal.displayInfo('[INFO] %s %s %s' % ('maketx.exe', hdrOption, HDRmyFile))               
                
                elif fnmatch.fnmatch(texFileIn, '*%s*'%'.exr'):
                    exrOption ='%s' '%s:' '%s ' '%s ' '%s' %('--compression ', cType,cLevel, '--format exr -d half', AddOptions )
                    call('%s/maketx.exe %s "%s"' % (makeTxPath, exrOption, texFileIn), shell=True)
                    myPath, EXRmyFile = os.path.split(texFileIn)
                    MGlobal.displayInfo('[INFO] %s %s %s' % ('maketx.exe', exrOption, EXRmyFile))
                elif fnmatch.fnmatch(texFileIn, '*%s*'%StringMatch):
                    
       
                    call('%s/maketx.exe %s "%s"' % (makeTxPath, LinearOption, texFileIn), shell=True)
                    myPath, matchmyFile = os.path.split(texFileIn)
                    MGlobal.displayInfo('[INFO] %s %s %s' % ('maketx.exe', LinearOption, matchmyFile))
                      
                else:
                    call('%s/maketx.exe %s "%s"' % (makeTxPath, AddOptions,texFileIn), shell=True)
                    myPath, shormyFile = os.path.split(texFileIn)
                    MGlobal.displayInfo('[INFO] %s %s %s' % ('maketx.exe', AddOptions, shormyFile)) 
                    

     
                # Check if the texture has been converted and add the errors to a list

                if not os.path.isfile(texFileOut):
                        lErrors.append(texFileOut)
                
            elif convertType == 1:
                sourceFileDate = datetime.datetime.fromtimestamp(os.path.getmtime(texFileIn))
                
                try:
                    with open(texFileOut, 'r') as f:
                        destFileDate = datetime.datetime.fromtimestamp(os.path.getmtime(texFileOut))
                except:
                    destFileDate = datetime.datetime.min
                    

                
                if sourceFileDate > destFileDate:
                    

                     ##does it match string?
                    if fnmatch.fnmatch(texFileIn, '*%s*'%'.hdr'):
                        hdrOption ='%s' '%s:' '%s ' '%s ' '%s' %('--compression ', cType,cLevel, '--format exr -d half', AddOptions )
                        call('%s/maketx.exe %s "%s"' % (makeTxPath, hdrOption, texFileIn), shell=True)
                        myPath, HDRmyFile = os.path.split(texFileIn)
                        MGlobal.displayInfo('[INFO] %s %s %s' % ('maketx.exe', hdrOption, HDRmyFile))               
                    
                    elif fnmatch.fnmatch(texFileIn, '*%s*'%'.exr'):
                        exrOption ='%s' '%s:' '%s ' '%s ' '%s' %('--compression ', cType,cLevel, '--format exr -d half', AddOptions )
                        call('%s/maketx.exe %s "%s"' % (makeTxPath, exrOption, texFileIn), shell=True)
                        myPath, EXRmyFile = os.path.split(texFileIn)
                        MGlobal.displayInfo('[INFO] %s %s %s' % ('maketx.exe', exrOption, EXRmyFile))
                    elif fnmatch.fnmatch(texFileIn, '*%s*'%StringMatch):
                        
           
                        call('%s/maketx.exe %s "%s"' % (makeTxPath, LinearOption, texFileIn), shell=True)
                        myPath, matchmyFile = os.path.split(texFileIn)
                        MGlobal.displayInfo('[INFO] %s %s %s' % ('maketx.exe', LinearOption, matchmyFile))
                                                               
                    
                    else:
                        call('%s/maketx.exe %s "%s"' % (makeTxPath, AddOptions,texFileIn), shell=True)
                        myPath, shormyFile = os.path.split(texFileIn)
                        MGlobal.displayInfo('[INFO] %s %s %s' % ('maketx.exe', AddOptions, shormyFile))                                                
         
                    if not os.path.isfile(texFileOut):
                        lErrors.append(texFileOut)
            
                else:

                    MGlobal.displayInfo('[INFO] %s is up to date' % (texFileOut))
            else:
                MGlobal.displayInfo('[INFO] %s already present, skipped' % texFileOut)    
                                            
            counter = counter + 1 
            
        mc.columnLayout(self.progressLayout, e=True, manage=False)
        
        if lErrors:
            MGlobal.displayInfo('[ERROR] unable to write the following files: %s' % lErrors)

# Class used to pass arguments to commands (like with buttons)
class Callback(object): 
        def __init__(self, func, *args, **kwargs): 
                self.func = func 
                self.args = args 
                self.kwargs = kwargs
        def __call__(self, *args): 
                return self.func( *self.args, **self.kwargs )