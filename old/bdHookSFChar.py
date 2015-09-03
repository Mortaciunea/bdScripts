import pymel.core as pm

def bdChainConstraint(source,target,includeRoot):
	#selection = pm.ls(sl=True)
	source = pm.ls(source)[0]
	target = pm.ls(target)[0]

	sourceChildren = source.listRelatives(f=True, ad=True,type='joint')
	if includeRoot:
		sourceAll = sourceChildren + [source]
	else:
		sourceAll = sourceChildren 

	targetChildren = target.listRelatives(f=True, ad=True,type='joint')
	if includeRoot:
		targetAll = targetChildren + [target]
	else:
		targetAll = targetChildren 

	i=0
	for target in targetAll:
		pm.parentConstraint(sourceAll[i],target,mo=1)
		pm.scaleConstraint(sourceAll[i],target,mo=1)
		i+=1    

def bdConnectFingers(namespace):
	tsmFingers = ['LeftThumb_joint1','LeftThumb_joint2','LeftThumb_joint3','LeftFinger1_joint1','LeftFinger1_joint2','LeftFinger1_joint3','LeftFinger1_joint4','LeftFinger2_joint1','LeftFinger2_joint2','LeftFinger2_joint3','LeftFinger2_joint4','LeftFinger3_joint1','LeftFinger3_joint2','LeftFinger3_joint3','LeftFinger3_joint4','LeftFinger4_joint1','LeftFinger4_joint2','LeftFinger4_joint3','LeftFinger4_joint4']
	capcomFingers = ['LThumb1','LThumb2','LThumb3','LRH','LIndex1','LIndex2','LIndex3','LCH','LMiddle1','LMiddle2','LMiddle3','LLH','LRing1','LRing2','LRing3','LLH','LPinky1','LPinky2','LPinky3']
	i=0

	for jnt in tsmFingers:
		targetLeft = pm.ls(namespace + capcomFingers[i])[0]
		sourceLeft = pm.ls( jnt )[0]
		targetRight = pm.ls(namespace + 'R' + capcomFingers[i][1:])[0]
		sourceRight = pm.ls( jnt.replace('Left','Right') )[0]
		i+=1

		pm.parentConstraint(sourceLeft,targetLeft,mo=True)    
		pm.scaleConstraint(sourceLeft,targetLeft,mo=True)    
		pm.parentConstraint(sourceRight,targetRight,mo=True)
		pm.scaleConstraint(sourceRight,targetRight,mo=True)


def bdConnectArms(namespace):
	print 'adasdasdasda'
	sides = {'Left':'L', 'Right':'R'}
	tsmArmChain = ['Arm_joint1','Arm_joint2','Arm_joint3','Arm_joint5','Arm_influence7_intermediate_constrain','Arm_joint6','Arm_joint7','Arm_joint8','Arm_joint7']
	capcomArmChain = ['Shoulder','ArmDir','Arm1','Arm2','Elbow','ARoll3','ARoll4','handRot','handXR'] 

	i=0

	for jnt in tsmArmChain:
		try:
			target = pm.ls(namespace + sides['Left'] + capcomArmChain[i])[0]
		except:
			print ' cant find', capcomArmChain[i]
			
		source = pm.ls(sides.keys()[1] + jnt )[0]
		i+=1

		pm.parentConstraint(source,target,mo=True)
		pm.scaleConstraint(source,target,mo=True)

	i=0

	for jnt in tsmArmChain:
		target = pm.ls(namespace + sides['Right'] + capcomArmChain[i])[0]
		source = pm.ls(sides.keys()[0] + jnt )[0]
		i+=1

		pm.parentConstraint(source,target,mo=True)        
		pm.scaleConstraint(source,target,mo=True)


def bdConnectLegs(namespace):
	sides = {'Left':'L', 'Right':'R'}
	tsmLegChain = ['Leg_joint8','Leg_joint7','Leg_joint4','Leg_influence5_intermediate_constrain_halfNode','Leg_joint1','Leg_joint1']
	capcomLegChain = ['Toe','Foot','Leg2','Knee','Leg1','LegDir']

	i=0  
	for jnt in tsmLegChain:
		target = pm.ls(namespace + sides['Left'] + capcomLegChain[i])[0]
		source = pm.ls(sides.keys()[1] + jnt )[0]
		i+=1

		pm.parentConstraint(source,target,mo=True)   
		pm.scaleConstraint(source,target,mo=True)

	i=0  
	for jnt in tsmLegChain:
		target = pm.ls(namespace + sides['Right'] + capcomLegChain[i])[0]
		source = pm.ls(sides.keys()[0] + jnt )[0]
		i+=1

		pm.parentConstraint(source,target,mo=True)
		pm.scaleConstraint(source,target,mo=True)

def bdConnectSpine(namespace):

	tsmSpine = ['Spine_joint2','Spine_joint4','Spine_joint6','Head_joint1','Head_joint3']
	capcomSpine = ['Waist','Stomach','Chest','Neck','Head']


	i=0

	for jnt in tsmSpine:
		target = pm.ls(namespace + capcomSpine[i])[0]
		source = pm.ls( jnt )[0]
		i+=1

		pm.parentConstraint(source,target,mo=True)
		pm.scaleConstraint(source,target,mo=True)

def bdConnectExtras(namespace):
	animExtras = ['anim_Head','anim_FClothRoot','anim_BClothRoot','anim_SCDD_00_00_RBust','anim_SCDD_00_00_LBust']
	
	for extra in animExtras:
		capcomRoot = namespace + extra.replace('anim_','')
		if extra == 'anim_Head':
			bdChainConstraint(extra,capcomRoot,0)
		else:
			bdChainConstraint(extra,capcomRoot,1)
	

def bdRenameLipJoints(namespace):

	tsmCornerLipJoints = ['lip_corner_right_speak','lip_corner_left_speak']
	tsmLipJoints = ['upper_lip_right_speak','upper_lip_open_center_speak','upper_lip_center_speak','upper_lip_left_speak']

	capcomCornerLipJoints = ['Face_RMouthCorners','Face_LMouthCorners']
	capcomLipJoints = ['Face_RMouthTop2','Face_RMouthTop1','Face_LMouthTop1','Face_LMouthTop2']

	for jnt in capcomCornerLipJoints:
		toRename = pm.ls( namespace+ jnt)[0]
		try:
			toRename.rename(tsmCornerLipJoints[capcomCornerLipJoints.index(jnt)])
		except:
			print 'some shit happened'

	for jnt in capcomLipJoints:
		toRenameUpper = pm.ls(namespace + jnt,ap=True)[0]
		toRenameLower = pm.ls(namespace + jnt.replace('Top','Bottom'),ap=True)[0]
		try:
			toRenameUpper.rename(tsmLipJoints[capcomLipJoints.index(jnt)])    
		except:
			print 'some shit happened while renaming ', toRenameUpper.name()

		try:
			toRenameLower.rename(tsmLipJoints[capcomLipJoints.index(jnt)].replace('upper','lower'))    
		except:
			print 'some shit happened while renaming ', toRenameLower.name()   
			
			
def bdRenameForMB():
	capcomJoints = ['Waist','LLeg1','LLeg2','LFoot','RLeg1','RLeg2','RFoot','Stomach','LArm1','LArm2','LhandRot','RArm1','RArm2','RhandRot','LToe','RToe','LShoulder','RShoulder']
	newNames  = ['Hips','LeftUpLeg','LeftLeg','LeftFoot','RightUpLeg','RightLeg','RightFoot','Spine','LeftArm','LeftForeArm','LeftHand','RightArm','RightForeArm','RightHand','LeftToeBase','RightToeBase','LeftShoulder','RightShoulder']
	
	i=0
	for jnt in capcomJoints:
		jntObj = pm.ls(jnt)[0]
		jntObj.rename(newNames[i])
		i+=1
		
def bdConnectEyebrows(namespace):
	zoobeEyebrows = ['inner_eyebrow_left','center_eyebrow_left','outer_eyebrow_left']
	capcomEyebrows = ['Face_LEyeBrows1','Face_LEyeBrows2','Face_LEyeBrows3']
	
	i=0

	for jnt in zoobeEyebrows:
		targetLeft = pm.ls(namespace + capcomEyebrows[i])[0]
		sourceLeft = pm.ls( jnt )[0]
		targetRight = pm.ls(namespace + capcomEyebrows[i].replace('_L','_R'))[0]
		sourceRight = pm.ls( jnt.replace('_left','_right') )[0]
		i+=1

		pm.parentConstraint(sourceLeft,targetLeft,mo=True)    
		pm.scaleConstraint(sourceLeft,targetLeft,mo=True)    
		pm.parentConstraint(sourceRight,targetRight,mo=True)
		pm.scaleConstraint(sourceRight,targetRight,mo=True)

def bdConnectEyes(namespace):
	zoobeEyes = ['eye_rot_left','eyelid_upper_left','eyelid_lower_left']
	capcomEyes = ['Face_LEye','Face_LEyelidTop','Face_LEyelidBottom']
	
	i=0

	for jnt in zoobeEyes:
		targetLeft = pm.ls(namespace + capcomEyes[i])[0]
		sourceLeft = pm.ls( jnt )[0]
		targetRight = pm.ls(namespace + capcomEyes[i].replace('_L','_R'))[0]
		sourceRight = pm.ls( jnt.replace('_left','_right') )[0]
		i+=1
		
		if 'upper' in jnt:
			pm.pointConstraint(sourceLeft,targetLeft,mo=True)    
			pm.scaleConstraint(sourceLeft,targetLeft,mo=True)    
			pm.pointConstraint(sourceRight,targetRight,mo=True)
			pm.scaleConstraint(sourceRight,targetRight,mo=True)		
		else:
			pm.parentConstraint(sourceLeft,targetLeft,mo=True)    
			pm.scaleConstraint(sourceLeft,targetLeft,mo=True)    
			pm.parentConstraint(sourceRight,targetRight,mo=True)
			pm.scaleConstraint(sourceRight,targetRight,mo=True)
			

def bdConnectFace(namespace):
	zoobeFace = ['nose_wrinkle_left','nose_wing_left','cheek_raise_left','lip_stretch_left','cheek_puff_left']
	capcomFace = ['Face_LNose','Face_LCheekLineTop','Face_LCheekTop','Face_LCheekLineBottom','Face_LCheekBottom']
	
	i=0

	for jnt in zoobeFace:
		targetLeft = pm.ls(namespace + capcomFace[i])[0]
		sourceLeft = pm.ls( jnt )[0]
		targetRight = pm.ls(namespace + capcomFace[i].replace('_L','_R'))[0]
		sourceRight = pm.ls( jnt.replace('_left','_right') )[0]
		i+=1

		pm.parentConstraint(sourceLeft,targetLeft,mo=True)    
		pm.scaleConstraint(sourceLeft,targetLeft,mo=True)    
		pm.parentConstraint(sourceRight,targetRight,mo=True)
		pm.scaleConstraint(sourceRight,targetRight,mo=True)
		

def bdConnectMouth(namespace):
	zoobeCenter = ['lower_lip_center_speak','upper_lip_center_speak']
	capcomCenterDown = ['lower_lip_center_speak','lower_lip_open_center_speak']
	capcomCenterUp = ['upper_lip_center_speak','upper_lip_open_center_speak']
	
	zoobeMouth = ['upper_lip_left_speak','lip_corner_left_speak','lower_lip_left_speak']
	capcomMouth = ['upper_lip_left_speak','lip_corner_left_speak','lower_lip_left_speak']

	zoobeJaw = 'lower_jaw_speak'
	capcomJaw = 'lower_jaw_speak'
	
	sourceJaw = pm.ls(zoobeJaw)[0]
	targetJaw = pm.ls(namespace + capcomJaw)[0]
	
	pm.parentConstraint(sourceJaw,targetJaw,mo=True)    
	pm.scaleConstraint(sourceJaw,targetJaw,mo=True)
	
	
	sourceUp = pm.ls( zoobeCenter[1] )[0]
	sourceDown = pm.ls( zoobeCenter[0] )[0]
	
	for jnt in capcomCenterUp:
		target = pm.ls(namespace + jnt)[0]
		
		pm.parentConstraint(sourceUp,target,mo=True)    
		pm.scaleConstraint(sourceUp,target,mo=True)
	
	for jnt in capcomCenterDown:
		target = pm.ls(namespace + jnt)[0]
		
		pm.parentConstraint(sourceDown,target,mo=True)    
		pm.scaleConstraint(sourceDown,target,mo=True)
		
		i=0
	
	for jnt in zoobeMouth:
		targetLeft = pm.ls(namespace + capcomMouth[i])[0]
		sourceLeft = pm.ls( jnt )[0]
		targetRight = pm.ls(namespace + capcomMouth[i].replace('_left','_right'))[0]
		sourceRight = pm.ls( jnt.replace('_left','_right') )[0]
		i+=1

		pm.parentConstraint(sourceLeft,targetLeft,mo=True)    
		pm.scaleConstraint(sourceLeft,targetLeft,mo=True)    
		pm.parentConstraint(sourceRight,targetRight,mo=True)
		pm.scaleConstraint(sourceRight,targetRight,mo=True)