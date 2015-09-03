#############
# Creating Camera Path Utils
#############



import maya.cmds as cmds

def createPathNode(*arg):
	pathNode = cmds.spaceLocator(n='pathNode')
	selPos = cmds.xform('walkCamera', q=True,a=True,t=True)
	cmds.xform(pathNode,ws=True,t=selPos)
	cmds.scale(20,20,20,pathNode)

def createPathCurve(*arg):
	pathNodes = cmds.ls('pathNode*',type='transform')
	print pathNodes
	pathCurve = 'pathCurve'
	i=0
	for node in pathNodes:
		if i==0:
			nodePos = cmds.xform(node, q=True,a=True,t=True)
			pathCurve = cmds.curve(n=pathCurve,p=[nodePos])
			i+=1
		else:
			nodePos = cmds.xform(node, q=True,a=True,t=True)
			cmds.curve(pathCurve,a=True,p=[nodePos])


def connectToPath(*arg):
	selected = cmds.ls(sl=True)
			

def createSwimCycle(*argv):
	fromTo = cmds.textFieldGrp('cycleFromTo',q=True,text=True)
	startCycle,endCycle = fromTo.split('-')
	lengthCycle = cmds.textFieldGrp('cycleLength',q=True,text=True)
	amplitude = int(cmds.textFieldGrp('amplitude',q=True,text=True))
	
	numberOfCycles = (int(endCycle)-int(startCycle))/int(lengthCycle)
	 
	for i in range(0,numberOfCycles+1,1):
		frame = int(startCycle)+i*int(lengthCycle )
		cmds.setKeyframe("*:Head_Anim.rotateY",t=frame,value=amplitude)
		cmds.setKeyframe("*:Head_Anim.rotateY",t=frame+int(lengthCycle)*0.5,value=(-1)*amplitude)
		
		cmds.setKeyframe("*:Body_Anim.rotateY",t=frame,value=(-1)*amplitude   )
		cmds.setKeyframe("*:Body_Anim.rotateY",t=frame+int(lengthCycle)*0.5,value=amplitude)

def createPathLocators(*argv):
    counter = ''
    if len(cmds.ls('pathLocator?',type='transform')) > 0:
        counter = len(cmds.ls('pathLocator?',type='transform'))+1
        print counter
    oPathLoc = cmds.spaceLocator(n='pathLocator'+str(counter))
    oStopLoc = cmds.spaceLocator(n='stopLocator'+str(counter))
    oPathLocGrp = cmds.group(oPathLoc,n='pathLocatorGrp'+str(counter))
    oStopGrp = cmds.group(oStopLoc,n='stopLocatorGrp'+str(counter))
    counter = ''
    if len(cmds.ls('pathCurve?',l=True)) > 0:
        counter = len(cmds.ls('pathCurve?',l=True))
    cmds.pathAnimation( oPathLocGrp, stu=0, etu=1000, fa='x', ua='y', bank=True, fm = True,c=('pathCurve' + str(counter)) )
    cmds.parentConstraint(oPathLoc,oStopLoc,cmds.ls('*:Master_Anim')[0])
    cmds.setAttr(cmds.ls('Master_Anim_parentConstraint*',l=True)[0] + '.stopLocatorW1',0)
    


	
def pathCreatorUI():
	pathWin = 'pathWinUI'
	if cmds.window(pathWin,exists=True):
		cmds.deleteUI(pathWin)
	cmds.window(pathWin,title='Create Path')
	
	cmds.columnLayout(adj=True,co=('both',10))
	cmds.button(label = 'Create Path Node',c=createPathNode)
	cmds.separator(height=10, style='double' )
	cmds.button(label = 'Create Path',c=createPathCurve)
	cmds.separator(height=10, style='double' )
	cmds.button(label = 'Create path locators',c=createPathLocators)
	cmds.separator(height=10, style='double' )
	cmds.textFieldGrp('cycleFromTo', label='From - To' )
	cmds.textFieldGrp('cycleLength', label='Length in frames',text = '30' )
	cmds.textFieldGrp('amplitude',l='Amplitude', text='40')
	cmds.button(label = 'Create Swim Cycle',c=createSwimCycle)

	
	cmds.showWindow(pathWin )

	
pathCreatorUI()
