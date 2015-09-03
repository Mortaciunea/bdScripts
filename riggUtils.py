import maya.cmds as mc
import functools
import maya.mel as mm

def ruJointRadius(args):
    rootJoint = mc.ls(sl=True, type='transform')
    radius = mc.floatSliderGrp('ruJointRadius',q=True, v=True)
    ruModifyRadius(str(rootJoint[0]),radius)
    

def ruModifyRadius(jointName,radius):
    mc.setAttr(jointName + '.radius', radius)
    children = mc.listRelatives(jointName, children=True, type='transform', fullPath=True)
    if children:
        for child in children:
            ruModifyRadius(child,radius)

def ruCreateLocator(args):
    selection = mc.ls(sl=True)
    vertices = mc.polyListComponentConversion(selection,tv=True)
    verticesPos =  mc.xform(q=True, ws=True, translation=True ) 

    temp = []
    for i in range(0,len(verticesPos),3):
        temp.append((verticesPos[i],verticesPos[i+1],verticesPos[i+2]))

    tempFace = mc.polyCreateFacet(p=temp)
    mc.xform(cp=True)
    tempFacePivotPos = mc.xform(q=True, ws=True, rp = True)
    nameLoc = mc.spaceLocator(name="jointHolder",position=(tempFacePivotPos[0],tempFacePivotPos[1],tempFacePivotPos[2]))
    mc.xform(nameLoc, cp = True)
    mc.delete(tempFace)
    mc.select(clear=True)
    
def ruCreateJointLocator(args):
    jointLocators = mc.ls('jointHolder*',type='transform')

    jointStartPos = mc.xform(jointLocators[0],q=True,  ws = True, rp=True)
    parentJointName = mc.joint(p = jointStartPos)

    for i in range(1,len(jointLocators),1):
        jointLocatorPos = mc.xform(jointLocators[i],q=True,  ws = True, rp=True)
        tempName = mc.joint(p = jointLocatorPos)
        mc.joint(parentJointName,e=True,zso=True,oj='zxy',sao='yup',al=True)
        parentJointName=tempName
    
def ruOrientJoint(args):
    print "Bla"    


def ruRenameFinger(rootChain,newnametemplate,finger,indexNumber):
    children =  mc.listRelatives(rootChain, children=True, type='transform')
    newName = newnametemplate + '_' + finger + '_0' + str(indexNumber)
    mc.rename(rootChain,newName)
    print newName
    if children:
        for child in children:
            indexNumber += 1
            ruRenameFinger(child,'j_Finger',finger,indexNumber)


def ruRenameFingerChain(args):
    root = mc.ls(sl=True, type='transform')
    ruRenameFinger(str(root[0]),'j_Finger','Pinky',0)

def ruMainWindow():
	ruWin = "riggUtils"
	if mc.window(ruWin,q=True,ex=True):
		mc.deleteUI(ruWin)

	mc.window(ruWin,title = "Rigging Utilities")
	mc.scrollLayout(horizontalScrollBarThickness=16)
	ruMainColumn = mc.columnLayout(columnAttach=("both",5),rowSpacing=10,columnWidth=320)
	mc.frameLayout(label="General",bs="etchedOut",w=300,mw=5,cll=1)
	mc.button(label='Show Axis',command='mc.toggle(state=True, localAxis=True)')
	mc.button(label='Hide Axis',command='mc.toggle(state=False, localAxis=True)')
		
	mc.frameLayout(label="Non T-Pose joint placer",bs="etchedOut",w=300,mw=5,cll=1,p=ruMainColumn)
	mc.columnLayout(rs=5,adj=1)
	mc.button(l="Create Helper Locator",c =ruCreateLocator)
	mc.button(l="Create Joint on Helper Locator",c =ruCreateJointLocator)
	mc.floatSliderGrp("ruJointRadius",en=1,label="Joint Radius",field=True,minValue=0,maxValue=5,fieldMinValue=0,fieldMaxValue=5,value=0.5,cw3=(70,30,10),dc=ruJointRadius)
	
	mc.frameLayout(label="Fingers Utils",bs="etchedOut",w=300,mw=5,cll=1,p=ruMainColumn)
	mc.columnLayout(rs=5,adj=1)
	mc.floatSliderGrp("ruJointOrientation",en=1,label="Finger Orient",field=True,minValue=0,maxValue=5,fieldMinValue=0,fieldMaxValue=5,value=0.5,cw3=(70,30,10),dc=ruOrientJoint)
	mc.frameLayout(label="Finger Renaming",bs="etchedOut",w=300,mw=5,cll=1)
	mc.optionMenu('ruFinger',l='Choose finger')
	mc.menuItem(l='Thumb')
	mc.menuItem(l='Index')
	mc.menuItem(l='Middle')
	mc.menuItem(l='Ring')
	mc.menuItem(l='Pinky')
	mc.textFieldButtonGrp( label='Template string', text='', buttonLabel='Rename', bc=ruRenameFinger, cw3=[120,70,70],ct3=['left','left','left'],co3=[2,2,2] )
	
	mc.showWindow(ruWin)
	
ruMainWindow()