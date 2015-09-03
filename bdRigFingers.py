import bdRigUtils
import maya.cmds as cmds
reload(bdRigUtils)



def bdAddAllFingerAttr(side):
	fingerAnim = cmds.ls(side + '_fingers_anim',type='transform')[0]
	fingerList = ['Index','Middle','Ring','Pinky','Thumb']
	attrList = ['Spread','Base','Middle','Tip']
	for finger in fingerList:
		bdRigUtils.bdAddSeparatorAttr(fingerAnim,'_' + finger + '_')
		fingerPart = 0
		for attr in attrList:
			cmds.addAttr(fingerAnim,ln=finger + '_' + attr,at = 'float',min = -90,max=90,dv=0)
			cmds.setAttr((fingerAnim + "." + finger + '_' + attr),e=True, keyable=True)
			fingerJoint = cmds.ls(side + '_' + finger.lower() + '_bnd_jnt_0' + str(fingerPart) ,type='joint')[0]
			
			if attr == 'Spread':
				cmds.connectAttr(fingerAnim + "." + finger + '_' + attr,fingerJoint + '.rotateY')
			else:
				reverseVal = cmds.createNode('reverse',n = side + '_' + finger + '_' + str(fingerPart)) 
				cmds.connectAttr(fingerAnim + "." + finger + '_' + attr,reverseVal + '.inputZ')
				cmds.connectAttr(reverseVal + '.outputZ',fingerJoint + '.rotateZ')
			
				fingerPart += 1
				
#rig fingers
def bdAddFingerAttr(side,finger):
	fingerAnim = cmds.ls(side + finger + 'anim',type='transform')[0]
	bdRigUtils.bdAddSeparatorAttr(fingerAnim,'_Bend_')
	attrList = ['All','Base','Middle','Tip']
	bdRigUtils.bdAddAttribute(fingerAnim,attrList,'float')

	
def bdCreateFingerIKAnim(finger):
	fingerEnd = cmds.ls(finger + 'jnt_end')
	animCtrl = cmds.circle(n = finger + 'ik_anim',nr=(0, 1, 0), c=(0, 0, 0) )
	cmds.delete(animCtrl[0], constructionHistory=True)
	animGroup = cmds.group(n = finger + 'ik_anim_grp')
	cmds.select(clear=True)
	pc = cmds.parentConstraint(fingerEnd,animGroup)
	cmds.delete(pc)	
	
	
def bdCreateFingerIK(side, finger):
	startJoint = cmds.ls(side + finger + 'ik_jnt_00')
	endEffector = cmds.ls(side + finger + 'ik_jnt*' ,type='transform',recursive=True)[-1]
	for j in cmds.ls(side + finger + 'ik_jnt*' ,type='transform',recursive=True):
		cmds.setAttr(j+'.preferredAngleZ',10)
	
	fingerIKhandle = cmds.ikHandle(n= side + finger + 'ikHandle', sj = startJoint[0] ,ee = endEffector,solver = 'ikRPsolver')
	ikGroup = cmds.group(n=side + finger + 'ikHandle_grp', empty = True)
	pc = cmds.parentConstraint(endEffector,ikGroup)
	cmds.delete(pc)
	cmds.parent(fingerIKhandle[0], ikGroup)
	ikAnim = cmds.ls(side + finger + 'ik_anim',type='transform')[0]
	cmds.parentConstraint(ikAnim,fingerIKhandle[0])
	

def bdRigFingers(side):
	for f in ['_thumb_','_index_','_middle_','_ring_','_pinky_']:
		#create ik controlers
		#bdCreateFingerIKAnim(side+f)
		#bdCreateFingerIK(side,f)
		#bdRigUtils.bdConstrainChain(side + f + 'ik_jnt_00',side + f + 'fk_jnt_00',side + f + 'bnd_jnt_00')
		bdAddFingerAttr(side,f)
		#bdRigUtils.bdRecursiveIKFKSwitch(side,f,side + f + 'anim')
		
bdAddAllFingerAttr("L")