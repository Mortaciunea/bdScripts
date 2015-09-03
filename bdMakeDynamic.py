import pymel.core as pm
import pymel.core.datatypes as dt

from PyQt4 import QtCore
from PyQt4 import QtGui

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

try:
	bdMakeDynamicUI_form,bdMakeDynamicUI_base = uic.loadUiType(uiFile)
except:
	print 'Could not find the UI file'
	
	
class bdMakeDynamic():
        def __init__(self, *args, **kargs):
                rootName = kargs.setdefault('start')
                self.hairSystem = kargs.setdefault('hairSystem')
                self.hairSystemUserName = kargs.setdefault('hairSystemName')                
                try:
                        self.rootObj = pm.ls(rootName,type='joint')[0]
                except:
                        pm.warning('select the root joint of the chain you want to convert')

                self.dynRootObj, self.dynCrv = self.bdCreateDynChain()
                self.fkRootObj = self.bdCreateFKChain()
                self.bdConnectDyn()

        def bdCreateFKChain(self):
                fkRootObj = pm.duplicate(self.rootObj)[0]
                fkRootObj.rename(self.rootObj.name() + '_FK')
                
                fkChain = fkRootObj.listRelatives(type='joint', ad=True, f=True)
                #fkChain.append(fkRootObj)
                fkChain.reverse()

                for jnt in fkChain:
                        jnt.rename(jnt.name() + '_FK')
                
                pm.skinCluster(fkRootObj,self.dynCrv)
                return fkRootObj
                
        def bdCreateDynChain(self):
                jntPosArray = []
                
                dynRootObj = pm.duplicate(self.rootObj)[0]
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

                return dynRootObj,drvCrv

        def bdConnectDyn(self):
                rootDesc = self.rootObj.listRelatives(type='joint', ad=True, f=True)
                rootDesc.append(self.rootObj)

                dynChainDesc = self.dynRootObj.listRelatives(type='joint', ad=True, f=True)
                dynChainDesc.append(self.dynRootObj)

                fkChainDesc = self.fkRootObj.listRelatives(type='joint', ad=True, f=True)
                fkChainDesc.append(self.fkRootObj)

                i=0 
                for jnt in dynChainDesc:
                        pm.parentConstraint(jnt,rootDesc[i],w=1)
                        i+=1

                i=0 
                for jnt in fkChainDesc:
                        pm.parentConstraint(jnt,rootDesc[i],w=0)
                        i+=1


class bdMakeDynamicUI(QtGui.QDialog):
        def __init__(self, parent=getMayaWindow()):
                super(bdMakeDynamicUI, self).__init__(parent)
                self.setWindowTitle("Make Dynamic Chain")
                self.setFixedSize(250, 80)

                self.create_layout()
                self.create_connections()



        def create_layout(self):
                hairSystemsLayout = QtGui.QHBoxLayout()
                hairSystemsLayout.setSpacing(2)
                hairSystemsLayout.setMargin(2)
                
                
                hairSystemNameLayout = QtGui.QHBoxLayout()
                hairNameLabel = QtGui.QLabel('Hair system name')
                self.hairSystemName = QtGui.QLineEdit()
                hairSystemNameLayout.addWidget(hairNameLabel)
                hairSystemNameLayout.addWidget(self.hairSystemName)
                
                textHair = QtGui.QLabel('Hair systems in scene')
                self.hairSystemsList = QtGui.QComboBox()
                self.bdPopulate_hairSystemsList()
                hairSystemsLayout.addWidget(textHair)
                hairSystemsLayout.addWidget(self.hairSystemsList)
                
                
                buttonLayout = QtGui.QHBoxLayout()
                buttonLayout.setSpacing(2)
                buttonLayout.setMargin(2)
               
                self.makeDynBtn = QtGui.QPushButton('Make Selected Dynamic')
                buttonLayout.addWidget(self.makeDynBtn)
                
                main_layout = QtGui.QVBoxLayout()
                main_layout.setSpacing(2)
                main_layout.setMargin(2)
                
                main_layout.addLayout(hairSystemNameLayout)
                main_layout.addLayout(hairSystemsLayout)
                main_layout.addLayout(buttonLayout)

                self.setLayout(main_layout)
        
        def create_connections(self):
                self.makeDynBtn.clicked.connect(self.bdMakeDynamic)
        
        def bdMakeDynamic(self):
                hairSystem = str(self.hairSystemsList.currentText())
                hairSystemName = str(self.hairSystemName.text())
                if hairSystem == "New":
                        hairSystem = ''
                else:
                        hairSystem = hairSystem.replace('Shape','')
                
                selection = pm.ls(sl = True)
                if len(selection) <> 1:
                        pm.warning('Select the root joint')
                else:
                        dynFk = bdMakeDynamic(start=selection[0],hairSystem = hairSystem, hairSystemName = hairSystemName)
                
                self.bdPopulate_hairSystemsList()
                
                
        def bdPopulate_hairSystemsList(self):
                self.hairSystemsList.clear()
                hairSystems = pm.ls(type='hairSystem')
                self.hairSystemsList.addItem('New')
                for hs in hairSystems:
                        self.hairSystemsList.addItem(hs.name())
                        

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