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

def widgetPath(windowName, widgetNames):
	"""
	@param windowName: Window instance name to search
	@param widgetNames: list of names to search for
	taken from http://www.chris-g.net/2011/06/24/maya-qt-interfaces-in-a-class/
	"""

	returnDict = {}
	mayaWidgetList = cmds.lsUI(dumpWidgets=True)

	for widget in widgetNames:
		for mayaWidget in mayaWidgetList:
			if windowName in mayaWidget:
				if mayaWidget.endswith(widget):
					returnDict[widget] = mayaWidget

	return returnDict

class bdMultiRenameUI(object):
	def __init__(self,uiFile):
		uiWidgetList = ['inputRenameMask','inputCounterText','inputPrefix','inputSufix','inputSearch','inputReplace','listOriginal','listPreview','updateBtn','renameBtn','replaceBtn']
		self.window = 'bdMRMainWindow'

		if cmds.window(self.window,exists=True):
			cmds.deleteUI(self.window)
		self.window = cmds.loadUI(f=uiFile)

		self.uiObjects = widgetPath(self.window,uiWidgetList)

		cmds.showWindow(self.window)

		intValidator = QIntValidator()
		self.inputStartCounter.setValidator(intValidator)
		self.startCount = 1
		self.inputStartCounter.setText(self.startCount)
		self.bdPopulateListOriginal()
		cmds.button(self.uiObjects['renameBtn'], edit = True, command = self.bdRenameSelected)
		cmds.button(self.uiObjects['updateBtn'], edit = True, command = self.bdUpdateSelected)
		cmds.button(self.uiObjects['replaceBtn'], edit = True, command = self.bdReplaceSelected)


	def bdUpdateSelected(self,*args):
		cmds.textScrollList(self.uiObjects['listOriginal'],edit = True, ra = True)
		self.bdPopulateListOriginal()

	def bdReplaceSelected(self,*args):
		selectedObj = []
		selectedObj = cmds.ls(selection = True,ap=True )	
		strSearch = cmds.textField(self.uiObjects['inputSearch'], q = True, text = True )
		strReplace = cmds.textField(self.uiObjects['inputReplace'], q = True, text = True )
		print strSearch, strReplace
		strNewNames = []

		if strSearch != '':
			cmds.textScrollList(self.uiObjects['listPreview'],edit = True, ra = True)
			for obj in selectedObj:
				newName = obj.split('|')[-1].replace(strSearch,strReplace)
				print newName
				cmds.textScrollList(self.uiObjects['listPreview'],edit = True, append = newName)
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
		strPrefix = cmds.textField(self.uiObjects['inputPrefix'], q = True, text = True )
		strSufix = cmds.textField(self.uiObjects['inputSufix'], q = True, text = True )
		strRenameMask = cmds.textField(self.uiObjects['inputRenameMask'], q = True, text = True )

		strNewNames = []
		if (strRenameMask != ''):

			strIndex = ''
			for i in range(0,strDigits):
				strRenameMask = strRenameMask.replace('#','')
				strIndex = strIndex + '0'	    
			cmds.textScrollList(self.uiObjects['listPreview'],edit = True, ra = True)
			countStart = 1
			for i in range(0,len(selectedObj) ):
				print selectedObj[i]

				if (i + countStart)<=9:
					newName = strPrefix +  strRenameMask + strIndex[0:-1] + str(i+countStart) +  strSufix
					cmds.textScrollList(self.uiObjects['listPreview'],edit = True, append = newName)
					strNewNames.append(newName)
				elif (i + countStart) > 9 and (i + countStart) < 100:
					newName = strPrefix +  strRenameMask + strIndex[0:-2] + str(i+countStart) +  strSufix
					print newName
					cmds.textScrollList(self.uiObjects['listPreview'],edit = True, append = newName)
					strNewNames.append(newName)
				elif (i + countStart) > 99 :
					newName = strPrefix +  strRenameMask + strIndex[0:-3] + str(+countStart) +  strSufix
					cmds.textScrollList(self.uiObjects['listPreview'],edit = True, append = newName)
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
			cmds.textScrollList(self.uiObjects['listOriginal'],edit = True, append = item)


def bdMain():
	uiFile = os.path.join(os.path.dirname(__file__), 'bdMultiRename.ui')
	win = bdMultiRenameUI(uiFile)



