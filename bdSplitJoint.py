import maya.cmds as cmds
import maya.OpenMaya as om

def bdSplitBone(startJnt,numSegments):
    jntChild = cmds.listRelatives(c=True,typ = 'joint')
    if jntChild:
        if len(jntChild) > 1:
            print 'Selected joint has more then one child, aborting split'
        else:
            #get joints position
            strJntRaw = cmds.xform(startJnt,ws=True,q=True,t=True)
            strJntPos = om.MVector(strJntRaw[0], strJntRaw[1], strJntRaw[2])
            
            endJntRaw = cmds.xform(jntChild[0],ws=True,q=True,t=True)
            endJntPos = om.MVector(endJntRaw[0], endJntRaw[1], endJntRaw[2])
            
            subJnt = endJntPos - strJntPos
            boneLength = subJnt.length()
            
            cmds.parent(jntChild[0],w=True)
            for i in range(1,numSegments,1):
                newJoint = cmds.duplicate(startJnt,rr=True,name = startJnt + '_seg_' + str(i) )
                newJntPos = subJnt * i * (1/numSegments) + strJntPos
                cmds.move(newJntPos.x,newJntPos.y,newJntPos.z,newJoint[0])
                cmds.parent(newJoint[0],startJnt)
                if i == numSegments-1:
                    cmds.parent(jntChild[0],newJoint[0])

            print  '%s'%(boneLength)

            

        
    else:
        print 'Selected joint has no child'
    
    
sel = cmds.ls(sl=True)

bdSplitBone(sel[0],4.0)