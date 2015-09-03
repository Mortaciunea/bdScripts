import pymel.core as pm



class bdMotionPathRbn():
        def __init__(self,*args,**kargs):
                self.numLocs = kargs.setdefault('sections')
                self.mpType = kargs.setdefault('type')
                self.mpCrv = ''
                self.startU = 0
                self.mpLength = 0
                self.bdBuildMotionPathRbn()


        def bdBuildMotionPathRbn(self):
                self.mpCrv = pm.ls(sl=1)[0]
                if self.mpType == 'closed':
                        startU = self.bdFindStart()
                self.mpLength = pm.arclen(self.mpCrv)
                print self.mpLength

                #oriCrv = self.bdGetOriCrv(self.mpCrv)
                #bdGetUPos(oriCrv)
                allCtrlGrp = pm.group(name = self.mpCrv.name().replace('crv','loc_grp'),empty=1)
                allCtrlGrp.setScalePivot(self.mpCrv.boundingBox().center())
                allCtrlGrp.setRotatePivot(self.mpCrv.boundingBox().center())                
                for i in range(0,self.numLocs,1):
                        ctrl = pm.circle(n=self.mpCrv.name().replace('crv','ctrl_' + str(i)))[0]
                        ctrl.ry.set(90)
                        ctrl.setScale([0.2,0.2,0.2])
                        ctrl.overrideEnabled.set(1)
                        ctrl.overrideColor.set(18)
                        pm.makeIdentity(ctrl,a=1)
                        ctrlGrp = pm.group(name = ctrl.name() + '_grp')
                        if self.mpType == 'closed':
                                self.bdFindStart()
                        if self.mpType == 'closed':
                                uPos = startU + i/(self.numLocs*1.0)
                        else:
                                uPos = startU + i/(self.numLocs-1.0)
                        if uPos > 1:
                                uPos = uPos - 1
                        print uPos
                        mp = pm.pathAnimation(ctrlGrp,c = self.mpCrv.name(),su = uPos,follow = 1,followAxis = 'x', upAxis='y',worldUpType="vector")
                        uAnimCrv = pm.listConnections('%s.uValue'%mp)
                        pm.delete(uAnimCrv)

                        pm.select(cl=1)
                        jnt = pm.joint(n=ctrl.name().replace('ctrl','JNT'))
                        pm.select(cl=1)
                        pm.parent(jnt,ctrl)
                        for axis in ['X','Y','Z']:
                                jnt.attr('translate'+axis).set(0)
                        pm.parent(ctrlGrp,allCtrlGrp)

        def bdFindStart(self):
                bb = self.mpCrv.boundingBox()
                bbMax = bb.max()
                bbCenter = bb.center()
                closestTo = pm.datatypes.Point(bbCenter.x,bbMax.y,bbMax.z)
                maxPoint = self.mpCrv.closestPoint(closestTo)
                uVal = self.mpCrv.getParamAtPoint(maxPoint)
                return uVal
                
        def bdGetOriCrv(self,crv):
                rebuiltCrv = pm.listConnections('%s.create'%crv.getShape().name(),plugs=1,c=0,s=1)[0]
                rebuiltCrv =  rebuiltCrv.nodeName()
                oriCrv = pm.listConnections('%s.inputCurve'%rebuiltCrv,plugs=1,c=0,s=1)[0]
                return oriCrv.nodeName()

        def bdGetUPos(self,crv):
                crv = pm.ls(crv)[0]
                length = pm.arclen(crv)
                print length
                cvs = crv.getCVs()
                numCvs = crv.numCVs()
                uPos = []
                l=0
                for i in range(numCvs-1):
                        p1 = crv.getCV(i)
                        p2 = crv.getCV(i+1)
                        p3 = p2.distanceTo(p1)
                        l = l + p3
                        print l

                print uPos
                return uPos