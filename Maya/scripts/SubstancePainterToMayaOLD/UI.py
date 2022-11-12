from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets
from shiboken2 import wrapInstance
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
        mayaMainWindow = wrapInstance(int(mayaMainWindowPtr), QtWidgets.QWidget)

        # Create our main window
        self.mainWindow = QtWidgets.QDialog()
        self.mainWindow.setParent(mayaMainWindow)
        self.mainWindow.setWindowTitle(self.PLUGIN_NAME + ' version ' + self.PLUGIN_VERSION)
        # self.mainWindow.setFixedSize(220,450)
        self.mainWindow.setWindowFlags(QtCore.Qt.Window)

        # Create vertical layout
        self.layVMainWindowMain = QtWidgets.QVBoxLayout()
        self.mainWindow.setLayout(self.layVMainWindowMain)

        # Create horizontal layout
        self.layHMainWindowMain = QtWidgets.QHBoxLayout()
        self.layVMainWindowMain.insertLayout(0, self.layHMainWindowMain, stretch=1)

        # Create two vertical layouts
        self.layVMainWindow01 = QtWidgets.QVBoxLayout()
        self.layHMainWindowMain.insertLayout(0, self.layVMainWindow01, stretch=1)
        self.layVMainWindow02 = QtWidgets.QVBoxLayout()
        self.layHMainWindowMain.insertLayout(1, self.layVMainWindow02, stretch=3)

        # Texture Folder
        self.grpBrowseForDirectory = QtWidgets.QGroupBox('Textures Folder')
        self.layVMainWindow01.addWidget(self.grpBrowseForDirectory)

        self.textureFolderLayout = QtWidgets.QHBoxLayout()
        self.grpBrowseForDirectory.setLayout(self.textureFolderLayout)

        # Add Texture folder widgets
        sourceImagesFolder = self.actualWorkspace + '/' + self.TEXTURE_FOLDER
        self.texturePath = QtWidgets.QLineEdit(sourceImagesFolder)
        self.texturePath.setToolTip('Set the path of your texture folder')
        self.textureFolderLayout.addWidget(self.texturePath)

        self.getButton = QtWidgets.QPushButton('Get')
        self.getButton.clicked.connect(lambda: self.getTextureFolder())
        self.textureFolderLayout.addWidget(self.getButton)
        self.getButton.setToolTip('Get your texture folder using a dialog window')
        self.getButton.setToolTipDuration(2000)

        # Naming Convention
        self.grpNamingConvention = QtWidgets.QGroupBox('Naming Convention')
        self.layVMainWindow01.addWidget(self.grpNamingConvention)

        self.namingConventionLayout = QtWidgets.QVBoxLayout()
        self.grpNamingConvention.setLayout(self.namingConventionLayout)

        self.nomenclatureInfo = QtWidgets.QLabel(
            'Enter the name of one of your shaders, and an example map type\n (dif, bmp, etc.) used in the texture file\'s naming convention.'
        )
        self.nomenclatureInfo.setToolTip(
            'The script uses the defined textureSet and map\'s names to understand your naming convention. \nI.e: myProject_character_left_arm_metalness.png will have character_left_arm as textureSet and metalness as map\nThen the script will find all your textureSets and maps, looking for the different parts of your files names'
        )
        self.namingConventionLayout.addWidget(self.nomenclatureInfo)

        self.namingConventionSubLayout1 = QtWidgets.QHBoxLayout()
        self.namingConventionLayout.insertLayout(-1, self.namingConventionSubLayout1, stretch=0)

        self.namingConventionSubLayoutLabel = QtWidgets.QVBoxLayout()
        self.namingConventionSubLayout1.insertLayout(1, self.namingConventionSubLayoutLabel, stretch=0)

        self.namingConventionSubLayoutValue = QtWidgets.QVBoxLayout()
        self.namingConventionSubLayout1.insertLayout(2, self.namingConventionSubLayoutValue, stretch=0)

        # Add Naming Convention widgets
        self.textureSetLabel = QtWidgets.QLabel('Texture Set/Shader Name')
        self.namingConventionSubLayoutLabel.addWidget(self.textureSetLabel)

        self.textureSet = QtWidgets.QLineEdit('enter_shader_name')
        self.textureSet.setToolTip(
            'Example of the part of the texture file name containing the material\'s name (textureSet)'
        )
        self.namingConventionSubLayoutValue.addWidget(self.textureSet)

        self.mapLabel = QtWidgets.QLabel('Map Type')
        self.namingConventionSubLayoutLabel.addWidget(self.mapLabel)
        self.mapLabel.resize(200,200)

        self.map = QtWidgets.QLineEdit('dif')
        self.map.setToolTip(
            'Example of the part of the texture file name defining the map type.'
        )
        self.namingConventionSubLayoutValue.addWidget(self.map)

        self.grpRadioTextureSets = QtWidgets.QButtonGroup()
        self.textureSetRadio1 = QtWidgets.QRadioButton('Use all found texture sets')
        self.textureSetRadio1.setChecked(True)
        self.grpRadioTextureSets.addButton(self.textureSetRadio1)
        self.textureSetRadio2 = QtWidgets.QRadioButton('Use only specified texture set')
        self.grpRadioTextureSets.addButton(self.textureSetRadio2)

        self.namingConventionLayout.addWidget(self.textureSetRadio1)
        self.namingConventionLayout.addWidget(self.textureSetRadio2)

        # Renderer
#        self.grpRenderer = QtWidgets.QGroupBox('Renderer')
#        self.layVMainWindow01.addWidget(self.grpRenderer)

        self.rendererLayout = QtWidgets.QVBoxLayout()
#        self.grpRenderer.setLayout(self.rendererLayout)

        # Add Renderer widgets
        self.grpRadioRenderer = QtWidgets.QButtonGroup()
        self.rendererRadio1 = QtWidgets.QRadioButton('Arnold (aiStandardSurface)')
        self.rendererRadio1.setChecked(True)
        self.rendererRadio1.setVisible(False)

        self.grpRadioRenderer.addButton(self.rendererRadio1)

#        self.rendererRadio2 = QtWidgets.QRadioButton('VRay (VrayMtl)')
#        self.grpRadioRenderer.addButton(self.rendererRadio2)
#        self.rendererRadio3 = QtWidgets.QRadioButton('Renderman (PxrDisney)')
#        self.grpRadioRenderer.addButton(self.rendererRadio3)
#        self.rendererRadio4 = QtWidgets.QRadioButton('Renderman (PxrSurface)')
#        self.grpRadioRenderer.addButton(self.rendererRadio4)
#        self.rendererRadio5 = QtWidgets.QRadioButton('Redshift (RedshiftMaterial)')
#        self.grpRadioRenderer.addButton(self.rendererRadio5)
#        self.rendererRadio6 = QtWidgets.QRadioButton('StingrayPBS')
#        self.rendererRadio6.toggled.connect(lambda: self.stingraySwitch())
#        self.grpRadioRenderer.addButton(self.rendererRadio6)

        self.rendererLayout.addWidget(self.rendererRadio1)

#        self.rendererLayout.addWidget(self.rendererRadio2)
#        self.rendererLayout.addWidget(self.rendererRadio3)
#        self.rendererLayout.addWidget(self.rendererRadio4)
#        self.rendererLayout.addWidget(self.rendererRadio5)
#        self.rendererLayout.addWidget(self.rendererRadio6)

        # Materials
        self.grpMaterials = QtWidgets.QGroupBox('Materials')
        self.layVMainWindow01.addWidget(self.grpMaterials)

        self.materialsLayout = QtWidgets.QVBoxLayout()
        self.grpMaterials.setLayout(self.materialsLayout)

        # Add Materials widgets
        self.grpRadioMaterials = QtWidgets.QButtonGroup()

        self.materialsRadio1 = QtWidgets.QRadioButton(
            'Use existing materials, if they don\'t exist, create new ones')
        self.grpRadioMaterials.addButton(self.materialsRadio1)
        self.materialsRadio1.setChecked(True)

        self.materialsRadio2 = QtWidgets.QRadioButton('Create new materials')
        self.grpRadioMaterials.addButton(self.materialsRadio2)

        self.materialsRadio3 = QtWidgets.QRadioButton('Use existing materials')
        self.grpRadioMaterials.addButton(self.materialsRadio3)

        self.materialsLayout.addWidget(self.materialsRadio1)
        self.materialsLayout.addWidget(self.materialsRadio2)
        self.materialsLayout.addWidget(self.materialsRadio3)

        # Launch button
        self.grpLaunch = QtWidgets.QGroupBox('Check for textures')
        self.layVMainWindow01.addWidget(self.grpLaunch)

        self.launchLayout = QtWidgets.QVBoxLayout()
        self.grpLaunch.setLayout(self.launchLayout)

        # Add Launch widgets
        self.launchButton = QtWidgets.QPushButton('Launch')
        self.launchLayout.addWidget(self.launchButton)

        # Found Maps
        self.grpFoundMaps = QtWidgets.QGroupBox('Found Maps')
        self.layVMainWindow02.addWidget(self.grpFoundMaps)

        self.foundMapsLayout = QtWidgets.QVBoxLayout()
        self.grpFoundMaps.setLayout(self.foundMapsLayout)

        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setWidget(self.grpFoundMaps)
        self.scroll.setWidgetResizable(True)
        self.scroll.setFixedHeight(300)
        self.scroll.setFixedWidth(500)
        self.layVMainWindow02.addWidget(self.scroll)

        # Options
        self.grpOptions = QtWidgets.QGroupBox('Options')
        self.layVMainWindow02.addWidget(self.grpOptions)

        self.optionsLayout = QtWidgets.QVBoxLayout()
        self.grpOptions.setLayout(self.optionsLayout)

        self.optionsSubLayout1 = QtWidgets.QVBoxLayout()
        self.optionsLayout.insertLayout(1, self.optionsSubLayout1, stretch=1)

        self.optionsSubLayout2 = QtWidgets.QHBoxLayout()
        self.optionsLayout.insertLayout(2, self.optionsSubLayout2, stretch=1)

        # Options Widgets
        self.checkboxUDIMs = QtWidgets.QCheckBox('Use UDIMs')
        self.checkboxUDIMs.setChecked(True)
        self.checkboxUDIMs.setVisible(False)
        self.optionsSubLayout1.addWidget(self.checkboxUDIMs)

        self.checkbox1 = QtWidgets.QCheckBox('Use height as bump')
        self.checkbox1.setChecked(True)
        self.checkbox1.setVisible(False)
        self.optionsSubLayout1.addWidget(self.checkbox1)

        self.checkbox2 = QtWidgets.QCheckBox('Use height as displacement')
        self.checkbox2.setVisible(False)
        self.optionsSubLayout1.addWidget(self.checkbox2)


        self.checkbox3 = QtWidgets.QCheckBox('Force texture replacement')
        self.checkbox3.setChecked(True)
        self.checkbox3.setEnabled(False)
        self.checkbox3.setVisible(False)
        self.optionsSubLayout1.addWidget(self.checkbox3)

        self.checkboxRem = QtWidgets.QCheckBox('Delete flat texture map files (bump, normal, spec, metal)')
        self.checkboxRem.setChecked(False)
        self.optionsSubLayout1.addWidget(self.checkboxRem)

        self.checkbox4 = QtWidgets.QCheckBox('Create layer shader networks (When \"layer\"" texture map found)')
        self.checkbox4.setChecked(True)
        self.optionsSubLayout1.addWidget(self.checkbox4)

        # Proceed
        self.grpProceed = QtWidgets.QGroupBox('Proceed')
        self.layVMainWindow02.addWidget(self.grpProceed)

        self.proceedLayout = QtWidgets.QVBoxLayout()
        self.grpProceed.setLayout(self.proceedLayout)

        # Proceed widgets
        self.proceedButton = QtWidgets.QPushButton('Proceed')
        self.proceedLayout.addWidget(self.proceedButton)

        # Infos
        self.grpInfos = QtWidgets.QGroupBox('Credits')
        self.layVMainWindowMain.addWidget(self.grpInfos)

        self.infosLayout = QtWidgets.QVBoxLayout()
        self.grpInfos.setLayout(self.infosLayout)

        # Infos widgets
        self.infos = QtWidgets.QLabel(self.INFOS)
        self.infosLayout.addWidget(self.infos)
        self.infos.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)

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

    def stingraySwitch(self):

        if self.rendererRadio6.isChecked():
            self.materialsRadio1.setEnabled(False)
            self.materialsRadio2.setEnabled(False)

            self.materialsRadio3.setChecked(True)
        else:
            self.materialsRadio1.setEnabled(True)
            self.materialsRadio2.setEnabled(True)


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

    def addArnoldSubdivisionsCheckbox(self):
        """
        Enable or disable subdivisions in the interface
        :return: None
        """

        # If subdivisions is checked
        if self.checkbox5.isChecked():
            self.subdivType.setEnabled(True)
            self.subdivIter.setEnabled(True)

        # If subdivisions is not checked
        else:
            self.subdivType.setEnabled(False)
            self.subdivIter.setEnabled(False)

    def addVraySubdivisionsCheckbox(self):
        """
        Enable or disable subdivisions in the interface
        :return: None
        """

        # If subdivisions is checked
        if self.checkbox6.isChecked():
            self.subdivIterVray.setEnabled(True)
            self.maxSubdivIterVray.setEnabled(True)

        # If subdivisions is not checked
        else:
            self.subdivIterVray.setEnabled(False)
            self.maxSubdivIterVray.setEnabled(False)

    def addRendermanSubdivisionsCheckbox(self):
        """
        Enable or disable subdivisions in the interface
        :return: None
        """

        # If subdivisions is checked
        if self.checkbox7.isChecked():
            self.subdivIterRenderman.setEnabled(True)
            self.subdivInterRenderman.setEnabled(True)

        # If subdivisions is not checked
        else:
            self.subdivIterRenderman.setEnabled(False)
            self.subdivInterRenderman.setEnabled(False)

    def addRedshiftSubdivisionsCheckbox(self):
        """

        :return:
        """
        # If subdivisions is checked
        if self.checkbox8.isChecked():
            self.subdivIterRedshift.setEnabled(True)
            self.subdivMin.setEnabled(True)
            self.subdivMax.setEnabled(True)

        # If subdivisions is not checked
        else:
            self.subdivIterRedshift.setEnabled(False)
            self.subdivMin.setEnabled(False)
            self.subdivMax.setEnabled(False)
