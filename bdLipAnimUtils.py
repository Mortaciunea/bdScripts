import pymel.core as pm
import pymel.core.datatypes as dt
import re,os
import maya.OpenMaya as OM

import logging
import maya.OpenMayaUI as mui
import maya.OpenMaya as om
import sip,os, shiboken
import PySide.QtGui as QtGui
import PySide.QtCore as QtCore

import pyside_util
reload(pyside_util)



# #####################
TOOLS_PATH = os.path.dirname( __file__ )
WINDOW_TITLE = 'Lip Anim Tools'
WINDOW_VERTION = 1.0
WINDOW_NAME = 'bdLipAnimUtilWin'
# ###################

UI_FILE_PATH = os.path.join( TOOLS_PATH, 'UI/bdLipAnimUtils.ui' )
UI_OBJECT, BASE_CLASS = pyside_util.get_pyside_class( UI_FILE_PATH )


pysideLoggers = ['pysideuic.properties','pysideuic.uiparser']
for log in pysideLoggers:
    logger = logging.getLogger(log)
    logger.setLevel(logging.ERROR)

def widgetPath(windowName, widgetNames):
    """
    @param windowName: Window instance name to search
    @param widgetNames: list of names to search for
    taken from http://www.chris-g.net/2011/06/24/maya-qt-interfaces-in-a-class/
    """

    returnDict = {}
    mayaWidgetList = pm.lsUI(dumpWidgets=True)

    for widget in widgetNames:
        for mayaWidget in mayaWidgetList:
            if windowName in mayaWidget:
                if mayaWidget.endswith(widget):
                    returnDict[widget] = mayaWidget

    return returnDict


def removeNamespace():
    sceneNS = pm.namespaceInfo(lon=True,r=True)
    importNS = []
    mayaNS = set([u'UI', u'shared'])
    for ns in sceneNS:
        if ns not in mayaNS:
            importNS.append(ns)
    importNS.reverse()

    for ns in importNS:
        pm.namespace( rm = ns,mergeNamespaceWithRoot=True)

class LipAnimSliderUI(QtGui.QWidget):
    def __init__( self, parent=None,*args,**kargs):
        super(LipAnimSliderUI, self).__init__(parent)
        self.labelName = kargs.setdefault('name','')
        self.blendshapes = kargs.setdefault('blendshapes',[])
        
        horLayout = QtGui.QHBoxLayout()
        sld = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        sld.setSingleStep(100)
        sld.valueChanged.connect(self.bdSliderValueChanged)
        label = QtGui.QLabel(self.labelName)

        horLayout.addWidget(label)
        horLayout.addWidget(sld)
        self.setLayout(horLayout)
        
    def bdSliderValueChanged(self,value):
        for bs in self.blendshapes:
            pm.setAttr('%s.%s'%(bs.name(),self.labelName),value/100.0)
        
    def bdSliderSetZero(self):
        for bs in self.blendshapes:
            pm.setAttr('%s.%s'%(bs.name(),self.labelName),0)

        
class LipAnimUI(BASE_CLASS, UI_OBJECT):
    def __init__( self, parent = pyside_util.get_maya_window(), *args ):

        super( LipAnimUI, self ).__init__( parent )
        self.path = ''
        self.lipAnimBlendshapes = []
        self.sliders = []

        self.setupUi( self )
        self.setWindowTitle( '{0} {1}'.format( WINDOW_TITLE, str( WINDOW_VERTION ) ) )

        self.bdPopulateMeshes()
        self.bdAddSliders()
        self.show()

    def closeEvent(self, event):
        for slider in self.sliders:
            slider.bdSliderSetZero()
            
        event.accept()

    def bdAddSliders(self):
        if len(self.lipAnimBlendshapes) > 0:
            aliases =  [alias[0] for alias in self.lipAnimBlendshapes[0].listAliases() if 'lip_anim' in alias[0]]
            newAliases = []
            for al in aliases:
                newAliases.append(int(al.split('_')[-2]))
            
            newAliases = sorted(newAliases)
            aliases = [('lip_anim_blend_' + str(index) + '_') for index in newAliases]
                
            
            if len(aliases) > 0:
                for al in aliases:
                    newSlider = LipAnimSliderUI(name=al,blendshapes = self.lipAnimBlendshapes)
                    self.sliders.append(newSlider)
                    self.slidersLayout.addWidget(newSlider)



    def bdSetLipAnimTarget(self,index,value):
        sceneBs = pm.ls(type='blendShape')
        print sceneBs
        for bs in sceneBs:
            aliases = sorted([alias[0] for alias in bs.listAliases()])
            if 'lip_anim_blend_0_' in aliases:
                pm.setAttr('%s.lip_anim_blend_%s_'%(bs,str(index)),value)

    def bdPopulateMeshes(self):
        sceneBs = pm.ls(type='blendShape')
        for bs in sceneBs:
            aliases = sorted([alias[0] for alias in bs.listAliases()])
            if 'lip_anim_blend_0_' in aliases:
                self.lipAnimBlendshapes.append(bs)

        for item in self.lipAnimBlendshapes:
            self.lipAnimMeshes_listWidget.addItem(item.name())





def bdSetLipAnimTarget(index,value):
    sceneBs = pm.ls(type='blendShape')
    print sceneBs
    for bs in sceneBs:
        aliases = sorted([alias[0] for alias in bs.listAliases()])
        if 'lip_anim_blend_0_' in aliases:
            pm.setAttr('%s.lip_anim_blend_%s_'%(bs,str(index)),value)

def bdMain():
    UI_FILE_PATH = os.path.join( TOOLS_PATH, 'UI/bdLipAnimUtils.ui' )
    UI_OBJECT, BASE_CLASS = pyside_util.get_pyside_class( UI_FILE_PATH )

    if pm.window( WINDOW_NAME, exists = True, q = True ):
        pm.deleteUI( WINDOW_NAME )

    LipAnimUI()

bdMain()