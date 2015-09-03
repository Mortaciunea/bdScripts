import sip,os
import maya.OpenMayaUI as mui
import pymel.core as pm
import logging
from functools import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic
import maya.cmds as cmds

pyqtLoggers = ['PyQt4.uic.properties','PyQt4.uic.uiparser']
for log in pyqtLoggers:
	logger = logging.getLogger(log)
	logger.setLevel(logging.ERROR)

	
def getMayaWindow():
	ptr = mui.MQtUtil.mainWindow()
	return sip.wrapinstance(long(ptr), QObject)

uiFile = os.path.join(os.path.dirname(__file__), 'bdMultiRename.ui')

try:
	bdMultiRenameUI_form,bdMultiRenameUI_base = uic.loadUiType(uiFile)
except:
	print 'Could not find the UI file'

def bdGetWidgetByName(name):
	widgetPtr = mui.MQtUtil.findControl(name)
	widget = sip.wrapinstance(long(widgetPtr), QObject)
	return widget

class bdMultiRenameUI(bdMultiRenameUI_form,bdMultiRenameUI_base):
	def __init__(self, parent=getMayaWindow()):
		self.window = 'bdMRMainWindow'
		super(bdMultiRenameUI, self).__init__(parent)
		self.setupUi(self)
		
		self.startCount = 1
		self.inputStartCounter.setValue(self.startCount)
		
		self.bdPopulateListOriginal()
		
		self.renameBtn.clicked.connect(self.bdRenameSelected)
		self.updateBtn.clicked.connect(self.bdUpdateSelected)
		self.replaceBtn.clicked.connect(self.bdReplaceSelected)
		self.inputStartCounter.valueChanged[int].connect(self.bdStartCount)

		
	def bdStartCount(self, val):
		self.startCount = val
		
	def bdUpdateSelected(self,*args):
		self.listOriginal.clear()
		self.bdPopulateListOriginal()

	def bdReplaceSelected(self,*args):
		selectedObj = []
		selectedObj = cmds.ls(selection = True,ap=True )	
		strSearch = str(self.inputSearch.text())
		strReplace = str(self.inputReplace.text())
		strPrefix = str(self.inputPrefixReplace.text())
		strSufix = str(self.inputSufixReplace.text())
		
		strNewNames = []

		if strSearch != '':
			self.listPreview.clear()
			for obj in selectedObj:
				newName = strPrefix + obj.split('|')[-1].replace(strSearch,strReplace) + strSufix
				self.listPreview.addItem(newName)
				strNewNames.append(newName)
		else:
			if strPrefix != '' or strSufix != '':
				self.listPreview.clear()
				for obj in selectedObj:
					newName = strPrefix + obj.split('|')[-1] + strSufix
					self.listPreview.addItem(newName)
					strNewNames.append(newName)				

		strNewNames = list(reversed(strNewNames))
		strSelected = list(reversed(selectedObj))
		for i in range(len(strNewNames)):
			print 'new name for %s is %s'%(strSelected[i],strNewNames[i])
			cmds.rename(strSelected[i],strNewNames[i])	

	def bdRenameSelected(self,*args):
		selectedObj = []
		selectedObj = cmds.ls(selection = True,ap=True )	
		strDigits = 2
		if len(selectedObj) > 100:
			strDigits = 3
		strPrefix = str(self.inputPrefix.text())
		strSufix = str(self.inputSufix.text())
		strRenameMask = str(self.inputRenameMask.text()) 
		
		strNewNames = []
		if (strRenameMask != ''):

			strIndex = ''
			for i in range(0,strDigits):
				strRenameMask = strRenameMask.replace('#','')
				strIndex = strIndex + '0'
			self.listPreview.clear()
			
			countStart = self.startCount
			for i in range(0,len(selectedObj) ):
				print selectedObj[i]

				if (i + countStart)<=9:
					newName = strPrefix +  strRenameMask + strIndex[0:-1] + str(i+countStart) +  strSufix
					self.listPreview.addItem(newName)
					strNewNames.append(newName)
				elif (i + countStart) > 9 and (i + countStart) < 100:
					newName = strPrefix +  strRenameMask + strIndex[0:-2] + str(i+countStart) +  strSufix
					self.listPreview.addItem(newName)
					strNewNames.append(newName)
				elif (i + countStart) > 99 :
					newName = strPrefix +  strRenameMask + strIndex[0:-3] + str(+countStart) +  strSufix
					self.listPreview.addItem(newName)
					strNewNames.append(newName)
			strNewNames = list(reversed(strNewNames))
			strSelected = list(reversed(selectedObj))
			for i in range(len(strNewNames)):
				print 'new name for %s is %s'%(strSelected[i],strNewNames[i])
				cmds.rename(strSelected[i],strNewNames[i])

		else:
			print 'Need a mask'

	def bdPopulateListOriginal(self,*args):
		selectedObj = []
		selectedObj = cmds.ls(selection = True )
		for item in selectedObj:
			self.listOriginal.addItem(item)
			


def bdMain():
	global bdMultiRenameWin
	
	try:
		bdMultiRenameWin.close()
	except:
		print 'No prev window, opening one'
		pass
	
	bdMultiRenameWin = bdMultiRenameUI()
	bdMultiRenameWin.show()



