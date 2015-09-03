import pymel.core as pm
import traceback,os, logging

from PySide import QtCore
from PySide import QtGui

from shiboken import wrapInstance

import maya.cmds as cmds
import maya.OpenMayaUI as omui

import pyside_util
reload(pyside_util)



# #####################
TOOLS_PATH = os.path.dirname( __file__ )
WINDOW_TITLE = 'Parent Switch'
WINDOW_VERSION = 1.0
WINDOW_NAME = 'bdSwitchParentWin'
# ###################
UI_FILE_PATH = os.path.join( TOOLS_PATH, 'UI/bdSwitchPropsParentUI.ui' )
UI_OBJECT, BASE_CLASS = pyside_util.get_pyside_class( UI_FILE_PATH )


pysideLoggers = ['pysideuic.properties','pysideuic.uiparser']
for log in pysideLoggers:
    logger = logging.getLogger(log)
    logger.setLevel(logging.ERROR)

def maya_main_window():
    '''
    Return the Maya main window widget as a Python object
    '''
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)


class SwitchParentUi(BASE_CLASS, UI_OBJECT):
    def __init__(self, parent=maya_main_window()):
        super(SwitchParentUi, self).__init__(parent)
        self.setupUi( self )
        self.setWindowTitle( '{0} {1}'.format( WINDOW_TITLE, str( WINDOW_VERSION ) ) )

        self.headToL.clicked.connect(lambda: self.bdSwitchHatParent(2))
        self.headToR.clicked.connect(lambda: self.bdSwitchHatParent(1))
        self.handToHead.clicked.connect(lambda: self.bdSwitchHatParent(0))

        self.candyboxToL.clicked.connect(lambda: self.bdSwitchCBParent(2))
        self.candyboxToR.clicked.connect(lambda: self.bdSwitchCBParent(1))
        self.candyboxToWorld.clicked.connect(lambda: self.bdSwitchCBParent(0))

        self.candyboxLidToL.clicked.connect(lambda: self.bdSwitchCBLidParent(2))
        self.candyboxLidToR.clicked.connect(lambda: self.bdSwitchCBLidParent(1))
        self.candyboxLidToBox.clicked.connect(lambda: self.bdSwitchCBLidParent(0))
        
        self.show()

    def bdSwitchHatParent(self,newParent):
        selection = pm.ls(sl=1,type='transform')
        if selection:
            pass
        else:
            pm.warning('Nothing selected !!!')
            return
        if 'hat' in selection[0].name():
            hatCtrl = selection[0]
            try:
                currentParent = hatCtrl.attr('parent').get()
            except:
                pm.warning('Current selection has no Parent attribute, aborting!')
                return
            print currentParent 
            switchFrame = pm.currentTime(q=1)


            pm.currentTime(switchFrame-1,e=1)
            pm.setKeyframe(hatCtrl)
            pm.currentTime(switchFrame,e=1)

            hatPos = hatCtrl.getTranslation(space='world')
            hatRot = hatCtrl.getRotation(space='world')


            #World Parent
            if newParent == 0:
                print 'Hat new parent: Head'
                hatCtrl.attr('parent').set(0)

            elif newParent == 1:
                print 'Hat new  parent: Right Hand'

                hatCtrl.attr('parent').set(1)

            elif newParent == 2:
                print 'Hat new  parent: Left Hand'

                hatCtrl.attr('parent').set(2)

            hatCtrl.setTranslation(hatPos,space='world')
            hatCtrl.setRotation(hatRot,space='world')


            pm.setKeyframe(hatCtrl )



        else:
            pm.warning('Select hat_ctrl')


    def bdSwitchCBParent(self,newParent):
        selection = pm.ls(sl=1,type='transform')
        if selection:
            pass
        else:
            pm.warning('Nothing selected !!!')
            return
        if 'candybox_ctrl' in selection[0].name():
            candyboxCtrl = selection[0]
            try:
                currentParent = candyboxCtrl.attr('parent').get()
            except:
                pm.warning('Current selection has no Parent attribute, aborting!')
                return
            print currentParent 
            switchFrame = pm.currentTime(q=1)


            pm.currentTime(switchFrame-1,e=1)
            pm.setKeyframe(candyboxCtrl)
            pm.currentTime(switchFrame,e=1)

            hatPos = candyboxCtrl.getTranslation(space='world')
            hatRot = candyboxCtrl.getRotation(space='world')


            #World Parent
            if newParent == 0:
                print 'Candybox new parent: World'
                candyboxCtrl.attr('parent').set(0)

            elif newParent == 2:
                print 'Candybox new  parent: Right Hand'

                candyboxCtrl.attr('parent').set(2)

            elif newParent == 1:
                print 'Candybox new  parent: Left Hand'

                candyboxCtrl.attr('parent').set(1)

            candyboxCtrl.setTranslation(hatPos,space='world')
            candyboxCtrl.setRotation(hatRot,space='world')


            pm.setKeyframe(candyboxCtrl )



        else:
            pm.warning('Select candybox_ctrl')

    def bdSwitchCBLidParent(self,newParent):
        selection = pm.ls(sl=1,type='transform')
        if selection:
            pass
        else:
            pm.warning('Nothing selected !!!')
            return
        if 'candybox_lid' in selection[0].name():
            candyboxLidCtrl = selection[0]
            try:
                currentParent = candyboxLidCtrl.attr('parent').get()
            except:
                pm.warning('Current selection has no Parent attribute, aborting!')
                return
            print currentParent 
            switchFrame = pm.currentTime(q=1)


            pm.currentTime(switchFrame-1,e=1)
            pm.setKeyframe(candyboxLidCtrl)
            pm.currentTime(switchFrame,e=1)

            hatPos = candyboxLidCtrl.getTranslation(space='world')
            hatRot = candyboxLidCtrl.getRotation(space='world')


            #World Parent
            if newParent == 0:
                print 'Candybox new parent: Candybox'
                candyboxLidCtrl.attr('parent').set(0)

            elif newParent == 1:
                print 'Candybox new  parent: Right Hand'

                candyboxLidCtrl.attr('parent').set(1)

            elif newParent == 2:
                print 'Candybox new  parent: Left Hand'

                candyboxLidCtrl.attr('parent').set(2)

            candyboxLidCtrl.setTranslation(hatPos,space='world')
            candyboxLidCtrl.setRotation(hatRot,space='world')


            pm.setKeyframe(candyboxLidCtrl )



        else:
            pm.warning('Select candybox_lid_ctrl')


def bdMain():
    UI_FILE_PATH = os.path.join( TOOLS_PATH, 'UI/bdSwitchPropsParentUI.ui' )
    UI_OBJECT, BASE_CLASS = pyside_util.get_pyside_class( UI_FILE_PATH )

    if pm.window( WINDOW_NAME, exists = True, q = True ):
        pm.deleteUI( WINDOW_NAME )

    SwitchParentUi()