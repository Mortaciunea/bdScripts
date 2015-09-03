import maya.cmds as cmds
import functools
import maya.mel as mm


class bdAutoRigUI(object):
    use = None
    @classmethod
    def showUI(cls,uiFile):
        win = cls(uiFile)
        win.create()
        return win
        
    def __init__(self,uiPath):
        bdAutoRigUI.use =self
        self.window = 'bdARMainWindow'
        self.charName = 'inputCharName'
        self.uiFile = uiPath
    def create(self,verbose = False):
        if cmds.window(self.window,exists=True):
            cmds.deleteUI(self.window)
        self.window = cmds.loadUI(f=self.uiFile,verbose=verbose)
        cmds.showWindow(self.window)

    def bdCreateGuides(self,*args):
        charNameCtrlPath = '|'.join([self.window,'centralwidget',self.charName])
    	#charName = cmds.textFieldGrp(charNameCtrlPath,q=True,tx=True)
    	print charNameCtrlPath

    
def bdARMain():
    win = bdAutoRigUI('bdAutoRigUI.ui')
    win.create(verbose=True)
    

bdARMain()
