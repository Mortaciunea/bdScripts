import pymel.core as pm
import pymel.core.datatypes as dt
import math


class TailIk:
    jntList = []
    ctrlList = []
    drvJntList = []
    srf = None
    jntGrp = None
    allCtrlGrp = None
    mainGrp = None
    mainCtrl = None
    ikCrv = None
    width = 0
    widthMult = 0.1

    def __init__(self,*args,**kargs):
        self.name = kargs.setdefault('name','test')
        self.crv = kargs.setdefault('curve')
        self.numCtrl = kargs.setdefault('numCtrl',3)
        self.numJnt = kargs.setdefault('numJnt',9)
        
        pm.select(cl=1)
        self.mainGrp = pm.group(n=self.name + '_grp')
        
        self.addIk()
        
    
    def addIk(self):
        self.createJntChain()
        #create the surface that will be skinned to the joints
        self.createSrf()
        self.createIkCrv()
        #create the follicles on the surface and also the controllers
        self.createFlcAndCtrl('u', 1)
        #get the joint position on the surface and store it as an attribute
        self.addJntPosAttr()
    
        self.jntGrp = pm.group(name=self.name+'_ik_jnt_grp')
        pm.rotate(self.jntGrp ,0,-90,0,r=1)
        pm.parent(self.jntList[0],self.jntGrp)
    
        pm.parent(self.jntGrp,self.mainGrp)
        self.addMainCtrl()
    
        self.skinSrf()
        
    
    def skinSrf(self):
        self.createDrvJnt()
        
        skinCls = pm.skinCluster( self.srf,self.drvJntList, tsb=1, ih=1, skinMethod = 0, maximumInfluences = 1, dropoffRate = 10.0 )[0]
        crvSkinCls = pm.skinCluster( self.ikCrv,self.drvJntList, tsb=1, ih=1, skinMethod = 0, maximumInfluences = 1, dropoffRate = 10.0 )[0]
        for i in range(len(self.drvJntList)):
            if i == 0:
                pm.skinPercent(skinCls.name(),self.srf.name() + '.cv[0:1][0:3]',tv=[(self.drvJntList[i],1)])
                pm.skinPercent(crvSkinCls.name(),self.ikCrv.name() + '.cv[0:1]',tv=[(self.drvJntList[i],1)])
            elif i > 0 and i < self.numJnt-1:
                pm.skinPercent(skinCls.name(),self.srf.name() + '.cv[' + str(i+1) + '][0:3]',tv=[(self.drvJntList[i],1)])
                pm.skinPercent(crvSkinCls.name(),self.ikCrv.name() + '.cv[' + str(i+1) + ']',tv=[(self.drvJntList[i],1)])
            elif i == self.numJnt-1:
                pm.skinPercent(skinCls.name(),self.srf.name() + '.cv[' + str(i+1) + ':' + str(i+2) + '][0:3]',tv=[(self.drvJntList[i],1)])
                pm.skinPercent(crvSkinCls.name(),self.ikCrv.name() + '.cv[' + str(i+1) + ':' + str(i+2) + ']',tv=[(self.drvJntList[i],1)])

    def createDrvJnt(self):
        i=0
        for ctrl in self.ctrlList:
            print str(i).zfill(2)
            pos = ctrl.getTranslation(space='world')
            pm.select(cl=1)
            drvJnt = pm.joint(name=self.name + '_drv_jnt_' + (str(i)).zfill(2))
            drvJntGrp = pm.group(drvJnt,name = drvJnt.name() + '_grp')
            drvJntGrp.setTranslation(pos,space='world')
            self.drvJntList.append(drvJnt)
            pm.parentConstraint(ctrl,drvJntGrp)
            i+=1

        
    def createJntChain(self):
        print 'creating joint chain'
        jntList = []
        crv = pm.ls(self.crv)[0]
        crv = pm.rebuildCurve(crv,rpo=1,rt=0,end=1, kr=0,kcp=0,kep=1,kt=0, s=0,d=3,tol=0)[0]
        numCvs = crv.getShape().numCVs()
        
        #jnt pos is calculated by sampling a closest point on crv in order to same length segments no matter the cv num and position
        pociNode = pm.shadingNode('pointOnCurveInfo',asUtility = 1)
        pociNode.turnOnPercentage.set(1)
        crv.getShape().worldSpace[0] >> pociNode.inputCurve
        tempLoc = pm.spaceLocator()
        pociNode.position >> tempLoc.translate
        segmentLength = 1.0 /( self.numJnt - 1)
        pm.select(cl=1)
        for i in range(self.numJnt):
            pociNode.parameter.set(i*segmentLength)
            jntPos = tempLoc.getTranslation(space='world')
            
            jnt = pm.joint(p=jntPos,name = self.name + '_ik_jnt_' + (str(i)).zfill(2) )
            jntList.append(jnt)
    
        pm.joint(jntList[0],e=True, oj='xyz',secondaryAxisOrient='yup',ch= True,zso=True)
        jntList[-1].jointOrient.set([0,0,0])
    
        pm.delete([tempLoc,pociNode])
        
        self.jntList = jntList

        
    def addMainCtrl(self):
        pos = self.jntList[0].getTranslation(space='world')
        ctrl = pm.circle(name = self.name + '_main_ctrl',radius = self.width * 2)[0]
        pm.delete(ctrl,ch=1)
        
        ctrlGrp = pm.group(ctrl,name = ctrl.name() + '_grp')
        pm.parent(ctrlGrp,self.mainGrp)
        
        ctrlGrp.setTranslation(pos,space='world')
        pm.parentConstraint(ctrl,self.jntGrp,mo=1)
        
        self.mainCtrl = ctrl

        
                    
    def createSrf(self):
        #calculate the witdth of the surface as a fraction of the total joint chain length
        jntChainLength = 0
        crvPoints = []
        for i in range(1,self.numJnt):
            pos1 = self.jntList[i-1].getTranslation(space='world')
            crvPoints.append(pos1)
            pos2 = self.jntList[i].getTranslation(space='world')
    
            jntChainLength += (pos2 - pos1).length()
            if i == self.numJnt - 1:
                crvPoints.append(pos2)
        
        jntChainLength = math.ceil(jntChainLength )
        self.width = jntChainLength * self.widthMult
        
        crv1 = pm.curve(n=self.name + '_crv1',d=1,p=crvPoints)
        pm.move(crv1,self.width / 2.0,0,0,r=1)
        pm.parent(crv1,self.mainGrp)
        crv2 = pm.curve(n=self.name + '_crv2',d=1,p=crvPoints)
        pm.move(crv2,self.width / -2.0,0,0,r=1)
        pm.parent(crv2,self.mainGrp)
        
        pm.select(cl=1)
        loftSrf = pm.loft(crv2,crv1,ch=1,u=1,c= 0,ar= 1,d=3,ss= 1,rn=0,po=0,rsn=1,n=self.name + "_srf")[0]
        rebuiltLoftSrf = pm.rebuildSurface(loftSrf,ch=1, rpo=1, rt=0, end=1, kr=0, kcp=0, kc=0, su=self.numCtrl-1, du=3, sv=0, dv=3, tol=0, fr=0, dir=2 )[0]
        
        
        self.srf = loftSrf 
        pm.parent(self.srf,self.mainGrp)
    

    def createIkCrv(self):
        ikCrv = pm.duplicate(self.crv)
        ikCrv = pm.rebuildCurve(ikCrv[0],ch=0, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=self.numCtrl-1, d=3, tol=0)[0]
        ikCrv.rename(self.name + '_ik_crv')
        self.ikCrv = ikCrv
        
    def createFlcAndCtrl(self,direction,ends):
        folicles = []
        ctrlList = []
        pm.select(cl=1)
        self.allCtrlGrp = pm.group(n=self.name + '_ctrl_grp')
        
        for i in range(self.numCtrl):
            pm.select(cl=1)
            flcShape = pm.createNode('follicle', name = self.srf.name() + '_flcShape_' + str(i).zfill(2) )
            flcTransform = flcShape.getParent()
            flcTransform.rename(flcShape.name().replace('flcShape','flc') )
            folicles.append(flcTransform)
            ctrl = self.addCtrl(i)
            self.ctrlList.append(ctrl)
            
            srfShape = pm.listRelatives(self.srf)[0]
            srfShape.local.connect(flcShape.inputSurface)
            srfShape.worldMatrix[0].connect(flcShape.inputWorldMatrix)
    
            flcShape.outRotate.connect(flcTransform.rotate)
            flcShape.outTranslate.connect(flcTransform.translate)
            #flcShape.flipDirection.set(1)
            
            pSeg = 1.0 / (self.numCtrl - 1)
            pStart = 0
            if not ends:
                pSeg = 1.0 / (self.numCtrl + 1)
                pStart = pSeg
            
            pos = i*pSeg + pStart
            
            if(direction == 'v'):
                flcShape.parameterU.set(0.5)
                flcShape.parameterV.set(pos)
            else:
                flcShape.parameterV.set(0.5)
                flcShape.parameterU.set(pos)
            
            flcPos = flcTransform.getTranslation(space='world')
            ctrlMainGrp  = self.getCtrlMainGrp(ctrl)
            ctrlMainGrp.setTranslation(flcPos)
            
            #pm.parentConstraint(flcTransform,ctrlMainGrp,mo=1)
            pm.parent(ctrlMainGrp,self.allCtrlGrp)

        flcGrp = pm.group(folicles,n=self.srf.name() + '_flc_grp')
        pm.select(cl=1)
        pm.parent(flcGrp,self.mainGrp)
        pm.parent(self.allCtrlGrp,self.mainGrp)
    
    def getCtrlMainGrp(self,ctrl):
        chainParents = []
        parent =  pm.listRelatives(ctrl,p=1)
        chainParents.append(parent)
        while parent :
            parent  = pm.listRelatives(parent ,p=1)
            chainParents.append(parent )
           
        chainParents.pop()
        
        return chainParents[-1][0]
            
        
    def addCtrl(self,num):
        ctrl = pm.circle(name = self.name + '_ik_ctrl_0' + str(num),nr=[1,0,0],radius = self.width * 1.2)[0]
        pm.delete(ctrl,ch=1)
        #ctrl.translate.lock()
        '''
        for a in ['X','Y','Z']:
            ctrl.attr('translate' + a).set( lock = True, keyable = False, channelBox = False )
        ctrl.scaleX.set( lock = True, keyable = False, channelBox = False )
        '''
        #pm.addAttr(ctrl,ln='falloff',defaultValue=0.2, minValue=0.01, maxValue=1,keyable=1)
        #pm.addAttr(ctrl,ln='position',defaultValue=0, minValue=0, maxValue=1,keyable=1)
        ctrlGrp = pm.group(ctrl,name=ctrl.name() + '_grp')
        
        pm.rotate(ctrlGrp,0,-90,0,r=1)
        
        return ctrl
   
        
    def addJntPosAttr(self):
        for jnt in self.jntList:
            cposNode = pm.shadingNode( 'closestPointOnSurface', asUtility = True )
            decMtx = pm.shadingNode('decomposeMatrix',asUtility = True )
            
            self.srf.getShape().worldSpace[0].connect(cposNode.inputSurface)
            decMtx.outputTranslate.connect(cposNode.inPosition)
    
            jnt.worldMatrix[0].connect(decMtx.inputMatrix)
            pm.addAttr(jnt, shortName='jointPosition', longName='jointPosition', defaultValue=0, minValue=0, maxValue=1)
            jntPos = cposNode.parameterU.get()
            jnt.jointPosition.set(jntPos)
    
            pm.delete([cposNode,decMtx])
            
