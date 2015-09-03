import bdRigUtils
reload(bdRigUtils)
import maya.cmds as cmds


def bdRigLegCtrl(side):
	print "Rigging %s side leg controller"%side
	
#create a group based rig for a leg
def bdRigLegBones(side):
        legBones = ['leg','knee','foot','toe','toe_end']
        for i in range(len(legBones)):
                legBones[i] = side + '_' + legBones[i] + '_ik_jnt'
	#START setup foot roll 
	legIk = cmds.ikHandle(sol= 'ikRPsolver',sticky='sticky', startJoint=legBones[0],endEffector = legBones[2],name = side + '_leg_ikHandle')
	footIk = cmds.ikHandle(sol= 'ikSCsolver',sticky='sticky', startJoint=legBones[2],endEffector = legBones[3],name = side + '_foot_ikHandle')
	toeIk = cmds.ikHandle(sol= 'ikSCsolver',sticky='sticky', startJoint=legBones[3],endEffector = legBones[4],name = side + '_toe_ikHandle')
	#create the groups that will controll the foot animations ( roll, bend, etc etc)
	bdRigUtils.bdCreateOffsetLoc(legBones[2],side + '_foot_loc')
	bdRigUtils.bdCreateOffsetLoc(legBones[3],side + '_ball_loc')
	bdRigUtils.bdCreateOffsetLoc(legBones[4],side + '_toe_loc')
	bdRigUtils.bdCreateOffsetLoc(legBones[2],side + '_heel_loc')
	
	cmds.parent([side + '_ball_loc_grp',side + '_toe_loc_grp',side + '_heel_loc_grp'],side + '_foot_loc')
	cmds.parent([legIk[0],footIk[0],toeIk[0]],side + '_foot_loc')
	cmds.parent([legIk[0]],side + '_ball_loc')
	cmds.parent([side + '_ball_loc_grp',footIk[0],toeIk[0]],side + '_toe_loc')
	cmds.parent([side + '_toe_loc_grp'],side + '_heel_loc')
	

	#add atributes on the footGrp - will be conected later to an anim controler
	attrList = ['Heel','Ball','Toe','kneeTwist']
	animCtrl = cmds.ls(side + '_foot_ik_anim')[0]
	bdRigUtils.bdAddSeparatorAttr(animCtrl,'______')
	bdRigUtils.bdAddAttribute(animCtrl,attrList,'float')
	#connect the attributes
	cmds.connectAttr(animCtrl + '.' + attrList[0],side + '_heel_loc' + '.rz')
	cmds.connectAttr(animCtrl + '.' + attrList[1],side + '_ball_loc' + '.rz')
	cmds.connectAttr(animCtrl + '.' + attrList[2],side + '_toe_loc' + '.rz')
	#setup the controller 
	bdRigLegCtrl(side)
	#END setup foot roll 
	
	
	
	#START no flip knee knee 
	reverse = 1
	if side == 'right':
		reverse = -1
		
	poleVectorLoc = cmds.spaceLocator()
	poleVectorLoc = cmds.rename(poleVectorLoc,side + 'poleVector')
	poleVectorLocGrp = cmds.group(poleVectorLoc,n=poleVectorLoc + '_GRP')
	
	thighPos = cmds.xform(legBones[0],q=True,ws=True,t=True)
	
	cmds.move(thighPos[0] + reverse * 5,thighPos[1],thighPos[2],poleVectorLocGrp)
	
	cmds.poleVectorConstraint(poleVectorLoc,legIk[0])
	
	shadingNodeADL = cmds.shadingNode('addDoubleLinear', asUtility=True,name = side + 'adl_twist')
	ikZval = cmds.getAttr(str(legIk[0]) + '.rotateZ')
	cmds.setAttr(shadingNodeADL + '.input2',reverse * 90)
	cmds.connectAttr(animCtrl + '.' + attrList[3],shadingNodeADL + '.input1')
	cmds.connectAttr(shadingNodeADL + '.output',legIk[0] + '.twist')
	thighRot = cmds.xform(legBones[0],q=True,ro=True,ws=True)
	startTwist = reverse * 90
	limit = 0.001
	increment = reverse * 0.01

	while True:
		cmds.select(cl=True)
		thighRot = cmds.xform(legBones[0],q=True,ro=True,os=True)
		print thighRot[0]
		if ((thighRot[0] > limit)):
			startTwist = startTwist - increment
			cmds.setAttr(shadingNodeADL + '.input2',startTwist )
		else:
			break	
	
	#END knee 


        