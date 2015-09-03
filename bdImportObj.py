import pymel.core as pm
import pymel.core.datatypes as dt
import re,os
import maya.OpenMaya as OM

import logging
import maya.OpenMayaUI as mui
import maya.OpenMaya as om
import sip,os, shiboken
import PySide.QtGui as QtGui
import PySide.QtCore as QtCore

import pyside_util
reload(pyside_util)



# #####################
TOOLS_PATH = os.path.dirname( __file__ )
WINDOW_TITLE = 'Import Objs Tool'
WINDOW_VERTION = 1.0
WINDOW_NAME = 'bdImportObjWin'
# ###################

UI_FILE_PATH = os.path.join( TOOLS_PATH, 'UI/bdImportObjUI.ui' )
UI_OBJECT, BASE_CLASS = pyside_util.get_pyside_class( UI_FILE_PATH )


pysideLoggers = ['pysideuic.properties','pysideuic.uiparser']
for log in pysideLoggers:
	logger = logging.getLogger(log)
	logger.setLevel(logging.ERROR)

def widgetPath(windowName, widgetNames):
	"""
	@param windowName: Window instance name to search
	@param widgetNames: list of names to search for
	taken from http://www.chris-g.net/2011/06/24/maya-qt-interfaces-in-a-class/
	"""

	returnDict = {}
	mayaWidgetList = pm.lsUI(dumpWidgets=True)

	for widget in widgetNames:
		for mayaWidget in mayaWidgetList:
			if windowName in mayaWidget:
				if mayaWidget.endswith(widget):
					returnDict[widget] = mayaWidget

	return returnDict


def removeNamespace():
	sceneNS = pm.namespaceInfo(lon=True,r=True)
	importNS = []
	mayaNS = set([u'UI', u'shared'])
	for ns in sceneNS:
		if ns not in mayaNS:
			importNS.append(ns)
	importNS.reverse()

	for ns in importNS:
		pm.namespace( rm = ns,mergeNamespaceWithRoot=True)

class ImportObjUI(BASE_CLASS, UI_OBJECT):
	def __init__( self, parent = pyside_util.get_maya_window(), *args ):

		super( ImportObjUI, self ).__init__( parent )
		self.path = ''
		self.setupUi( self )
		self.setWindowTitle( '{0} {1}'.format( WINDOW_TITLE, str( WINDOW_VERTION ) ) )

		self.objPathBtn.clicked.connect(self.bdGetObjPath)

		self.importBtn.clicked.connect(self.bdImportObjs)
		self.exportBtn.clicked.connect(self.bdExportObjs)


		self.show()




	def bdGetObjPath(self):
		projectPath = pm.workspace.name

		self.path = pm.fileDialog2(dir=projectPath,ds=2,fm=3,okc='Select Folder')[0]
		if self.path:
			self.objPath.setText(self.path)
			self.bdPopulateFiles()


	def bdPopulateFiles(self):
		fileList = [f for f in sorted(os.listdir(self.path)) if f.endswith('.obj') ]

		self.objFilesTableWidget.setColumnCount(1)
		self.objFilesTableWidget.setRowCount(len(fileList))

		for i in range(len(fileList)):
			item = QtGui.QTableWidgetItem(fileList[i])
			item.setFlags(~QtCore.Qt.ItemIsEditable)
			self.objFilesTableWidget.setItem(i, 0, item)	                


	def bdImportObjs(self):
		selected = self.objFilesTableWidget.selectedItems()
		print len(selected)
		if len(selected) > 0 :
			for item in selected:
				objFile = item.text()
				self.bdImportFile(objFile)
		else:
			for i in range(self.objFilesTableWidget.rowCount()):
				objFile = self.objFilesTableWidget.item(i,0).text()
				self.bdImportFile(objFile)



	def bdImportFile(self,objFile):
		print 'Importing'
		objPath = os.path.join(self.path,objFile )
		pm.importFile(objPath ,namespace= 'tempObj')
		mesh = pm.ls('tempObj:*',type='mesh')[0].getParent()
		print mesh
		mesh.rename(objFile.split('.')[0])
		removeNamespace()

	def bdExportObjs(self):
		print 'Exporting'
		selection = pm.ls(sl=1)
		for mesh in selection:
			if mesh.getShapes()[0].type() == 'mesh':
				print mesh.name()
				pm.select(mesh)
				command = 'file -force -options "groups=0;ptgroups=1;materials=0;smoothing=1;normals=1" -typ "OBJexport" -pr -es "' + os.path.join(self.path, mesh.name()+'.obj') +  '";'
				pm.mel.eval(command)



def bdMain():
	UI_FILE_PATH = os.path.join( TOOLS_PATH, 'UI/bdImportObjUI.ui' )
	UI_OBJECT, BASE_CLASS = pyside_util.get_pyside_class( UI_FILE_PATH )

	if pm.window( WINDOW_NAME, exists = True, q = True ):
		pm.deleteUI( WINDOW_NAME )

	ImportObjUI()

