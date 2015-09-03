import maya.cmds as cmds
import functools
import maya.mel as mm

def createLimb(bones=1):
    xPos= 10
    #joints
    for i in range(0,bones,1):
        limbJnt = cmds.sphere(n='joint_'+str(i))
        cmds.move(i*xPos,0,0,limbJnt)
    #bones
    for i in range(0,bones-1,1):
        bone = cmds.polyCylinder(n='bone_'+str(i),height=10,radius=0.2)
        cmds.move(i*xPos + xPos/2,0,0,bone)
        cmds.rotate(0,0,-90,bone)
    #clusters
    cmds.select(clear=True)    
    for i in range(0,bones,1):
        jntCluster = cmds.cluster()
        cmds.move(i*xPos,0,0,jntCluster)
        cmds.select(clear=True)

    
    
    
createLimb(5)