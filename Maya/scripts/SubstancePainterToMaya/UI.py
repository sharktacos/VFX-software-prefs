try:
    import PySide2 as PySide
except:
    import PySide6 as PySide

try:
    from shiboken2 import wrapInstance
except:
    from shiboken6 import wrapInstance

from maya import OpenMayaUI as omui
import maya.cmds as mc
import os
from SubstancePainterToMaya import config as cfg
from importlib import reload
reload(cfg)

class PainterToMayaUI:

    def __init__(self):

        self.actualWorkspace = mc.workspace(fullName=True)
        self.PLUGIN_NAME = self.PLUGIN_VERSION = self.TEXTURE_FOLDER = ''
        self.PLUGIN_NAME = cfg.PLUGIN_NAME
        self.PLUGIN_VERSION = cfg.PLUGIN_VERSION
        self.TEXTURE_FOLDER = mc.workspace(fre='sourceImages')
        self.INFOS = cfg.INFOS
        self.PAINTER_IMAGE_EXTENSIONS = cfg.PAINTER_IMAGE_EXTENSIONS
        self.DELIMITERS = cfg.DELIMITERS

        print('\n\n' + self.PLUGIN_NAME + ' version ' + self.PLUGIN_VERSION + '\n')

    def createUI(self):
        """
        Creates the UI
        :return: None
        """

        mayaMainWindowPtr = omui.MQtUtil.mainWindow()
        mayaMainWindow = wrapInstance(int(mayaMainWindowPtr), PySide.QtWidgets.QWidget)

        # Create our main window
        self.mainWindow = PySide.QtWidgets.QDialog()
        self.mainWindow.setParent(mayaMainWindow)
        self.mainWindow.setWindowTitle(self.PLUGIN_NAME + ' version ' + self.PLUGIN_VERSION)
        # self.mainWindow.setFixedSize(220,450)
        self.mainWindow.setWindowFlags(PySide.QtCore.Qt.Window)

        # Create vertical layout
        self.layVMainWindowMain = PySide.QtWidgets.QVBoxLayout()
        self.mainWindow.setLayout(self.layVMainWindowMain)

        # Create horizontal layout
        self.layHMainWindowMain = PySide.QtWidgets.QHBoxLayout()
        self.layVMainWindowMain.insertLayout(0, self.layHMainWindowMain, stretch=1)

        # Create two vertical layouts
        self.layVMainWindow01 = PySide.QtWidgets.QVBoxLayout()
        self.layHMainWindowMain.insertLayout(0, self.layVMainWindow01, stretch=1)
        self.layVMainWindow02 = PySide.QtWidgets.QVBoxLayout()
        self.layHMainWindowMain.insertLayout(1, self.layVMainWindow02, stretch=3)

        # Texture Folder
        self.grpBrowseForDirectory = PySide.QtWidgets.QGroupBox('Textures Folder')
        self.layVMainWindow01.addWidget(self.grpBrowseForDirectory)

        self.textureFolderLayout = PySide.QtWidgets.QHBoxLayout()
        self.grpBrowseForDirectory.setLayout(self.textureFolderLayout)

        # Add Texture folder widgets
        sourceImagesFolder = self.actualWorkspace + '/' + self.TEXTURE_FOLDER
        self.texturePath = PySide.QtWidgets.QLineEdit(sourceImagesFolder)
        self.texturePath.setToolTip('Set the path of your texture folder')
        self.textureFolderLayout.addWidget(self.texturePath)

        self.getButton = PySide.QtWidgets.QPushButton('Get')
        self.getButton.clicked.connect(lambda: self.getTextureFolder())
        self.textureFolderLayout.addWidget(self.getButton)
        self.getButton.setToolTip('Get your texture folder using a dialog window')
        self.getButton.setToolTipDuration(2000)

        # Naming Convention
        self.grpNamingConvention = PySide.QtWidgets.QGroupBox('Naming Convention')
        self.layVMainWindow01.addWidget(self.grpNamingConvention)


        self.namingConventionLayout = PySide.QtWidgets.QVBoxLayout()
        self.grpNamingConvention.setLayout(self.namingConventionLayout)

        self.nomenclatureInfo = PySide.QtWidgets.QLabel(
            'Enter the name of one of your shaders, and an example map type\n (dif, bmp, etc.) used in the texture file\'s naming convention.'
        )

        self.nomenclatureInfo.setToolTip(
            'The script uses the defined textureSet and map\'s names to understand your naming convention. \nI.e: myProject_character_left_arm_metalness.png will have character_left_arm as textureSet and metalness as map\nThen the script will find all your textureSets and maps, looking for the different parts of your files names'
        )

        self.namingConventionLayout.addWidget(self.nomenclatureInfo)

#        self.namingConventionSubLayout1 = PySide.QtWidgets.QHBoxLayout()
#        self.namingConventionLayout.insertLayout(-1, self.namingConventionSubLayout1, stretch=0)

#        self.namingConventionSubLayoutLabel = PySide.QtWidgets.QVBoxLayout()
     
#        self.namingConventionSubLayout1.insertLayout(1, self.namingConventionSubLayoutLabel, stretch=0)

#        self.namingConventionSubLayoutValue = PySide.QtWidgets.QVBoxLayout()
#        self.namingConventionSubLayout1.insertLayout(2, self.namingConventionSubLayoutValue, stretch=0)






        # Add Naming Convention widgets
        self.textureSetLabel = PySide.QtWidgets.QLabel('Texture Set/Shader Name')
        self.namingConventionLayout.addWidget(self.textureSetLabel)

        self.textureSet = PySide.QtWidgets.QLineEdit('enter_shader_name')
        # enter_shader_name
        self.textureSet.setToolTip(
            'Example of the part of the texture file name containing the material\'s name (textureSet)'
        )
        self.namingConventionLayout.addWidget(self.textureSet)

        self.mapLabel = PySide.QtWidgets.QLabel('Map Type')
        self.namingConventionLayout.addWidget(self.mapLabel)
        self.mapLabel.resize(200,200)

        self.map = PySide.QtWidgets.QLineEdit('dif')
        self.map.setToolTip(
            'Example of the part of the texture file name defining the map type.'
        )
        self.namingConventionLayout.addWidget(self.map)



        # option "use all" or "use selected" (disabled)
        self.grpRadioTextureSets = PySide.QtWidgets.QButtonGroup()
        self.textureSetRadio1 = PySide.QtWidgets.QRadioButton('Use all found texture sets')
        self.textureSetRadio1.setChecked(True)
        self.textureSetRadio1.setVisible(False)

        self.grpRadioTextureSets.addButton(self.textureSetRadio1)
        self.textureSetRadio2 = PySide.QtWidgets.QRadioButton('Use only specified texture set')
        self.textureSetRadio2.setVisible(False)
        self.grpRadioTextureSets.addButton(self.textureSetRadio2)

        self.namingConventionLayout.addWidget(self.textureSetRadio1)
        self.namingConventionLayout.addWidget(self.textureSetRadio2)






        # Renderer
        self.grpRenderer = PySide.QtWidgets.QGroupBox('Renderer')
        self.layVMainWindow01.addWidget(self.grpRenderer)

        self.rendererLayout = PySide.QtWidgets.QVBoxLayout()
        self.grpRenderer.setLayout(self.rendererLayout)

        # Add Renderer widgets
        self.grpRadioRenderer = PySide.QtWidgets.QButtonGroup()

        self.rendererRadio1 = PySide.QtWidgets.QRadioButton('Arnold (aiStandardSurface)')
        self.rendererRadio1.setChecked(True)
        self.grpRadioRenderer.addButton(self.rendererRadio1)

        self.rendererRadio2 = PySide.QtWidgets.QRadioButton('Unreal Engine (Blinn) for FBX')
        self.grpRadioRenderer.addButton(self.rendererRadio2)
        
        self.rendererRadio3 = PySide.QtWidgets.QRadioButton('MaterialX for Maya 2025')
        self.grpRadioRenderer.addButton(self.rendererRadio3)

        self.rendererLayout.addWidget(self.rendererRadio1)
        self.rendererLayout.addWidget(self.rendererRadio2)
        self.rendererLayout.addWidget(self.rendererRadio3)


        # Materials 
        #self.grpMaterials = PySide.QtWidgets.QGroupBox('Materials')
        self.grpMaterials = PySide.QtWidgets.QGroupBox('')
        self.layVMainWindow01.addWidget(self.grpMaterials)

        self.materialsLayout = PySide.QtWidgets.QVBoxLayout()
        self.grpMaterials.setLayout(self.materialsLayout)

        # Add Materials widgets
        self.grpRadioMaterials = PySide.QtWidgets.QButtonGroup()

        self.materialsRadio1 = PySide.QtWidgets.QRadioButton(
            'Use existing materials, if they don\'t exist, create new ones (not assigned)')
        self.materialsRadio1.setVisible(False)
        self.grpRadioMaterials.addButton(self.materialsRadio1)

        self.materialsRadio2 = PySide.QtWidgets.QRadioButton('Create new materials (not assigned)')
        self.materialsRadio2.setVisible(False)
        self.grpRadioMaterials.addButton(self.materialsRadio2)

        self.materialsRadio3 = PySide.QtWidgets.QRadioButton('Use existing materials. Convert if wrong material type.')
        self.grpRadioMaterials.addButton(self.materialsRadio3)
        self.materialsRadio3.setChecked(True)
        self.materialsRadio3.setVisible(False)
        self.materialsLayout.addWidget(self.materialsRadio3)
        

        self.materialsLayout.addWidget(self.materialsRadio1)
        self.materialsLayout.addWidget(self.materialsRadio2)
        self.materialsLayout.addWidget(self.materialsRadio3)






        # Launch button
        self.grpLaunch = PySide.QtWidgets.QGroupBox('Check for textures')
        self.layVMainWindow01.addWidget(self.grpLaunch)

        self.launchLayout = PySide.QtWidgets.QVBoxLayout()
        self.grpLaunch.setLayout(self.launchLayout)

        # Add Launch widgets
        self.launchButton = PySide.QtWidgets.QPushButton('Launch')
        self.launchLayout.addWidget(self.launchButton)

        # Found Maps
        self.grpFoundMaps = PySide.QtWidgets.QGroupBox('Found Maps')
        self.layVMainWindow02.addWidget(self.grpFoundMaps)

        self.foundMapsLayout = PySide.QtWidgets.QVBoxLayout()
        self.grpFoundMaps.setLayout(self.foundMapsLayout)

        self.scroll = PySide.QtWidgets.QScrollArea()
        self.scroll.setWidget(self.grpFoundMaps)
        self.scroll.setWidgetResizable(True)
        self.scroll.setFixedHeight(300)
        self.scroll.setFixedWidth(500)
        self.layVMainWindow02.addWidget(self.scroll)

        # Options
        self.grpOptions = PySide.QtWidgets.QGroupBox('Options')
        self.layVMainWindow02.addWidget(self.grpOptions)

        self.optionsLayout = PySide.QtWidgets.QVBoxLayout()
        self.grpOptions.setLayout(self.optionsLayout)

        self.optionsSubLayout1 = PySide.QtWidgets.QVBoxLayout()
#        self.optionsLayout.insertLayout(1, self.optionsSubLayout1, stretch=1)

        self.optionsSubLayout2 = PySide.QtWidgets.QHBoxLayout()
#        self.optionsLayout.insertLayout(2, self.optionsSubLayout2, stretch=1)

        
        # Options Widgets
        self.checkboxUDIMs = PySide.QtWidgets.QCheckBox('Use UDIMs')
        self.checkboxUDIMs.setChecked(True)
        self.checkboxUDIMs.setVisible(False)
        self.optionsLayout.addWidget(self.checkboxUDIMs)

        self.checkbox1 = PySide.QtWidgets.QCheckBox('Use height as bump')
        self.checkbox1.setChecked(True)
        self.checkbox1.setVisible(False)

        self.checkbox2 = PySide.QtWidgets.QCheckBox('Use height as displacement')
        self.checkbox2.setVisible(False)
        self.optionsLayout.addWidget(self.checkbox2)


        self.checkbox3 = PySide.QtWidgets.QCheckBox('Force texture replacement')
        self.checkbox3.setChecked(True)
        self.checkbox3.setEnabled(False)
        self.checkbox3.setVisible(False)
        self.optionsLayout.addWidget(self.checkbox3)

        self.checkboxFlatX = PySide.QtWidgets.QCheckBox('Disconnect flat texture maps for MaterialX')
        self.checkboxFlatX.setChecked(True)
        self.optionsLayout.addWidget(self.checkboxFlatX)
        
        self.checkboxRem = PySide.QtWidgets.QCheckBox('Delete flat texture map files (bump, normal, spec, metal)')
        self.checkboxRem.setChecked(False)
        self.optionsLayout.addWidget(self.checkboxRem)

        self.checkbox4 = PySide.QtWidgets.QCheckBox('Create layer shader networks (When \"layer\"" texture map found)')
        self.optionsLayout.addWidget(self.checkbox4)
        # If UE render hide layer option
        if self.grpRadioRenderer.checkedId() == -3:
            print ('it is true')
            self.checkbox4.setChecked(False)
            self.checkbox4.setVisible(False)
        else:
            self.checkbox4.setChecked(True)

        # Proceed
        self.grpProceed = PySide.QtWidgets.QGroupBox('Proceed')
        self.layVMainWindow02.addWidget(self.grpProceed)

        self.proceedLayout = PySide.QtWidgets.QVBoxLayout()
        self.grpProceed.setLayout(self.proceedLayout)

        # Proceed widgets
        self.proceedButton = PySide.QtWidgets.QPushButton('Proceed')
        self.proceedLayout.addWidget(self.proceedButton)

        # Infos
        self.grpInfos = PySide.QtWidgets.QGroupBox('Credits')
        self.layVMainWindowMain.addWidget(self.grpInfos)

        self.infosLayout = PySide.QtWidgets.QVBoxLayout()
        self.grpInfos.setLayout(self.infosLayout)

        # Infos widgets
        self.infos = PySide.QtWidgets.QLabel(self.INFOS)
        self.infosLayout.addWidget(self.infos)
        self.infos.setAlignment(PySide.QtCore.Qt.AlignCenter | PySide.QtCore.Qt.AlignVCenter)

        # Hide some
        self.grpFoundMaps.setVisible(False)
        self.grpOptions.setVisible(False)
        self.grpProceed.setVisible(False)
        self.scroll.setVisible(False)

        global window

        try:
            window.close()
            window.deleteLater()
        except:
            pass

        window = self.mainWindow

        self.mainWindow.show()
        print('UI opened')


    def getTextureFolder(self):
        """
        Get the base texture path in the interface, the file dialog starts in the base texture path of the project
        :return: The texture directory
        """

        # Get project
        projectDirectory = mc.workspace(rootDirectory=True, query=True)

        # Set base texture folder
        textureFolder = projectDirectory + '/' + self.TEXTURE_FOLDER

        if os.path.isdir(textureFolder):
            textures = textureFolder
        else:
            textures = projectDirectory

        # Open a file dialog
        result = mc.fileDialog2(startingDirectory=self.texturePath.text(), fileMode=2, okCaption='Select')

        if result is None:
            return

        workDirectory = result[0]

        # Update the texture path in the interface
        self.texturePath.setText(workDirectory)

        return workDirectory

