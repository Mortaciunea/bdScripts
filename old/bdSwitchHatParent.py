import pymel.core as pm
import traceback

from PySide import QtCore
from PySide import QtGui

from shiboken import wrapInstance

import maya.cmds as cmds
import maya.OpenMayaUI as omui


def maya_main_window():
    '''
    Return the Maya main window widget as a Python object
    '''
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)


class SwitchParentUi(QtGui.QDialog):

    def __init__(self, parent=maya_main_window()):
        super(SwitchParentUi, self).__init__(parent)

    def create(self):
        '''
        Set up the UI prior to display
        '''

        self.setWindowTitle("Props Parent Switch")
        self.setWindowFlags(QtCore.Qt.Tool)

        self.create_controls()
        self.create_layout()
        self.create_connections()

    def create_controls(self):
        '''
        Create the widgets for the dialog
        '''
        self.headToL = QtGui.QPushButton("Hat -> Left Hand")
        self.headToR = QtGui.QPushButton("Hat -> Righ Hand")
        self.handToHead = QtGui.QPushButton("Hand -> Head")
        
        self.candyboxToL = QtGui.QPushButton("Candybox -> Left Hand")
        self.candyboxToR = QtGui.QPushButton("Candybox -> Righ Hand")
        self.candyboxToWorld = QtGui.QPushButton("Candybox -> World")
        
        self.candyboxLidToL = QtGui.QPushButton("Candybox Lid -> Left Hand")
        self.candyboxLidToR = QtGui.QPushButton("Candybox Lid -> Righ Hand")
        self.candyboxLidToBox = QtGui.QPushButton("Candybox Lid -> Candy Box")        


    def create_layout(self):
        '''
        Create the layouts and add widgets
        '''
        hatButLayout = QtGui.QVBoxLayout()
        hatButGrp = QtGui.QGroupBox("Hat")
        
        hatButLayout.setContentsMargins(2, 2, 2, 2)
        hatButLayout.addWidget(self.headToL)
        hatButLayout.addWidget(self.headToR)
        hatButLayout.addWidget(self.handToHead)  
        hatButGrp.setLayout(hatButLayout)
        
        candyLayout = QtGui.QVBoxLayout()
        candyGrp = QtGui.QGroupBox("Candy Box")
        
        candyLayout.setContentsMargins(2, 2, 2, 2)
        candyLayout.addWidget(self.candyboxToL)
        candyLayout.addWidget(self.candyboxToR)
        candyLayout.addWidget(self.candyboxToWorld) 
        
        candyLayout.addWidget(self.candyboxLidToL)
        candyLayout.addWidget(self.candyboxLidToR)
        candyLayout.addWidget(self.candyboxLidToBox) 
        
        candyGrp.setLayout(candyLayout)        
        
        main_layout = QtGui.QVBoxLayout()
        main_layout.setContentsMargins(6, 6, 6, 6)
        
        main_layout.addWidget(hatButGrp)
        main_layout.addWidget(candyGrp)



        main_layout.addStretch()

        self.setLayout(main_layout)

    def create_connections(self):
        '''
        Create the signal/slot connections
        '''
        self.headToL.clicked.connect(lambda: self.bdSwitchHatParent(2))
        self.headToR.clicked.connect(lambda: self.bdSwitchHatParent(1))
        self.handToHead.clicked.connect(lambda: self.bdSwitchHatParent(0))

        self.candyboxToL.clicked.connect(lambda: self.bdSwitchCBParent(2))
        self.candyboxToR.clicked.connect(lambda: self.bdSwitchCBParent(1))
        self.candyboxToWorld.clicked.connect(lambda: self.bdSwitchCBParent(0))

        self.candyboxLidToL.clicked.connect(lambda: self.bdSwitchCBLidParent(1))
        self.candyboxLidToR.clicked.connect(lambda: self.bdSwitchCBLidParent(2))
        self.candyboxLidToBox.clicked.connect(lambda: self.bdSwitchCBLidParent(0))
    #--------------------------------------------------------------------------
    # SLOTS
    #--------------------------------------------------------------------------
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

            elif newParent == 2:
                print 'Candybox new  parent: Right Hand'

                candyboxLidCtrl.attr('parent').set(2)

            elif newParent == 1:
                print 'Candybox new  parent: Left Hand'

                candyboxLidCtrl.attr('parent').set(1)

            candyboxLidCtrl.setTranslation(hatPos,space='world')
            candyboxLidCtrl.setRotation(hatRot,space='world')


            pm.setKeyframe(candyboxLidCtrl )



        else:
            pm.warning('Select candybox_lid_ctrl')
            
            
if __name__ == "__main__":
    # Development workaround for PySide winEvent error (in Maya 2014)
    # Make sure the UI is deleted before recreating
    try:
        test_ui.close()
    except:
        pass

    # Create minimal UI object
    test_ui = SwitchParentUi()

    # Delete the UI if errors occur to avoid causing winEvent
    # and event errors (in Maya 2014)
    try:
        test_ui.create()
        test_ui.show()
    except:
        test_ui.close()
        traceback.print_exc()


