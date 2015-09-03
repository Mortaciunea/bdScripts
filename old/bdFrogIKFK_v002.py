import pymel.core as pm
import maya.OpenMaya as om

class frogIKFK():
    def __init__(self, *args, **kargs):
        self.legChainNames = ['leg','knee','shinTwist','ankle','foot','toeBase']
        self.armChainNames = ['shoulder','elbow','wrist']
        
        self.ikArmCons = ['_armIK_','_armPV_']
        self.fkArmCons = ['_shoulderFK_','_elbowFK_','_wristFK_']
        
        self.direction = kargs.setdefault('direction')
        self.limb = kargs.setdefault('limb')
        self.side = kargs.setdefault('side')

        self.armSwitchCon = pm.ls(self.side + '_armIK_CON',type= 'transform')[0]  
    
    def bdSwitch(self):
        if self.direction == 'IKFK':
            self.bdSwitchIKFK(self.limb,self.side)
        elif self.direction == 'FKIK':
            self.bdSwitchFKIK(self.limb,self.side)
    
    def bdSwitchIKFK(self,limb,side):
        if 'arm' in limb:
            print side + ' arm switch'
            
            ikRotations = []
            for armJoint in self.armChainNames:
                jntObj = pm.ls(side +  armJoint + 'DRV' ,type= 'joint')[0]
                rot = jntObj.getRotation(space = 'object')
                ikRotations.append(rot)
            
            i=0
            for fkCon in self.fkArmCons:
                fkConObj  = pm.ls(side + fkCon + 'CON' ,type= 'transform')[0]
                fkConObj.setRotation(ikRotations[i])
                i+=1
            
            i=0
            self.armSwitchCon.attr('ikFkBlend').set(1)
            
        elif 'leg' in limb:
            print side + ' leg switch'


    def bdSwitchFKIK(self,limb,side):
        if 'arm' in limb:
            print side + ' FK->IK arm switch ' 
            
            fkWristConObj = pm.ls(side + self.fkArmCons[2] + 'CON')[0]
            fkWristPos = fkWristConObj.getTranslation(space='world')
            fkWristRot = fkWristConObj.getRotation(space='world')
            
            ikWristConObj = pm.ls(side + self.ikArmCons[0] + 'CON')[0]
            ikPVCon = pm.ls(side + self.ikArmCons[1] + 'CON')[0]
            
            ikWristConObj.setTranslation(fkWristPos,space='world')
            ikWristConObj.setRotation(fkWristRot,space='world')
            
            #vector fun
            fkWristVec = om.MVector(fkWristPos)
            
            fkElbowConObj = pm.ls(side + self.fkArmCons[1] + 'CON')[0]
            fkElbowPos =  fkElbowConObj.getTranslation(space = 'world')
            fkElbowVec = om.MVector(fkElbowPos)
            
            fkShoulderConObj = pm.ls(side + self.fkArmCons[0] + 'CON')[0]
            fkShoulderPos =  fkShoulderConObj.getTranslation(space = 'world')
            fkShoulderVec = om.MVector(fkShoulderPos)
            
            
            fkMidPoint = (fkWristVec + fkShoulderVec) / 2 
            
            
                        
            pvVec = (( fkElbowVec - fkMidPoint ) * 4 ) + fkMidPoint
            tempObj = pm.circle(c=[pvVec.x,pvVec.y,pvVec.z])[0]
            tempObj.centerPivots()
            
            #ikPVCon.setTranslation([pvVec.x,pvVec.y,pvVec.z],space='world')
            tempCnstr = pm.pointConstraint(tempObj,ikPVCon)
            
            pm.delete([tempCnstr,tempObj])
                       
            self.armSwitchCon.attr('ikFkBlend').set(0)