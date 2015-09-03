import pymel.core as pm


class VarFk:
    #add attrs for ctrl: Position, Falloff, Joints Affected
    def __init__(self,**kargs):
        self.ctrlList = []
        self.varFkJnt = []
        self.numVarJnt = 0
        self.ctrlPma = []
        self.rotGrp = []
        
    def addNullGroups(self,jnt):
        jntPos = jnt.getTranslation(space='world')
        startGrp = ''
        jntParent = jnt.getParent()
        print jntParent
        
        for i in range(3):
            pm.select(cl=1)
            grp = pm.group(name = jnt.name() + '_ctrl_' + str(i) + '_rot')
            if i==0:
                pm.parent(grp,jntParent)
                pm.parent(jnt,grp)
                startGrp = grp
            else:
                pm.parent(grp,jntParent)
                pm.parent(startGrp,grp)
                startGrp = grp
            

    def addJntPosAttr(self,jntList,srf):
        cposNode = pm.shadingNode( 'closestPointOnSurface', asUtility = True )
        decMtx = pm.shadingNode('decomposeMatrix',asUtility = True )
        
        srf.getShape().worldSpace[0].connect(cposNode.inputSurface)
        decMtx.outputTranslate.connect(cposNode.inPosition)
        
        for jnt in jntList:
            jnt.worldMatrix[0].connect(decMtx.inputMatrix)
            pm.addAttr(jnt, shortName='jointPosition', longName='jointPosition', defaultValue=0, minValue=0, maxValue=1)
            jntPos = cposNode.parameterV.get()
            jnt.jointPosition.set(jntPos)
            jnt.worldMatrix[0].disconnect(decMtx.inputMatrix)
        
        pm.delete([cposNode,decMtx])
    
    
    def addCtrlJntAffected(ctrl,jntTotal):
        pm.addAttr(ctrl,longName='jointsAffected', defaultValue=0, minValue=0.0, maxValue=jntTotal,keyable=False)
        
        numJntMd = pm.shadingNode('multiplyDivide', asUtility = True )
        numJntSr = pm.shadingNode('setRange', asUtility = True )
        
        ctrl.falloff.connect(numJntMd.input1.input1X)
        numJntMd.input2.input2X.set(2)
        numJntMd.output.outputX.connect(numJntSr.value.valueX)
        
        numJntSr.maxX.set(jntTotal)
        numJntSr.oldMaxX.set(1)
        
        numJntSr.outValueX.connect(ctrl.jointsAffected)
    
    def setUpCtrl(ctrl):
        #posMinFalloff
        print 'Setting up ctrl'
    
    def addPmaCtrl(ctrlList):
    
selection = pm.ls(sl=1,type='joint')

if selection:
    for jnt in selection:
        addNullGroups(jnt)