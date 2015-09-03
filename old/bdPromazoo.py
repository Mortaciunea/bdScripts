import sip,os, math, fnmatch
import maya.OpenMayaUI as mui
import maya.OpenMaya as om
import pymel.core as pm
import logging
from functools import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic


pyqtLoggers = ['PyQt4.uic.properties','PyQt4.uic.uiparser']
for log in pyqtLoggers:
	logger = logging.getLogger(log)
	logger.setLevel(logging.ERROR)

def getMayaWindow():
	ptr = mui.MQtUtil.mainWindow()
	return sip.wrapinstance(long(ptr), QObject)

uiFile = os.path.join(os.path.dirname(__file__), 'bdPromazoo.ui')

try:
	bdPromazoo_form,bdPromazoo_base = uic.loadUiType(uiFile)
except:
	print 'Could not find the UI file'

def bdGetWidgetByName(name):
	widgetPtr = mui.MQtUtil.findControl('createConBtn1')
	widget = sip.wrapinstance(long(widgetPtr), QObject)
	return widget

class bdPromazooUI(bdPromazoo_form,bdPromazoo_base):
	def __init__(self, parent=getMayaWindow()):
		super(bdPromazooUI, self).__init__(parent)
		self.setupUi(self)

		self.scan_pushButton.clicked.connect(self.bdScanForProjects)

	def bdScanForProjects(self,projectFolder):
		rootPath = 'p:/street_fighter/'
		
		for fn in os.listdir(rootPath):
			if fn == 'working_project':
				print fn



def bdMain():
	global bdPromazooWin

	try:
		bdPromazooWin.close()
	except:
		print 'No prev window, opening one'
		pass

	bdPromazooWin = bdPromazooUI()
	bdPromazooWin.show()