import pymel.core as pm
import pymel.core.datatypes as dt

from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4 import uic

import logging
import maya.OpenMayaUI as mui
import maya.OpenMaya as om
import sip,os

pyqtLoggers = ['PyQt4.uic.properties','PyQt4.uic.uiparser']
for log in pyqtLoggers:
	logger = logging.getLogger(log)
	logger.setLevel(logging.ERROR)

def getMayaWindow():
	ptr = mui.MQtUtil.mainWindow()
	return sip.wrapinstance(long(ptr),QtCore.QObject)

uiFile = os.path.join(os.path.dirname(__file__), 'bdMakeDynamicUI.ui')

print uiFile

try:
	bdMakeDynamicUI_form,bdMakeDynamicUI_base = uic.loadUiType(uiFile)
except:
	print 'Could not find the UI file'


class bdMakeDynamic():
	fkCtrlTop = ''
	rootObj = ''
	dynRootObj = ''
	dynCrv = ''
	fkRootObj = ''
	
	def __init__(self, *args, **kargs):
		rootName = kargs.setdefault('start')
		self.hairSystem = kargs.setdefault('hairSystem')
		self.hairSystemUserName = kargs.setdefault('hairSystemName')                
		try:
			self.rootObj = pm.ls(rootName,type='joint')[0]
		except:
			pm.warning('select the root joint of the chain you want to convert')

		#self.dynRootObj, self.dynCrv = self.bdCreateDynChain()
		#self.fkRootObj = self.bdCreateFKChain()
		#self.bdConnectDyn()


	def bdCreateFKChain(self):
		fkRootObj = pm.duplicate(self.rootObj)[0]
		try:
			pm.parent(fkRootObj,w=True)
		except:
			pass
		
		fkRootObj.rename(self.rootObj.name() + '_FK')

		fkChain = fkRootObj.listRelatives(type='joint', ad=True, f=True)
		#fkChain.append(fkRootObj)
		fkChain.reverse()

		for jnt in fkChain:
			jnt.rename(jnt.name() + '_FK')

		pm.skinCluster(fkRootObj,self.dynCrv)
		self.fkRootObj = fkRootObj
		
		#return fkRootObj

	def bdCreateDynChain(self):
		jntPosArray = []

		dynRootObj = pm.duplicate(self.rootObj)[0]
		try:
			pm.parent(dynRootObj,w=True)
		except:
			pass
		
		dynRootObj.rename(self.rootObj.name() + '_DYN')
		jntPos = dynRootObj.getTranslation(space='world')
		jntPosArray.append(jntPos)

		dynChain = dynRootObj.listRelatives(type='joint', ad=True, f=True)
		#dynChain.append(dynRootObj)

		dynChain.reverse()

		for jnt in dynChain:
			jnt.rename(jnt.name() + '_DYN')
			jntPos = jnt.getTranslation(space='world')
			jntPosArray.append(jntPos)

		drvCrv = pm.curve(d=1,p=jntPosArray,k=[i for i in range(len(jntPosArray))])
		drvCrv.rename(self.rootObj.name() + '_CRV')
		drvCrvShape = drvCrv.getShape()
		print drvCrvShape.name()
		pm.select(drvCrv)

		#sceneHairSystems = pm.ls(type = 'hairSystem')
		if self.hairSystem == '':
			if self.hairSystemUserName == '':
				self.hairSystemUserName = self.rootObj.name()

			pm.mel.eval( 'makeCurvesDynamicHairs 1 0 1;' )
			# get the follicle + dyn curve + hair system
			try:
				flcShape = pm.listConnections('%s.worldSpace' % drvCrvShape, s=False )[0]
				flcShape.pointLock.set(1)
				flcShape.restPose.set(1)
				flcShape.rename(self.rootObj.name() + '_FLC')
				print flcShape.name()
			except:
				pm.warning('couldnt find follicle ' )

			try:
				outCurveShape = pm.listConnections('%s.outCurve' % flcShape , s = False) [0]
				outCurveShape.rename(self.rootObj.name() + '_DYN_CRV')
				print outCurveShape.name()
			except:
				pm.warning('couldnt find out curve ' )

			try:
				hairSystem = pm.listConnections('%s.outHair' % flcShape , s = False) [0]
				hairSystem.rename(self.hairSystemUserName + '_hairSystem')
				print hairSystem.name()
			except:
				pm.warning('couldnt find hairsystem ' )

			flcParent = flcShape.getParent()
			print flcParent.name()
			flcParent.rename(hairSystem.name() + 'Follicles') 

			outCurveParent = outCurveShape.getParent()
			outCurveParent.rename(hairSystem.name() + 'OutputCurves')
		else:
			assignHair = pm.ls(self.hairSystem)[0]

			pm.mel.eval( 'assignHairSystem %s' % assignHair )
			try:
				flcShape = pm.listConnections('%s.worldSpace' % drvCrvShape, s=False )[0]
				flcShape.pointLock.set(1)
				flcShape.restPose.set(1)
				flcShape.rename(self.rootObj.name() + '_FLC')
				print flcShape.name()
			except:
				pm.warning('couldnt find follicle ' )

			try:
				outCurveShape = pm.listConnections('%s.outCurve' % flcShape , s = False) [0]
				outCurveShape.rename(self.rootObj.name() + '_DYN_CRV')
				print outCurveShape.name()
			except:
				pm.warning('couldnt find out curve ' )            

		dynChainIkHandle = pm.ikHandle(sol='ikSplineSolver', sj=dynRootObj, ee=dynChain[-1],c=outCurveShape, ccv=False, roc =  False, pcv = False)[0]
		dynChainIkHandle.rename(self.rootObj.name() + '_ikHandle')
		self.dynCrv = drvCrv
		self.dynRootObj = dynRootObj
		#return dynRootObj,drvCrv

	def bdConnectDyn(self,driver,influence):
		rootDesc = self.rootObj.listRelatives(type='joint', ad=True, f=True)
		rootDesc.append(self.rootObj)
		if driver == 'dyn':
			dynChainDesc = self.dynRootObj.listRelatives(type='joint', ad=True, f=True)
			dynChainDesc.append(self.dynRootObj)

			i=0 
			for jnt in dynChainDesc:
				pm.parentConstraint(jnt,rootDesc[i],w=influence,mo=1)
				i+=1			
		elif driver == 'fk':
			fkChainDesc = self.fkRootObj.listRelatives(type='joint', ad=True, f=True)
			fkChainDesc.append(self.fkRootObj)

			i=0 
			for jnt in fkChainDesc:
				pm.parentConstraint(jnt,rootDesc[i],w=0,mo=1)
				i+=1

	
	def bdAddFkCtrls(self, ctrl):
		ctrlGrpAll = []
		
		tempCtrl = ctrl.duplicate()[0]
		ctrlGrp = self.bdSetUpCtrl(ctrl,self.fkRootObj)
		ctrlGrpAll.append(ctrlGrp)
		pm.addAttr(ctrl, ln = "dynamic", at = 'double', min = 0, max = 1 , dv = 0)
		ctrl.attr('dynamic').setKeyable(True)
		ctrl.overrideEnabled.set(1)
		ctrl.overrideColor.set(6)

		self.fkCtrlTop = ctrl
		
		fkChainDesc = self.fkRootObj.listRelatives(type='joint', ad=True, f=True)
		fkChainDesc.reverse()

		for jnt in fkChainDesc[:-1]:
			newCtrl = tempCtrl.duplicate()[0]
			newCtrl.overrideEnabled.set(1)
			newCtrl.overrideColor.set(6)
			ctrlGrp = self.bdSetUpCtrl(newCtrl, jnt)
			ctrlGrpAll.append(ctrlGrp)
		
		print range(len(ctrlGrpAll))
		
		for i in range(len(ctrlGrpAll)-1,0,-1):
			pm.parent(ctrlGrpAll[i],ctrlGrpAll[i-1].getChildren()[0])
			
		pm.delete([tempCtrl])
		self.bdCreateFkDynSwitch()

	def bdCreateFkDynSwitch(self):
		parentCnstrAll = self.rootObj.listRelatives(type='parentConstraint', ad=True, f=True)
		reverseNode = pm.createNode('reverse',n=self.rootObj.name() + '_DYN_REV')
		self.fkCtrlTop.attr('dynamic').connect(reverseNode.inputX)
		
		
		for cnstr  in parentCnstrAll:
			dynAttrW = pm.listAttr(cnstr, st='anim*DYN*')[0]
			fkAttrW = pm.listAttr(cnstr, st='anim*FK*')[0]
			self.fkCtrlTop.attr('dynamic').connect(cnstr.attr(dynAttrW))
			reverseNode.outputX.connect(cnstr.attr(fkAttrW))


	def bdSetUpCtrl(self,ctrl,jnt):
		ctrl.rename(jnt.name().replace('FK','CTRL'))
		ctrlGrp = pm.group([ctrl])
		ctrl.setTranslation([0,0,0],space='object')
		ctrl.setRotation([0,0,0],space='object')
		ctrlGrp.rename(ctrl.name() + '_GRP')
		ctrlGrp.centerPivots()
		
		tempConstraint = pm.parentConstraint(jnt,ctrlGrp)
		pm.delete(tempConstraint)
		
		pm.parentConstraint(ctrl,jnt,mo =True)
		
		return ctrlGrp




class bdMakeDynamicUI(bdMakeDynamicUI_form,bdMakeDynamicUI_base):
	
	dynFk = ''
	def __init__(self, parent=getMayaWindow()):
		super(bdMakeDynamicUI, self).__init__(parent)


		self.create_layout()
		self.create_connections()



	def create_layout(self):
		self.setupUi(self)
		self.bdPopulate_hairSystemsList()


	def create_connections(self):
		self.addDynChainBtn.clicked.connect(self.bdAddDynamicChain)
		#self.addFkChainBtn.clicked.connect(self.bdAddFkChain)
		self.pickCtrlBtn.clicked.connect(self.bdPickFkCtrl)
		self.addFkCtrlBtn.clicked.connect(self.bdAddFkCtrl)

	def bdAddDynamicChain(self):
		hairSystem = str(self.hairSystemsList.currentText())
		hairSystemName = str(self.hairSystemName.text())
		if hairSystem == "New":
			hairSystem = ''
		else:
			hairSystem = hairSystem.replace('Shape','')
			hairSystemName = hairSystem.replace('_hairSystemShape','')
			print hairSystemName 

		selection = pm.ls(sl = True)
		if len(selection) <> 1:
			pm.warning('Select the root joint')
		else:
			self.dynFk = bdMakeDynamic(start=selection[0],hairSystem = hairSystem, hairSystemName = hairSystemName)
			self.dynFk.bdCreateDynChain()
			self.dynFk.bdConnectDyn('dyn', 1)

		self.bdPopulate_hairSystemsList()


	def bdPopulate_hairSystemsList(self):
		self.hairSystemsList.clear()
		hairSystems = pm.ls(type='hairSystem')
		self.hairSystemsList.addItem('New')
		for hs in hairSystems:
			self.hairSystemsList.addItem(hs.name())

	def bdPickFkCtrl(self):
		selection = pm.ls(sl=True,type='transform')
		
		if selection:
			fkCtrl = selection[0]
		
		self.fkCtrlName.setText(fkCtrl.name())

	def bdAddFkChain(self):
		self.dynFk.bdCreateFKChain()
		self.dynFk.bdConnectDyn('fk', 0)

	def bdAddFkCtrl(self):
		fkCtrl = str(self.fkCtrlName.text())
		fkCtrlObj = pm.ls(fkCtrl)[0]
		self.dynFk.bdAddFkCtrls(fkCtrlObj)


def bdMain():
	global bdMakeDynamicWin

	try:
		bdMakeDynamicWin.close()
	except:
		print 'No prev window, opening one'
		pass

	bdMakeDynamicWin = bdMakeDynamicUI()
	bdMakeDynamicWin.show()

bdMain()