import maya.cmds as cmds

def createAnimRanges(*argv):
    animRangesLoc = cmds.spaceLocator(n='AnimRanges')


def addAnimRange(*argv):
    animRanges = cmds.ls('AnimRanges')
    if len(animRanges) > 0:
        animRangeName = cmds.textFieldGrp('animRangeName', q=True, text=True )
        animRange = cmds.textFieldGrp('animRange', q=True, text=True )
        cmds.textFieldGrp(p='arMainCL', label = animRangeName, text=animRange )
        cmds.addAttr(animRanges[0],ln = animRangeName,dt="string" )
        cmds.setAttr((animRanges[0]+'.'+ animRangeName),animRange,type="string" )
    else:
        print 'There is no Anim Range'   
	
def animRangesUI():
	pathWin = 'animRangeUI'
	if cmds.window(pathWin,exists=True):
		cmds.deleteUI(pathWin)
	cmds.window(pathWin,title='Animation Ranges')
	
	cmds.columnLayout('arMainCL',adj=True,co=('both',10))
	cmds.button(label = 'Create Anim Ranges',c=createAnimRanges)
	cmds.textFieldGrp('animRangeName', label='Sequence Name' )
	cmds.textFieldGrp('animRange', label='Start-End' )
	cmds.button(label = 'Add Anim Range',c=addAnimRange)
	cmds.separator(height=10, style='double' )
	
	cmds.showWindow(pathWin )


	
animRangesUI()