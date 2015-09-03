import sip,os, math,sys
import maya.OpenMayaUI as mui
import maya.OpenMaya as om
import pymel.core as pm
import logging
from functools import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic
import pymel.core.datatypes as dt
from xml.dom.minidom import Document,parse

pyqtLoggers = ['PyQt4.uic.properties','PyQt4.uic.uiparser']
for log in pyqtLoggers:
	logger = logging.getLogger(log)
	logger.setLevel(logging.ERROR)

def getMayaWindow():
	ptr = mui.MQtUtil.mainWindow()
	return sip.wrapinstance(long(ptr), QObject)

uiFile = os.path.join(os.path.dirname(__file__), 'bdAnimCon2.ui')

try:
	bdAnimCon_form,bdAnimCon_base = uic.loadUiType(uiFile)
except:
	print 'Could not find the UI file'

def bdGetWidgetByName(name):
	widgetPtr = mui.MQtUtil.findControl('createConBtn1')
	widget = sip.wrapinstance(long(widgetPtr), QObject)
	return widget

class bdAnimCon(object):
	def __init__(self):
		self.conName = 'name'

	@staticmethod
	def bdExportCtrl():
		selection = pm.ls(sl=1, type = 'transform')
		xmlPath = 'c:\\Users\\bogdan_d\\Documents\\bdPyScripts\\controllers\\'
		xmlFile = ''

		if selection:
			if len(selection) ==1:
				cvPos = {}
				toExport = selection[0]
				shape = toExport.getShapes()
				xmlFile = toExport.name().replace(toExport.namespace(),'') + '.xml'
				xmlDoc = Document()
				root = xmlDoc.createElement('controller')
				root.setAttribute('name',toExport.name().replace(toExport.namespace(),''))
				xmlDoc.appendChild(root)
				for s in shape:
					if 'Orig' not in s.name():
						if s.type() == 'nurbsCurve':
							node = xmlDoc.createElement('shape')
		
							periodic = '0'
							if s.form() == 'periodic':
								periodic='1'
							node.setAttribute('periodic',periodic)
							degree = s.degree()
							node.setAttribute('degree',str(degree))
							
							cvPos = [ (x.x , x.y, x.z) for x in s.getCVs(space='world')]
							node.setAttribute('cvs',str(cvPos))
							knots =  [ k for k in s.getKnots()]
							node.setAttribute('knots',str(knots))
							node.setAttribute('name',s.name().replace(toExport.namespace(),''))

							root.appendChild(node)
						else:
							pm.warning('You can only export NURBS curves')
							break

				attrListNode = xmlDoc.createElement('attributesList')
				udAttr = toExport.listAttr(ud=True)
				for attr in udAttr:
					attrNode = xmlDoc.createElement('attribute')
					attrName = attr.name(includeNode=0).replace(toExport.namespace(),'')
					attrType = attr.type()
					if attrType == 'enum':
						dictEnum = attr.getEnums()
						val = [str(k) for k in dictEnum.keys() ]
						enumValues = str(val).strip('[]').replace('\'','')
						attrNode.setAttribute('enumValues',enumValues)
					attrLocked = attr.get(l=True)
					attrCB = attr.get(cb=True)
					attrValue = attr.get()
					attrMinMax = str(attr.getRange())
					
					
					attrNode.setAttribute('name',attrName)
					attrNode.setAttribute('type',attrType)
					attrNode.setAttribute('locked',str(attrLocked))
					attrNode.setAttribute('channelBox',str(attrCB))
					attrNode.setAttribute('value',str(attrValue))
					attrNode.setAttribute('minMax',attrMinMax)
					
					attrListNode.appendChild(attrNode)
					
				root.appendChild(attrListNode)
				f= open(xmlPath + xmlFile, 'w')
				f.write(xmlDoc.toprettyxml())
				f.close()


			else:
				pm.warning( 'Select only one controller !!!' )
		else:
			pm.warning( 'Select a Nurbs Curve' )
	
	@staticmethod
	def bdImportCon(con):
		xmlPath = 'c:\\Users\\bogdan_d\\Documents\\bdPyScripts\\controllers\\'
		dom = parse(xmlPath + con)
		controllerNode = dom.getElementsByTagName('controller')
		for node in controllerNode :
			conName =  node.getAttribute('name')
			shapeNodes = node.getElementsByTagName('shape')
			curvesToParent = []
			for s in shapeNodes:
				shapeName = s.getAttribute('name')
				print shapeName 
				shapeCvs = s.getAttribute('cvs')
				pos = [float(pos.strip('[](),')) for pos in shapeCvs.split(" ")]
				reconstructedPos = [(pos[i],pos[i+1],pos[i+2]) for i in range(0,len(pos),3)]

				shapeKnots = s.getAttribute('knots')
				knots = [float(k.strip('[](),')) for k in shapeKnots.split(" ")]
				reconstructedKnots = [k for k in knots]
				
				shapeDegree = int(s.getAttribute('degree'))
				shapePeriodic = int(s.getAttribute('periodic'))

				curve = pm.curve( p= reconstructedPos , k = reconstructedKnots , d = shapeDegree, per = shapePeriodic)
				curve.rename(shapeName.replace('Shape',''))
				curvesToParent.append(curve)
			
			parentCurve = curvesToParent[0]
			for curve in curvesToParent[1:]:
				pm.parent(curve.getShape(),parentCurve,r=1,shape=1)
				pm.delete(curve)
			
			pm.select(cl=1)
			parentCurve.centerPivots()
			
			atributesList = node.getElementsByTagName('attribute')
			for attr in atributesList:
				attrType = attr.getAttribute('type')
				attrName = attr.getAttribute('name')
				attrLocked = attr.getAttribute('locked')
				attrCB = attr.getAttribute('channelBox')
				attrVal = attr.getAttribute('value')
				attrMinMax = attr.getAttribute('minMax')
				
				if attrType == 'string':
					pm.addAttr(parentCurve, ln = attrName,dt = attrType )
					parentCurve.attr(attrName).setLocked(attrLocked)

				else:
					pm.addAttr(parentCurve, ln = attrName,at = attrType)
					parentCurve.attr(attrName).setLocked(attrLocked)				


class bdAnimConUI(bdAnimCon_form,bdAnimCon_base):
	conColors = {'':17,'L_':6,'R_':13}
	conBtn = []
	conList = []
	iconList = []
	def __init__(self, parent=getMayaWindow()):
		super(bdAnimConUI, self).__init__(parent)
		self.setupUi(self)
		conPrefixes = ['','L_','R_']
		
		self.mirrorOptionRBtn1.setChecked(True)
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
			
		self.rxBtn.clicked.connect(partial(self.bdRotateCon,'x'))
		self.ryBtn.clicked.connect(partial(self.bdRotateCon,'y'))
		self.rzBtn.clicked.connect(partial(self.bdRotateCon,'z'))
		n=0
		numRows = int(math.ceil(numCon/3.0))
		numCol = 3
		for i in range(numRows):
			for j in range(numCol):
				if n < numCon:
					self.conBtnGridLayout.addWidget(self.conBtn[n],i,j)
					n = n+1
				else:
					break
		
		self.inputConSide.addItems(conPrefixes)
	
		
		self.mirrorConBtn.clicked.connect(self.bdMirrorCon)
		self.inputConSide.currentIndexChanged[str].connect(self.bdButtonsColor)
		validator = QDoubleValidator(0,100,2,self)
		self.inputConSize.setValidator(validator)
		

		
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
			conTransformChidlren = conTransform.getChildren(ad=True,type='transform')
			
			for child in conTransformChidlren :
				child.rename(str(self.inputConSide.currentText()) + child.name())
				
			scaleVector = om.MVector(1,1,1) * float(conSize)
			conTransform.setScale([scaleVector.x,scaleVector.y,scaleVector.z])
			pm.makeIdentity(conTransform,apply=True,t=0,r=0,s=1)
			
			for shape in conTransform.getChildren():
				shape.overrideEnabled.set(1)
				shape.overrideColor.set(overrideColor)
				
			conTransformGrp = pm.group(conTransform,name=conTransform.name() + '_GRP')
			conTransformGrp.setPivots([0,0,0])
			
			conTransformGrp.setTranslation(selPos,space='world')
			conTransformGrp.setRotation(selRot,space='world')
			

	
	def bdListControllers(self):
		scriptPath = os.path.dirname(__file__)
		print scriptPath 
		'''
		scriptPath  = repr(sys.argv[0])
		print scriptPath 
		print repr(__file__)
		print repr(os.getcwd())
		print os.path.dirname(__file__)
		'''
		conPath = os.path.join(scriptPath, 'controllers')
		print conPath 
		conFiles = [f.replace('.ma','') for f in os.listdir(conPath) if f.endswith('.ma')]
		iconFiles = [(conPath + '/' + f) for f in os.listdir(conPath) if f.endswith('.jpg')]
		return conFiles,iconFiles
		
	def bdMirrorCon(self):
		print 'Mirror Controller'
		mirrorType = self.mirrorRadioBtn.checkedId()
		
		
		selection = pm.ls(sl=True)
		if selection.count > 0:
			for sel in selection:
				if ('L_' in sel.name()) or ('R_' in sel.name()):
					conGrp = sel.getParent()
					conGrpPos = conGrp.getTranslation(space='world')
					conGrpRot = conGrp.getRotation(space='world')
					
					exp = ['L_','R_']
					if 'R_' in conGrp.name():
						exp.reverse()
					
					mirrorConGrp = ''
					if mirrorType == -2:
						mirrorConGrp = pm.duplicate(conGrp,name = conGrp.name().replace(exp[0],exp[1]))[0]
						scaleGrp = pm.group(mirrorConGrp)
						scaleGrp.setPivots([0,0,0])
						scaleGrp.scaleX.set(-1)
						
						pm.parent(mirrorConGrp,world=True)
						pm.makeIdentity(mirrorConGrp,apply=True,t=0,r=0,s=1)
						pm.delete(scaleGrp)
						mirrorConGrpRot = mirrorConGrp.getRotation(space='world')
						print mirrorConGrpRot 
						mirrorConGrp.setRotation([mirrorConGrpRot[0],-1 * mirrorConGrpRot[1],180 - abs(mirrorConGrpRot[2])])
						
					elif mirrorType == -3:
						mirrorConGrp = pm.duplicate(conGrp,name = conGrp.name().replace(exp[0],exp[1]))[0]
					
					mirrorConChildren = mirrorConGrp.getChildren(ad=True,type='transform')
					
					for child in mirrorConChildren :
						child.rename(child.name().replace(exp[0],exp[1]))
					
					if mirrorType == -3:
						mirrorConGrp.setTranslation([conGrpPos[0]*-1,conGrpPos[1],conGrpPos[2]])
					for child in mirrorConChildren :
						for shape in child.getChildren(type='shape'):
							shape.overrideEnabled.set(1)
							shape.overrideColor.set(self.conColors[exp[1]])
							targetShape = pm.ls(child.name().replace(exp[1],exp[0]) + '*',type='shape')[0]
							if mirrorType == -3:
								self.bdMirrorShape(shape,targetShape)
						
				else:
					pm.warning( 'Central controller, no need (sic) to mirror it!')
				
				                           
	def bdMirrorShape(self,shapeDest,shapeTarget):
		print 'Mirror shape'
		shapeDestCVs = shapeDest.cv
		shapeTargetCVs = shapeTarget.cv
		
		for i in range(len(shapeDestCVs)):
			targetCVPos = shapeTargetCVs[i].getPosition(space='world')
			shapeDestCVs[i].setPosition([targetCVPos[0] * -1 , targetCVPos[1] ,targetCVPos[2]] ,space='world')
			shapeDest.updateCurve()
			shapeTarget.updateCurve()
		
	def bdGetConName(self):
		animConName = str(self.inputConName.text())
		animConSide = str(self.inputConSide.currentText())
		
		if animConName:
			animConName = animConSide + animConName + '_ctrl'
		else:
			animConName = ''

		return animConName 
	
	def bdRotateCon(self,axis):
		selection = pm.ls(sl=True)
		conChild = ''
		if selection.count > 0:
			print selection[0].name()
			if 'GRP' in selection[0].name():
				pm.warning('Select the curves not the GRP')
			else:
				rotPivot = selection[0].getTranslation(space='world')
				for sel in selection:
					shapes = sel.getChildren()
					for shape in shapes:
						selCVs = shape.cv
						if axis == 'x':
							pm.rotate(selCVs,90,0,0,r=True,p=rotPivot,os=True,)
						elif axis == 'y':
							pm.rotate(selCVs,0,90,0,r=True,p=rotPivot,os=True,)	
						elif axis == 'z':
							pm.rotate(selCVs,0,0,90,r=True,p=rotPivot,os=True,)	
				
	
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

