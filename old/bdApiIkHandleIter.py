import maya.OpenMaya as om
import maya.OpenMayaAnim as oma
import sys
import math

def bdMain():
	dagPath = om.MDagPath()
	mObj = om.MObject()
	selection = om.MSelectionList()
	
	status = om.MGlobal.getActiveSelectionList(selection)

	try:
		status = selection.getDependNode(0,mObj)
	except:
		sys.stderr.write('Nothing is selected, you need to select the IK handle')
		return
	
	if mObj.hasFn(om.MFn.kIkHandle):
		ikHandleFn = oma.MFnIkHandle(mObj)
		startJointPath = om.MDagPath()
		ikHandleFn.getStartJoint(startJointPath)
		
		startJointTransformNode = startJointPath.transform()
		startJointTransformFn = om.MFnTransform(startJointTransformNode)
				
		print startJointTransformFn.name()
		
		
		rotateOrientation = startJointTransformFn.rotateOrientation(om.MSpace.kTransform)
		rotateOrientationEuler = rotateOrientation .asEulerRotation()
		
		print 'Rotation axis', math.degrees(rotateOrientationEuler.x), math.degrees(rotateOrientationEuler.y), math.degrees(rotateOrientationEuler.z)
		
		matrix = om.MTransformationMatrix(startJointTransformFn.transformationMatrix())
		rotOrderAxis = matrix.rotationOrder()
		
		print rotOrderAxis
		quatRotation  = om.MQuaternion()
		startJointTransformFn.getRotation(quatRotation)
		eulerRotation = quatRotation.asEulerRotation()
	
		print 'Local Rotation ', math.degrees(eulerRotation.x), math.degrees(eulerRotation.y), math.degrees(eulerRotation.z)
		
		translation = matrix.getTranslation(om.MSpace.kWorld)
		print 'World transation', translation.x, translation.y, translation.z
		

		ikJoint = oma.MFnIkJoint(startJointTransformNode)
		jointOrient = om.MEulerRotation()
		quatJointOrient = om.MQuaternion()
		ikJoint.getRotation(quatJointOrient)
		ikJoint.getOrientation(jointOrient)
		
		print 'Joint orientation', math.degrees(jointOrient.x) , math.degrees(jointOrient.y), math.degrees(jointOrient.z)

		globalRot = om.MQuaternion()
		globalRot = rotateOrientation * quatRotation * quatJointOrient
		globalRotEuler = globalRot.asEulerRotation()
		print 'World orientation', math.degrees(globalRot.x) , math.degrees(globalRot.y), math.degrees(globalRot.z)
		
		print bdGetChainLength(ikJoint)


		
def bdGetChainLength(root):
	if root.childCount() > 0:
		mChild = om.MFnTransform(root.child(0))
		matrix = om.MTransformationMatrix(mChild.transformationMatrix())
		translation = matrix.getTranslation(om.MSpace.kWorld)
		return bdGetChainLength(mChild) + translation.x
	return 0

