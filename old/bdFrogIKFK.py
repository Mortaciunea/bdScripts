import pymel.core as pm
import maya.OpenMaya as om

class frogIKFK():
    def __init__(self, *args, **kargs):
        selected = pm.ls(sl=True)
        if len(selected) == 0:
            pm.warning('Select a frog controller')
            return
        else:
            self.namespace = self.bdFrogNS()        
            self.ikArmCons = ['_armIK_','_armPV_']
            self.fkArmCons = ['_shoulderFK_','_elbowFK_','_wristFK_']
            
            self.ikLegCons = ['_legIK_','_legPV_']
            self.fkLegCons = ['_legFK_','_kneeFK_','_ankleFK_','_footFK_']
                        
            self.limb = kargs.setdefault('limb')
            self.side = kargs.setdefault('side')
    
            self.armSwitchCon = pm.ls(self.namespace + self.side + '_armIK_CON',type= 'transform')[0]  
            self.legSwitchCon = pm.ls(self.namespace + self.side + '_legIK_CON',type= 'transform')[0]  
            if self.limb == 'arm':
                self.bdSwitchArm()
            elif self.limb == 'leg':
                self.bdSwitchLeg()
    
    def bdSwitchArm(self):
        currentState = self.armSwitchCon.attr('ikFkBlend').get()
        if (currentState > 0.5) and (currentState <= 1):
            self.bdSwitchFKIK()
        elif (currentState >= 0) and (currentState <= 0.5):
            self.bdSwitchIKFK()
            
    def bdSwitchLeg(self):
        currentState = self.legSwitchCon.attr('ikFkBlend').get()
        if (currentState > 0.5) and (currentState <= 1):
            self.bdSwitchFKIK()
        elif (currentState >= 0) and (currentState <= 0.5):
            self.bdSwitchIKFK()    
            
    def bdSwitchIKFK(self):
        if 'arm' in self.limb:
            print self.side + ' arm IK -> FK switch'
            
            for loc in self.fkArmCons:
                shadowLoc = pm.ls(self.namespace + self.side +  loc + 'LOC')[0]
                tempLoc = pm.duplicate(shadowLoc)
                pm.parent(tempLoc,w=True)
                
                fkCon = pm.ls(self.namespace + self.side +  loc + 'CON',type='transform')[0]
                tempCnstr = pm.orientConstraint(tempLoc,fkCon)
                
                pm.delete([tempCnstr,tempLoc])
                
            
            self.armSwitchCon.attr('ikFkBlend').set(1)
            
        elif 'leg' in self.limb:
            print self.side + ' leg IK->FK switch ' 
            
            for loc in self.fkLegCons:
                shadowLoc = pm.ls(self.namespace + self.side +  loc + 'LOC')[0]
                tempLoc = pm.duplicate(shadowLoc)
                pm.parent(tempLoc,w=True)
                
                fkCon = pm.ls(self.namespace + self.side +  loc + 'CON',type='transform')[0]
                tempCnstr = pm.orientConstraint(tempLoc,fkCon)
                
                pm.delete([tempCnstr,tempLoc])
                
            
            self.legSwitchCon.attr('ikFkBlend').set(1)            


    def bdSwitchFKIK(self):
        if 'arm' in self.limb:
            print self.side + ' arm FK->IK switch ' 
            
            for loc in self.ikArmCons:
                shadowLoc = pm.ls(self.namespace + self.side +  loc + 'LOC')[0]
                tempLoc = pm.duplicate(shadowLoc)
                pm.parent(tempLoc,w=True)
                
                ikCon = pm.ls(self.namespace + self.side +  loc + 'CON',type='transform')[0]
                if ikCon.name().find('armIK') > 0:
                    tempCnstr = pm.parentConstraint(tempLoc,ikCon)
                else:
                    tempCnstr = pm.pointConstraint(tempLoc,ikCon)
                pm.delete([tempCnstr,tempLoc])
                       
            self.armSwitchCon.attr('ikFkBlend').set(0)
        
        elif 'leg' in self.limb:
            print self.side + ' leg FK->IK switch ' 
            
            for loc in self.ikLegCons:
                shadowLoc = pm.ls(self.namespace + self.side +  loc + 'LOC')[0]
                tempLoc = pm.duplicate(shadowLoc)
                pm.parent(tempLoc,w=True)
                
                ikCon = pm.ls(self.namespace + self.side +  loc + 'CON',type='transform')[0]
                if ikCon.name().find('legIK') > 0:
                    tempCnstr = pm.parentConstraint(tempLoc,ikCon)
                else:
                    tempCnstr = pm.pointConstraint(tempLoc,ikCon)
                pm.delete([tempCnstr,tempLoc])
                       
            self.legSwitchCon.attr('ikFkBlend').set(0)
        
        

    def bdFrogNS(self):
        ns=''
        try:
            selected = pm.ls(sl=True)[0]
            ns = selected.namespace()
        except:
            pm.warning('Select a snail controller')
            

        return ns

def bdSwitchLeftArm(args):
    frogIKFK(limb = 'arm', side = 'L')

def bdSwitchRightArm(args):
    frogIKFK(limb = 'arm', side = 'R')

def bdSwitchLeftLeg(args):
    frogIKFK(limb = 'leg', side = 'L')

def bdSwitchRightLeg(args):
    frogIKFK(limb = 'leg', side = 'R')
    
def bdFrogIKFKUI():
    bdFrogWin = "FrogIKFK"
    if pm.window(bdFrogWin,q=True,ex=True):
	    pm.deleteUI(bdFrogWin)

    pm.window(bdFrogWin,title = "Frog IK <=> FK Switch", widthHeight = [280,80],sizeable=False)
    pm.scrollLayout(horizontalScrollBarThickness=16)
    mainCL = pm.columnLayout(columnAttach=("both",5),rowSpacing=10,columnWidth=280)
    pm.rowColumnLayout(nc=2,cw=[(1,138),(2,138)],p=mainCL)
    pm.button(l="Left Arm",c=bdSwitchLeftArm)
    pm.button(l="Right Arm",c=bdSwitchRightArm)
    pm.button(l="Left Leg",c=bdSwitchLeftLeg)
    pm.button(l="Right Leg",c=bdSwitchRightLeg)
    pm.text(l='Remeber to have a controller selected',p=mainCL)
    pm.showWindow(bdFrogWin)