import pymel.core as pm
import pymel.core.datatypes as dt
import math


class VarFk:
    jntList = []
    ctrlList = []
    srf = ''
    jntGrp = ''
    allCtrlGrp = ''
    width = 0
    widthMult = 0.1
    mainGrp = ''
    mainCtrl = ''
    
    def __init__(self,*args,**kargs):
        self.name = kargs.setdefault('name','test')
        self.crv = kargs.setdefault('curve')
        self.numCtrl = kargs.setdefault('numCtrl',3)
        self.numJnt = kargs.setdefault('numJnt',9)
        
        pm.select(cl=1)
        self.mainGrp = pm.group(n=self.name + '_grp')
        
        #self.addVarFk()
        #self.addIk()
        
    
    def addIk(self):
        self.createJntChain()
        #create the surface that will be skinned to the joints
        self.createSrf()
        #create the follicles on the surface and also the controllers
        self.createFlcAndCtrl('u', 0)
        #get the joint position on the surface and store it as an attribute
        self.addJntPosAttr()
    
        self.jntGrp = pm.group(name=self.name+'_drv_jnt_grp')
        pm.rotate(self.jntGrp ,0,-90,0,r=1)
        pm.parent(self.jntList[0],self.jntGrp)
    
        pm.parent(self.jntGrp,self.mainGrp)
        self.addMainCtrl()
    
        pm.skinCluster( self.srf,self.jntList, tsb=1, ih=1, skinMethod = 0, maximumInfluences = 1, dropoffRate = 10.0 )        
    
    def addVarFk(self):
        #create  the joints
        self.createJntChain()
        #create the surface that will be skinned to the joints
        self.createSrf()
        #create the follicles on the surface and also the controllers
        self.createFlcAndCtrl('u', 0)
        #get the joint position on the surface and store it as an attribute
        self.addJntPosAttr()
        
        self.jntGrp = pm.group(name=self.name+'_drv_jnt_grp')
        pm.rotate(self.jntGrp ,0,-90,0,r=1)
        pm.parent(self.jntList[0],self.jntGrp)
        
        pm.parent(self.jntGrp,self.mainGrp)
        self.addMainCtrl()
        
        self.skinSrf()

        self.riggVarfk()
        
    def skinSrf(self):
        skinCls = pm.skinCluster( self.srf,self.jntList, tsb=1, ih=1, skinMethod = 0, maximumInfluences = 1, dropoffRate = 10.0 )[0]
        for i in range(self.numJnt):
            if i == 0:
                pm.skinPercent(skinCls.name(),self.srf.name() + '.cv[0:1][0:3]',tv=[(self.jntList[i],1)])
            elif i > 0 and i < self.numJnt-1:
                pm.skinPercent(skinCls.name(),self.srf.name() + '.cv[' + str(i+1) + '][0:3]',tv=[(self.jntList[i],1)])
            elif i == self.numJnt-1:
                pm.skinPercent(skinCls.name(),self.srf.name() + '.cv[' + str(i+1) + ':' + str(i+2) + '][0:3]',tv=[(self.jntList[i],1)])
                
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
            
            jnt = pm.joint(p=jntPos,name = self.name + '_vfk_jnt_' + (str(i)).zfill(2) )
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
        rebuiltLoftSrf = pm.rebuildSurface(loftSrf,ch=1, rpo=1, rt=0, end=1, kr=0, kcp=0, kc=0, su=0, du=3, sv=0, dv=3, tol=0, fr=0, dir=2 )[0]
        
        
        self.srf = loftSrf 
        pm.parent(self.srf,self.mainGrp)
    

        
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
            
            ctrl.position.set((i*pSeg + pStart))
            
            if(direction == 'v'):
                flcShape.parameterU.set(0.5)
                ctrl.position >> flcShape.parameterV
            else:
                flcShape.parameterV.set(0.5)
                ctrl.position >> flcShape.parameterU
            
            flcPos = flcTransform.getTranslation(space='world')
            ctrlMainGrp  = self.getCtrlMainGrp(ctrl)
            ctrlMainGrp.setTranslation(flcPos)
            #pm.parent(ctrlMainGrp,flcTransform)
            pm.parentConstraint(flcTransform,ctrlMainGrp,mo=1)
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
        ctrl = pm.circle(name = self.name + '_vfk_ctrl_0' + str(num),nr=[1,0,0],radius = self.width * 1.2)[0]
        pm.delete(ctrl,ch=1)
        #ctrl.translate.lock()
        for a in ['X','Y','Z']:
            ctrl.attr('translate' + a).set( lock = True, keyable = False, channelBox = False )
        ctrl.scaleX.set( lock = True, keyable = False, channelBox = False )
        
        pm.addAttr(ctrl,ln='falloff',defaultValue=0.2, minValue=0.01, maxValue=1,keyable=1)
        pm.addAttr(ctrl,ln='position',defaultValue=0, minValue=0, maxValue=1,keyable=1)
        ctrlRev = pm.group(ctrl,name=ctrl.name() + '_rev_rot')
        ctrlGrp = pm.group(ctrlRev,name=ctrl.name() + '_grp')
        
        rotRev = pm.shadingNode('reverse',name = ctrl.name() + '_rot_rev',asUtility=1)
        ctrl.rotate >> rotRev.input
        rotRev.output >> ctrlRev.rotate
        
        pm.rotate(ctrlGrp,0,-90,0,r=1)
        
        return ctrl
    '''
    def addNullGroups(jntList,ctrlList):
        startGrp = ''
    
        for jnt in jntList:
            jntPos = jnt.getTranslation(space='world')
            jntRot = jnt.getRotation(space='world')
            jntParent = jnt.getParent()
    
            
            for i in range(len(ctrlList)):
                pm.select(cl=1)
                grp = pm.group(name = jnt.name() + '_' + ctrlList[i].name() + '_rot')
                grp.setTranslation(jntPos,space='world')
                grp.setRotation(jntRot,space='world')
                if i==0:
                    if jntParent:
                        pm.parent(grp,jntParent)
                    pm.parent(jnt,grp)
                else:
                    if jntParent:
                        pm.parent(grp,jntParent)
                    pm.parent(startGrp,grp)
                startGrp = grp
            
        pm.select(cl=1)
    '''
    
        
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
            
    def riggVarfk(self):
        i=0
        for ctrl in self.ctrlList:
            for jnt in self.jntList:
                ctrlJntDistPma = pm.shadingNode('plusMinusAverage', name=jnt.name() + '_' + ctrl.name() + '_jnt_pos_minus_ctrl_pos_pma',asUtility = True)
                ctrlJntDistPma.operation.set(2)
                
                ctrl.position >> ctrlJntDistPma.input1D[0]
                jnt.jointPosition >> ctrlJntDistPma.input1D[1]
                
                powMd1 = pm.shadingNode('multiplyDivide',name = jnt.name() + '_' + ctrl.name() + '_pow2_md',asUtility = True)
                powMd1.operation.set(3)
                
                ctrlJntDistPma.output1D >> powMd1.input1.input1X
                powMd1.input2.input2X.set(2)
                
                powMd2 = pm.shadingNode('multiplyDivide',name = jnt.name() + '_' + ctrl.name() + '_powhalf_md',asUtility = True)
                powMd2.operation.set(3)
    
                powMd1.output.outputX >> powMd2.input1.input1X
                powMd2.input2.input2X.set(0.5)
                
                falloffRv = pm.shadingNode('remapValue',name = jnt.name() + '_' + ctrl.name() + '_falloff_rv',asUtility = True)
                falloffRv.value[0].value_FloatValue.set(1)
                falloffRv.value[0].value_Interp.set(2)
                falloffRv.value[1].value_FloatValue.set(0)
                falloffRv.value[2].value_FloatValue.set(0)
                falloffRv.value[2].value_Interp.set(2)
                
                powMd2.output.outputX >> falloffRv.inputValue
                ctrl.falloff >> falloffRv.value[2].value_Position
                
                rotMultMd  = pm.shadingNode('multiplyDivide',name = jnt.name() + '_' + ctrl.name() + '_rotMult_md',asUtility = True)
                ctrl.rotate >> rotMultMd.input1
                falloffRv.outValue >> rotMultMd.input2.input2X
                falloffRv.outValue >> rotMultMd.input2.input2Y
                falloffRv.outValue >> rotMultMd.input2.input2Z
                
                allRotAddPma = pm.ls(jnt.name() + '_rot_add_pma',type='plusMinusAverage')
                if not allRotAddPma:
                    allRotAddPma = pm.shadingNode('plusMinusAverage', name=jnt.name() + '_rot_add_pma',asUtility = True)
                    allRotAddPma = pm.ls(allRotAddPma)
                    allRotAddPma[0].output3D >> jnt.rotate
                
                rotMultMd.output >> allRotAddPma[0].input3D[i]
                
                #setting scale
                #scalePma = pm.shadingNode('plusMinusAverage', name=jnt.name() + '_' + ctrl.name() + '_scale_pma',asUtility = True)
                #scalePma.operation.set(1)
                zeroScalePma = pm.shadingNode('plusMinusAverage', name=jnt.name() + '_' + ctrl.name() + '_zero_scale_pma',asUtility = True)
                zeroScalePma.operation.set(2)
                scaleMultMd = pm.shadingNode('multiplyDivide',name = jnt.name() + '_' + ctrl.name() + '_scaleMult_md',asUtility = True)
                
                falloffRv.outValue >> scaleMultMd.input2.input2X
                falloffRv.outValue >> scaleMultMd.input2.input2Y
                falloffRv.outValue >> scaleMultMd.input2.input2Z
                
                ctrl.scale >> zeroScalePma.input3D[0]
                zeroScalePma.input3D[1].set([1,1,1])
                
                zeroScalePma.output3D >> scaleMultMd.input1
                
                #scalePma.input3D[0].set([1,1,1])
                #scaleMultMd.output >> scalePma.input3D[1]
                
                allScaleAddPma =  pm.ls(jnt.name() + '_scale_add_pma',type='plusMinusAverage')
                if not allScaleAddPma:
                    allScaleAddPma = pm.shadingNode('plusMinusAverage', name=jnt.name() + '_scale_add_pma',asUtility = True)
                    allScaleAddPma.operation.set(1)
                    allScaleAddPma.input3D[0].set([1,1,1])
                    allScaleAddPma = pm.ls(allScaleAddPma)
                    allScaleAddPma[0].output3D >> jnt.scale
                
                scaleMultMd.output >> allScaleAddPma[0].input3D[i+1]
                
                
                i=i+1
        


