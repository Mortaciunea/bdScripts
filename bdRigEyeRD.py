#riggin a fleshy eye. needs a certain naming convention i norder to work

import bdRigTemplate
reload(bdRigTemplate)

from bdRigTemplate import bdRigTemplate


class bdEyeTemplate(bdRigTemplate):
	def __init__(self, *args, **kargs):
		bdRigTemplate.__init__(self, *args, **kargs)
		self.templateType = 'eye'
		self.eyeJointNames = []
		self.eyeParts = []
		self.bdImportTemplate()

	def bdBuildJointsFromGuides(self):
		print 'Building joints'
		parts = []
		if self.templateSide == 'both':
			parts = ['left','right']
		else:
			parts = [self.templateSide]
		for side in parts:
			eyeCenter = pm.ls(side + ':eye_center_guide', type='transform')[0]
			eyeCenterPos = eyeCenter.getRotatePivot(space='world')
			pm.select(cl=True)
			eyelidsBaseJnt = pm.joint(p = eyeCenterPos,radius = 0.2, n=side + '_eyelids_base')
			pm.select(cl=True)
			eyeJoint = pm.joint(p = eyeCenterPos,radius = 0.2, n=side + '_eye_bnd_jnt')
			
			eyeCenterUD = eyeCenter.listAttr(ud=True)
			for attr in eyeCenterUD:
				if attr.type() == 'message':
					eyeChild = pm.listConnections(attr.name())[0]
					eyeChildPos = eyeChild.getRotatePivot(space='world')
					self.eyeParts.append(eyeChild)

					pm.select(cl=True)
					chainRoot = pm.joint(p = eyeCenterPos,radius = 0.2, n=(side + '_' + eyeChild.name().split(':')[1].replace('guide','01_jnt')))
					endChain = pm.joint(p = eyeChildPos,radius = 0.2, n=(side + '_' + eyeChild.name().split(':')[1].replace('guide','02_jnt')))
					pm.joint(chainRoot,e=True,zso = True, oj = 'xyz',sao = 'yup')

					endChain.jointOrientX.set(0)
					endChain.jointOrientY.set(0)
					endChain.jointOrientZ.set(0)
					pm.parent(chainRoot,eyelidsBaseJnt)
			
			eyeAnimGuide = pm.ls(side + ':eye_guide_anim', type='transform')[0]
			eyeAnimGuidePos = eyeAnimGuide.getRotatePivot(space='world')
			eyeAnim = pm.circle(n = (side + '_' + eyeAnimGuide.name().split(':')[1].replace('_guide','') ),nr=(0, 0, 1), c=eyeAnimGuidePos,radius = 1 )[0]
			eyeAnim.centerPivots()







	def bdBuildJointStructure(self,target,ctrlName,ikName):
		startDrv = pm.duplicate(target,po=True,name=target.replace('jnt','side_drv_jnt'))
		drvChain = pm.duplicate(target,name=target.replace('jnt','drv_jnt'))
		drvChainChildren = pm.listRelatives(drvChain[0], c=True,type='joint',f=True)
		for child in drvChainChildren:
			if '02' in child.name():
				pm.parentConstraint(child,ctrlName.replace('anim','anim_CON'),mo=True,w=1)
	
		pm.parent(drvChain[0],startDrv[0])
		if 'upper' in startDrv[0].name():
			pm.parent(startDrv[0],startDrv[0].split('_')[0] + '_eyelid_upper_blink_jnt')
		elif 'lower' in startDrv[0].name():
			pm.parent(startDrv[0],startDrv[0].split('_')[0] + '_eyelid_lower_blink_jnt')
	
	
	def bdAddEyeAttr(self,eyeCtrl):
		eyeAttr = '______'
		pm.addAttr(eyeCtrl, ln=eyeAttr,nn=eyeAttr,at='bool' )
		eyeCtrl.attr(eyeAttr).setKeyable(True)
		eyeCtrl.attr(eyeAttr).setLocked(True)
		
		eyeAttr = ['BlinkUpper','BlinkLower']
		for nodeAttr in eyeAttr:
			pm.addAttr(eyeCtrl,ln= nodeAttr ,at = 'double',min = -10 ,max=10,dv=0)
			eyeCtrl.attr(nodeAttr).setKeyable(True)
		
		eyeAttr = 'BlinkLine'
		pm.addAttr(eyeCtrl,ln= eyeAttr ,at = 'double',min = -50 ,max=50,dv=0)
		eyeCtrl.attr(eyeAttr).setKeyable(True)
	

	def bdCreateVerticalFollow(self,side):
		blinkUpJnt = pm.ls(side + '_eyelid_upper_blink_jnt')[0]
		blinkLowJnt = pm.ls(side + '_eyelid_lower_blink_jnt')[0]
		
		eyeJoint = pm.ls(side + "*eye*jnt")[0]
		eyeAnimCtrl = pm.ls(side + '_eye_anim')[0]
	
		blinkUpMD = pm.createNode('multiplyDivide',name= blinkUpJnt.replace ('blink_jnt','_follow_MD'))
		blinkLowMD = pm.createNode('multiplyDivide',name= blinkLowJnt.replace ('blink_jnt','_follow_MD'))
	
		blinkUpClamp = pm.createNode('clamp',name= blinkUpJnt.replace ('blink_jnt','_CL'))
		pm.setAttr(blinkUpClamp + '.minR',-30)
		pm.setAttr(blinkUpClamp + '.maxR',20)
		blinkLowClamp = pm.createNode('clamp',name= blinkLowJnt.replace ('blink_jnt','_CL'))    
		pm.setAttr(blinkLowClamp + '.minR',-10)
		pm.setAttr(blinkLowClamp + '.maxR',5)    
	
		blinkRemapValue = pm.createNode('remapValue',name= side + '_blink_RV')
		pm.setAttr(blinkRemapValue + ".color[0].color_Color",0.4, 0.1, 0, type='double3' ) 
		pm.setAttr(blinkRemapValue + ".color[1].color_Color",0.07, 0.07, 0, type='double3' ) 
		pm.setAttr(blinkRemapValue + ".inputMax",10)
	
		blinkAverage = pm.createNode('plusMinusAverage',name= side + '_blinks_AVG')
		pm.setAttr(blinkAverage + '.operation',3)
		pm.setAttr(blinkAverage + '.input1D[0]',0)
		pm.setAttr(blinkAverage + '.input1D[1]',0)
	
		#start connecting
		#get an average of the two eye blinks 
		pm.connectAttr(eyeAnimCtrl + '.BlinkUpper',blinkAverage + '.input1D[0]')
		pm.connectAttr(eyeAnimCtrl + '.BlinkLower',blinkAverage + '.input1D[1]')
		#connect the avg output into the remapValue to set up the SDK system
		pm.connectAttr(blinkAverage + '.output1D', blinkRemapValue + '.inputValue')
	
		#UPPER LID
		#connect the RV output into the MD to be used for vertical follow of the eye as the damp factor for the eye rot x
		pm.connectAttr(blinkRemapValue + '.outColorR' ,blinkUpMD + '.input2X')
		pm.connectAttr(eyeJoint + '.rotateX',blinkUpMD + '.input1X')
		#clamp the damp output to prevent the eye blinking over certain values
		pm.connectAttr(blinkUpMD + '.outputX',blinkUpClamp + '.inputR')
		#and finally connecting the actuall drv joint
		pm.connectAttr(blinkUpClamp + '.outputR', blinkUpJnt + '.rotateX')
		#LOWER LID
		#connect the RV output into the MD to be used for vertical follow of the eye as the damp factor for the eye rot x
		pm.connectAttr(blinkRemapValue + '.outColorG' ,blinkLowMD + '.input2X')
		pm.connectAttr(eyeJoint + '.rotateX',blinkLowMD + '.input1X')
		#clamp the damp output to prevent the eye blinking over certain values
		pm.connectAttr(blinkLowMD + '.outputX',blinkLowClamp + '.inputR')
		#and finally connecting the actuall drv joint
		pm.connectAttr(blinkLowClamp + '.outputR', blinkLowJnt + '.rotateX')

	def bdCreateSideFollow(self,side):
		mirror = 1
		if side == 'right':
			mirror = -1
		
		eyeJoint = pm.ls(side + "*eye*jnt")[0]
		eyeAnimCtrl = pm.ls(side + '_eye_anim')[0]    
		upLidSideJnt = pm.ls(side + '*upper*side_drv_jnt')
		lowLidSideJnt = pm.ls(side + '*lower*side_drv_jnt')
	
		#need to implement negative values for the right eye
		sideUpRemapValue = pm.createNode('remapValue',name= side + '_side_upper_RV')
		pm.setAttr(sideUpRemapValue + ".color[0].color_Color",mirror * 0.1, mirror * -0.1, 0.05, type='double3' ) 
		pm.setAttr(sideUpRemapValue + ".color[1].color_Color",0.0, 0.0, 0, type='double3' ) 
		pm.setAttr(sideUpRemapValue + ".inputMax",10)    
	
		sideLowRemapValue = pm.createNode('remapValue',name= side + '_side_lower_RV')
		pm.setAttr(sideLowRemapValue + ".color[0].color_Color",mirror * -0.05, mirror * 0.05,   -0.05, type='double3' ) 
		pm.setAttr(sideLowRemapValue + ".color[1].color_Color",0.0, 0.0, 0, type='double3' ) 
		pm.setAttr(sideLowRemapValue + ".inputMax",10)    
	
		sideUpMD = pm.createNode('multiplyDivide',name= side + '_side_upper_MD')
		sideLowMD = pm.createNode('multiplyDivide',name= side + '_side_lower_MD')   
	
		#UPPER LID
		#start connecting
		pm.connectAttr(eyeAnimCtrl + '.BlinkUpper',sideUpRemapValue + '.inputValue')
		for pair in [['X','R'],['Y','G'],['Z','B']]:
			pm.connectAttr(eyeJoint + '.rotateY',sideUpMD + '.input1' + pair[0])
			pm.connectAttr(sideUpRemapValue + '.outColor'+ pair[1],  sideUpMD + '.input2' + pair[0])
	
		pm.connectAttr(sideUpMD + '.outputX', upLidSideJnt[2] + '.rotateZ')
		pm.connectAttr(sideUpMD + '.outputY', upLidSideJnt[0] + '.rotateZ')
		pm.connectAttr(sideUpMD + '.outputZ', upLidSideJnt[1] + '.rotateZ')
	
		#LOWER LID
		#start connecting
		pm.connectAttr(eyeAnimCtrl + '.BlinkLower',sideLowRemapValue + '.inputValue')
		for pair in [['X','R'],['Y','G'],['Z','B']]:
			pm.connectAttr(eyeJoint + '.rotateY',sideLowMD + '.input1' + pair[0])
			pm.connectAttr(sideLowRemapValue + '.outColor'+ pair[1],  sideLowMD + '.input2' + pair[0])
	
		pm.connectAttr(sideLowMD + '.outputX', lowLidSideJnt[2] + '.rotateZ')
		pm.connectAttr(sideLowMD + '.outputY', lowLidSideJnt[0] + '.rotateZ')
		pm.connectAttr(sideLowMD + '.outputZ', lowLidSideJnt[1] + '.rotateZ')

	def bdCreateBlink(self,side):
		# The blink is created using a relativly complex network of maya utility nodes.
		# The following info is needed:
		# - the eye joint, eye anim controller
		# - the joints driving the lids
		# - the anim controllers for the driver joints
		# 
		#
		
		mirror = 1
		if side == 'right':
			mirror = -1
			
		eyeJoint = pm.ls(side + "*eye*jnt")[0]
		eyeAnimCtrl = pm.ls(side + '_eye_anim')[0]    
		upLidDrvJnt = pm.ls(side + '*upper*01_drv_jnt')
		lowLidDrvJnt = pm.ls(side + '*lower*01_drv_jnt')  
		upLidAnim = pm.ls(side + '*upper_*_anim')
		lowLidAnim = pm.ls(side + '*lower_*_anim')
	
		baseLidsJnt = pm.ls(side + '*eyelids*base')[0]
		#create the locators that hold the default eye open angle
		upLidLocator  = pm.spaceLocator(n=side + '_upper_eyelid_rot_loc')
		lowLidLocator = pm.spaceLocator(n=side + '_lower_eyelid_rot_loc')

		upLidInnerLocator  = pm.spaceLocator(n=side + '_upper_inner_eyelid_rot_loc')
		lowLidInnerLocator = pm.spaceLocator(n=side + '_lower_inner_eyelid_rot_loc')

		pm.parent([upLidLocator,lowLidLocator,upLidInnerLocator,lowLidInnerLocator],baseLidsJnt)
		
		for axes in ['X','Y','Z']:
			pm.setAttr(upLidLocator + '.translate' + axes,0)
			pm.setAttr(lowLidLocator + '.translate' + axes,0)
			pm.setAttr(upLidInnerLocator + '.translate' + axes,0)
			pm.setAttr(lowLidInnerLocator + '.translate' + axes,0)
			
		#getting the middle joint driver to allow getting the default eye open angle. vectors used
		for lidJnt in upLidDrvJnt:
			if 'mid' in lidJnt.name():
				angle = self.bdGetEyelidJntAngle(lidJnt)
				upLidLocator.rotateX.set(angle)

		for lidJnt in lowLidDrvJnt:
			if 'mid' in lidJnt.name():
				angle = self.bdGetEyelidJntAngle(lidJnt)
				lowLidLocator.rotateX.set(angle)

		for lidJnt in upLidDrvJnt:
			if 'inner' in lidJnt.name():
				angle = self.bdGetEyelidJntAngle(lidJnt)
				upLidInnerLocator.rotateX.set(angle)

		for lidJnt in lowLidDrvJnt:
			if 'inner' in lidJnt.name():
				angle = self.bdGetEyelidJntAngle(lidJnt)
				lowLidInnerLocator.rotateX.set(angle)
				
		#create the uti nodes
		upLidRotRev = pm.createNode('reverse',name= side + '_upper_eyelid_rot_REV')
		lowLidRotRev = pm.createNode('reverse',name= side + '_lower_eyelid_rot_REV')
	
	
		upLidBlinkSub = pm.createNode('plusMinusAverage',name= side + '_upper_eyelid_blink_SUB')
		pm.setAttr(upLidBlinkSub + '.operation',2)
		pm.setAttr(upLidBlinkSub + '.input1D[0]',0)
		pm.setAttr(upLidBlinkSub + '.input1D[1]',0)    
		lowLidBlinkSub = pm.createNode('plusMinusAverage',name= side + '_lower_eyelid_blink_SUB')
		pm.setAttr(lowLidBlinkSub + '.operation',2)
		pm.setAttr(lowLidBlinkSub + '.input1D[0]',0)
		pm.setAttr(lowLidBlinkSub + '.input1D[1]',0)     
	
		blinkPosMD = pm.createNode('multiplyDivide',name= side + '_blink_pos_MD')
		pm.setAttr(blinkPosMD + '.operation' ,2)
		#pm.setAttr(blinkPosMD + '.input2X',10)
		#pm.setAttr(blinkPosMD + '.input2Y',10)    
	
		upLidBlinkMD = pm.createNode('multiplyDivide',name= side + '_upper_eyelid_blink_MD')     
		lowLidBlinkMD = pm.createNode('multiplyDivide',name= side + '_lower_eyelid_blink_MD')     
	
		upLidBlinkRV = pm.createNode('remapValue',name= side + '_upper_eyelid_blink_RV')
		pm.setAttr(upLidBlinkRV + ".color[0].color_Color",-0.5, -0.5, -0.5, type='double3' ) 
		pm.setAttr(upLidBlinkRV + ".color[1].color_Color",0, 0, 0, type='double3' ) 
		pm.setAttr(upLidBlinkRV + ".color[1].color_Position",0.5 ) 
		pm.setAttr(upLidBlinkRV + ".inputMax",10)
		pm.setAttr(upLidBlinkRV + ".inputMin",-10)
	
	
		lowLidBlinkRV = pm.createNode('remapValue',name= side + '_lower_eyelid_blink_RV')  
		pm.setAttr(lowLidBlinkRV + ".color[0].color_Color",-0.5, -0.5, -0.5, type='double3' ) 
		pm.setAttr(lowLidBlinkRV + ".color[1].color_Color",0, 0, 0, type='double3' ) 
		pm.setAttr(lowLidBlinkRV + ".color[1].color_Position",0.5 ) 
		pm.setAttr(lowLidBlinkRV + ".inputMax",10)
		pm.setAttr(lowLidBlinkRV + ".inputMin",-10)
	
	
		#le connections
		pm.connectAttr(upLidLocator + '.rotateX',upLidRotRev + '.inputZ')
		pm.connectAttr(lowLidLocator + '.rotateX',lowLidRotRev + '.inputZ')
	
		pm.connectAttr(upLidRotRev + '.outputZ',upLidBlinkSub + '.input1D[0]')
		pm.connectAttr(lowLidRotRev + '.outputZ',lowLidBlinkSub + '.input1D[0]')
	
		pm.connectAttr(eyeAnimCtrl + '.BlinkLine',upLidBlinkSub + '.input1D[1]')
		pm.connectAttr(eyeAnimCtrl + '.BlinkLine',lowLidBlinkSub + '.input1D[1]')
	
		pm.connectAttr(eyeAnimCtrl + '.BlinkUpper',upLidBlinkRV + '.inputValue')
		pm.connectAttr(eyeAnimCtrl + '.BlinkLower',lowLidBlinkRV + '.inputValue')
	
		pm.connectAttr(upLidBlinkSub + '.output1D', blinkPosMD + '.input1X')
		pm.connectAttr(lowLidBlinkSub + '.output1D', blinkPosMD + '.input1Y')
	
		for pair in [['X','R'],['Y','G'],['Z','B']]:
			pm.connectAttr(blinkPosMD + '.outputX', upLidBlinkMD + '.input1' + pair[0])
			pm.connectAttr(blinkPosMD + '.outputY', lowLidBlinkMD + '.input1' + pair[0])
			pm.connectAttr(upLidBlinkRV + '.outColor' + pair[1], upLidBlinkMD + '.input2' + pair[0])
			pm.connectAttr(lowLidBlinkRV + '.outColor' + pair[1], lowLidBlinkMD + '.input2' + pair[0])
	
		for pair in [[2,'R'],[1,'G'],[0,'B']]:
			pm.connectAttr(upLidAnim[pair[0]] + '.BlinkPosition',upLidBlinkRV + '.color[2].color_Color' + pair[1])
			pm.connectAttr(lowLidAnim[pair[0]] + '.BlinkPosition',lowLidBlinkRV + '.color[2].color_Color' + pair[1])
		pm.setAttr(upLidBlinkRV + ".color[2].color_Position",1 ) 
		pm.setAttr(lowLidBlinkRV + ".color[2].color_Position",1 ) 
	
	
		pm.connectAttr(upLidBlinkMD + '.outputX',upLidDrvJnt[2] + '.rz')
		pm.connectAttr(upLidBlinkMD + '.outputY',upLidDrvJnt[1] + '.rz')
		pm.connectAttr(upLidBlinkMD + '.outputZ',upLidDrvJnt[0] + '.rz')
	
		pm.connectAttr(lowLidBlinkMD + '.outputX',lowLidDrvJnt[2] + '.rz')       
		pm.connectAttr(lowLidBlinkMD + '.outputY',lowLidDrvJnt[1] + '.rz')       
		pm.connectAttr(lowLidBlinkMD + '.outputZ',lowLidDrvJnt[0] + '.rz')       

	def bdGetEyelidJntAngle(self, lidJnt):
		lidJntEnd = pm.listRelatives(lidJnt, c=True,type='joint',f=True)[0]
		startVectorUpperMid =  dt.Vector(lidJnt.getRotatePivot(space = 'world'))
		endVectorUpperMid =  dt.Vector(lidJntEnd.getRotatePivot(space = 'world'))
		diff = endVectorUpperMid - startVectorUpperMid
		angle = 90 - math.degrees(math.acos(diff.normal().y))
		
		return angle

	def bdCleanupGuides(self,side):
		pm.delete(pm.ls(side + ":*"))
		pm.namespace(rm=side)
			
	def bdRigEye(self):
		#create IK handles for the bind joints, for now getting the joints based on the name
		parts = []
		if self.templateSide == 'both':
			parts = ['left','right']
		else:
			parts = [self.templateSide]
		for side in parts:		
			eyeLidsJnt = pm.ls(side + '*eyelid_*_01_jnt')
			eyeJoint = pm.ls(side + "*eye*jnt")[0]
			eyeCorners = pm.ls(side + "*eye*corner*01_jnt")
			eyeAnim = pm.ls(side + '_eye_anim')
			pm.aimConstraint(eyeAnim[0],eyeJoint,offset = [0, 0, 0] ,weight=1 , aimVector =[0 ,0 ,1] ,upVector=[0, 1, 0] ,worldUpType="vector" ,worldUpVector= [0,1,0])
		
			blinkUpJnt = pm.duplicate(eyeJoint,name = side + '_eyelid_upper_blink_jnt',po=True)
			blinkLowJnt = pm.duplicate(eyeJoint,name = side + '_eyelid_lower_blink_jnt',po=True)
			
			baseLidsJnt = pm.ls(side + '*lids*base')
			pm.parent([blinkUpJnt[0],blinkLowJnt[0]],baseLidsJnt[0])
			for joint in (eyeLidsJnt + eyeCorners):
				endJoint = pm.listRelatives(joint,c=True,type='joint')
				
				ikName = endJoint[0].name().replace('02_jnt','ikHandle')
				ctrlName = endJoint[0].name().replace('02_jnt','anim')
				
				bdRigUtils.bdAddIk(joint.name(),endJoint[0].name(),'ikSCsolver',ikName)
				bdRigUtils.bdBuildSquareController(endJoint[0].name(),ctrlName,0.2)
				#bdRigUtils.bdBuildBoxController(endJoint[0].name(),ctrlName,0.2)
				if 'corner' not in ctrlName:
					bdRigUtils.bdAddAttributeMinMax(ctrlName,['BlinkPosition'],'double',-5,5,1)
				pm.parent(ikName,ctrlName)
				self.bdBuildJointStructure(joint,ctrlName,ikName)
			
			'''
			allAnimsGrps = pm.ls(self.templateSide + '*eye*CON_??',type='transform')
			globalAnimGrp = pm.ls('controllers') 
			pm.parent(allAnimsGrps,globalAnimGrp[0])
			'''
			
			self.bdAddEyeAttr(eyeAnim[0])
			self.bdCreateVerticalFollow(side)
			self.bdCreateSideFollow(side)
			self.bdCreateBlink(side)
			self.bdCleanupGuides(side)




