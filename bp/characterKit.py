import pymel.core as pm
import pymel.core.datatypes as dt
import re,os,shutil,glob

import logging

import shiboken
import PySide.QtGui as QtGui
import PySide.QtCore as QtCore

import maya.OpenMayaUI


def get_maya_window():
    maya_window_util = maya.OpenMayaUI.MQtUtil.mainWindow()
    maya_window = shiboken.wrapInstance( long( maya_window_util ), QtGui.QWidget )
    return maya_window

characterKitWin = 'characterKitWindow'

class CharacterKitUI(QtGui.QMainWindow):
    def __init__(self,parent=get_maya_window()):
        if pm.window( characterKitWin, exists = True, q = True ):
            pm.deleteUI( characterKitWin)
            
        super(CharacterKitUI,self).__init__(parent)
        self.setObjectName(characterKitWin)
        self.setWindowTitle('Character Kit 2.1')
        
        centralWidget = QtGui.QWidget()
        mainLayout = QtGui.QVBoxLayout()
        
        leftSideListsLSplitter = QtGui.QSplitter(QtCore.Qt.Vertical)
        rightSideListsLSplitter = QtGui.QSplitter(QtCore.Qt.Horizontal)
        
        #left side lists
        #characters list
        self.charactersList = QtGui.QListView()
        #skins list
        self.skinsList = QtGui.QListView()
        #body parts list
        self.bodyPartsList = QtGui.QListView()
        
        leftSideListsLSplitter.addWidget(self.charactersList)
        leftSideListsLSplitter.addWidget(self.skinsList)
        leftSideListsLSplitter.addWidget(self.bodyPartsList)

        mainLayout.addWidget(leftSideListsLSplitter)
        
        
        centralWidget.setLayout(mainLayout)
        self.setCentralWidget(centralWidget)
        
        #menu bar
        self.addMenu()

        self.show()
        self.resize(860,600)

    def addMenu(self):
        self.menuBar = self.menuBar()
        self.fileMenu = self.menuBar.addMenu('File')
        self.fileMenu.addAction('Load skeleton')
        self.fileMenu.addAction('Save skeleton')
        self.toolsMenu = self.menuBar.addMenu('Tools')
        self.toolsMenu.addAction('Create Picking Geometry')
        
