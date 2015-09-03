import maya.cmds as cmds
import pymel.core as pm
import json

import pymel.core as pm
import os

shapesFolder = 'd:\\bogdan\\shapes'

def bdJointOnCurveFromEdge():
    edgeCurveAll = pm.polyToCurve (form = 2,degree=1)
    pm.select(cl=1)
    meshName = pm.listConnections('%s.inputPolymesh'%edgeCurveAll[1])[0]

    edgeCurve = pm.ls(edgeCurveAll[0])
    numCv = edgeCurve[0].getShape().numCVs()
    baseJoints = []
    for i in range(numCv):
        pos = edgeCurve[0].getShape().getCV(i, space='world')
        baseJoints.append(pm.joint(n=meshName + '_jnt_' + str(i),p=pos))
    pm.joint(baseJoints[0],e=True, oj='xzy',secondaryAxisOrient='zdown',ch= True,zso=True)        

def bdCleanKeyframes():
    start = pm.playbackOptions(q=1,ast=1)
    end = pm.playbackOptions(q=1,aet=1)

    sel = pm.ls(sl=1,type='transform')

    for i in range(8,end-10,1):
        if not (i%4):
            print i
            pm.currentTime(i)
            pm.setKeyframe(sel,t=i)
        else:
            pm.cutKey(sel,clear=1,an='objects',iub=0,t=(i,i+1))

def bdCopyPasteChunli():
    #copy animation from the softimage fbx to the chunli mocap rig 
    fbxJnt = pm.ls('RM_Cnl_Middle:*',type='joint')

    skeleton = []
    for jnt in fbxJnt:
        skeletonJnt = ''
        skeletonJnt  = pm.ls(jnt.stripNamespace())
        if skeletonJnt :
            if (skeletonJnt[0].find('cloth') < 0) and (skeletonJnt[0].find('ribbon') < 0):
                print jnt
                pm.select(jnt)
                pm.copyKey()
                pm.select(skeletonJnt[0])
                pm.pasteKey()

def bdConstrainToSameParent():
    #afla jointurile care conduc un chain si constrain alt chain la driver
    parentSource = ''
    selection = pm.ls(sl=1, type= 'joint')
    children =  pm.listRelatives('export_Root_M', ad=True, type='joint')
    selection += children

    for jnt in selection:
        incomingCon = pm.listConnections('%s.translateX'%jnt,s=1,d=0,type='constraint')
        print incomingCon 
        for con in incomingCon:
            if 'parent' in con.name():
                parentSource = pm.listConnections(('%s.target[0].targetTranslate')%con,s=1,d=0)[0]
                print parentSource
                break

        geoTarget = pm.ls ('GEO:' + jnt.name())[0]
        pm.parentConstraint(parentSource,geoTarget,mo=1)
        pm.scaleConstraint(parentSource,geoTarget,mo=1)


def bdJointsOnEdge():
    edgeSelection = pm.ls(sl=True)
    vertices = pm.polyListComponentConversion(edgeSelection, fromEdge=1 , tv=1)
    pm.select(vertices)
    vertices = pm.ls(sl=1,fl=1)

    mesh = vertices[0].name().split('.')[0].replace('Shape','')
    locators = []

    for vert in vertices:
        #vertUV = vert.getUV()
        uv = pm.polyListComponentConversion(vert, fromVertex =1 , tuv=1)
        vertUV = pm.polyEditUV(uv[0] , query = True)
        locator = pm.spaceLocator(n='loc_%s'%vert)
        locators.append(locator)
        cnstr = pm.animation.pointOnPolyConstraint(vert,locator)
        pm.setAttr('%s.%sU0'%(cnstr,mesh),vertUV[0])
        pm.setAttr('%s.%sV0'%(cnstr,mesh),vertUV[1])

    for loc in locators:
        pm.select(cl=1)
        jnt = pm.joint(p=(0,0,0),name=loc.name().replace('loc','jnt'))
        print jnt
        pm.pointConstraint(loc,jnt,mo=False)


def bdApplyTsmFormat():
    exportHeadJnt  = pm.ls('export_Head_jnt')[0]
    facialJoints = exportHeadJnt.listRelatives(ad=True,type='joint')
    for facialJnt in facialJoints:
        if ('left' in facialJnt.name()):
            #export_eyelid_outcorner_fleshy_left
            newName = ''
            nameParts = facialJnt.name().replace('_left','').split('_')
            nameParts[1] = 'Left' + nameParts[1].title()
            print nameParts
            for part in nameParts:
                newName = newName + part + '_'

            facialJnt.rename(newName[:-1])
        elif ('right' in facialJnt.name()):
            #export_eyelid_outcorner_fleshy_left
            newName = ''
            nameParts = facialJnt.name().replace('_right','').split('_')
            nameParts[1] = 'Right' + nameParts[1].title()
            print nameParts
            for part in nameParts:
                newName = newName + part + '_'

            facialJnt.rename(newName[:-1])



def bdBuildChains():
    selection = pm.ls(sl = True)
    rootJnt = selection[0]
    selection.remove(rootJnt)
    rootPos = rootJnt.getTranslation(space = 'world')
    for jnt in selection:
        pm.select(cl=True)
        endPos = jnt.getTranslation(space = 'world')
        chainRoot = pm.joint(p = rootPos,radius = 0.2)
        endChain = pm.joint(p = endPos,radius = 0.2)
        pm.joint(chainRoot,e=True,zso = True, oj = 'xyz',sao = 'yup')
        pm.joint(endChain,e= True,oj= 'none', ch = True,zso = True)
        pm.delete(jnt)

def bdAddFingersSDK(side):
    fingers = ['Thumb','Index','Middle','Ring','Pinky']
    fingersPyNodes = []

    for finger in fingers:
        fingerCons = pm.ls(side + finger + '*_CON',type = 'transform')
        fingersPyNodes = []
        for con in fingerCons:
            fingersPyNodes.append(con)
            print con.name()

        for node in fingersPyNodes:
            print node.name()
            sdkCon = pm.duplicate(node,name = node.name().replace('CON','SDK'))
            for axis in ['X','Y','Z']:
                sdkCon[0].attr('translate' + axis).setKeyable(True)
                sdkCon[0].attr('translate' + axis).setLocked(False)
            sdkConRelatives = pm.listRelatives(sdkCon,ad = True)
            #print sdkConRelatives
            pm.delete(sdkConRelatives)
            pm.parent(node,sdkCon)

def bdAddExtraGrp(nameMaskCon,grpType,empty):

    controllers = pm.ls(nameMaskCon,type = 'transform')
    conPyNodes = []
    for con in controllers:
        conPyNodes.append(con)

    for node in conPyNodes:
        if empty:
            pm.select(cl=True)
            conGrp = pm.group(name = node.name() + '_' + grpType)
            pos = node.getTranslation(space='world')
            rot = node.getRotation(space='world')
            conGrp.setTranslation(pos)
            conGrp.setRotation(rot)
            parent = node.getParent()
            pm.parent(conGrp,parent)

        else:
            conGrp = pm.duplicate(node,name = node.name().replace('CON',grpType))
        '''
		for axis in ['X','Y','Z']:
			conGrp[0].attr('translate' + axis).setKeyable(True)
			conGrp[0].attr('translate' + axis).setLocked(False)
		'''
        conGrpRelatives = pm.listRelatives(conGrp,ad = True)
        #print sdkConRelatives
        pm.delete(conGrpRelatives)
        pm.parent(node,conGrp)
#TO IMPLEMENT
'''
def bdCreateIkTwist(side):
	driver = side + 'hand_bnd_jnt_00'
	twistLocators = cmds.ls(side + '_arm_ik_twist_loc_*')
	for l in twistLocators:
		print l
	#twistMd = cmds.createNode('multiplyDivide',name= multDivName)

'''

#order - fk chain root, ik chain root, bind chain
def bdConstrainChain(ik,fk,bind):
    ikChild = cmds.listRelatives(ik, c=True, typ = 'joint')
    fkChild = cmds.listRelatives(fk, c=True, typ = 'joint')
    bindChild = cmds.listRelatives(bind, c=True, typ = 'joint')

    cmds.parentConstraint(ik ,bind ,mo=True,weight=1)
    cmds.parentConstraint(fk ,bind ,mo=True,weight=0)

    if (ikChild != None) and (bindChild != None) and (fkChild != None):
        bdConstrainChain(ikChild,fkChild,bindChild)	

# Create an IKFK switch
def bdConnectSwitch(root,mdNode,revNode):
    parentCnstr = cmds.listRelatives(root,c=True, typ = 'parentConstraint')
    cRoot = cmds.listRelatives(root, c=True, typ = 'joint')

    #check for a parent constraint
    if parentCnstr != None:
        attr = cmds.listAttr(parentCnstr, v=True,ud=True)
        cmds.connectAttr(mdNode + '.outputX',(str(parentCnstr[0]) + "." + str(attr[0])),force=True)
        cmds.connectAttr(revNode + '.outputX',(str(parentCnstr[0]) + "." + str(attr[1])),force=True)
        #check for a child
        if cRoot != None:
            bdConnectSwitch(cRoot,mdNode,revNode)


def bdRecursiveIKFKSwitch(side,limb,controller):
    ctrlAnim = [controller]

    bdAddSeparatorAttr(ctrlAnim[0],'_Switch_')
    cmds.addAttr( ctrlAnim[0] ,ln="IKFK" ,at='long'  ,min=0 ,max=1 ,dv=0)
    cmds.setAttr((ctrlAnim[0] + "." + 'IKFK'),keyable=True)

    multDivName = side  + limb + 'ikfkSwitchMD'
    revName = side  + limb + 'switchRev'
    multDivNode = cmds.createNode('multiplyDivide',name= multDivName)
    revNode = cmds.createNode('reverse',name= revName )

    cmds.connectAttr((ctrlAnim[0] + '.IKFK'),multDivName + '.input1X',force=True)
    cmds.connectAttr( multDivName+ '.outputX',revName + '.inputX',force=True)

    startJoint = cmds.ls(side + limb + 'bnd_jnt')
    bdConnectSwitch(startJoint[0],multDivName,revName)



def bdAddAttribute(object, attrList,attrType ):
    for a in attrList:
        cmds.addAttr(object,ln=a,at = attrType)
        cmds.setAttr((object + "." + a),e=True, keyable=True)

def bdAddAttributeMinMax(object, attrList,attrType,minVal,maxVal,defVal ):
    for a in attrList:
        cmds.addAttr(object,ln=a,at = attrType,min = minVal,max=maxVal,dv=defVal)
        cmds.setAttr((object + "." + a),e=True, keyable=True)

def bdAddSeparatorAttr(object, attr):
    cmds.addAttr(object ,ln=attr,nn=attr,at='bool'  )
    cmds.setAttr((object + "." + attr),keyable = True)
    cmds.setAttr((object + "." + attr),lock = True)


def bdCreateGroup(objects,grpName,pivot,rot=False):
    grp = cmds.group(objects,n=grpName)
    footJntPos = cmds.xform(pivot,q=True,ws=True,t=True)
    cmds.move(footJntPos[0],footJntPos[1],footJntPos[2],grp + '.rp',grp + '.sp')
    return grp


def bdCleanUpController(object,attrList,lockFlag=True):
    for attr in attrList:
        cmds.setAttr(object + '.' + attr,lock=lockFlag,keyable=False,channelBox=False)

def bdCreateOffsetLoc(destination,name):
    loc = pm.spaceLocator(n=name)
    destPos = destination.getScalePivot()
    loc.setTranslation(destPos)
    locGrp = cmds.duplicate(loc,name=str(loc[0] + "_GRP"))
    cmds.parent(loc,locGrp)

def bdAddIk(start,end,ikType,ikName):
    cmds.ikHandle(sol= ikType,sticky='sticky', startJoint=start,endEffector = end,name = ikName)


def bdBuildBoxController(target,ctrlName,scale):
    defaultPointsList = [(1,-1,1),(1,-1,-1),(-1,-1,-1),(-1,-1,1),(1,1,1),(1,1,-1),(-1,1,-1),(-1,1,1)]
    pointsList = []
    for p in defaultPointsList:
        pointsList.append(( p[0] * scale, p[1] * scale , p[2] * scale ))

    knotsList = [i for i in range(16)]
    curvePoints = [pointsList[0], pointsList[1], pointsList[2], pointsList[3], 
                   pointsList[7], pointsList[4], pointsList[5], pointsList[6],
                   pointsList[7], pointsList[3], pointsList[0], pointsList[4],
                   pointsList[5], pointsList[1], pointsList[2], pointsList[6] ]

    ctrl = cmds.curve(d=1, p = curvePoints , k = knotsList )
    ctrl = cmds.rename(ctrl,ctrlName)
    ctrlGrp = cmds.group(ctrl,n=ctrlName.replace("anim","anim_CON"))
    targetPos = cmds.xform(target,q=True,ws=True,t=True)
    cmds.move(targetPos[0],targetPos[1],targetPos[2],ctrlGrp)
    return [ctrl,ctrlGrp]

def bdBuildSquareController(target,ctrlName,scale,pivotOfset=0.5):
    defaultPointsList = [(-1,1,0),(1,1,0),(1,-1,0),(-1,-1,0)]
    pointsList = []
    targetPos = pm.xform(target,q=True,ws=True,t=True)
    for p in defaultPointsList:
        pointsList.append(( p[0] * scale, p[1] * scale , p[2] * scale ))

    curvePoints = [pointsList[0], pointsList[1], pointsList[2], pointsList[3],pointsList[0]]

    ctrl = pm.curve(d=1, p = curvePoints )
    ctrl.rename(ctrlName)
    ctrlGrp = pm.group(ctrl,n=ctrlName.replace("anim","anim_CON"))
    pm.move(targetPos[0],targetPos[1],targetPos[2],ctrlGrp,ws=True)
    ctrl.translateZ.set(pivotOfset)
    pm.makeIdentity(ctrl, apply=True, translate=True, rotate=True, scale=True )
    ctrl.setPivots([0,0,0])
    return [ctrl,ctrlGrp]

def bdBuildSphereController(target,ctrlName,scale):
    circleA = cmds.circle(n = ctrlName + 'A',nr=(0, 1, 0), c=(0, 0, 0),radius=scale )
    circleB = cmds.circle(n = ctrlName + 'B',nr=(1, 0, 0), c=(0, 0, 0), radius=scale  )
    circleBShape = cmds.listRelatives(circleB[0],c=True)
    circleC = cmds.circle(n = ctrlName + 'C',nr=(0, 0, 1), c=(0, 0, 0),radius=scale  )
    circleCShape = cmds.listRelatives(circleC[0],c=True)
    cmds.parent(circleBShape[0],circleA[0],r=True,s=True)
    cmds.parent(circleCShape[0],circleA[0],r=True,s=True)
    cmds.delete(circleB,circleC)
    ctrl = cmds.rename(circleA[0],ctrlName)
    ctrlGrp = cmds.group(ctrl,n=ctrlName.replace("anim","anim_CON"))	
    targetPos = cmds.xform(target,q=True,ws=True,t=True)
    targetRot = cmds.xform(target,q=True,ws=True,ro=True)
    cmds.move(targetPos[0],targetPos[1],targetPos[2],ctrlGrp)
    cmds.rotate(targetRot[0],targetRot[1],targetRot[2],ctrlGrp)

def bdAddDamp(attribute, axes ):
    selection = cmds.ls(sl=True)
    source  = selection[0]
    target = selection[1]

    multDivName = target.replace("jnt","MD")
    multDivNode = cmds.createNode('multiplyDivide',name= multDivName)
    for axis in axes:
        cmds.connectAttr((source + '.' + attribute + axis.upper()),multDivName + '.input1' + axis.upper(),force=True)
        cmds.connectAttr( multDivName+ '.output' + axis.upper() ,target + '.' + attribute + axis.upper(),force=True)	



def bdGetJntFromMesh():
    import pymel.core as pm
    sel = pm.ls(sl=True)[0].getShape()
    skinCls = pm.listConnections('%s.inMesh'%sel)
    print skinCls
    jnts = pm.skinCluster(skinCls,q=True,influence=True)
    names = [str(jnt.name()) for jnt in jnts]
    pm.select([names])    

def bdLocOnJnt():
    try:
        rootJnt = pm.ls(sl=True)[0]
    except:
        pm.warning('Nothing selected')
        return
    try:
        crvPath  = pm.ls(sl=True)[1]
    except:
        pm.warning('No curve selected')
        return

    allJnt = rootJnt.listRelatives(f=True, ad=True,type='joint')
    allJnt = allJnt + [rootJnt]
    allJnt.reverse()

    locators = []
    for jnt in allJnt:
        print jnt
        loc = pm.spaceLocator(name = jnt.name().replace( '_jnt','_loc'))
        locGrp = pm.group(n = loc.name() + '_grp')

        tempCnstr = pm.pointConstraint(jnt,locGrp,mo=0);
        pm.delete(tempCnstr )
        locators.append(locGrp)

    bdMultiMotionPath(crvPath, locators)
    bdParentJntToLocs(allJnt)

def bdMultiMotionPath(crvPath, objects,interval=2,speed=20):
    numObjects = len(objects)
    startTime = pm.playbackOptions(q=1,minTime=1)
    endTime = pm.playbackOptions(q=1,maxTime=1)
    allMotionPath = []
    for i in range(numObjects):
        #motionPath = pm.pathAnimation(objects[i],c=crvPath,n=objects[i].name() + '_mp',stu = i*interval , etu = i*interval + speed,follow = 1, followAxis = 'x', upAxis = 'y',fractionMode =1)
        pm.currentTime(0)
        motionPath = pm.pathAnimation(objects[i],c=crvPath,n=objects[i].name() + '_mp',follow = 1, followAxis = 'x', upAxis = 'y',fractionMode =1)
        allMotionPath.append(motionPath)
        pm.setAttr(motionPath + '.worldUpType',1)


    bdSetStartMp(allMotionPath)
    startCycleFrame = i*interval + speed + 2

    #bdCyclePath(allMotionPath,startCycleFrame,interval,speed,repeat = 4)

def bdCyclePath(allMotionPath,startCycleFrame,interval,speed,repeat):
    scaleOffset = 1
    for i in range(1,len(allMotionPath)+1):
        print 'locator ',i
        for r in range(repeat):
            loc = allMotionPath[i-1].replace('_grp_mp','')
            if i == 0:
                pm.setKeyframe(allMotionPath[i-1] + '.uValue', time = r * (startCycleFrame + 1)+  i*interval , value = 0)
                bdScaleLocAnim(loc,r * (startCycleFrame + 1)+  i*interval -1 ,0.001)
                bdScaleLocAnim(loc,r * (startCycleFrame + 1)+  i*interval + scaleOffset -1, 1)
                pm.setKeyframe(allMotionPath[i-1] + '.uValue', time = r * (startCycleFrame + 1)+ i*interval + speed, value = 1)
                bdScaleLocAnim(loc,r * (startCycleFrame + 1)+ i*interval + speed - scaleOffset -1 ,1)
                bdScaleLocAnim(loc,r * (startCycleFrame + 1)+ i*interval + speed  -1 ,0.001)
                pm.setKeyframe(allMotionPath[i-1] + '.uValue', time = (r + 1) * startCycleFrame  , value = 1)
                pm.setKeyframe(allMotionPath[i-1] + '.uValue', time = (r + 1) * startCycleFrame  + 1, value = 0)
                bdScaleLocAnim(loc,(r + 1) * startCycleFrame  -1,0.001)
            else:
                pm.setKeyframe(allMotionPath[i-1] + '.uValue', time = r * startCycleFrame +  i*interval , value = 0)
                bdScaleLocAnim(loc,r * (startCycleFrame )+  i*interval -1 ,0.001)
                bdScaleLocAnim(loc,r * (startCycleFrame )+  i*interval + scaleOffset -1 , 1)

                pm.setKeyframe(allMotionPath[i-1] + '.uValue', time = r * startCycleFrame + i*interval + speed, value = 1)
                bdScaleLocAnim(loc,r * (startCycleFrame )+ i*interval + speed - scaleOffset -1 ,1)
                bdScaleLocAnim(loc,r * (startCycleFrame )+ i*interval + speed  -1 ,0.001)

                pm.setKeyframe(allMotionPath[i-1] + '.uValue', time = (r + 1) * startCycleFrame  , value = 1)
                pm.setKeyframe(allMotionPath[i-1] + '.uValue', time = (r + 1) * startCycleFrame  + 1, value = 0)
                bdScaleLocAnim(loc,(r + 1) * startCycleFrame  -1 ,0.001)




def bdScaleLocAnim(loc,time,val):
    pm.setKeyframe(loc + '.scaleX', time = time, value = val)
    pm.setKeyframe(loc+ '.scaleY', time = time, value = val)
    pm.setKeyframe(loc + '.scaleZ', time = time, value = val)

def bdParentJntToLocs(allJnt):
    for jnt in allJnt:
        loc = pm.ls(jnt.name().replace('_jnt','_loc'))[0]
        pm.parentConstraint(jnt.name().replace('_jnt','_loc'),jnt,mo=0)
        #pm.scaleConstraint(jnt.name().replace('_jnt','_loc'),jnt,mo=0)
        loc.scaleX.connect(jnt.scaleX)
        loc.scaleY.connect(jnt.scaleY)
        loc.scaleZ.connect(jnt.scaleZ)
        jntMp = pm.ls(jnt.name().replace('_jnt','_loc_grp_mp'))

def bdSetStartMp(allMotionPath):
    animCtrl = pm.ls('L_crying_CTL')[0]
    interval = 1.0/(len(allMotionPath) -1 )
    for i in range(len(allMotionPath)):
        uAnim = pm.listConnections('%s.uValue'%allMotionPath[i])
        if uAnim:
            pm.delete(uAnim)
        motionPath = pm.ls(allMotionPath[i])[0]
        remapNode = pm.createNode('remapValue',n=motionPath.name().replace('_grp_mp','_rv'))
        pm.setAttr(remapNode + ".color[0].color_Color",0, 0, 0, type='double3' )
        pm.setAttr(remapNode + ".color[2].color_Position", 0.5)
        pm.setAttr(remapNode + ".color[2].color_Color",1 - i*interval, 0, 0, type='double3' )
        pm.setAttr(remapNode + ".color[0].color_Interp", 1)
        pm.setAttr(remapNode + ".color[1].color_Interp", 1)
        pm.setAttr(remapNode + ".color[2].color_Interp", 1)

        remapNode.inputMax.set(10)
        #remapNode.outputMax.set(1 - i*interval)

        animCtrl.attr('crying_tears').connect(remapNode.inputValue)
        #remapNode.outValue.connect(motionPath.uValue)
        remapNode.outColorR.connect(motionPath.uValue)
        

def bdCreateDistanceCnd():
    jnt = pm.ls(sl=1)[0]
    #loc1,loc2,jnt = pm.ls(sl=1)
    jntCnstr = jnt.listRelatives(type='pointConstraint')[0]
    loc1,loc2 = pm.pointConstraint(jntCnstr,q=1,tl=1)
    
    matrixLoc1 = pm.createNode('decomposeMatrix',name = loc1.name().replace('_loc','_dm'))
    matrixLoc2 = pm.createNode('decomposeMatrix',name = loc2.name().replace('_loc','_dm'))
    pma = pm.createNode('plusMinusAverage',name = loc1.name().replace('_loc','_pma'))
    pma.operation.set(2)
    rv = pm.createNode('remapValue',name = loc1.name().replace('_loc','_rv'))
    rv.inputMin.set(0.1)
    
    rev = pm.createNode('reverse',name = loc1.name().replace('_loc','_rev'))

    
    loc1.worldMatrix[0].connect(matrixLoc1.inputMatrix)
    loc2.worldMatrix[0].connect(matrixLoc2.inputMatrix)
    matrixLoc1.outputTranslateY.connect(pma.input1D[0])
    matrixLoc2.outputTranslateY.connect(pma.input1D[1])
    pma.output1D.connect(rv.inputValue)
    
    rv.outValue.connect(jntCnstr.attr(loc1.name() + 'W0'))
    rv.outValue.connect(rev.inputX)
    rev.outputX.connect(jntCnstr.attr(loc2.name() + 'W1'))
    
def bdPoinOnPoly():
    verts = pm.ls(sl=1,fl=1)
    vertsUV = {}
    locs = []
    
    for i in range(len(verts)):
        loc = pm.spaceLocator(n='eyelid_' + str(i) + '_drv_loc')
        locs.append(loc)
        melCmd = 'doCreatePointOnPolyConstraintArgList 2 {   "0" ,"0" ,"0" ,"1" ,"" ,"1" ,"0" ,"0" ,"0" ,"0" };'
        pm.select(verts[i])
        pm.select(loc,add=1)
        pm.mel.eval(melCmd)    
        
def bdBuildSplineSolverScale():
    selection = pm.ls(sl=1,type='transform')
    startJoint = ''
    if selection:
        startJoint = selection[0]
    else:
        return
    
    print startJoint
    
    ikSpline  = pm.listConnections(startJoint,type='ikHandle')[0]
    print ikSpline  
    solver = ikSpline.ikSolver.inputs()[0]
    
    if 'ikSplineSolver' in solver.name():
        sclChain = pm.duplicate(startJoint,name = startJoint.name() + '_SCL')[0]
        sclChainAll = sclChain.listRelatives(f=True, ad=True,type='joint')
        
        print sclChainAll  
        
        for sclJnt in sclChainAll:
            pm.rename(sclJnt,sclJnt+'_SCL')
        
        splineCurve = pm.listConnections(ikSpline, type = 'nurbsCurve')[0]
    
        effector = pm.listConnections(ikSpline ,source=True, type='ikEffector')[0]
        endJoint = pm.listConnections(effector,source=True, type='joint')[0]
        jointChain = startJoint.listRelatives(f=True, ad=True,type='joint')
        jointChain  = jointChain + [startJoint]
        jointChain.reverse()
        print jointChain
        
        splineCurveScl = pm.duplicate(splineCurve,name = splineCurve.name().replace('crv','crv_scl'))
        strArclenSCL = pm.arclen(splineCurveScl,ch=True)
        strArclenCRV = pm.arclen(splineCurve,ch=True)
        arclenSCL = pm.ls( strArclenSCL ) [0]
        arclenCRV = pm.ls( strArclenCRV ) [0]
        arclenSCL.rename(splineCurveScl[0].name() + '_length')
        arclenCRV.rename(splineCurve.name() + '_length')
        
        mdScaleFactor = pm.createNode('multiplyDivide', name = splineCurve.name().replace('crv','crv_scaleFactor_md'))
        arclenCRV.arcLength.connect(mdScaleFactor.input1X)
        arclenSCL.arcLength.connect(mdScaleFactor.input2X)
        mdScaleFactor.operation.set(2)
    
        for jnt in jointChain[1:]:
            mdJntTr = pm.createNode('multiplyDivide', name = jnt + '_trX_MD')
            #mdJntTr.operation.set(2)
            
            sclJnt = pm.ls(jnt + '_SCL')[0]
            mdScaleFactor.outputX.connect(mdJntTr.input2X)
            sclJnt.translateX.connect(mdJntTr.input1X)
            mdJntTr.outputX.connect(jnt.translateX)
            

def bdScaleAlong():
    travelLoc = pm.ls('Mag01TailFront_scaleFollicle')[0]
    rigJnt = pm.ls(sl=1,type='joint')
    
    if rigJnt:
        for jnt in rigJnt:
            distance = pm.shadingNode('distanceBetween',asUtility=1,n=jnt.name() + '_DB')
            print distance
            pm.connectAttr(travelLoc + '.worldMatrix[0]',distance + '.inMatrix1')
            pm.connectAttr(travelLoc + '.rotatePivotTranslate',distance + '.point1')
            flc = jnt.getParent()
            print flc 
            pm.connectAttr(flc + '.worldMatrix[0]',distance + '.inMatrix2')
            pm.connectAttr(flc + '.rotatePivotTranslate',distance + '.point2')
            
            rv = pm.shadingNode('remapValue',asUtility=1,n=jnt.name() + '_RV')
            rv.inputMin.set(3)
            rv.inputMax.set(0)
            rv.outputMin.set(1)
            rv.outputMax.set(2)
            pm.connectAttr(distance + '.distance',rv.name() + '.inputValue')
            pm.connectAttr(rv.name() + '.outValue',jnt.name() + '.scaleX')
            pm.connectAttr(rv.name() + '.outValue',jnt.name() + '.scaleY')
            pm.connectAttr(rv.name() + '.outValue',jnt.name() + '.scaleZ')

def creatNullParentGrp(suffix):
    selection = pm.ls(sl=1)
    if selection:
        ctrl = selection[0]
        pm.select(cl=1)
        nullGrp = pm.group(n=ctrl.name() + suffix)
        temp = pm.parentConstraint(ctrl,nullGrp)
        pm.delete(temp)
        ctrlParent = ctrl.getParent()
        pm.parent(nullGrp,ctrlParent)
        pm.parent(ctrl,nullGrp)
        
def bdAddFkCtrls(scale=1,color=1):
    selection = pm.ls(sl=1,type='joint')
    pm.select(cl=1)
    if selection:
        for rootJnt in selection:
            chainJnt = rootJnt.listRelatives(type='joint', ad=True, f=True)
            #chainJnt.reverse()
            chainJnt.append(rootJnt)
            
            for jnt in chainJnt:
                pos = jnt.getTranslation(space='world')
                rot = jnt.getRotation(space='world')
                pm.select(cl=1)
                ctrl = pm.circle(name = jnt.name() + '_ctrl',c=[0,0,0],nr=[1,0,0],ch=0,radius = scale)[0]
                ctrlGrp = pm.group(ctrl,n=ctrl.name() + '_grp')
                pm.select(cl=1)    
                ctrlGrp.setTranslation(pos,space='world')
                ctrlGrp.setRotation(rot,space='world')
                
                ctrl.getShape().overrideEnabled.set(1)
                ctrl.getShape().overrideColor.set(color)
                

    
def crvShapeSave():
    selection = pm.ls(sl=1)
    if selection:
        for obj in selection:
            shapes = obj.getShapes()
            objName = obj.name().replace('|','_')
            for shape in shapes:
                if shape.type() == 'nurbsCurve':
                    shapeInfoDict = getShapeInfo(shape)
                    shapeFile = os.path.join(shapesFolder,objName+'.json')
                    with open(shapeFile, 'w') as outfile:
                        json.dump(shapeInfoDict, outfile)

def getShapeInfo(shape):
    name = shape.name()
    cvNum = shape.numCVs()
    cvPos = []
    
    for i in range(cvNum):
        pos = pm.xform(shape.name() + '.cv[' + str(i) + ']',q=1,a=1,t=1,ws=1)
        cvPos.append(pos)
        
    info = {'name':name, 'cvsPos':cvPos}
    return info

def crvShapeLoad():
    selection = pm.ls(sl=1)
    if selection:
        for obj in selection:
            shapes = obj.getShapes()
            objName = obj.name().replace('|','_')
            for shape in shapes:
                if shape.type() == 'nurbsCurve':
                    shapeFile = os.path.join(shapesFolder,objName+'.json')
                    if os.path.isfile(shapeFile):
                        with open(shapeFile) as data_file:    
                            shapeInfo = json.load(data_file)
                            setShape(shape,shapeInfo)

def setShape(shape,shapeInfo):
    cvPos = shapeInfo['cvsPos']
    for i in range(len(cvPos)):
        pm.move(shape.name() + '.cv[' + str(i) + ']',cvPos[i][0],cvPos[i][1],cvPos[i][2],a=1,ws=1,)
        
    #shape.setCVs(cvPos,space='world')
    #shape.updateCurve()