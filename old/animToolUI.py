import pymel.core as pm
import pymel.core.datatypes as dt
import re,os,shutil,glob

import logging

import sip,shiboken
import PySide.QtGui as QtGui
import PySide.QtCore as QtCore

import maya.OpenMayaUI


def get_maya_window():
	maya_window_util = maya.OpenMayaUI.MQtUtil.mainWindow()
	maya_window = shiboken.wrapInstance( long( maya_window_util ), QtGui.QWidget )
	return maya_window

bdAnimToolWin = 'bdAnimToolWindow'

class AnimToolUI(QtGui.QMainWindow):

	def __init__(self,parent=get_maya_window()):
		super(AnimToolUI,self).__init__(parent)
		self.setObjectName(bdAnimToolWin)
		self.setWindowTitle('Anim Tool')
		
		self.wipFolderPath = ''
		self.playblastCam = None
		self.filterString = ''
		
		centralWidget = QtGui.QWidget()
		mainLayout = QtGui.QVBoxLayout()
		# settings
		settingsGrp = QtGui.QGroupBox('Settings')
		settingsGrpLayout = QtGui.QVBoxLayout()
		settingsGrp.setLayout(settingsGrpLayout)
		
		animFolderLayout = QtGui.QHBoxLayout()
		animFolderLabel = QtGui.QLabel('Wip Animation Folder')
		self.wipFolderEdit = QtGui.QLineEdit()
		self.wipAnimBtn = QtGui.QPushButton('Browse')
		self.openFolderBtn = QtGui.QPushButton('View in Explorer')
		animFolderLayout.addWidget(animFolderLabel)
		animFolderLayout.addWidget(self.wipFolderEdit )
		animFolderLayout.addWidget(self.wipAnimBtn)
		animFolderLayout.addWidget(self.openFolderBtn)
		
		'''
		cameraLayout = QtGui.QHBoxLayout()
		playblastCamLabel = QtGui.QLabel('Playblast camera')
		self.playblastCamEdit = QtGui.QLineEdit()
		self.playblastCamBtn = QtGui.QPushButton('Pick Camera')
		cameraLayout.addWidget(playblastCamLabel)
		cameraLayout.addWidget(self.playblastCamEdit)
		cameraLayout.addWidget(self.playblastCamBtn)
		'''
		
		formatLayout = QtGui.QHBoxLayout()
		formatLabel = QtGui.QLabel('Playblast format')
		self.animFormatComboBox = QtGui.QComboBox()
		items = ['mov','avi','uncompressed']
		self.animFormatComboBox.addItems(items)
		spacer = QtGui.QSpacerItem(300, 1, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
		formatLayout.addWidget(formatLabel)
		formatLayout.addWidget(self.animFormatComboBox)
		formatLayout.addItem(spacer)
		
		settingsGrpLayout.addLayout(animFolderLayout)
		#settingsGrpLayout.addLayout(cameraLayout)
		settingsGrpLayout.addLayout(formatLayout)
		
		#end settings
		
		#folders
		foldersGrp = QtGui.QGroupBox('Folders')
		foldersGrpLayout = QtGui.QVBoxLayout()
		foldersGrp.setLayout(foldersGrpLayout)
		
		charNameLayout = QtGui.QHBoxLayout()
		self.charNameEdit = QtGui.QLineEdit('Enter character name')
		self.animTypeCombo = QtGui.QComboBox()
		items = ['action','entry','exit','idle',]
		self.animTypeCombo.addItems(items)
		self.animNumberCombo = QtGui.QComboBox()
		items = []
		for i in range(1,21):
			if i < 10:
				items.append('0' + str(i))
			else:
				items.append(str(i))
		self.animNumberCombo.addItems(items)
		self.newAnimBtn = QtGui.QPushButton('Create new animation')
		charNameLayout.addWidget(self.charNameEdit)
		charNameLayout.addWidget(self.animTypeCombo)
		charNameLayout.addWidget(self.animNumberCombo)
		charNameLayout.addWidget(self.newAnimBtn)
		
		line = QtGui.QFrame()
		line.setFrameShape(QtGui.QFrame.HLine)
		
		
		filterLayout = QtGui.QHBoxLayout()
		filterLabel = QtGui.QLabel('Filter')
		self.filterEdit = QtGui.QLineEdit()
		self.filterBtn = QtGui.QPushButton('Filter animations')
		filterLayout.addWidget(filterLabel)
		filterLayout.addWidget(self.filterEdit)
		filterLayout.addWidget(self.filterBtn)
		
		
		actionsLayout = QtGui.QHBoxLayout()
		self.openFileBtn = QtGui.QPushButton('Open Selected')
		self.saveFileBtn = QtGui.QPushButton('Save new version')
		self.copyToPreviewBtn = QtGui.QPushButton('Copy Wip To Preview')
		self.playblastBtn = QtGui.QPushButton('Playblast current scene')
		self.copyPlayblastBtn = QtGui.QPushButton('Move playblast to preview')
		actionsLayout.addWidget(self.openFileBtn)
		actionsLayout.addWidget(self.saveFileBtn)
		actionsLayout.addWidget(self.copyToPreviewBtn)
		actionsLayout.addWidget(self.playblastBtn)
		actionsLayout.addWidget(self.copyPlayblastBtn)
		
		self.filesTabs = QtGui.QTabWidget()
		tableTitles = ['Animation File','Version','Has Playblast?']
		self.wipAnimTable = self.createTable(tableTitles)
		self.previewAnimTable = self.createTable(tableTitles)
		
		self.filesTabs.addTab(self.wipAnimTable,'01_wip')
		self.filesTabs.addTab(self.previewAnimTable,'03_preview')
		
		foldersGrpLayout.addLayout(charNameLayout)
		foldersGrpLayout.addLayout(actionsLayout)
		foldersGrpLayout.addWidget(line)
		foldersGrpLayout.addLayout(filterLayout)
		foldersGrpLayout.addWidget(self.filesTabs)
		
		#end folders
		mainLayout.addWidget(settingsGrp)
		mainLayout.addWidget(foldersGrp)
		
		centralWidget.setLayout(mainLayout)
		self.setCentralWidget(centralWidget)
		
		
		self.getWipFolder()
		self.wipAnimBtn.clicked.connect(self.setWipFolder)
		self.openFileBtn.clicked.connect(self.openSelectedFile)
		self.openFolderBtn.clicked.connect(self.openFolder)
		
		self.saveFileBtn.clicked.connect(self.saveNewVersion)
		self.copyToPreviewBtn.clicked.connect(self.copyAnim)
		self.playblastBtn.clicked.connect(self.playblastCurrent)
		self.copyPlayblastBtn.clicked.connect(self.copyPlayblast)
		#self.playblastCamBtn.clicked.connect(self.pickCamera)
		self.newAnimBtn.clicked.connect(self.createAnimFile)
		self.filterBtn.clicked.connect(self.filterAnimations)
		self.wipAnimTable.cellPressed.connect(self.clearPreviewSelection)
		self.wipAnimTable.doubleClicked.connect(self.openSelectedFile)
		
		
		#self.wipAnimTable.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
		#self.wipAnimTable.customContextMenuRequested.connect(self.previewTableMenu)
		
		self.previewAnimTable.cellPressed.connect(self.clearWipSelection)
		self.previewAnimTable.doubleClicked.connect(self.openSelectedFile)
		
		#self.lastVersionCheckBox.stateChanged.connect(self.bdGetLastVersion)
		self.show()
		self.resize(860,600)

		
		
	
	def createTable(self,headerTitles):
		colNum = len(headerTitles)
		
		table = QtGui.QTableWidget(0,colNum)
		
		hheader = QtGui.QHeaderView(QtCore.Qt.Orientation.Horizontal)
		hheader.setStretchLastSection(True)
		hheader.setClickable(True)
		table.setHorizontalHeader(hheader)
		table.setHorizontalHeaderLabels(headerTitles)
		table.setAlternatingRowColors(1)

		return table		

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
		animNumber = self.animNumberCombo.currentText()
		
		if character:
			if 'name' not in character:
				#animNumber = self.getLastAnim(animType)
				fullName = character + '_' + animType + '_' + animNumber + '_01.ma'
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
		if 'wip' in currentSceneName.lower():
			path,sceneName = os.path.split(currentSceneName)
			self.wipFolderEdit.setText(path)
			self.wipFolderPath = path
			self.bdPopulateFiles()
		else:
			projectPath = pm.workspace.path
			charactersFolder = os.path.join(projectPath,'scenes')
			if os.path.isdir(charactersFolder):
				characters = os.path.join(charactersFolder,'characters')
				if os.path.isdir(characters):
					charactersFolder = characters
					
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
			projectPath = pm.workspace.path
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
		
		if self.filterString:
			filtered = []
			for anim in wipFileList:
				if self.filterString in anim:
					filtered.append(anim)
			if len(filtered):
				wipFileList = filtered
				
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
		
		wipHeader = self.wipAnimTable.horizontalHeader()
		wipHeader.setStretchLastSection(True)
		
		self.updateLastVersion()
		
		


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
		
		previewHeader = self.previewAnimTable.horizontalHeader()
		previewHeader.setStretchLastSection(True)		
		
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

		
		#self.bdPopulateFiles()

	
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
				
			pm.optionVar(stringValueAppend=('RecentFilesList', currentFile))
			pm.optionVar(stringValueAppend=('RecentFilesTypeList', 'mayaAscii'))			

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
		playblastFormat = self.animFormatComboBox.currentText()
		print playblastFormat 
		qtPlayblastMelCmd = 'playblast  -format qt -sequenceTime 0 -clearCache 1 -viewer 1 -showOrnaments 1 -fp 4 -percent 100 -compression "H.264" -quality 100 -widthHeight 1280 720;';
		xvidPlayblastMelCmd  = 'playblast  -format avi -sequenceTime 0 -clearCache 1 -viewer 1 -showOrnaments 1 -fp 4 -percent 100 -compression "XVID" -quality 100 -widthHeight 1280 720;';
		uncommpresedPlayblastMelCmd = 'playblast  -format avi -sequenceTime 0 -clearCache 1 -viewer 1 -showOrnaments 1 -fp 4 -percent 100 -compression "none" -quality 100 -widthHeight 1280 720;';
		tempFile = ''
		if playblastFormat == 'mov':
			tempFile = pm.mel.eval(qtPlayblastMelCmd)
		elif playblastFormat == 'avi':
			tempFile = pm.mel.eval(xvidPlayblastMelCmd)
		elif playblastFormat == 'uncompressed':
			tempFile = pm.mel.eval(uncommpresedPlayblastMelCmd)
		
		if os.path.isfile(tempFile):
			path,fileName = os.path.split(pm.sceneName())
			extension = '.mov'
			if playblastFormat == 'avi' or playblastFormat == 'uncompressed':
				extension  = '.avi'

			movFile = fileName.split('.')[0] + extension
			try:
				shutil.copy2(tempFile, os.path.join(path,movFile))
			except:
				pm.error("Coulnd't copy the temp blast")
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
					if destPath == wipPath:
						destPath = wipPath.replace('01_WIP','03_PREVIEW')
					dest = os.path.abspath(os.path.join(destPath,blastFileName))
					
					
					if os.path.isfile(blastFile):
						if os.path.isfile(dest):
							pm.warning('Blast exists already, will not overwrite ( save new version ? )')
						else:
							try:
								print("copying")
								shutil.copyfile(blastFile, dest)
								try:
									os.remove(blastFile)
								except OSError:
									pass
								self.bdPopulateFiles()
							except:
								pm.error('Could not copy blast file to preview')
	
	def updateLastVersion(self):
		lastVersion = self.getLastVersion()
		rows  = self.wipAnimTable.rowCount()
		print lastVersion
		
		for i in range(rows):
			anim = self.wipAnimTable.item(i,0).text().split('.')[0]
			print anim
			if anim in lastVersion:
				item = self.wipAnimTable.item(i,1)
				font = QtGui.QFont("",9,QtGui.QFont.Bold)
				brush = QtGui.QBrush(QtCore.Qt.green)
				#item.setBackground(QtGui.QColor(0,100,0))
				item.setForeground(brush)
				item.setFont(font)
				
				
	def getLastVersion(self):
		fileList = []
		baseNameList = []
		lastVersionList = []

		rows  = self.wipAnimTable.rowCount()
		for i in range(rows):
			print self.wipAnimTable.item(i,0)
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

		return lastVersionList
	
	def pickCamera(self):
		selection  = pm.ls(sl=1)
		if selection:
			transform = selection[0]
			shape = pm.listRelatives(transform,c=1)
			if shape:
				if shape[0].type() == 'camera':
					self.playblastCamEdit.setText(transform.name())
				
			
	def setCamera(self):
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
				
	def filterAnimations(self):
		self.filterString = self.filterEdit.text()
		print self.filterString 
		self.bdPopulateFiles()
		
	'''
	def closeEvent(self, event):
		# do stuff
		print self.openSceneCallback
		if self.openSceneCallback:
			print 'Removing callback'
			om.MSceneMessage.removeCallback(self.openSceneCallback)
			self.openSceneCallback = None
		event.accept() 
	'''
	
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
		

def main():
	if pm.window( bdAnimToolWin, exists = True, q = True ):
		pm.deleteUI( bdAnimToolWin)

	AnimToolUI()