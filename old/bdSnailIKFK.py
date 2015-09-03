import pymel.core as pm
import maya.OpenMaya as om

class snailIKFK():
    def __init__(self, *args, **kargs):
        selected = pm.ls(sl=True)
        if len(selected) == 0:
            pm.warning('Select a snail controller')
            return
        else:
            self.namespace = self.bdSnailNS()
                       
            self.tailIk = ['tailUpr_CON','tailMid_CON','tailLwr_CON','tailEnd_CON']
            self.tailFk = ['fkTail_01_CON','fkTail_02_CON','fkTail_03_CON','fkTail_04_CON']
            
            self.tailFkIkHelpers= ['tailUpr_LOC','tailMid_LOC','tailLwr_LOC','tailEnd_LOC']
            self.tailIkFkHelpers= ['fkTail_02_LOC','fkTail_03_LOC','fkTail_04_LOC','fkTail_05_LOC']
            
            
            self.switchCon = pm.ls(self.namespace + 'tailEnd_CON',type= 'transform')[0] 
            self.ikScaleFactorNode = pm.ls(self.namespace + 'ikTail_distances',type= 'transform')[0] 
            self.bdSwitch()
        
    def bdSwitch(self):
        currentState = self.switchCon.attr('ikFk').get()
        if (currentState > 0.5) and (currentState <= 1):
            self.bdSwitchFKIK()
        elif (currentState >= 0) and (currentState <= 0.5):
            self.bdSwitchIKFK()
    
    def bdSwitchFKIK(self):
        print 'FK -> IK'
        if self.switchCon.attr('ikFk').get() == 0:
            pm.warning('Already in IK mode, exiting')
        else:
            translations = []
            fkHelperObj = []
            for helper in self.tailFkIkHelpers:
                fkHelper = pm.ls(self.namespace + helper)[0]
                fkHelperObj.append(fkHelper)
                fkTrans = fkHelper.getTranslation(space='world')
                translations.append(fkTrans)
                
                
            i=0            
            for con in self.tailIk:
                ikCon = pm.ls(self.namespace + con)[0]
                ikCon.setTranslation(translations[i],space='world')
                tempCnstr = pm.orientConstraint(fkHelperObj[i],ikCon)
                pm.delete([tempCnstr])
                i+=1
            
            self.switchCon.attr('ikFk').set(0)

    def bdSwitchIKFK(self):
        print 'IK -> FK'
        if self.switchCon.attr('ikFk').get() == 1:
            pm.warning('Already in FK mode, exiting')
        else:
            translations = []
            ikHelperObj = []
            for helper in self.tailIkFkHelpers:
                ikHelper = pm.ls(self.namespace + helper)[0]
                ikHelperObj.append(ikHelper)
                
                ikHelperTrans = ikHelper.getTranslation(space='world')
                translations.append(ikHelperTrans)
                
               
            scaleFactors = []
            for seg in ['A','B','C','D']:
                scaleFactors.append(self.ikScaleFactorNode.attr('scaleFactor' + seg).get())
    
            i=0
            for con in self.tailFk:
                fkCon = pm.ls(self.namespace + con)[0]
                fkCon.scaleX.set(scaleFactors[i])
                i+=1 
            i=0     
            for con in self.tailFk:
                fkCon = pm.ls(self.namespace + con)[0]
                ikCon = pm.ls(self.namespace + self.tailIk[i])[0]
                tempCnstr = pm.aimConstraint(ikCon,fkCon,aimVector = [1,0,0],upVector = [0,1,0],worldUpType="object",worldUpObject=self.namespace + self.tailIkFkHelpers[i].replace('LOC','LOC_AIM')) 
                pm.delete(tempCnstr)
                i+=1
            
            i=0
            for con in self.tailFk[1:]:
                fkCon = pm.ls(self.namespace + con)[0]
                fkCon.setTranslation(translations[i],space='world')
                i+=1 
       
            self.switchCon.attr('ikFk').set(1)
        
    def bdSnailNS(self):
        ns=''
        try:
            selected = pm.ls(sl=True)[0]
            ns = selected.namespace()
        except:
            pm.warning('Select a snail controller')
            

        return ns