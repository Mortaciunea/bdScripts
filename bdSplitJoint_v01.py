import maya.cmds as cmds
import maya.OpenMaya as om
import math

def bdSplitBone(startJnt,numSegments):
    jntChild = cmds.listRelatives(c=True,typ = 'joint')
    if numSegments < 2:
        print 'Need at least 2 segments to split, aborting'
        return
        
    if jntChild:
        if len(jntChild) > 1:
            print 'Selected joint has more then one child, aborting split'
        else:
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
                

            print  '%s'%(boneLength)
            cmds.delete(dupJoint[0])

    else:
        print 'Selected joint has no child'

def bdCheckRotationAxis(endJoint):
    endJntRaw = cmds.xform(endJoint,q=True,t=True)
    endJntPos = om.MVector(endJntRaw[0], endJntRaw[1], endJntRaw[2])
    
    endJntNorm = endJntPos.normal()
    if not abs(endJntNorm.x + endJntNorm.y + endJntNorm.z)
        error 'Warning, joint are not properly oriented !!!'


sel = cmds.ls(sl=True)
bdSplitBone(sel[0],4.0)
#bdCheckRotationAxis(sel[0])
