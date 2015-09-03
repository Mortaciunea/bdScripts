#riggin a fleshy eye. needs a certain naming convention i norder to work

import bdRigUtils
import maya.cmds as cmds
reload(bdRigUtils)


def bdBuildJointStructure(target,ctrlName,ikName):
	startDrv = cmds.duplicate(target,po=True,name=target.replace('jnt','side_drv_jnt'))
	drvChain = cmds.duplicate(target,name=target.replace('jnt','drv_jnt'))
	drvChainChilren = cmds.listRelatives(drvChain[0], c=True,type='joint',f=True)
	for child in drvChainChilren:
		if 'bnd' in child:
			newName = cmds.rename(child,child.split('|')[-1].replace('bnd','b_drv'))
			cmds.parentConstraint(newName,ctrlName.replace('anim','anim_CON'),mo=True,w=1)

	cmds.parent(drvChain[0],startDrv[0])
	if 'up' in startDrv[0]:
		cmds.parent(startDrv[0],startDrv[0].split('_')[0] + '_eye_upLid_blink_jnt')
	elif 'low' in startDrv[0]:
		cmds.parent(startDrv[0],startDrv[0].split('_')[0] + '_eye_lowLid_blink_jnt')


def bdAddEyeAttr(eyeCtrl):

	bdRigUtils.bdAddSeparatorAttr(eyeCtrl,'______')
	eyeAttr = ['BlinkUpper','BlinkLower']
	bdRigUtils.bdAddAttributeMinMax(eyeCtrl,eyeAttr,'double',-10,10,0)
	eyeAttr = ['BlinkLine']
	bdRigUtils.bdAddAttributeMinMax(eyeCtrl,eyeAttr,'double',-50,50,0)


def bdCreateVerticalFollow(side):
	blinkUpJnt = cmds.ls(side + '_eye_upLid_blink_jnt')[0]
	blinkLowJnt = cmds.ls(side + '_eye_lowLid_blink_jnt')[0]
	eyeJoint = cmds.ls(side + "*eye*jnt")[0]
	eyeAnimCtrl = cmds.ls(side + '_eye_anim')[0]

	blinkUpMD = cmds.createNode('multiplyDivide',name= blinkUpJnt.replace ('blink_jnt','follow_MD'))
	blinkLowMD = cmds.createNode('multiplyDivide',name= blinkLowJnt.replace ('blink_jnt','follow_MD'))

	blinkUpClamp = cmds.createNode('clamp',name= blinkUpJnt.replace ('blink_jnt','CL'))
	cmds.setAttr(blinkUpClamp + '.minR',-30)
	cmds.setAttr(blinkUpClamp + '.maxR',10)
	blinkLowClamp = cmds.createNode('clamp',name= blinkLowJnt.replace ('blink_jnt','CL'))    
	cmds.setAttr(blinkLowClamp + '.minR',-10)
	cmds.setAttr(blinkLowClamp + '.maxR',5)    

	blinkRemapValue = cmds.createNode('remapValue',name= side + '_blink_RV')
	cmds.setAttr(blinkRemapValue + ".color[0].color_Color",0.4, 0.1, 0, type='double3' ) 
	cmds.setAttr(blinkRemapValue + ".color[1].color_Color",0.07, 0.07, 0, type='double3' ) 
	cmds.setAttr(blinkRemapValue + ".inputMax",10)

	blinkAverage = cmds.createNode('plusMinusAverage',name= side + '_blinks_AVG')
	cmds.setAttr(blinkAverage + '.operation',3)
	cmds.setAttr(blinkAverage + '.input1D[0]',0)
	cmds.setAttr(blinkAverage + '.input1D[1]',0)

	#start connecting
	#get an average of the two eye blinks 
	cmds.connectAttr(eyeAnimCtrl + '.BlinkUpper',blinkAverage + '.input1D[0]')
	cmds.connectAttr(eyeAnimCtrl + '.BlinkLower',blinkAverage + '.input1D[1]')
	#connect the avg output into the remapValue to set up the SDK system
	cmds.connectAttr(blinkAverage + '.output1D', blinkRemapValue + '.inputValue')

	#UPPER LID
	#connect the RV output into the MD to be used for vertical follow of the eye as the damp factor for the eye rot x
	cmds.connectAttr(blinkRemapValue + '.outColorR' ,blinkUpMD + '.input2Z')
	cmds.connectAttr(eyeJoint + '.rotateZ',blinkUpMD + '.input1Z')
	#clamp the damp output to prevent the eye blinking over certain values
	cmds.connectAttr(blinkUpMD + '.outputZ',blinkUpClamp + '.inputR')
	#and finally connecting the actuall drv joint
	cmds.connectAttr(blinkUpClamp + '.outputR', blinkUpJnt + '.rotateZ')
	#LOWER LID
	#connect the RV output into the MD to be used for vertical follow of the eye as the damp factor for the eye rot x
	cmds.connectAttr(blinkRemapValue + '.outColorG' ,blinkLowMD + '.input2Z')
	cmds.connectAttr(eyeJoint + '.rotateZ',blinkLowMD + '.input1Z')
	#clamp the damp output to prevent the eye blinking over certain values
	cmds.connectAttr(blinkLowMD + '.outputZ',blinkLowClamp + '.inputR')
	#and finally connecting the actuall drv joint
	cmds.connectAttr(blinkLowClamp + '.outputR', blinkLowJnt + '.rotateZ')

def bdCreateSideFollow(side):
	eyeJoint = cmds.ls(side + "*eye*jnt")[0]
	eyeAnimCtrl = cmds.ls(side + '_eye_anim')[0]    
	upLidSideJnt = cmds.ls(side + '*upLid*side_drv_jnt*')
	lowLidSideJnt = cmds.ls(side + '*lowLid*side_drv_jnt*')

	#need to implement negative values for the right eye
	sideUpRemapValue = cmds.createNode('remapValue',name= side + 'sideUp_RV')
	cmds.setAttr(sideUpRemapValue + ".color[0].color_Color",-0.2, 0.11, 0.3, type='double3' ) 
	cmds.setAttr(sideUpRemapValue + ".color[1].color_Color",0.0, 0.0, 0, type='double3' ) 
	cmds.setAttr(sideUpRemapValue + ".inputMax",10)    

	sideLowRemapValue = cmds.createNode('remapValue',name= side + 'sideLow_RV')
	cmds.setAttr(sideLowRemapValue + ".color[0].color_Color",0.17, -0.05, 0.1, type='double3' ) 
	cmds.setAttr(sideLowRemapValue + ".color[1].color_Color",0.0, 0.0, 0, type='double3' ) 
	cmds.setAttr(sideLowRemapValue + ".inputMax",10)    

	sideUpMD = cmds.createNode('multiplyDivide',name= side + 'sideUp_MD')
	sideLowMD = cmds.createNode('multiplyDivide',name= side + 'sideLow_MD')   

	#UPPER LID
	#start connecting
	cmds.connectAttr(eyeAnimCtrl + '.BlinkUpper',sideUpRemapValue + '.inputValue')
	for pair in [['X','R'],['Y','G'],['Z','B']]:
		cmds.connectAttr(eyeJoint + '.rotateY',sideUpMD + '.input1' + pair[0])
		cmds.connectAttr(sideUpRemapValue + '.outColor'+ pair[1],  sideUpMD + '.input2' + pair[0])

	cmds.connectAttr(sideUpMD + '.outputX', upLidSideJnt[2] + '.rotateZ')
	cmds.connectAttr(sideUpMD + '.outputY', upLidSideJnt[0] + '.rotateZ')
	cmds.connectAttr(sideUpMD + '.outputZ', upLidSideJnt[1] + '.rotateZ')

	#LOWER LID
	#start connecting
	cmds.connectAttr(eyeAnimCtrl + '.BlinkLower',sideLowRemapValue + '.inputValue')
	for pair in [['X','R'],['Y','G'],['Z','B']]:
		cmds.connectAttr(eyeJoint + '.rotateY',sideLowMD + '.input1' + pair[0])
		cmds.connectAttr(sideLowRemapValue + '.outColor'+ pair[1],  sideLowMD + '.input2' + pair[0])

	cmds.connectAttr(sideLowMD + '.outputX', lowLidSideJnt[2] + '.rotateZ')
	cmds.connectAttr(sideLowMD + '.outputY', lowLidSideJnt[0] + '.rotateZ')
	cmds.connectAttr(sideLowMD + '.outputZ', lowLidSideJnt[1] + '.rotateZ')

def bdCreateBlink(side):
	eyeJoint = cmds.ls(side + "*eye*jnt")[0]
	eyeAnimCtrl = cmds.ls(side + '_eye_anim')[0]    
	upLidDrvJnt = cmds.ls(side + '*upLid_drv_jnt_??')
	lowLidDrvJnt = cmds.ls(side + '*lowLid_drv_jnt_??')  
	print upLidDrvJnt, lowLidDrvJnt
	
	upLidAnim = cmds.ls(side + '*upLid_anim_??')
	lowLidAnim = cmds.ls(side + '*lowLid_anim_??')

	baseLidsJnt = cmds.ls(side + '*lids*base')[0]
	#create the locators that hold the max rot blinks
	upLidLocator  = cmds.spaceLocator(n=side + '_upLid_rot_loc')[0]
	lowLidLocator = cmds.spaceLocator(n=side + '_lowLid_rot_loc')[0]
	cmds.parent([upLidLocator,lowLidLocator],baseLidsJnt)
	for axes in ['X','Y','Z']:
		cmds.setAttr(upLidLocator + '.translate' + axes,0)
		cmds.setAttr(lowLidLocator + '.translate' + axes,0)

	upLidDrvChild = cmds.listRelatives(upLidDrvJnt, c=True,type='joint',f=True)[0]
	lowLidDrvChild = cmds.listRelatives(lowLidDrvJnt, c=True,type='joint',f=True)[0]
	upLidLocAim = cmds.aimConstraint (upLidDrvChild,upLidLocator,offset = [0, 0, 0] ,weight=1 , aimVector =[1 ,0 ,0] ,upVector=[0, 1, 0] ,worldUpType="vector" ,worldUpVector= [0,1,0])
	lowLidLocAim  = cmds.aimConstraint (lowLidDrvChild,lowLidLocator,offset = [0, 0, 0] ,weight=1 , aimVector =[1 ,0 ,0] ,upVector=[0, 1, 0] ,worldUpType="vector" ,worldUpVector= [0,1,0])

	cmds.delete([upLidLocAim[0],lowLidLocAim[0]])
	#end

	#create the uti nodes
	upLidRotRev = cmds.createNode('reverse',name= side + '_upLid_rot_REV')
	lowLidRotRev = cmds.createNode('reverse',name= side + '_lowLid_rot_REV')


	upLidBlinkSub = cmds.createNode('plusMinusAverage',name= side + '_upLid_blink_SUB')
	cmds.setAttr(upLidBlinkSub + '.operation',2)
	cmds.setAttr(upLidBlinkSub + '.input1D[0]',0)
	cmds.setAttr(upLidBlinkSub + '.input1D[1]',0)    
	lowLidBlinkSub = cmds.createNode('plusMinusAverage',name= side + '_lowLid_blink_SUB')
	cmds.setAttr(lowLidBlinkSub + '.operation',2)
	cmds.setAttr(lowLidBlinkSub + '.input1D[0]',0)
	cmds.setAttr(lowLidBlinkSub + '.input1D[1]',0)     

	blinkPosMD = cmds.createNode('multiplyDivide',name= side + '_blink_pos_MD')
	cmds.setAttr(blinkPosMD + '.operation' ,2)
	#cmds.setAttr(blinkPosMD + '.input2X',10)
	#cmds.setAttr(blinkPosMD + '.input2Y',10)    

	upLidBlinkMD = cmds.createNode('multiplyDivide',name= side + '_upLid_blink_MD')     
	lowLidBlinkMD = cmds.createNode('multiplyDivide',name= side + '_lowLid_blink_MD')     

	upLidBlinkRV = cmds.createNode('remapValue',name= side + '_upLid_blink_RV')
	cmds.setAttr(upLidBlinkRV + ".color[0].color_Color",-0.5, -0.5, -0.5, type='double3' ) 
	cmds.setAttr(upLidBlinkRV + ".color[1].color_Color",0, 0, 0, type='double3' ) 
	cmds.setAttr(upLidBlinkRV + ".color[1].color_Position",0.5 ) 
	cmds.setAttr(upLidBlinkRV + ".inputMax",10)
	cmds.setAttr(upLidBlinkRV + ".inputMin",-10)


	lowLidBlinkRV = cmds.createNode('remapValue',name= side + '_lowLid_blink_RV')  
	cmds.setAttr(lowLidBlinkRV + ".color[0].color_Color",-0.5, -0.5, -0.5, type='double3' ) 
	cmds.setAttr(lowLidBlinkRV + ".color[1].color_Color",0, 0, 0, type='double3' ) 
	cmds.setAttr(lowLidBlinkRV + ".color[1].color_Position",0.5 ) 
	cmds.setAttr(lowLidBlinkRV + ".inputMax",10)
	cmds.setAttr(lowLidBlinkRV + ".inputMin",-10)


	#le connections
	cmds.connectAttr(upLidLocator + '.rotateZ',upLidRotRev + '.inputZ')
	cmds.connectAttr(lowLidLocator + '.rotateZ',lowLidRotRev + '.inputZ')

	cmds.connectAttr(upLidRotRev + '.outputZ',upLidBlinkSub + '.input1D[0]')
	cmds.connectAttr(lowLidRotRev + '.outputZ',lowLidBlinkSub + '.input1D[0]')

	cmds.connectAttr(eyeAnimCtrl + '.BlinkLine',upLidBlinkSub + '.input1D[1]')
	cmds.connectAttr(eyeAnimCtrl + '.BlinkLine',lowLidBlinkSub + '.input1D[1]')

	cmds.connectAttr(eyeAnimCtrl + '.BlinkUpper',upLidBlinkRV + '.inputValue')
	cmds.connectAttr(eyeAnimCtrl + '.BlinkLower',lowLidBlinkRV + '.inputValue')

	cmds.connectAttr(upLidBlinkSub + '.output1D', blinkPosMD + '.input1X')
	cmds.connectAttr(lowLidBlinkSub + '.output1D', blinkPosMD + '.input1Y')

	for pair in [['X','R'],['Y','G'],['Z','B']]:
		cmds.connectAttr(blinkPosMD + '.outputX', upLidBlinkMD + '.input1' + pair[0])
		cmds.connectAttr(blinkPosMD + '.outputY', lowLidBlinkMD + '.input1' + pair[0])
		cmds.connectAttr(upLidBlinkRV + '.outColor' + pair[1], upLidBlinkMD + '.input2' + pair[0])
		cmds.connectAttr(lowLidBlinkRV + '.outColor' + pair[1], lowLidBlinkMD + '.input2' + pair[0])

	for pair in [[2,'R'],[1,'G'],[0,'B']]:
		cmds.connectAttr(upLidAnim[pair[0]] + '.BlinkPosition',upLidBlinkRV + '.color[2].color_Color' + pair[1])
		cmds.connectAttr(lowLidAnim[pair[0]] + '.BlinkPosition',lowLidBlinkRV + '.color[2].color_Color' + pair[1])
	cmds.setAttr(upLidBlinkRV + ".color[2].color_Position",1 ) 
	cmds.setAttr(lowLidBlinkRV + ".color[2].color_Position",1 ) 


	cmds.connectAttr(upLidBlinkMD + '.outputX',upLidDrvJnt[2] + '.rz')
	cmds.connectAttr(upLidBlinkMD + '.outputY',upLidDrvJnt[1] + '.rz')
	cmds.connectAttr(upLidBlinkMD + '.outputZ',upLidDrvJnt[0] + '.rz')

	cmds.connectAttr(lowLidBlinkMD + '.outputX',lowLidDrvJnt[2] + '.rz')       
	cmds.connectAttr(lowLidBlinkMD + '.outputY',lowLidDrvJnt[1] + '.rz')       
	cmds.connectAttr(lowLidBlinkMD + '.outputZ',lowLidDrvJnt[0] + '.rz')       


def bdRigEye(side):
	#create IK handles for the bind joints, for now getting the joints based on the name
	bindJoints = cmds.ls(side + "*Lid_jnt_*")
	eyeJoint = cmds.ls(side + "*eye*jnt")[0]
	eyeAnim = cmds.ls(side + '_eye_anim')
	cmds.aimConstraint(eyeAnim[0],eyeJoint,offset = [0, 0, 0] ,weight=1 , aimVector =[1 ,0 ,0] ,upVector=[0, 1, 0] ,worldUpType="vector" ,worldUpVector= [0,1,0])

	blinkUpJnt = cmds.duplicate(eyeJoint,name = side + '_eye_upLid_blink_jnt',po=True)
	blinkLowJnt = cmds.duplicate(eyeJoint,name = side + '_eye_lowLid_blink_jnt',po=True)
	baseLidsJnt = cmds.ls(side + '*lids*base')
	cmds.parent([blinkUpJnt[0],blinkLowJnt[0]],baseLidsJnt[0])
	for joint in bindJoints:
		print joint
		endJoint = cmds.listRelatives(joint,c=True,type='joint')
		ikName = endJoint[0].replace('bnd_jnt','ikHandle')
		ctrlName = endJoint[0].replace('bnd_jnt','anim')

		bdRigUtils.bdAddIk(joint,endJoint[0],'ikSCsolver',ikName)
		bdRigUtils.bdBuildBoxController(endJoint[0],ctrlName,0.2)
		bdRigUtils.bdAddAttributeMinMax(ctrlName,['BlinkPosition'],'double',-5,5,1)
		cmds.parent(ikName,ctrlName)
		bdBuildJointStructure(joint,ctrlName,ikName)

	allAnimsGrps = cmds.ls(side + '*eye*CON_??',type='transform')
	globalAnimGrp = cmds.ls('controllers') 
	cmds.parent(allAnimsGrps,globalAnimGrp[0])

	bdAddEyeAttr(eyeAnim[0])
	bdCreateVerticalFollow(side)
	bdCreateSideFollow(side)
	bdCreateBlink(side)


#eyeGuides = bdEyeTemplate()
#eyeGuides.bdImportTemplate()

bdRigEye("left")
#bdRigEye("right")