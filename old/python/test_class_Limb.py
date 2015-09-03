import maya.cmds as cmds
import functools
import maya.mel as mm
import maya.OpenMaya as om

class limb():
    limbCircles = []
    limbJoints = []
    limbLoftBones = []
    def __init__(self):
        xPos= 10
        #joints
        loftCircles = self.limbCircles
        limbJoints = self.limbJoints
        loftBone = self.limbLoftBones
        
        for i in range(0,2,1):
            limbJnt = cmds.sphere(n='joint_'+str(i))
            limbJoints.append(limbJnt[0])
            cmds.move(i*xPos,0,0,limbJnt)
            circleJnt = cmds.circle(n='circlelJnt_' + str(i),radius=0.4)
            cmds.move(i*xPos,0,0,circleJnt)
            cmds.rotate(0,-90,0,circleJnt)
            loftCircles.append(circleJnt[0])
 
            cmds.parent(circleJnt[0],limbJnt[0])
            
        loftBone = cmds.loft(loftCircles[0],loftCircles[1],n='loftBone')
        cmds.setAttr(loftBone[0] +  '.inheritsTransform',0)
        cmds.aimConstraint(limbJoints[1],loftCircles[0],mo=True)
        cmds.aimConstraint(limbJoints[0],loftCircles[1],mo=True)
        cmds.group(limbJoints[0],limbJoints[1],loftBone[0],n='limb')


    
    def getComponents(self):
        print self.loftBone
        
limb1 = limb()
limb1.getComponents()