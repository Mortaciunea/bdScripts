import pymel.core as pm


def bdRigLegCtrl(side):
    print "Rigging %s side leg controller"%side

#create a group based rig for a leg
def bdRigLegBones(side):
    ikAnimCon = pm.ls(side + '*foot*IK_CON',type='transform')[0]
    legBonesNames = ['thigh','knee','foot','toe']
    legBones = []
    for bone in legBonesNames:
        legBone = pm.ls(side + '_' + bone + '_ik')[0]
        legBones.append(legBone)
        print legBone.name()
    toeEnd = pm.ls(side + '_' + 'toe_ik_end')[0]
    legBones.append(toeEnd)

    #START setup foot roll 
    footIk = pm.ikHandle(sol= 'ikRPsolver',sticky='sticky', startJoint=legBones[0],endEffector = legBones[2],name = side + '_foot_ikHandle')[0]
    footIk.visibility.set(0)
    ballIk = pm.ikHandle(sol= 'ikSCsolver',sticky='sticky', startJoint=legBones[2],endEffector = legBones[3],name = side + '_ball_ikHandle')[0]
    ballIk.visibility.set(0)
    toeIk = pm.ikHandle(sol= 'ikSCsolver',sticky='sticky', startJoint=legBones[3],endEffector = legBones[4],name = side + '_toe_ikHandle')[0]
    toeIk.visibility.set(0)
    #create the groups that will controll the foot animations ( roll, bend, etc etc)
    footHelpers = pm.ls(side + '*_helper',type='transform')

    ankleLoc = bdCreateOffsetLoc(legBones[2],side + '_ankle_loc')
    footLoc = bdCreateOffsetLoc(legBones[2],side + '_foot_loc')
    ballLoc = bdCreateOffsetLoc(legBones[3],side + '_ball_loc')
    ballTwistLoc = bdCreateOffsetLoc(legBones[3],side + '_ball_twist_loc')
    toeLoc = bdCreateOffsetLoc(legBones[4],side + '_toe_loc')
    toeBendLoc = bdCreateOffsetLoc(legBones[3],side + '_toe_bend_loc')


    innerLoc = outerLoc = heelLoc = ''
    for helper in footHelpers:
        if 'inner' in helper.name():
            innerLoc = bdCreateOffsetLoc(helper,side + '_inner_bank_loc')
        elif 'outer' in helper.name():
            outerLoc = bdCreateOffsetLoc(helper,side + '_outer_bank_loc')
        elif 'heel' in helper.name():
            heelLoc = bdCreateOffsetLoc(helper,side + '_heel_loc')

    #pm.delete(footHelpers)


    pm.parent(footIk, footLoc)
    pm.parent(ballIk, ballLoc)
    pm.parent(toeIk,toeBendLoc)
    pm.parent(toeBendLoc,toeLoc)

    pm.parent(footLoc,ballLoc)
    pm.parent(ballLoc,toeLoc)
    pm.parent(toeLoc,ballTwistLoc)
    pm.parent(ballTwistLoc,innerLoc)
    pm.parent(innerLoc,outerLoc)
    pm.parent(outerLoc,heelLoc)
    pm.parent(heelLoc,ankleLoc)

    print "start adding attributes"
    #add atributes on the footGrp - will be conected later to an anim controler
    autoRollAttrList = ['Roll','ToeStart','BallStraight']
    footAttrList = ['HeelTwist','BallTwist','TipTwist','Bank','ToeBend','KneeTwist']
    normalRollAttrList = ['HeelRoll','BallRoll','TipRoll']

    pm.addAttr(ikAnimCon ,ln='__AutoFootRoll__',nn='__AutoFootRoll__',at='bool'  )
    ikAnimCon.attr('__AutoFootRoll__').setKeyable(True)
    ikAnimCon.attr('__AutoFootRoll__').setLocked(True)

    pm.addAttr(ikAnimCon ,ln='Enabled',nn='Enabled',at='long'  )
    ikAnimCon.attr('Enabled').setKeyable(True)
    ikAnimCon.attr('Enabled').setMin(0)
    ikAnimCon.attr('Enabled').setMax(1)
    ikAnimCon.attr('Enabled').set(1)

    pm.addAttr(ikAnimCon ,ln='______',nn='______',at='bool'  )
    ikAnimCon.attr('______').setKeyable(True)
    ikAnimCon.attr('______').setLocked(True)	

    for attr in autoRollAttrList:
        pm.addAttr(ikAnimCon ,ln=attr,nn=attr,at='float' )
        ikAnimCon.attr(attr).setKeyable(True)

    pm.addAttr(ikAnimCon ,ln='__FootRoll__',nn='__FootRoll__',at='bool'  )
    ikAnimCon.attr('__FootRoll__').setKeyable(True)
    ikAnimCon.attr('__FootRoll__').setLocked(True)

    for attr in normalRollAttrList:
        pm.addAttr(ikAnimCon ,ln=attr,nn=attr,at='float' )
        ikAnimCon.attr(attr).setKeyable(True)

    pm.addAttr(ikAnimCon ,ln='__FootAttr__',nn='__FootAttr__',at='bool'  )
    ikAnimCon.attr('__FootAttr__').setKeyable(True)
    ikAnimCon.attr('__FootAttr__').setLocked(True)

    for attr in footAttrList:
        pm.addAttr(ikAnimCon ,ln=attr,nn=attr,at='float' )
        ikAnimCon.attr(attr).setKeyable(True)

    ikAnimCon.attr('ToeStart').set(40)
    ikAnimCon.attr('BallStraight').set(80)
    bdCreateReverseFootRoll(ikAnimCon,heelLoc,ballLoc,toeLoc)


    #connect the attributes
    ikAnimCon.attr('HeelTwist').connect(heelLoc.rotateY)
    ikAnimCon.attr('BallTwist').connect(ballTwistLoc.rotateY)
    ikAnimCon.attr('TipTwist').connect(toeLoc.rotateY)
    ikAnimCon.attr('ToeBend').connect(toeBendLoc.rotateX)

    bdConnectBank(ikAnimCon,innerLoc,outerLoc)





    #START no flip knee knee 
    mirror = 1
    if side == 'R':
        mirror = -1

    poleVectorLoc = pm.spaceLocator(name = side + '_knee_loc_PV')
    poleVectorLocGrp = pm.group(poleVectorLoc,n=poleVectorLoc + '_GRP')

    thighPos = legBones[0].getTranslation(space='world')
    poleVectorLocGrp.setTranslation([thighPos[0] + mirror * 5,thighPos[1],thighPos[2]])

    pm.poleVectorConstraint(poleVectorLoc,footIk)

    adlNode = pm.createNode('addDoubleLinear',name = side + '_adl_twist')

    adlNode.input2.set(mirror * 90)

    ikAnimCon.attr('KneeTwist').connect(adlNode.input1)
    adlNode.output.connect(footIk.twist)


    startTwist = mirror * 90
    limit = 0.001
    increment = mirror * 0.01

    while True:
        pm.select(cl=True)
        thighRot = pm.xform(legBones[0],q=True,ro=True,os=True)
        if ((thighRot[0] > limit)):
            startTwist = startTwist - increment
            adlNode.input2.set(startTwist)

        else:
            break	

    #END knee 

    pm.parent(ankleLoc,ikAnimCon)

def bdCreateOffsetLoc(destination,name):
    loc = pm.spaceLocator(n=name)
    destPos = destination.getTranslation(space='world')
    loc.setTranslation(destPos,space='world')
    return loc

def bdConnectChains():
    selection = pm.ls(sl=True)
    bindChainChildren = []

    if len(selection) == 2:
        bindChain = selection[0]
        ikfkCon = selection[1]		

        fkJnt = pm.ls(bindChain.name().replace('JNT','FK'))[0]
        ikJnt = pm.ls(bindChain.name().replace('JNT','IK'))[0]

        bdCreateBlend(bindChain,fkJnt,ikJnt,ikfkCon)

        bindChainChildren = bindChain.listRelatives(c=True, type= 'joint',ad=True)
        for child in bindChainChildren :
            if 'END' not in child.name():
                fkJnt = pm.ls(child.name().replace('JNT','FK'))[0]
                ikJnt = pm.ls(child.name().replace('JNT','IK'))[0]

                bdCreateBlend(child,fkJnt,ikJnt,ikfkCon)




def bdCreateBlend(bindJnt,fkJnt, ikJnt,ikfkCon):
    blendColorPos = pm.createNode('blendColors',name = bindJnt.name().replace('JNT','POS_BC'))
    blendColorRot = pm.createNode('blendColors',name = bindJnt.name().replace('JNT','ROT_BC'))
    blendColorScl = pm.createNode('blendColors',name = bindJnt.name().replace('JNT','SCL_BC'))

    ikfkCon.attr('IKFK').connect(blendColorPos.blender)
    ikfkCon.attr('IKFK').connect(blendColorRot.blender)
    ikfkCon.attr('IKFK').connect(blendColorScl.blender)

    fkJnt.translate.connect(blendColorPos.color1)
    ikJnt.translate.connect(blendColorPos.color2)
    blendColorPos.output.connect(bindJnt.translate)

    fkJnt.rotate.connect(blendColorRot.color1)
    ikJnt.rotate.connect(blendColorRot.color2)	
    blendColorRot.output.connect(bindJnt.rotate)

    fkJnt.scale.connect(blendColorScl.color1)
    ikJnt.scale.connect(blendColorScl.color2)	
    blendColorScl.output.connect(bindJnt.scale)

def bdCreateReverseFootRoll(ankleLoc,heelLoc,ballLoc,toeLoc):
    blendColorHeelAuto = pm.createNode('blendColors',name = heelLoc.name().replace('loc','auto_BC'))
    blendColorBallAuto= pm.createNode('blendColors',name = ballLoc.name().replace('loc','auto_BC'))
    blendColorToeAuto = pm.createNode('blendColors',name = toeLoc.name().replace('loc','auto_BC'))

    ankleLoc.attr('Enabled').connect(blendColorHeelAuto.blender)
    ankleLoc.attr('Enabled').connect(blendColorBallAuto.blender)
    ankleLoc.attr('Enabled').connect(blendColorToeAuto.blender)

    ankleLoc.attr('HeelRoll').connect(blendColorHeelAuto.color2R)
    ankleLoc.attr('BallRoll').connect(blendColorBallAuto.color2R)
    ankleLoc.attr('TipRoll').connect(blendColorToeAuto.color2R)

    #setup auto part
    clampHeel = pm.createNode('clamp',n=heelLoc.name().replace('loc','roll_CL'))
    clampHeel.minR.set(-90)

    setRangeToe = pm.createNode('setRange',n=toeLoc.name().replace('loc','linestep_SR'))
    setRangeToe.minX.set(0)
    setRangeToe.maxX.set(1)

    setRangeBall1 = pm.createNode('setRange',n=ballLoc.name().replace('loc','linestep_SR'))
    setRangeBall1.minX.set(0)
    setRangeBall1.maxX.set(1)
    setRangeBall1.oldMinX.set(0)

    mdToeRoll = pm.createNode('multiplyDivide',n=toeLoc.name().replace('loc','roll_MD'))
    mdBallRoll = pm.createNode('multiplyDivide',n=ballLoc.name().replace('loc','roll_MD'))

    mdBallRange2 = pm.createNode('multiplyDivide',n=ballLoc.name().replace('loc','roll_range_MD'))


    pmaBallRange = pm.createNode('plusMinusAverage',n=ballLoc.name().replace('loc','range_PMA'))
    pmaBallRange.input1D[0].set(1)
    pmaBallRange.operation.set(2)

    #connect the heel for negative rolls
    ankleLoc.attr('Roll').connect(clampHeel.inputR)
    clampHeel.outputR.connect(blendColorHeelAuto.color1R)
    blendColorHeelAuto.outputR.connect(heelLoc.rotateX)

    #connect the toe
    ankleLoc.attr('Roll').connect(setRangeToe.valueX)
    ankleLoc.attr('BallStraight').connect(setRangeToe.oldMaxX)
    ankleLoc.attr('ToeStart').connect(setRangeToe.oldMinX)

    ankleLoc.attr('Roll').connect(mdToeRoll.input2X)
    setRangeToe.outValueX.connect(mdToeRoll.input1X)

    mdToeRoll.outputX.connect(blendColorToeAuto.color1R)
    blendColorToeAuto.outputR.connect(toeLoc.rotateX)

    #connect the ball
    ankleLoc.attr('Roll').connect(setRangeBall1.valueX)
    ankleLoc.attr('ToeStart').connect(setRangeBall1.oldMaxX)

    setRangeToe.outValueX.connect(pmaBallRange.input1D[1])

    setRangeBall1.outValueX.connect(mdBallRange2.input1X)
    pmaBallRange.output1D.connect(mdBallRange2.input2X)



    ankleLoc.attr('Roll').connect(mdBallRoll.input2X)
    mdBallRange2.outputX.connect(mdBallRoll.input1X)	

    mdBallRoll.outputX.connect(blendColorBallAuto.color1R)
    blendColorBallAuto.outputR.connect(ballLoc.rotateX)
    #setup manual



def bdConnectBank(ikAnimCon,innerLoc,outerLoc):
    side = 'L'
    if 'R_' in ikAnimCon.name():
        side = 'R'
    clampInner = pm.createNode('clamp',n=innerLoc.name().replace('loc','CL'))
    if side == 'L':
        clampInner.maxR.set(90)
    else:
        clampInner.minR.set(-90)


    clampOuter = pm.createNode('clamp',n=outerLoc.name().replace('loc','CL'))
    if side == 'L':
        clampOuter.minR.set(-90)
    else:
        clampOuter.maxR.set(90)

    ikAnimCon.attr('Bank').connect(clampInner.inputR)
    clampInner.outputR.connect(innerLoc.rotateZ)

    ikAnimCon.attr('Bank').connect(clampOuter.inputR)
    clampOuter.outputR.connect(outerLoc.rotateZ)	

def bdScaleChain(side):
    pm.select(cl=True)
    ikAnimCon = pm.ls(side + '*foot*IK_CON',type='transform')[0]
    legBonesNames = ['Thigh','Knee','Foot']

    scaleBones = []
    for bone in legBonesNames:
        scaleBone = pm.ls(side + '_' + bone + '_SCL')[0]
        scaleBones.append(scaleBone)

    legBones = []
    for bone in legBonesNames:
        legBone = pm.ls(side + '_' + bone + '_IK')[0]
        legBones.append(legBone)


    distance1 = pm.createNode('distanceBetween',name = side + '_thigh_length')
    distance2 = pm.createNode('distanceBetween',name = side + '_femur_length')
    distanceStraight = pm.createNode('distanceBetween',name = side + '_straight_length')
    adlDistance = pm.createNode('addDoubleLinear',name = side + '_leg_length_ADL')
    condDistance = pm.createNode('condition',name = side + '_leg_length_CND')
    condDistance.colorIfTrueR.set(1)
    condDistance.secondTerm.set(1)
    condDistance.operation.set(5)

    mdScaleFactor = pm.createNode('multiplyDivide',name = side + '_leg_scaleFactor_MD')
    mdScaleFactor.operation.set(2)

    scaleBones[0].rotatePivotTranslate.connect(distance1.point1)
    scaleBones[1].rotatePivotTranslate.connect(distance1.point2)
    scaleBones[0].worldMatrix.connect(distance1.inMatrix1)
    scaleBones[1].worldMatrix.connect(distance1.inMatrix2)


    scaleBones[1].rotatePivotTranslate.connect(distance2.point1)
    scaleBones[2].rotatePivotTranslate.connect(distance2.point2)
    scaleBones[1].worldMatrix.connect(distance2.inMatrix1)
    scaleBones[2].worldMatrix.connect(distance2.inMatrix2)	

    scaleBones[0].rotatePivotTranslate.connect(distanceStraight.point1)
    ikAnimCon.rotatePivotTranslate.connect(distanceStraight.point2)
    scaleBones[0].worldMatrix.connect(distanceStraight.inMatrix1)
    ikAnimCon.worldMatrix.connect(distanceStraight.inMatrix2)		

    distance1.distance.connect(adlDistance.input1)
    distance2.distance.connect(adlDistance.input2)

    adlDistance.output.connect(mdScaleFactor.input2X)
    distanceStraight.distance.connect(mdScaleFactor.input1X)

    mdScaleFactor.outputX.connect(condDistance.firstTerm)
    mdScaleFactor.outputX.connect(condDistance.colorIfFalseR)

    condDistance.outColorR.connect(legBones[0].scaleX)
    condDistance.outColorR.connect(legBones[1].scaleX)

    print scaleBones
    print legBones




#bdRigLegBones('L')
#bdRigLegBones('R')
#bdConnectChains()

#bdScaleChain('R')
#bdScaleChain('L')