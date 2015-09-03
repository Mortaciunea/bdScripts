import sip,os
import maya.OpenMayaUI as mui
import pymel.core as pm

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic

import logging
pyqtLoggers = ['PyQt4.uic.properties','PyQt4.uic.uiparser']
for log in pyqtLoggers:
	logger = logging.getLogger(log)
	logger.setLevel(logging.ERROR)

def getMayaWindow():
	ptr = mui.MQtUtil.mainWindow()
	return sip.wrapinstance(long(ptr), QObject)

uiFile = os.path.join(os.path.dirname(__file__), 'bdUN.ui')

try:
	bdUN_form,bdUN_base = uic.loadUiType(uiFile)
except:
	print 'Could not find the UI file'



class bdUNManager(bdUN_form, bdUN_base):
	utilityNodesList = ['','multiplyDivide','condition','remapValue']
	pShapeMakers = [] 
	
	def __init__(self, parent=getMayaWindow()):
		super(bdUNManager, self).__init__(parent)
		self.setupUi(self)
		
		self.createUNBtn.clicked.connect(self.bdCreateUtilityNode)
		self.unPickSrcBtn.clicked.connect(self.bdPickSrc)
		self.unPickDestBtn.clicked.connect(self.bdPickDest)
		self.createConectionBtn.clicked.connect(self.bdCreateConnection)
		self.unListView.itemClicked.connect(self.bdItemClicked)
		self.filterName.textChanged.connect(self.bdFilterByName)
		self.filterComboBox.currentIndexChanged.connect(self.bdFilterByType)
		
		self.unComboBox.addItems(self.utilityNodesList)
		self.filterComboBox.addItems(self.utilityNodesList)
		
		self.bdPopulateUNList()
		
		self.addWidget()
	
		
	def bdPickSrc(self):
		selected = pm.ls(selection = True)
		self.unSrc.setText(selected[0].name())
	def bdPickDest(self):
		selected = pm.ls(selection = True)
		nodeType = str(self.unComboBox.currentText())
		self.unDest.setText(selected[0].name())
		self.unName.setText(selected[0].name() + '_' + nodeType)
		
	def bdCreateConnection(self):
		source = pm.ls(str(self.unSrc.text()))[0]
		
		dest = pm.ls(str(self.unDest.text()))[0]
		
		srcAttr = str(self.unSrcAttr.currentText())
		srcAxis = str(self.unSrcAxes.currentText())		
				
		destAttr = str(self.unDestAttr.currentText())
		destAxis = str(self.unDestAxes.currentText())
		
		nodeType = str(self.unComboBox.currentText())
		if nodeType == self.utilityNodesList[1]:
			utilityNode = self.bdCreateUtilityNode(nodeType)
			utilityNode.attr('input2' + srcAxis).set(0.5)
			source.attr(srcAttr + srcAxis).connect(utilityNode.attr('input1' + srcAxis))
			utilityNode.attr('output' + srcAxis).connect(dest.attr(destAttr + srcAxis))
		elif nodeType == self.utilityNodesList[2]:
			print nodeType
		
	def bdCreateUtilityNode(self,nodeType):
		unName = str(self.unName.text())
		unExists = pm.ls(unName)
		print unExists 
		if (unName != ''):
			if nodeType != '':
				node = ''
				if (unExists):
					node = unExists[0]
				else:
					node = pm.createNode(nodeType, n = unName)
				self.bdPopulateUNList()
				return node
			else:
				print 'Choose a node type'
		else:
			print 'Need a name'
			
	def bdPopulateUNList(self):
		allNodesType = [str(self.unComboBox.itemText(i)) for i in range(self.unComboBox.count())]
		nodeList = []
		for nodeType in allNodesType:
			if nodeType != "":
				nodeList += pm.ls(type = nodeType)
		pmNames = [pmNode.name() for pmNode in nodeList]
		
		self.unListView.clear()	
		self.unListView.addItems(pmNames)
		
	def bdItemClicked(self,item):
		pm.select(str(item.text()))
		selectedNode = pm.ls(selection=True)[0]
		selectedConnections  = selectedNode.connections()
		
		pmNames = [pmNode.name() for pmNode in selectedConnections]
		
		self.unConListView.clear()	
		self.unConListView.addItems(pmNames)
		
		nodeEditor =  pm.scriptedPanel(type="nodeEditorPanel", label="Node Editor")
		
			
	
	def bdFilterByName(self,text):
		itemsInList = [self.unListView.item(i) for i in range(self.unListView.count())]
		filteredList = []
		if str(text) != '':
			for item in itemsInList:
				if str(text) in str(item.text()):
					filteredList.append( str(item.text()))
			
			self.unListView.clear()	
			self.unListView.addItems(filteredList)
		else:
			self.bdPopulateUNList()
	
	def bdFilterByType(self,nodeTypeIndex):
		if nodeTypeIndex > 0:
			nodeType = str(self.unComboBox.itemText(nodeTypeIndex))
			nodeList = pm.ls(type = nodeType)
			pmNames = [pmNode.name() for pmNode in nodeList]
			
			self.unListView.clear()	
			self.unListView.addItems(pmNames)
		else:
			self.bdPopulateUNList()
			
	def addWidget(self):
		self.nodeEditorLayout.addRow(mdSettings())


class mdSettings(QWidget):
	def __init__( self, parent=None):
		super(mdSettings, self).__init__(parent)
		self.pushButton = QPushButton('I am in Test widget')
	   
		layout = QHBoxLayout()
		layout.addWidget(self.pushButton)
		self.setLayout(layout)		
		

global bdUNWindow

try:
	bdUNWindow.close()
except:
	print 'No prev window, opening one'
	pass

bdUNWindow = bdUNManager()
bdUNWindow.show()