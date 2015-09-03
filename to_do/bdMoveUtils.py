import sip
import maya.OpenMayaUI as mui
import pymel.core as pm

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic

def getMayaWindow():
	ptr = mui.MQtUtil.mainWindow()
	return sip.wrapinstance(long(ptr), QObject)

try:
	bdMU_form,bdMU_base = uic.loadUiType(r'C:/Users/Ender/Documents/maya/scripts/bdMoveUtils.ui')
except:
	print 'Could not find the UI file'

class bdPivot():
	def __init__(self):
		print 'Creating a pivot'

class bdMoveUtilsUI(bdMU_form, bdMU_base):
	def __init__(self, parent=getMayaWindow()):
		super(bdMoveUtilsUI, self).__init__(parent)
		self.setupUi(self)
		
		#only int values allowed
		self.holdStartFrameLE.setValidator(QIntValidator())
		self.holdEndFrameLE.setValidator(QIntValidator())
		self.pivotStartFrameLE.setValidator(QIntValidator())
		self.pivotEndFrameLE.setValidator(QIntValidator())
		
		#events connected
		self.holdBTN.clicked.connect(self.bdHoldPosition)
		self.addPivotBTN.clicked.connect(self.bdAddPivot)
	
	def bdHoldPosition(self):
		startFrame = self.holdStartFrameLE.text()
		endFrame = self.holdStartFrameLE.text()
		
		if (startFrame and endFrame):
			print startFrame, endFrame
		
	def bdAddPivot(self):
		pivot = bdPivot()
		

			
class bdPivot():
	def __init__(self):
		pm.sphere()
		print 'Creating a pivot'
		
def bdMUMain():
	global bdMUWin
	
	try:
		bdMUWin.close()
	except:
		print 'No prev window, opening one'
		pass
	
	bdMUWin = bdMoveUtilsUI()
	bdMUWin.show()