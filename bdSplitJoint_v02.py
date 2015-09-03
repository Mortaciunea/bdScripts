import maya.cmds as cmds
import maya.OpenMaya as om
import math

def bdSplitBone(args):
    sel = cmds.ls(sl=True)
    if not sel:
        print 'Nothing selected, returning'
        return
    startJnt = sel[0]
    numSegments = float(cmds.textFieldGrp("numSegments",q=True,tx = True))
    jntChild = cmds.listRelatives(c=True,typ = 'joint')
    if numSegments < 2:
        print 'Need at least 2 segments to split, aborting'
        return

    if jntChild:
        if len(jntChild) > 1:
            print 'Selected joint has more then one child, aborting split'
        else:
        	if bdCheckRotationAxis(jntChild[0]) <> '':
	            #get joints position
	            strJntRaw = cmds.xform(startJnt,ws=True,q=True,t=True)
	            strJntPos = om.MVector(strJntRaw[0], strJntRaw[1], strJntRaw[2])
	            
	            endJntRaw = cmds.xform(jntChild[0],ws=True,q=True,t=True)
	            endJntPos = om.MVector(endJntRaw[0], endJntRaw[1], endJntRaw[2])
	            
	            #substracting vectors in order to get to the segments position
	            subJnt = endJntPos - strJntPos
	            
	
	            cmds.parent(jntChild[0],w=True)
	            prevJoint = startJnt
	            dupJoint = cmds.duplicate(startJnt)
	
	            for i in range(1,int(numSegments),1):
	                newJoint = cmds.duplicate(dupJoint[0],rr=True,name = startJnt + '_seg_' + str(i) )
	
	                newJntPos = subJnt * i * (1/numSegments) + strJntPos
	                cmds.move(newJntPos.x,newJntPos.y,newJntPos.z,newJoint[0])
	                cmds.parent(newJoint[0],prevJoint)
	                prevJoint = newJoint[0]
	                if i == numSegments-1:
	                    cmds.parent(jntChild[0],newJoint[0])
	            cmds.delete(dupJoint[0])

    else:
        print 'Selected joint has no child'


def bdCheckRotationAxis(endJoint):
	endJntRaw = cmds.xform(endJoint,q=True,t=True)
	endJntPos = om.MVector(endJntRaw[0], endJntRaw[1], endJntRaw[2])
	downAxis = ''
	endJntNorm = endJntPos.normal()
	for i in range(0,3):
		print endJntNorm[i]
		if endJntNorm[i] == 1:
			if i==0:
				downAxis = 'x'
				print 'its x'
			elif i==1:
				downAxis = 'y'
				print 'its y'
			elif i==2:
				downAxis = 'z'
				print 'its z'
	return downAxis

def bdSplitBoneUI():
	bdSplitBoneWin = "SplitBone"
	if cmds.window(bdSplitBoneWin,q=True,ex=True):
		cmds.deleteUI(bdSplitBoneWin)

	cmds.window(bdSplitBoneWin,title = "Split Bone")
	cmds.scrollLayout(horizontalScrollBarThickness=16)
	mainColLayout = cmds.columnLayout(columnAttach=("both",5),rowSpacing=10,columnWidth=320)
	####
	frameLayout1 = cmds.frameLayout(label="Number of Segments",bs="etchedOut",w=300,mw=5,cll=1,p=mainColLayout)
	columnLayout1= cmds.columnLayout(rs=5,adj=1,p=frameLayout1)
	cmds.textFieldGrp("numSegments",l="",tx="2",cw2=[0,290])
	cmds.button(l="Split Bone",c=bdSplitBone)
	cmds.showWindow(bdSplitBoneWin)

	

	
bdSplitBoneUI()    




