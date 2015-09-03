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
WINDOW_TITLE = 'MultiBlast Tool'
WINDOW_VERTION = 1.0
WINDOW_NAME = 'bdMultiBlastWin'
# ###################

UI_FILE_PATH = os.path.join( TOOLS_PATH, 'UI/bdMultiBlastUI.ui' )
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


class MultiBlastUI(BASE_CLASS, UI_OBJECT):
	def __init__( self, parent = pyside_util.get_maya_window(), *args ):

		super( MultiBlastUI, self ).__init__( parent )
		self.setupUi( self )
		self.setWindowTitle( '{0} {1}'.format( WINDOW_TITLE, str( WINDOW_VERTION ) ) )
		#self.mayaFilesTableWidget.itemDoubleClicked.connect( self.bdToggleFile )
		self.mayaFilesPathBtn.clicked.connect(lambda: self.bdGetPath('maya'))
		self.blastsPathBtn.clicked.connect(lambda: self.bdGetPath('avi'))
		self.camPathBtn.clicked.connect(lambda: self.bdGetPath('cam'))
		self.rigPathBtn.clicked.connect(lambda: self.bdGetPath('rig'))
		self.playblastBtn.clicked.connect(self.bdPlayblastFolder)
		self.mayaFilesTableWidget.itemDoubleClicked.connect( self.bdToggleStatus )
		self.formatComboBox.currentIndexChanged.connect(self.bdFormatChanged)
		
		self.lastVersion.stateChanged.connect(self.bdGetLastVersion)

		self.mayaFilesTableWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
		self.mayaFilesTableWidget.customContextMenuRequested.connect(self.handleHeaderMenu)

		layout = mui.MQtUtil.fullName(long(shiboken.getCppPointer(self.playblastOptionGrp)[0]))
		formats = pm.playblast(q=1,format=1)
		self.formatComboBox.addItems(formats)
		selectedFormat = self.formatComboBox.currentText()
		cmd = 'playblast -format "' + selectedFormat + '" -q -compression'
		compression = pm.mel.eval(cmd)
		self.encodingComboBox.clear()
		self.encodingComboBox.addItems(compression)
		self.progressBar.hide()
		self.show()

	def handleHeaderMenu(self, pos):
		menu = QtGui.QMenu()
		self.playblastAll = menu.addAction('All')
		self.playblastAll .triggered.connect(lambda: self.bdPlayblastStatus('all'))

		self.playblastNone = menu.addAction('None')
		self.playblastNone .triggered.connect(lambda: self.bdPlayblastStatus('none'))

		self.invert = menu.addAction('Invert')
		self.invert.triggered.connect(lambda: self.bdPlayblastStatus('invert'))

		menu.exec_(QtGui.QCursor.pos())

	def bdToggleStatus(self,tableWidgetItem):
		row = tableWidgetItem.row()
		currentState = self.mayaFilesTableWidget.item(row,0).text()
		if currentState == 'Yes':
			item = QtGui.QTableWidgetItem('No')
		else:
			item = QtGui.QTableWidgetItem('Yes')

		item.setFlags(~QtCore.Qt.ItemIsEditable)
		self.mayaFilesTableWidget.setItem(row, 0, item)

	def bdPlayblastStatus(self,which):
		rowCount = self.mayaFilesTableWidget.rowCount()
		if rowCount > 0: 
			if which == 'all':
				for i in range(rowCount):
					item = QtGui.QTableWidgetItem('Yes')
					item.setFlags(~QtCore.Qt.ItemIsEditable)
					self.mayaFilesTableWidget.setItem(i, 0, item)
			elif which == 'none':
				for i in range(rowCount):
					item = QtGui.QTableWidgetItem('No')
					item.setFlags(~QtCore.Qt.ItemIsEditable)
					self.mayaFilesTableWidget.setItem(i, 0, item)
			elif which == 'invert':
				for i in range(rowCount):
					currentState = self.mayaFilesTableWidget.item(i,0).text()
					if currentState == 'Yes':
						item = QtGui.QTableWidgetItem('No')
					else:
						item = QtGui.QTableWidgetItem('Yes')

					item.setFlags(~QtCore.Qt.ItemIsEditable)
					self.mayaFilesTableWidget.setItem(i, 0, item)

	def bdFormatChanged(self,index):
		cmd = 'playblast -format "' + self.formatComboBox.currentText() + '" -q -compression'
		compression = pm.mel.eval(cmd)
		self.encodingComboBox.clear()
		self.encodingComboBox.addItems(compression)

	def bdGetPath(self,which):
		projectPath = pm.workspace.name

		if which == 'cam' or which == 'rig':
			multipleFilters = "Maya Files (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb);;All Files (*.*)"
			path = pm.fileDialog2(fileFilter=multipleFilters, dir=projectPath,ds=2,fm=1,okc='Select Camera')[0]
		else:
			path = pm.fileDialog2(dir=projectPath,ds=2,fm=3,okc='Select Folder')[0]
		if path:
			if which == 'maya':
				self.animPath.setText(path)
				self.bdPopulateFiles(path)
			elif which == 'avi':
				self.blastPath.setText(path)
			elif which == 'cam':
				self.camPath.setText(path)
			elif which == 'rig':
				self.rigPath.setText(path)                        


	def bdPopulateFiles(self,path):
		fileList = [f for f in sorted(os.listdir(path)) if f.endswith('.ma') or f.endswith('.mb')]

		self.mayaFilesTableWidget.setColumnCount(3)
		self.mayaFilesTableWidget.setRowCount(len(fileList))

		for i in range(len(fileList)):
			item = QtGui.QTableWidgetItem('Yes')
			item.setFlags(~QtCore.Qt.ItemIsEditable)
			self.mayaFilesTableWidget.setItem(i, 0, item)	                

			item = QtGui.QTableWidgetItem(fileList[i])
			item.setFlags(~QtCore.Qt.ItemIsEditable)
			self.mayaFilesTableWidget.setItem(i, 1, item)	                
	
	def bdGetLastVersion(self,state):
		fileList = []
		if state == 2:
			if self.mayaFilesTableWidget.rowCount() > 0:
				for r in range(self.mayaFilesTableWidget.rowCount()):
					fileList.append(self.mayaFilesTableWidget.item(r,1).text())
				lastVersions = []
				numFrames = []
				temp = []
				
				for f in fileList:
					if len(f) > 0:
						nameEnd = 0
						for char in f:
							try:
								firstNumber = int(char)
								break
							except ValueError:
								pass
							nameEnd += 1
						
						temp.append( f[:nameEnd+2])
		

				tempSet = list(set(sorted(temp)))
				print tempSet

				for t in sorted(tempSet):
					print '%s is counted %i'%(t,temp.count(t))
					#lastVersions.append(self.bdGetVersionName(t,temp.count(t),fileList))
					lastVersions.append(t)
				
				self.mayaFilesTableWidget.clearContents()
	
				self.mayaFilesTableWidget.setColumnCount(3)
				print fileList
				print lastVersions 
				self.mayaFilesTableWidget.setRowCount(len(lastVersions))
				for i in range(len(lastVersions)):
					item = QtGui.QTableWidgetItem('Yes')
					item.setFlags(~QtCore.Qt.ItemIsEditable)
					self.mayaFilesTableWidget.setItem(i, 0, item)	                
		
					item = QtGui.QTableWidgetItem(lastVersions[i])
					item.setFlags(~QtCore.Qt.ItemIsEditable)
					self.mayaFilesTableWidget.setItem(i, 1, item)
					
					print temp.count(lastVersions[i])
					item = QtGui.QTableWidgetItem(str(temp.count(lastVersions[i])))
					item.setFlags(~QtCore.Qt.ItemIsEditable)
					self.mayaFilesTableWidget.setItem(i, 2, item)
					
		else:
			self.mayaFilesTableWidget.clearContents()
			path = self.animPath.text()
			self.bdPopulateFiles(path)



	def bdGetVersionName(self,name,version,file): #def bdGetVersionName(self,name,version,fileList):
		print file
		'''
		strVersion = ''
		for f in fileList:
			if version < 10:
				strVersion = 'v0' + str(version)
			elif version > 10:
				strVersion = 'v' + str(version)
			
			if (name in f) and (strVersion in f):
				return f
		'''
		
	def bdPlayblastFolder(self):
		animDir = self.animPath.text()
		if not os.path.isdir(animDir):
			pm.warning('%s folder doesn\'t exist'%animDir )
			return

		movieDir = self.blastPath.text()

		characterRig = self.rigPath.text()
		if not os.path.isfile(characterRig):
			pm.warning('%s file doesn\'t exist'%characterRig )
			return

		cam = self.camPath.text()
		blastFormat = self.formatComboBox.currentText()
		blastCompression = self.encodingComboBox.currentText()

		self.progressBar.show()
		print animDir,movieDir,characterRig,blastFormat,blastCompression,cam
		self.bdPerformPlayblast(animDir,movieDir,characterRig,blastFormat,blastCompression,cam)
		self.progressBar.hide()

	def bdPerformPlayblast(self,folder,outFolder,characterRig, blastFormat, blastCompression, referenceCam):
		animDir = folder

		animFiles = []
		for i in range(self.mayaFilesTableWidget.rowCount()):
			status = self.mayaFilesTableWidget.item(i,0).text()
			if status == 'Yes':
				animFiles.append(self.mayaFilesTableWidget.item(i,1).text())
		#pm.mel.eval('setAllMainWindowComponentsVisible 0;')
		for f in sorted(animFiles):
			pathFile = animDir + '/' + f
			if outFolder == '':
				pathMovie = 'movies/' + f[:-3]
			else:
				pathMovie = outFolder + '/' +f[:-3]

			if os.path.isfile(pathFile):
				print pathFile
			else:
				print 'no file'
				return
			checkFileCallbackId = OM.MSceneMessage.addCheckFileCallback(OM.MSceneMessage.kBeforeReferenceCheck, self.bdReplaceRig)
			pm.newFile(f=1)
			
			pm.openFile(pathFile,f=1)
			#pm.mel.eval('setNamedPanelLayout "Four View"; updateToolbox();')
			'''
			openWin = pm.lsUI(windows=1)
			for win in openWin:
				if 'MayaWindow' not in win.name() and WINDOW_NAME not in win.name() and 'scriptEditorPanel'  not in win.name():
					pm.deleteUI(win)
			'''
			pm.setAttr("defaultResolution.width",1280) 
			pm.setAttr("defaultResolution.height",720) 
			OM.MMessage.removeCallback(checkFileCallbackId)
			self.bdSetCamera(referenceCam)
			print folder,outFolder,characterRig, blastFormat, blastCompression, referenceCam
			try:
				self.mayaFilesTableWidget.item(row,0).setBackground(QtGui.QColor(255,100,150))
				self.mayaFilesTableWidget.item(row,1).setBackground(QtGui.QColor(255,100,150))				
				pm.playblast(format = blastFormat, filename = pathMovie,forceOverwrite=1,sequenceTime=0,clearCache=0,viewer=0,showOrnaments=1,fp=4,percent = 100,compression = blastCompression,quality=100, widthHeight= [1280, 720])
			except:
				print "WTF!!!!!!!!!!!"

			progress = (float(animFiles.index(f) + 1.0) / float(len(animFiles)) ) * 100.0
			self.progressBar.setValue(int(progress))
			row = animFiles.index(f)

		#pm.mel.eval('setAllMainWindowComponentsVisible 1;')

	def bdSetCamera(self,referenceCam):
		pm.mel.eval('setNamedPanelLayout "Single Perspective View"; updateToolbox();')
		sceneReferences = pm.getReferences()
		print sceneReferences
		camera = ''
		for item in sceneReferences :
			if sceneReferences[item].isLoaded():
				if referenceCam.lower() in sceneReferences[item].path.lower():
					print 'cam loaded already'
					camera = pm.ls(item + ':*',type='camera')[0]
					break
		
		print referenceCam
		stageCam = pm.ls(referenceCam + '*',type='camera')[0]
		print stageCam
		
		if stageCam:
			camera = stageCam
		if camera == '':
			if os.path.isfile(referenceCam):
				pm.createReference(referenceCam,namespace="CAM")
				camera = pm.ls('CAM:*',type='camera')[0]
			else:
				print 'No cam file, creating a default one'
				cameraList = pm.camera(n='playblastCam')
				camera = cameraList[1]
				cameraList[0].setTranslation([0,10,60])

		'''
		perspModel = "".join(pm.getPanel(withLabel = 'Persp View'))
		if perspModel == '':
			perspModel = "".join(pm.getPanel(withLabel = 'Side View'))
		print camera, perspModel

		pm.setFocus(perspModel)
		'''

		perspView = pm.getPanel(wf=1)

		pm.modelEditor(perspView,e=1,alo=0,activeView = True)
		pm.modelEditor(perspView,e=1,polymeshes=1,wos=0,grid=0)
		pm.modelEditor(perspView,e=1,displayAppearance='smoothShaded',displayTextures=1)	


		try:
			pm.lookThru(perspView,camera)
		except:
			print 'Failed to look through playblast camera'


	def bdReplaceRig(self,retCode, fileObject, b):
		rigFile = self.rigPath.text()
		rf = fileObject.rawFullName()
		if os.path.basename(rf).find('_rig') > -1:
			pm.warning("\n\n\nMSG: Can't find rig file '%s' it would be resolved with '%s'.\n\n\n" % (rf, rigFile))
			fileObject.setRawFullName(rigFile)
			fileObject.overrideResolvedFullName(rigFile)

			OM.MScriptUtil.setBool(retCode, True) 	

def bdMain():
	UI_FILE_PATH = os.path.join( TOOLS_PATH, 'UI/bdMultiBlastUI.ui' )
	UI_OBJECT, BASE_CLASS = pyside_util.get_pyside_class( UI_FILE_PATH )

	if pm.window( WINDOW_NAME, exists = True, q = True ):
		pm.deleteUI( WINDOW_NAME )

	MultiBlastUI()

bdMain()