import pymel.core as pm
import pymel.core.datatypes as dt
import re,os,shutil,glob

import logging

import sip,shiboken
import PySide.QtGui as QtGui
import PySide.QtCore as QtCore

import maya.OpenMayaUI
import bdCreateCgfxShader as ccs
reload(ccs)

def get_maya_window():
    maya_window_util = maya.OpenMayaUI.MQtUtil.mainWindow()
    maya_window = shiboken.wrapInstance( long( maya_window_util ), QtGui.QWidget )
    return maya_window

bdCgfxToolWin = 'cgfxShaderUI'

class CgfxToolUI(QtGui.QMainWindow):

    def __init__(self,parent=get_maya_window()):
        super(CgfxToolUI,self).__init__(parent)
        self.setObjectName(bdCgfxToolWin)
        self.setWindowTitle('Create Cgfx shaders')

        centralWidget = QtGui.QWidget()
        mainLayout = QtGui.QVBoxLayout()
        self.widgetPairs = {}
        # settings
        settingsGrp = QtGui.QGroupBox('Presets')
        presetsGrpLayout = QtGui.QVBoxLayout()
        settingsGrp.setLayout(presetsGrpLayout)

        presetsFolderLayout = QtGui.QHBoxLayout()
        presetsFolderLabel = QtGui.QLabel('Presets Folder')
        self.presetsFolderEdit = QtGui.QLineEdit()
        self.presetsBtn = QtGui.QPushButton('Browse')
        self.openFolderBtn = QtGui.QPushButton('View in Explorer')
        presetsFolderLayout.addWidget(presetsFolderLabel)
        presetsFolderLayout.addWidget(self.presetsFolderEdit )
        presetsFolderLayout.addWidget(self.presetsBtn)
        presetsFolderLayout.addWidget(self.openFolderBtn)
        
        assetsFolderLayout = QtGui.QHBoxLayout()
        assetsFolderLabel = QtGui.QLabel('Assets Folder')
        self.assetsFolderEdit = QtGui.QLineEdit()
        self.assetsBtn = QtGui.QPushButton('Browse')
        self.openAssetsFolderBtn = QtGui.QPushButton('View in Explorer')
        assetsFolderLayout.addWidget(assetsFolderLabel)
        assetsFolderLayout.addWidget(self.assetsFolderEdit )
        assetsFolderLayout.addWidget(self.assetsBtn)
        assetsFolderLayout.addWidget(self.openAssetsFolderBtn)        
        
        line1 = QtGui.QFrame()
        line1.setFrameShape(QtGui.QFrame.HLine)
        line2 = QtGui.QFrame()
        line2.setFrameShape(QtGui.QFrame.HLine)        
        
        self.shadersLayout = QtGui.QVBoxLayout()
        self.buildShaderWidgets()

        
        btnLayout = QtGui.QVBoxLayout()
        self.createCgfxBtn = QtGui.QPushButton('Create CGFX shaders')
        self.copyTexToAssetsBtn = QtGui.QPushButton('Copy textures to assets')
        btnLayout.addWidget(self.createCgfxBtn)
        btnLayout.addWidget(self.copyTexToAssetsBtn)


        presetsGrpLayout.addLayout(presetsFolderLayout)
        presetsGrpLayout.addLayout(assetsFolderLayout)
        presetsGrpLayout.addWidget(line1)
        presetsGrpLayout.addLayout(self.shadersLayout)
        presetsGrpLayout.addWidget(line2)
        presetsGrpLayout.addLayout(btnLayout)

        spacer = QtGui.QSpacerItem(1, 1, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)


        mainLayout.addWidget(settingsGrp)
        mainLayout.addItem(spacer)

        centralWidget.setLayout(mainLayout)
        self.setCentralWidget(centralWidget)		

        self.presetsBtn.clicked.connect(self.setPresetsFolder)
        self.assetsBtn.clicked.connect(self.setAssetsFolder)
        self.createCgfxBtn.clicked.connect(self.createCgfxShaders)
        self.copyTexToAssetsBtn.clicked.connect(self.copyTexToAssets)
        

        self.show()

    def setPresetsFolder(self):
        defaultFolder = 'p:/happywow/working_project/renderData'
        presetsFolder = ''

        if not os.path.isdir(defaultFolder):
            defaultFolder = 'p:'
        print defaultFolder

        try:
            presetsFolder = pm.fileDialog2(dir=defaultFolder,ds=2,fm=3,okc='Select Folder')[0]
        except:
            pm.warning('No folder was selected')

        if presetsFolder:
            self.presetsFolderEdit.setText(presetsFolder)
            self.buildShaderWidgets()
            
    def setAssetsFolder(self):
        workspace = pm.workspace.path
        assetsFolder = workspace.replace('working_project','assets')

        #build the texture path
        charactersFolder = os.path.abspath(os.path.join(assetsFolder,'textures/characters'))
        
        if  os.path.isdir(assetsFolder):
            try:
                assetsFolder = pm.fileDialog2(dir=assetsFolder,ds=2,fm=3,okc='Select Folder')[0]
            except:
                pm.warning('No folder was selected') 
            
            if assetsFolder:
                self.assetsFolderEdit.setText(assetsFolder)
          
        
    def buildShaderWidgets(self):
        shaders = self.getShaders()
        print shaders
        for sh in shaders:
            row = self.buildShaderRow(sh[0],sh[1])
            self.shadersLayout.addLayout(row)
            
    
    def buildShaderRow(self,shaderType,shaderVersions):
        rowLayout = QtGui.QHBoxLayout()
        shaderTypeEdit = QtGui.QLineEdit(shaderType)
        shaderTypeEdit.setReadOnly(True)
        shaderVersionCombo = QtGui.QComboBox()
        items = []
        for i in range(1,int(shaderVersions)+1) :
            if i < 10:
                items.append('0' + str(i))
            else:
                items.append(str(i))
        shaderVersionCombo.addItems(items)
        rowLayout.addWidget(shaderTypeEdit)
        rowLayout.addWidget(shaderVersionCombo)
        
        self.widgetPairs[shaderTypeEdit] = shaderVersionCombo
        
        return rowLayout
        
    def getShaders(self):
        shaderFiles = []
        typeShader = []
        shaderVersions = []
        shadersPath = self.presetsFolderEdit.text()
        fullPathFiles = glob.glob(shadersPath + '/shader*_[0-9][0-9].m[ab]')
        for f in fullPathFiles:
            path,shaderFile = os.path.split(f)
            shaderFiles.append(shaderFile)
            part = shaderFile.split('_')[1]
            typeShader.append(part)
        
        tempTypeShader = list(set(typeShader))

        for p in tempTypeShader:
            count = typeShader.count(p)
            shaderVersions.append([p,count])
        
        return shaderVersions
        
    def createCgfxShaders(self):
        shaders = {}
        for k,v in self.widgetPairs.iteritems():
            shaders[str(k.text())] = str(v.currentText())
        
        ccs.createCgfxShader(shaders)


    def copyTexToAssets(self):
        assetFolder = self.assetsFolderEdit.text().split('/')[-1]
        ccs.copyTexturesToAssets(assetFolder)
        
def main():
    if pm.window( bdCgfxToolWin, exists = True, q = True ):
        pm.deleteUI( bdCgfxToolWin)

    CgfxToolUI()