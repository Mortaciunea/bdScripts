import sip,os
import maya.OpenMayaUI as mui
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

uiFile = os.path.join(os.path.dirname(__file__), 'bdAnimCon.ui')

try:
	bdAnimCon_form,bdAnimCon_base = uic.loadUiType(uiFile)
except:
	print 'Could not find the UI file'

def bdGetWidgetByName(name):
	widgetPtr = mui.MQtUtil.findControl('createConBtn1')
	widget = sip.wrapinstance(long(widgetPtr), QObject)
	return widget

class bdAnimConUI(bdAnimCon_form,bdAnimCon_base):
	conColors = {'':17,'L_':18,'R_':13}
	def __init__(self, parent=getMayaWindow()):
		super(bdAnimConUI, self).__init__(parent)
		self.setupUi(self)
		conPrefixes = ['','L_','R_']
		
		
		self.createConBtn1.clicked.connect(partial(self.bdCreateCon,1))
		self.createConBtn2.clicked.connect(partial(self.bdCreateCon,2))
		self.createConBtn3.clicked.connect(partial(self.bdCreateCon,3))
		
		self.createConBtn4.clicked.connect(partial(self.bdCreateCon,4))
		self.createConBtn5.clicked.connect(partial(self.bdCreateCon,5))
		self.createConBtn6.clicked.connect(partial(self.bdCreateCon,6))

		self.createConBtn7.clicked.connect(partial(self.bdCreateCon,7))
		self.createConBtn8.clicked.connect(partial(self.bdCreateCon,8))
		self.createConBtn9.clicked.connect(partial(self.bdCreateCon,9))
		
		self.createConBtn10.clicked.connect(partial(self.bdCreateCon,10))
		
		
		self.mirrorConBtn.clicked.connect(self.bdMirrorCon)
		self.inputConSide.currentIndexChanged[str].connect(self.bdButtonsColor)
		validator = QDoubleValidator(0,100,2,self)
		self.inputConSize.setValidator(validator)
		
		self.inputConSide.addItems(conPrefixes)

	
	def bdCreateCircleCon(self):
		print 'Circle Controller'
		test = mui.MQtUtil.findControl('createConBtn1')
		print test
		
		animConName = self.bdGetConName()
		if animConName != '':
			conSize = self.inputConSize.text()
			overrideColor = self.conColors[str(self.inputConSide.currentText())]
	
			if not conSize:
				conSize=1
				
			selection = pm.ls(sl = True)
			selPos = [0,0,0]
			selRot = [0,0,0]
			if selection:
				selPos = selection[0].getTranslation(space='world')
				selRot = selection[0].getRotation(space='world')
						
			circleCon = pm.circle(n = animConName ,nr=(0, 1, 0), c=(0, 0, 0),radius=float(conSize) ) [0]
			circleCon.getShape().overrideEnabled.set(1)
			circleCon.getShape().overrideColor.set(overrideColor)
			circleConGrp = pm.group(circleCon,name = circleCon.name() + '_GRP')
			circleConGrp.setTranslation(selPos)
			circleConGrp.setRotation(selRot)
		else:
			pm.warning('Need a name, aborting')


	def bdCreateCircleZCon(self):
		print 'Circle Z Controller'
		animConName = self.bdGetConName()
		if animConName!='':
			conSize = self.inputConSize.text()
			overrideColor = self.conColors[str(self.inputConSide.currentText())]
			if not conSize:
				conSize=1
				
			selection = pm.ls(sl = True)
			selPos = [0,0,0]
			selRot = [0,0,0]
			if selection:
				selPos = selection[0].getTranslation(space='world')
				selRot = selection[0].getRotation(space='world')
						
			circleCon = pm.circle(n = animConName ,nr=(0, 1, 0), c=(0, 0, 0),radius=int(conSize) )[0]
			circleCon.getShape().overrideEnabled.set(1)
			circleCon.getShape().overrideColor.set(overrideColor)
			
			circleConGrp = pm.group(circleCon,name = circleCon.name() + '_GRP')
			conCvs = circleCon.cv
			zDirectionPos = conCvs[5].getPosition(space = 'world')
			zDirectionPos[2] = zDirectionPos[2] * 1.25
			print zDirectionPos
			conCvs[5].setPosition(zDirectionPos)
			
			circleConGrp.setTranslation(selPos,space='world')
			circleConGrp.setRotation(selRot,space='world')
		else:
			pm.warning('Need a name, aborting')

	def bdCreateBoxCon(self):
		print 'Box Controller'
		selection = pm.ls(sl = True)
		animConName = self.bdGetConName()
		if animConName != '':
			overrideColor = self.conColors[str(self.inputConSide.currentText())]
			
			defaultPointsList = [(1,-1,1),(1,-1,-1),(-1,-1,-1),(-1,-1,1),(1,1,1),(1,1,-1),(-1,1,-1),(-1,1,1)]
			pointsList = []
			conSize = self.inputConSize.text()
			if not conSize:
				conSize=1		
			for p in defaultPointsList:
				pointsList.append(( p[0] * float(conSize), p[1] * float(conSize), p[2] * float(conSize) ))
		
			knotsList = [i for i in range(16)]
			curvePoints = [pointsList[0], pointsList[1], pointsList[2], pointsList[3], 
				           pointsList[7], pointsList[4], pointsList[5], pointsList[6],
				           pointsList[7], pointsList[3], pointsList[0], pointsList[4],
				           pointsList[5], pointsList[1], pointsList[2], pointsList[6] ]
		
			boxCon = pm.curve(d=1, p = curvePoints , k = knotsList,n= animConName)
			boxCon.getShape().overrideEnabled.set(1)
			boxCon.getShape().overrideColor.set(overrideColor)		
			boxConGrp= pm.group(boxCon,n=boxCon.name() + '_GRP')
			
			
			selPos = [0,0,0]
			selRot = [0,0,0]
			if selection:
				print selection
				selPos = selection[0].getTranslation(space='world')
				selRot = selection[0].getRotation(space='world')
				print selPos, selRot 
				
			print selPos, selRot 
			boxConGrp.setTranslation(selPos,space='world')
			boxConGrp.setRotation(selRot,space='world')
		else:
			pm.warning('Need a name, aborting')
		
	def bdMirrorCon(self):
		print 'Mirror Controller'
		
		selection = pm.ls(sl=True)
		if selection.count > 0:
			for sel in selection:
				if ('L_' in sel.name()) or ('R_' in sel.name()):
					print sel.name()
					conGrp = sel.getParent()
					conGrpPos = conGrp.getTranslation(space='world')
					conGrpRot = conGrp.getRotation(space='world')
					
					exp = ['L_','R_']
					if 'R_' in conGrp.name():
						exp.reverse()
					print exp
					mirrorConGrp = pm.duplicate(conGrp,name = conGrp.name().replace(exp[0],exp[1]))[0]
					mirroCon = mirrorConGrp.getChildren()[0]
					mirroCon.rename(sel.name().replace(exp[0],exp[1]))
					mirroCon.getShape().overrideColor.set(self.conColors[exp[1]])
					
					mirrorConGrp.setTranslation([conGrpPos[0]*-1,conGrpPos[1],conGrpPos[2]])
					mirrorConGrp.setRotation([conGrpRot[0],conGrpRot[1],conGrpRot[2]*-1])
				else:
					pm.warning( 'Central controller, no need (sic) to mirror it!')
				
				                           

	def bdGetConName(self):
		animConName = str(self.inputConName.text())
		animConSide = str(self.inputConSide.currentText())
		
		if animConName:
			animConName = animConSide + animConName + '_CON'
		else:
			animConName = ''

		return animConName 
	
	def bdButtonsColor(self,item):
		conColor = self.conColors[str(item)]
		#self.createCircleConBtn.setStyleSheet('background-color: ' + conColor)
		#self.createCircleZConBtn.setStyleSheet('background-color: ' + conColor)
		#self.createBoxConBtn.setStyleSheet('background-color: ' + conColor)

def bdMain():
	global bdAnimConWindow
	
	try:
		bdAnimConWindow.close()
	except:
		print 'No prev window, opening one'
		pass
	
	bdAnimConWindow = bdAnimConUI()
	bdAnimConWindow.show()

