import pymel.core as pm
import maya.OpenMaya as om

# Creates a ribbon setup as following ( based on a Rigging Dojo technique):
# - creates two 1 degree curves
# - creates driver joints for the curves to be skinned 
# - lofts the curves as 1 degree surface, history on
# - rebuilds the lofted surface as a 3 degree surface, history on


class bdRibbon():
    def __init__(self,*args,**kargs):
        self.nameRbn = kargs.setdefault('name')
        self.startRbn = kargs.setdefault('start')
        self.endRbn = kargs.setdefault('end')
        self.segmentsRbn = kargs.setdefault('segments')
        self.direction = kargs.setdefault('direction')
        self.ends = kargs.setdefault('ends')
        
        self.startJnt = ''
        self.endJnt = ''
        self.rbnSrf = ''
        self.rbnGrp = ''
        self.bdBuildSrf(self.nameRbn)
        #self.bdBuildRbnDT(self.nameRbn,self.startRbn, self.endRbn, self.segmentsRbn)
        #self.bdBuildRbnRD(self.segmentsRbn )

    def bdBuildSrf(self,name):
        selected = pm.ls(sl=1)
        if selected:
            if len(selected) == 1:
                if selected[0].type() == 'joint':
                    print 'start srf'
                    self.startJnt = selected[0]
                    children = self.startJnt.getChildren(type='joint')
                    print children 
                    #need to implement a case with more joint chidren
                    #build the one degree curves for lofting
                    self.endJnt = children[0]
                    startPos1,endPos1 = self.bdGetPos(-0.05)
                    startPos2,endPos2 = self.bdGetPos( 0.05)
                    pm.spaceLocator(p=startPos1)
                    pm.spaceLocator(p=startPos2)
                    pm.spaceLocator(p=endPos1)
                    pm.spaceLocator(p=endPos2)
                    
                    dif1 = (endPos1 - startPos1) 
                    dif2 = (endPos2 - startPos2) 
                    crv1Points = []
                    crv2Points = []
                    for i in range(self.segmentsRbn):
                        pos = dif1 * (i/(self.segmentsRbn*1.0)) + startPos1
                        crv1Points.append(pos )
                        pos = dif2 * (i/(self.segmentsRbn*1.0)) + startPos2
                        crv2Points.append(pos)

                    crv1Points.append(endPos1)
                    crv2Points.append(endPos2)
                    print 'building curve'
                    tmp = pm.curve(n=name + '_crv1',d=1,p=crv1Points)
                    crv1 = pm.ls(tmp)[0]
                    print crv1
                    #crv1.setScalePivot(startPos1)
                    #crv1.setRotatePivot(startPos1)
                    crv2 = pm.curve(n=name + '_crv2',d=1,p=crv2Points)
                    #crv2.setScalePivot(startPos2)
                    #crv2.setRotatePivot(startPos2)
                    drvGrp = self.bdCreateDrvJnt(crv1,crv2)
                    
                    #loft the curves
                    loftSrf = pm.loft(crv1,crv2,ch=1,u=1,c= 0,ar= 1,d=1,ss= 1,rn=0,po=0,rsn=1,n=name + "_lft_srf")[0]
                    #loftSrf.setScalePivot(startPos2)
                    #loftSrf.setRotatePivot(startPos2)
                    rebuiltLoftSrf = pm.rebuildSurface(ch=1, rpo = 0, rt = 0, end = 1, kr=1, kcp=0,kc=0, su=0, du=3, sv=0, dv=1, fr=0, dir=2 , n=name + "_srf")[0]
                    self.rbnSrf = rebuiltLoftSrf
                    crvGrp = pm.group([crv1,crv2],name=name+'_crv_grp')
                    crvGrp.centerPivots()
                    srfGrp = pm.group([loftSrf,rebuiltLoftSrf],name=name+'_srf_grp')
                    srfGrp.centerPivots()
                    self.rbnGrp = pm.group([crvGrp,srfGrp],n=name+"_grp")
                    pm.parent(drvGrp,self.rbnGrp)
                    


    def bdGetPos(self, offset):
        jnt1Pos = self.startJnt.getTranslation(space='world') 
        #jnt1Rot = self.startJnt.getRotation(space='world') 
        jnt2Pos = self.endJnt.getTranslation(space='world')
        '''
        tmpLoc = pm.spaceLocator(n='tempLoc')
        pm.move(jnt1Pos[0],jnt1Pos[1],jnt1Pos[2],a=1,ws=1)
        #tmpLoc.setTranslation(jnt1Pos)
        #tmpLoc.setRotation(jnt1Rot)


        pm.move(0,0,offset, r=1, os=1)
        startPos = tmpLoc.getTranslation(space='world')

        #tmpLoc.setTranslation(jnt2Pos)
        pm.move(jnt2Pos[0],jnt2Pos[1],jnt2Pos[2],a=1,ws=1)
        pm.move(0,0,offset, r=1, os=1)
        endPos = tmpLoc.getTranslation(space='world')

        pm.delete(tmpLoc)
        '''
        startPos = [jnt1Pos[0],jnt1Pos[1],jnt1Pos[2] + offset]
        endPos = [jnt2Pos[0],jnt2Pos[1],jnt2Pos[2] + offset]
        print startPos, endPos
        return startPos, endPos



    def bdBuildRbnRD(self,numFlc):

        if self.rbnSrf:
            flcGrp = self.bdCreateFol(self.rbnSrf,numFlc,self.direction,self.ends)
            self.bdCreateJoints(flcGrp)


    def bdCreateJoints(self,flcGrp):
        folicles = flcGrp.listRelatives(c=True,type='transform')
        for flc in folicles:
            flcJoint = pm.joint()
            flcJoint.rename(flc.name().replace('flc','JNT'))
            pm.parent(flcJoint,flc)
            flcJoint.setTranslation([0,0,0])
            self.bdCreateJntCtrl(flcJoint,0.15)
        

    def bdCreateJntCtrl(self,jnt,scale):
        ctrl = pm.circle(n=jnt.name().replace('JNT','ctrl'))[0]
        ctrl.ry.set(90)
        ctrl.setScale([scale,scale,scale])
        ctrl.overrideEnabled.set(1)
        ctrl.overrideColor.set(18)
        pm.makeIdentity(ctrl,a=1)
        ctrlGrp = pm.group(name = ctrl.name() + '_grp')
        if jnt.getParent():
            pm.parent(ctrlGrp,jnt.getParent())
            for axis in ['X','Y','Z']:
                ctrlGrp.attr('translate'+axis).set(0)
                ctrlGrp.attr('rotate'+axis).set(0)
            pm.parent(jnt,ctrl)
        else:
            pm.parent(ctrlGrp,jnt)
            for axis in ['X','Y','Z']:
                ctrlGrp.attr('translate'+axis).set(0)
                ctrlGrp.attr('rotate'+axis).set(0)
            pm.parent(ctrlGrp,w=1)
            pm.parent(jnt,ctrl)
        return ctrlGrp

    def bdFlcScaleCnstr(self,scaleGrp,flcGrp):
        folicles = flcGrp.listRelatives(c=True,type='transform')
        for flc in folicles:
            pm.scaleConstraint(scaleGrp,flc)


    def bdCreateFol(self,surfaceRbn,segments,direction,ends):
        folicles = []
        if not ends:
            flcRange = [i for i in range(1,segments)]
        else:
            flcRange = [i for i in range(segments+1)]

        for i in flcRange:
            flcShape = pm.createNode('follicle', name = surfaceRbn.name().replace('srf','FLCShape') + '_0' + str(i) )
            flcTransform = flcShape.getParent()
            flcTransform.rename(surfaceRbn.name().replace('srf','flc') + '_0' + str(i) )
            folicles.append(flcTransform) 

            surfaceRbn.getShape().local.connect(flcShape.inputSurface)
            surfaceRbn.getShape().worldMatrix[0].connect(flcShape.inputWorldMatrix)

            flcShape.outRotate.connect(flcTransform.rotate)
            flcShape.outTranslate.connect(flcTransform.translate)

            if(self.direction == 'v'):
                flcShape.parameterU.set(0.5)
                flcShape.parameterV.set((i*1.0)/segments)
            else:
                flcShape.parameterV.set(0.5)
                flcShape.parameterU.set((i*1.0)/segments)                


        flcGrp = pm.group(folicles,n=surfaceRbn.name().replace('srf','flc_grp'))
        pm.parent(flcGrp,self.rbnGrp)
        return flcGrp
    
    def bdCreateDrvJnt(self,crv1,crv2):
        pm.select(cl=1)
        drv1 = self.startJnt.duplicate(po=1)[0]
        pm.parent(drv1,w=1)
        drv1.rename(self.nameRbn + '_DRV_1_JNT')
        radius = self.startJnt.radius.get()
        drv1.radius.set(radius*1.5)
        pm.parentConstraint(self.startJnt,drv1,mo=0)
        
        drv2 = drv1.duplicate(po=1)[0]
        drv2.rename(self.nameRbn + '_DRV_2_JNT')
        
        drv3 = drv1.duplicate(po=1)[0]
        drv3.rename(self.nameRbn + '_DRV_3_JNT')
        pm.parentConstraint(self.endJnt,drv3,mo=0)

        startPos,endPos = self.bdGetPos(0)
        drv1.setTranslation(startPos)
        drv3.setTranslation(endPos)

        drv2CtrlGrp = self.bdCreateJntCtrl(drv2,0.20)
        pm.pointConstraint(drv1,drv2CtrlGrp,mo=0 )
        pm.pointConstraint(drv3,drv2CtrlGrp,mo=0 )
        aimLocator = pm.spaceLocator(n=drv2CtrlGrp.name().replace('DRV_2_CTRL_GRP','AIM'))
        drv2CtrlGrpPos = drv2CtrlGrp.getTranslation(space='world')
        aimLocator.setPosition(drv2CtrlGrpPos)
        for axis in ['X','Y','Z']:
            aimLocator.attr('localScale'+axis).set(0.1)
        aimLocatorGrp = pm.group(aimLocator,n=aimLocator.name() + '_grp')
        aimLocatorGrp.centerPivots()
        if self.direction == 'hor':
            pm.move(0,0.5,0, aimLocatorGrp, r=1, os=1, wd=1)
        elif self.direction == 'vert':
            pm.move(0,0,0.5, aimLocatorGrp, r=1, os=1, wd=1)
        pm.parentConstraint(self.startJnt,aimLocatorGrp,mo=1)
        print aimLocator.getTranslation(space='world').x
        if aimLocator.getTranslation(space='world').x > 0:
            pm.aimConstraint(drv3,drv2CtrlGrp,mo=1,weight=1,aimVector=[1, 0, 0],upVector = [0, 1, 0],worldUpType="object" , worldUpObject = aimLocator)
        else:
            pm.aimConstraint(drv3,drv2CtrlGrp,mo=1,weight=1,aimVector=[-1, 0, 0],upVector = [0, 1, 0],worldUpType="object" , worldUpObject = aimLocator)
        drvGrp = pm.group([drv1,drv2CtrlGrp,drv3],n=self.nameRbn + '_DRV_GRP')
        crv1Skin = pm.skinCluster(drv1,drv2,drv3,crv1)
        crv1Skin = pm.skinCluster(drv1,drv2,drv3,crv2)
        pm.parent(aimLocatorGrp,drvGrp)
        return drvGrp


    def bdBuildRbnDT(self,name,start,end,segments):
        surfaceRbn = pm.nurbsPlane(ax = [0,0,22], d=3, u=1, v=segments , w=1, lr = segments)[0]
        surfaceRbn.rename(name)
        flcGrp = self.bdCreateFol(surfaceRbn,segments)

        surfaceRbn_BS = surfaceRbn.duplicate()[0]
        surfaceRbn_BS.rename(name + '_BS')
        surfaceRbn_BS.translateX.set(segments * 0.5 )
        blendshapeNode = pm.blendShape(surfaceRbn_BS,surfaceRbn,name=surfaceRbn.name() + '_blendShape')[0]
        blendshapeNode.attr(surfaceRbn_BS.name()).set(1)

        locatorsRbn = []

        topLocator = pm.spaceLocator()
        topLocator.rename(name + '_loc_top_CON')
        topLocator.translateY.set(segments * 0.5)
        pm.makeIdentity(topLocator,apply=True,t=True,r=True,s=True)

        midLocator = pm.spaceLocator()
        midLocator.rename(name + '_loc_mid_CON')
        midLocatorGrp = pm.group(midLocator,name=midLocator.name() + '_grp')
        pm.makeIdentity(midLocator,apply=True,t=True,r=True,s=True)

        botLocator = pm.spaceLocator()
        botLocator.rename(name + '_loc_bot_CON')
        botLocator.translateY.set(segments * -0.5)
        pm.makeIdentity(botLocator,apply=True,t=True,r=True,s=True)

        locatorsRbn.append(topLocator)
        locatorsRbn.append(midLocator)
        locatorsRbn.append(botLocator)

        pm.pointConstraint(topLocator,botLocator,midLocatorGrp)
        conGrp = pm.group([topLocator,midLocatorGrp,botLocator],n=name.replace('srf','CON_GRP'))


        curveDrv = pm.curve(d=2, p=[(0, segments * 0.5, 0), (0, 0, 0), (0, segments * -0.5, 0)],k=[0,0,1,1])
        curveDrv.rename(name.replace('srf', 'wire_CRV'))
        curveDrv.translateX.set(segments * 0.5)

        wireDef = pm.wire(surfaceRbn_BS,w=curveDrv,en=1,gw=False,ce=0, li=0, dds = [0,20], n=name.replace('srf','wire'))

        #kind of a hack
        wireDefBase = wireDef[0].baseWire[0].listConnections(d=False,s=True)
        curveCLS,clsGrp = self.bdClustersOnCurve(curveDrv,segments)

        for i in range(3):
            locatorsRbn[i].translate.connect(curveCLS[i].translate)

        #organize a bit
        moveGrp = pm.group([conGrp,surfaceRbn],name=name.replace('srf','move_GRP'))
        extraGrp = pm.group([flcGrp,surfaceRbn_BS,clsGrp,curveDrv,wireDefBase],name = name.replace('srf','extra_GRP'))
        allGrp = pm.group([moveGrp,extraGrp],name = name.replace('srf','RBN'))

        self.bdFlcScaleCnstr(moveGrp,flcGrp)

        globalCon = pm.spaceLocator()
        globalCon.rename(name.replace("srf",'world_CON'))

        pm.parent(globalCon,allGrp)
        pm.parent(moveGrp,globalCon)

        self.bdCreateJoints(flcGrp)

        twistDef, twistDefTransform = self.bdAddTwist(surfaceRbn_BS)
        pm.parent(twistDefTransform, extraGrp)
        topLocator.rotateY.connect(twistDef.startAngle)
        botLocator.rotateY.connect(twistDef.endAngle)

        pm.reorderDeformers(wireDef[0],twistDef,surfaceRbn_BS)

    def bdAddTwist(self,surfaceRbn_BS):
        pm.select(surfaceRbn_BS)
        twistDef, twistDefTransform = pm.nonLinear(type='twist')
        twistDefTransform.rename(surfaceRbn_BS.name().replace('SRF_BS','twistHandle'))
        twistDef.rename(surfaceRbn_BS.name().replace('SRF_BS','twist'))
        twistDefTransform.rotateX.set(180)
        return twistDef, twistDefTransform


    def bdClustersOnCurve(self,curveDrv,segments):
        clusters = []
        curveCVs = curveDrv.cv
        topClusterTransform= pm.cluster([curveCVs[0],curveCVs[1]],rel=True)[1]
        topClusterTransform.rename(curveDrv.name() + '_top_CLS')
        topClusterTransform.getShape().originY.set(segments * 0.5)
        pivot = curveCVs[0].getPosition(space='world')
        topClusterTransform.setPivots(pivot)
        clusters.append(topClusterTransform)

        midClusterTransform = pm.cluster(curveCVs[1],rel=True)[1]
        midClusterTransform.rename(curveDrv.name() + '_mid_CLS')
        pivot = curveCVs[1].getPosition(space='world')
        midClusterTransform.setPivots(pivot)
        clusters.append(midClusterTransform)

        botClusterTransform = pm.cluster([curveCVs[1],curveCVs[2]],rel=True)[1]
        botClusterTransform.rename(curveDrv.name() + '_bot_CLS')
        botClusterTransform.getShape().originY.set(segments * - 0.5 )
        pivot = curveCVs[2].getPosition(space='world')
        botClusterTransform.setPivots(pivot)
        clusters.append(botClusterTransform)

        topCluster = topClusterTransform.listConnections(type='cluster')[0]
        botCluster = botClusterTransform.listConnections(type='cluster')[0]
        pm.percent(topCluster,curveCVs[1],v=0.5)
        pm.percent(botCluster,curveCVs[1],v=0.5)

        clsGrp = pm.group(clusters,n=curveDrv.name() + '_CLS_GRP')
        return clusters,clsGrp

'''        
def bdRibbonMain():
    selection = pm.ls(selection=True,type='transform')
    #if selection.count > 2:
    ribbon = bdRibbon(name='spine_SRF',start='start',end='end',segments=5)

bdRibbonMain()
'''