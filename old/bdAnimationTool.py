import pymel.core as pm
import pymel.core.datatypes as dt
import re,os,shutil,glob

import logging

import sip,shiboken
import PySide.QtGui as QtGui
import PySide.QtCore as QtCore

import pyside_util
reload(pyside_util)

import maya.OpenMaya as om

# #####################
TOOLS_PATH = os.path.dirname( __file__ )
WINDOW_TITLE = 'Animation Tool'
WINDOW_VERTION = 1.0
WINDOW_NAME = 'bdAnimationToolWin'
# ###################

UI_FILE_PATH = os.path.join( TOOLS_PATH, 'UI/bdAnimationToolUI.ui' )
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

class AnimationToolUI(BASE_CLASS, UI_OBJECT):
	def __init__( self, parent = pyside_util.get_maya_window(), *args ):

		super( AnimationToolUI, self ).__init__( parent )
		self.wipFolderPath = ''
		self.playblastCam = None
		self.setupUi( self )
		self.setWindowTitle( '{0} {1}'.format( WINDOW_TITLE, str( WINDOW_VERTION ) ) )
		
		self.wipHheader = self.wipAnimTable.horizontalHeader()
		self.wipHheader.setStretchLastSection(True)

		self.previewHheader = self.previewAnimTable.horizontalHeader()
		self.previewHheader.setStretchLastSection(True)

		self.wipAnimTable.setAlternatingRowColors(1)
		self.previewAnimTable.setAlternatingRowColors(1)
		
		
		self.getWipFolder()
		self.wipAnimBtn.clicked.connect(self.setWipFolder)
		self.openFileBtn.clicked.connect(self.openSelectedFile)
		self.openFolderBtn.clicked.connect(self.openFolder)
		
		self.saveFileBtn.clicked.connect(self.saveNewVersion)
		self.copyToPreviewBtn.clicked.connect(self.copyAnim)
		self.playblastBtn.clicked.connect(self.playblastCurrent)
		self.copyPlayblastBtn.clicked.connect(self.copyPlayblast)
		self.playblastCamBtn.clicked.connect(self.setCamera)
		self.newAnimBtn.clicked.connect(self.createAnimFile)
		self.wipAnimTable.cellPressed.connect(self.clearPreviewSelection)
		self.wipAnimTable.doubleClicked.connect(self.openSelectedFile)
		
		
		#self.wipAnimTable.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
		#self.wipAnimTable.customContextMenuRequested.connect(self.previewTableMenu)
		
		self.previewAnimTable.cellPressed.connect(self.clearWipSelection)
		self.previewAnimTable.doubleClicked.connect(self.openSelectedFile)
		
		self.lastVersionCheckBox.stateChanged.connect(self.bdGetLastVersion)
		self.show()
		self.resize(860,600)
		self.openSceneCallback  = None
		'''
		try:
			self.openSceneCallback = om.MSceneMessage.addCallback(om.MSceneMessage.kAfterOpen,self.afterOpen)
			print 'Callback created'
		except:
			pm.warning('Callback not created')
		'''
		
	def setCamera(self):
		selection = pm.ls(sl=1)
		if selection:
			shape = selection[0].getShape()

			if shape:
				node = pm.ls(shape)[0]
				print node
				if node.type() == 'camera':
					self.playblastCamEdit.setText(node.name())
	
	def createAnimFile(self):
		character = self.charNameEdit.text()
		animType = self.animTypeCombo.currentText()

		if character:
			if 'name' not in character:
				animNumber = self.getLastAnim(animType)
				fullName = character + '_' + animType + animNumber + '_01.ma'
				fullName = self.wipFolderPath + '/' + fullName
				print fullName
				if not os.path.isfile(fullName):
					pm.saveAs(fullName)
					self.bdPopulateFiles()
				else:
					pm.warning('File exist, will not overwrite')
					
			else:
				pm.warning('Enter a char name')
	
	def getLastAnim(self,anim):
		allAnim = glob.glob(self.wipFolderPath + '/*' + anim +'*.m[ab]')
		fileNames = [os.path.split(f)[1] for f in allAnim]
		animNum = []
		for f in fileNames:
			num = f.split('_')[-2]
			animNum.append(num)
		
		print fileNames
		print set(animNum)
		newVer = len(set(animNum)) + 1

		if newVer < 10:
			return '_0' + str(newVer)
		else:
			return  '_' + str(newVer)

		
	def afterOpen(self, *args):
		self.bdPopulateFiles()
		
	def previewTableMenu(self, pos):
		menu = QtGui.QMenu()
		self.playblastAll = menu.addAction('Open Folder')
		self.playblastAll .triggered.connect(self.openFolder)

		#self.playblastNone = menu.addAction('None')
		#self.playblastNone .triggered.connect(lambda: self.bdPlayblastStatus('none'))

		#self.invert = menu.addAction('Invert')
		#self.invert.triggered.connect(lambda: self.bdPlayblastStatus('invert'))

		menu.exec_(QtGui.QCursor.pos())

	def openFolder(self):
		folder=  self.wipFolderEdit.text()
		if folder:
			folder = folder.replace('/','\\')
			os.system('explorer -e,' + folder)

	def getWipFolder(self):
		currentSceneName = pm.sceneName()
		if 'wip' in currentSceneName:
			path,sceneName = os.path.split(currentSceneName)
			self.wipFolderEdit.setText(path)
			self.wipFolderPath = path
			self.bdPopulateFiles()
		else:
			projectPath = pm.workspace.name
			charactersFolder = os.path.join(projectPath,'scenes','characters')
			self.wipFolderEdit.setText(charactersFolder)

	def setWipFolder(self):
		currentScene = pm.sceneName()
		if currentScene:
			projectPath,fileName = os.path.split(currentScene)
			wipFolder = ''
			try:
				wipFolder = pm.fileDialog2(dir=projectPath,ds=2,fm=3,okc='Select Folder')[0]
			except:
				pm.warning('No folder was selected')

			if wipFolder:
				self.wipFolderEdit.setText(wipFolder)
				self.wipFolderPath = wipFolder
				self.bdPopulateFiles()
		else:
			projectPath = pm.workspace.name
			charactersFolder = os.path.abspath(os.path.join(projectPath,'scenes','characters'))
			path = ''
			try:
				path = pm.fileDialog2(dir=charactersFolder,ds=2,fm=3,okc='Select Folder')[0]
			except:
				pm.warning('No folder was selected')
			if path:
				self.wipFolderEdit.setText(path)
				self.wipFolderPath = path
				self.bdPopulateFiles()


	def bdPopulateFiles(self):
		#Wip files
		#wipFileList = [f for f in sorted(os.listdir(self.wipFolderPath)) if (f.endswith('.ma') or f.endswith('.mb'))]
		
		#get files based on pattern , will fetch only files ending in version token ( double digit number)
		path, currentFile = os.path.split(pm.sceneName())
		
		self.wipAnimTable.clearContents()
		self.wipAnimTable.setSortingEnabled(0)
		
		self.previewAnimTable.clearContents()
		self.previewAnimTable.setSortingEnabled(0)

		wipFileList = []
		
		tempList = glob.glob(self.wipFolderPath + '/*_*[0-9][0-9].m[ab]')
		for ele in tempList:
			path,filename = os.path.split(ele)
			wipFileList.append(filename)
		
		self.wipAnimTable.setColumnCount(3)
		self.wipAnimTable.setRowCount(len(wipFileList ))

		for i in range(len(wipFileList )):
			item = QtGui.QTableWidgetItem(wipFileList [i])
			item.setFlags(~QtCore.Qt.ItemIsEditable)
			if wipFileList [i] == currentFile:
				item.setBackground(QtGui.QColor(0,100,0))
			self.wipAnimTable.setItem(i, 0, item)

			version = self.getAnimVersion(wipFileList [i])
			item = QtGui.QTableWidgetItem(version)
			item.setFlags(~QtCore.Qt.ItemIsEditable)
			item.setTextAlignment(QtCore.Qt.AlignCenter)
			self.wipAnimTable.setItem(i, 1, item)
			
			hasPlayblast = 'No'
			if self.hasPlayblast(wipFileList[i]):
				hasPlayblast = 'Yes'
			item = QtGui.QTableWidgetItem(hasPlayblast)
			item.setFlags(~QtCore.Qt.ItemIsEditable)
			item.setTextAlignment(QtCore.Qt.AlignCenter)
			if hasPlayblast =='Yes':
				item.setBackground(QtGui.QColor(0,180,50))
			else:
				item.setBackground(QtGui.QColor(200,150,0))
			self.wipAnimTable.setItem(i, 2, item)
				
		self.wipAnimTable.resizeColumnsToContents()
		self.wipAnimTable.setSortingEnabled(1)
		self.wipAnimTable.sortItems(0,QtCore.Qt.AscendingOrder)
		
		self.wipHheader.setStretchLastSection(True)
		self.previewHheader.setStretchLastSection(True)


		#Populate Preview files
		#previewFileList = [f for f in sorted(os.listdir(self.wipFolderPath.replace('01_wip','03_preview'))) if (f.endswith('.ma') or f.endswith('.mb'))]
		previewFileList = []
		
		tempList = glob.glob(self.wipFolderPath.replace('01_wip','03_preview') + '/*[0-9].m[ab]')
		for ele in tempList:
			path,filename = os.path.split(ele)
			previewFileList.append(filename)

		self.previewAnimTable.setColumnCount(3)
		self.previewAnimTable.setRowCount(len(previewFileList  ))

		for i in range(len(previewFileList)):
			item = QtGui.QTableWidgetItem(previewFileList[i])
			item.setFlags(~QtCore.Qt.ItemIsEditable)
			self.previewAnimTable.setItem(i, 0, item)
			
			version = self.getAnimVersion(previewFileList [i])
			item = QtGui.QTableWidgetItem(version)
			item.setFlags(~QtCore.Qt.ItemIsEditable)
			item.setTextAlignment(QtCore.Qt.AlignCenter)
			self.previewAnimTable.setItem(i, 1, item)
			
			hasPlayblast = 'No'
			if self.hasPlayblast(previewFileList[i],'preview'):
				hasPlayblast = 'Yes'
			item = QtGui.QTableWidgetItem(hasPlayblast)
			item.setFlags(~QtCore.Qt.ItemIsEditable)
			item.setTextAlignment(QtCore.Qt.AlignCenter)
			if hasPlayblast =='Yes':
				item.setBackground(QtGui.QColor(0,180,50))
			else:
				item.setBackground(QtGui.QColor(200,150,0))
			self.previewAnimTable.setItem(i, 2, item)

		self.previewAnimTable.resizeColumnsToContents()
		self.previewAnimTable.setSortingEnabled(1)
		self.previewAnimTable.sortItems(0,QtCore.Qt.AscendingOrder)
		
	def getAnimVersion(self,animFile):
		version = animFile.split('.')[0].split('_')[-1]
		return version
	
	def openSelectedFile(self):
		try:
			item = self.previewAnimTable.selectedItems()[0]
			if item.column() == 0:
				self.openMayaFile(item.text(),'preview')
			elif item.column() == 2:
				if item.text() == 'Yes':
					filename = self.previewAnimTable.item(item.row(),0).text()
					self.openMovFile(filename,'preview')
		except:
			pass
		
		try:
			item = self.wipAnimTable.selectedItems()[0]
			if item.column() ==0:
				self.openMayaFile(item.text(),'wip')
			elif item.column() == 2:
				if item.text() == 'Yes':
					filename = self.wipAnimTable.item(item.row(),0).text()
					self.openMovFile(filename)
		except:
			pass
		currentFile = pm.sceneName()
		pm.optionVar(stringValueAppend=('RecentFilesList', currentFile))
		pm.optionVar(stringValueAppend=('RecentFilesTypeList', 'mayaAscii'))
		
		self.bdPopulateFiles()

	
	def openMayaFile(self,filename,folder):
		f=''
		wipPath = self.wipFolderEdit.text()
		print filename, folder
		if folder == 'wip':
			f = os.path.abspath(os.path.join(wipPath,filename))
		elif folder == 'preview':
			f = os.path.abspath(os.path.join(wipPath.replace('01_wip','03_preview'),filename))
		
		if os.path.isfile(f):
			saveDlg = saveChangesDlg()
			#saveDlg.setFixedSize(800,  300)
			result = saveDlg.exec_()
			if result == 1:
				pm.saveFile()
				pm.openFile(f)
			elif result == 2:
				pm.openFile(f,f=1)

	def openMovFile(self,filename,folder='wip'):
		f=''
		wipPath = self.wipFolderEdit.text()
		print filename, folder
		if folder == 'wip':
			f = self.hasPlayblast(filename,folder)
		elif folder == 'preview':
			f = self.hasPlayblast(filename,folder)
		
		if os.path.isfile(f):
			os.system('start ' + f)
			#copy path to clipboard
			command = 'echo ' + f + '| clip'
			os.system(command)
			


	def copyAnim(self):
		animFiles = []
		f=''
		wipPath = self.wipFolderEdit.text()

		selectedItems = self.wipAnimTable.selectedItems()

		if len(selectedItems):
			for item in selectedItems:
				if item.column() ==0:
					anim = item.text()
					print anim
					src = os.path.abspath(os.path.join(wipPath,anim))

					destPath = wipPath.replace('01_wip','03_preview')
					dest = os.path.abspath(os.path.join(destPath,anim))
					
					if os.path.isfile(src):
						if os.path.isfile(dest):
							pm.warning('Preview file exists already, will not overwrite ( save new version ? )')
						else:
							try:
								shutil.copyfile(src, dest)
							except:
								pm.error('Could not copy anim file to preview')
			
			self.bdPopulateFiles()

	def saveNewVersion(self):
		path,filename = os.path.split(pm.sceneName())
		name,extension = os.path.splitext(filename)
		version = name.split('_')[-1]
		newVersion = ''
		if int(version) < 9:
			newVersion = '0' + str(int(version) + 1)
		else:
			newVersion = str(int(version) + 1)
		
		print newVersion
		newName = filename.replace('_' + version + extension,'_' + newVersion + extension)
		
		
		pm.saveAs(os.path.join(path,newName),f=1)
		
		self.wipAnimTable.clearContents()
		self.bdPopulateFiles()

	def clearPreviewSelection(self,row,column):
		self.previewAnimTable.clearSelection()

	def clearWipSelection(self,row,column):
		self.wipAnimTable.clearSelection()
	
	def playblastCurrent(self):
		playblastMelCmd = 'playblast  -format qt -sequenceTime 0 -clearCache 0 -viewer 1 -showOrnaments 1 -fp 4 -percent 100 -compression "H.264" -quality 100';
		tempFile = pm.mel.eval(playblastMelCmd)
		
		if os.path.isfile(tempFile):
			path,fileName = os.path.split(pm.sceneName())
			movFile = fileName.split('.')[0] + '.mov'
			try:
				shutil.copy2(tempFile, os.path.join(path,movFile))
			except:
				pm.error("Couln't copy the temp blast")
			self.updatePlayblastStatus(fileName)
	
	def updatePlayblastStatus(self,filename):
		searchItems = self.wipAnimTable.findItems(filename,QtCore.Qt.MatchExactly)
		
		if len(searchItems):
			
			self.wipAnimTable.item(searchItems[0].row(), 2).setBackground(QtGui.QColor(0,180,50))
			self.wipAnimTable.item(searchItems[0].row(), 2).setText('Yes')


	def hasPlayblast(self,filename,folder='wip'):
		wipPath = wipPath = self.wipFolderEdit.text()
		blastPath = ''
		animFile =filename
		animFileName,extension = os.path.splitext(animFile)
		blastName = animFileName + '.mov'
		
		if folder == 'wip':
			blastPath=  os.path.abspath(os.path.join(wipPath,blastName))
		elif folder == 'preview':
			previewPath = wipPath.replace('01_wip','03_preview')
			blastPath=  os.path.abspath(os.path.join(previewPath,blastName))
			
		if os.path.isfile(blastPath):
			return blastPath
		
		return 0


	def copyPlayblast(self):
		blastFiles = []

		f=''
		wipPath = self.wipFolderEdit.text()

		selectedItems = self.wipAnimTable.selectedItems()
		
		if len(selectedItems):
			for item in selectedItems:
				if item.text() == 'Yes':
					animFile = self.wipAnimTable.item(item.row(),0).text()
					blastFile = self.hasPlayblast(animFile)
					wipBlastPath,blastFileName = os.path.split(blastFile)
					destPath = wipPath.replace('01_wip','03_preview')
					dest = os.path.abspath(os.path.join(destPath,blastFileName))
					
					
					if os.path.isfile(blastFile):
						if os.path.isfile(dest):
							pm.warning('Blast exists already, will not overwrite ( save new version ? )')
						else:
							try:
								print("copying")
								shutil.copyfile(blastFile, dest)
							except:
								pm.error('Could not copy blast file to preview')
	
	def bdGetLastVersion(self,state):
		fileList = []
		baseNameList = []
		lastVersionList = []
		if state == 2:
			rows  = self.wipAnimTable.rowCount()
			for i in range(rows):
				fileList.append(self.wipAnimTable.item(i,0).text().split('.')[0])
			for f in fileList:
				baseName = ''
				temp = f.split('_')
				if len(temp) > 5:
					for i in range(len(temp) -1 ):
						baseName += (temp[i] + '_')
					baseNameList.append(baseName[:-1])
				else:
					pm.warning('Didnt find versions for file %s'%f)
					continue

		print baseNameList
		tempSet = sorted(list(set(baseNameList)))
		for name in tempSet:
			if baseNameList.count(name) < 10:
				lastVersionList.append(name + '_0' +  str(baseNameList.count(name)))
			else:
				lastVersionList.append(name + '_' +  str(baseNameList.count(name)))

		print lastVersionList


	def closeEvent(self, event):
		# do stuff
		print self.openSceneCallback
		if self.openSceneCallback:
			print 'Removing callback'
			om.MSceneMessage.removeCallback(self.openSceneCallback)
			self.openSceneCallback = None
		event.accept() 

class saveChangesDlg(QtGui.QDialog):
	def __init__(self,parent=None):
		super(saveChangesDlg,self).__init__(parent)
		mainLayout = QtGui.QVBoxLayout()
		
		self.save = 0
		
		labelLayout = QtGui.QHBoxLayout()
		label = QtGui.QLabel('Save changes to current file ?')
		labelLayout.addWidget(label)
		
		btnLayout = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Save | QtGui.QDialogButtonBox.Discard ,QtCore.Qt.Horizontal, self)
		btnLayout.accepted.connect(self.accept)
		btnLayout.button(QtGui.QDialogButtonBox.Discard).clicked.connect(self.discarded)
		mainLayout.addLayout(labelLayout)
		mainLayout.addWidget(btnLayout)
		
		self.setLayout(mainLayout)
		self.setWindowTitle('Save changes')

	def discarded(self):
		self.done(2)
		
		


def bdMain():
	UI_FILE_PATH = os.path.join( TOOLS_PATH, 'UI/bdAnimationToolUI.ui' )
	UI_OBJECT, BASE_CLASS = pyside_util.get_pyside_class( UI_FILE_PATH )

	if pm.window( WINDOW_NAME, exists = True, q = True ):
		pm.deleteUI( WINDOW_NAME )

	AnimationToolUI()
