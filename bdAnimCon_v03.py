import sip,os, math
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

uiFile = os.path.join(os.path.dirname(__file__), 'bdAnimCon1.ui')

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
	conBtn = []
	conList = []
	iconList = []
	def __init__(self, parent=getMayaWindow()):
		super(bdAnimConUI, self).__init__(parent)
		self.setupUi(self)
		conPrefixes = ['','L_','R_']
		
		self.conList,self.iconList = self.bdListControllers()
		numCon = len(self.conList)
		for i in range(numCon):
			self.conBtn.append(QPushButton(self.conList[i]))
			self.conBtn[i].setFixedHeight(20)
			self.conBtn[i].setMinimumWidth(80)
			self.conBtn[i].setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Fixed)
			#self.conBtn[i].setIcon(QIcon(self.iconList[i]))
			#self.conBtn[i].setIconSize(QSize(80,80))
			self.conBtn[i].clicked.connect(partial(self.bdCreateCon,i))
			
		
		n=0
		numRows = math.ceil(numCon/3.0)
		numCol = 3
		for i in range(numRows):
			for j in range(numCol):
				if n < numCon:
					self.conBtnGridLayout.addWidget(self.conBtn[n],i,j)
					n = n+1
				else:
					break

		
		
		self.mirrorConBtn.clicked.connect(self.bdMirrorCon)
		self.inputConSide.currentIndexChanged[str].connect(self.bdButtonsColor)
		validator = QDoubleValidator(0,100,2,self)
		self.inputConSize.setValidator(validator)
		
		self.inputConSide.addItems(conPrefixes)

	
	def bdCreateCon(self,n):
		self.bdImportController(n)

	def bdImportController(self,n):
		con = self.conList[n]
		animConName = self.bdGetConName()
		overrideColor = self.conColors[str(self.inputConSide.currentText())]
		conSize = self.inputConSize.text()
		
		selection = pm.ls(sl = True)
		selPos = [0,0,0]
		selRot = [0,0,0]
		
		
		if selection:
			selPos = selection[0].getTranslation(space='world')
			selRot = selection[0].getRotation(space='world')		

		if not conSize:
			conSize=1		
		
		
		if animConName != '':		
			scriptPath = os.path.dirname(__file__)
			conFile = scriptPath + '/controllers/' + con + '.ma'
			conTransform = [f for f in pm.importFile(conFile,returnNewNodes=True,namespace='temp') if f.type()=='transform'][0]
			#conTransform = pm.importFile( conFile,returnNewNodes=True,namespace='temp') 
			sceneNS = pm.namespaceInfo(lon=True,r=True)
			importNS = []
			for ns in sceneNS:
				if 'temp' in ns:
					importNS.append(ns)
			importNS.reverse()
			
			for ns in importNS:
				pm.namespace( rm = ns,mergeNamespaceWithRoot=True) 			
			
			print conTransform 
			
			conTransform.rename(animConName)
			scaleVector = om.MVector(1,1,1) * float(conSize)
			conTransform.setScale([scaleVector.x,scaleVector.y,scaleVector.z])
			pm.makeIdentity(conTransform,apply=True,t=0,r=0,s=1)
			
			for shape in conTransform.getChildren():
				shape.overrideEnabled.set(1)
				shape.overrideColor.set(overrideColor)
				
			conTransformGrp = pm.group(conTransform,name=conTransform.name() + '_GRP')
			
			conTransformGrp.setTranslation(selPos)
			conTransformGrp.setRotation(selRot)
			
			
			#pm.makeIdentity(conTransformGrp,s=True)
			
			

	
	def bdListControllers(self):
		scriptPath = os.path.dirname(__file__)
		conPath = scriptPath + '/controllers'
		conFiles = [f.replace('.ma','') for f in os.listdir(conPath) if f.endswith('.ma')]
		iconFiles = [(conPath + '/' + f) for f in os.listdir(conPath) if f.endswith('.jpg')]
		return conFiles,iconFiles
		
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

