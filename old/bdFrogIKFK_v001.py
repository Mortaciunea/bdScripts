import pymel.core as pm
import maya.OpenMaya as om

class frogIKFK():
    def __init__(self, *args, **kargs):
        self.legChainNames = ['leg','knee','shinTwist','ankle','foot','toeBase']
        self.armChainNames = ['shoulder','elbow','wrist']
        self.armOffsets = [[0.01,-0.041,-0.171],[0,-0.122,0.601],[5.509,9.074,-31.75]]
        
        self.ikArmCons = ['armIK','armPV']
        self.fkArmCons = ['shoulderFK','elbowFK','wristFK']
        
        self.direction = kargs.setdefault('direction')
        self.limb = kargs.setdefault('limb')
        self.side = kargs.setdefault('side')
        #self.bdSwitch(direction,limb)
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
                jntObj = pm.ls(side + '_' + armJoint + '_DRV' ,type= 'joint')[0]
                rot = jntObj.getRotation(space = 'object')
                ikRotations.append(rot)
            
            i=0
            '''
            for offset in self.armOffsets:
                ikRotations[i][0] += offset[0]
                ikRotations[i][1] += offset[1]
                ikRotations[i][2] += offset[2]
                i+=1
            i=0
            '''
            for fkCon in self.fkArmCons:
                fkConObj  = pm.ls(side + '_' + fkCon + '_CON' ,type= 'transform')[0]
                fkConObj.setRotation(ikRotations[i])
                i+=1
            
            i=0
            '''
            for armJoint in self.armChainNames:
                ikJntObj = pm.ls(side + '_' + armJoint + 'IK_DRV' ,type= 'joint')[0]
                tmpLocator = pm.spaceLocator(name=ikJntObj.name() + '_TMP_LOC')
                tmp = pm.parentConstraint(ikJntObj,tmpLocator)
                pm.delete(tmp)
                #tmp = pm.parentConstraint(tmpLocator,self.fkArmCons[self.armChainNames.index(armJoint)])
            '''    
            self.armSwitchCon.attr('ikFkBlend').set(1)
            
        elif 'leg' in limb:
            print side + ' leg switch'


