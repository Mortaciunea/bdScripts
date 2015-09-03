import maya.OpenMaya as om
import maya.OpenMayaAnim as oma
import sys
import math


mObj = om.MObject()
dagPath = om.MDagPath()
selection = om.MSelectionList()
om.MGlobal.getActiveSelectionList(selection)

try:
	status = selection.getDependNode(0,mObj)
	selection.getDagPath(0,dagPath)
except:
	sys.stderr.write('Nothing is selected, you need to select the IK handle')

jointFn = oma.MFnIkJoint(mObj)
jointPath = om.MDagPath()


print jointFn.name(), dagPath.fullPathName()
inclusiveMatrix = om.MMatrix(dagPath.inclusiveMatrix())
transformMatrix = om.MTransformationMatrix(dagPath.inclusiveMatrix())

quatRotation  = om.MQuaternion()
quatRotation = transformMatrix.rotation()
eulerRotation = quatRotation.asEulerRotation()

print 'Global Rotation ', math.degrees(eulerRotation.x), math.degrees(eulerRotation.y), math.degrees(eulerRotation.z)

'''
for i in range(0,4):
	for j in range(0,4):
		print inclusiveMatrix(i,j)
'''		
exclusiveMatrix = om.MMatrix(dagPath.exclusiveMatrix())
'''
for i in range(0,4):
	for j in range(0,4):
		print exclusiveMatrix(i,j)
'''		

jointTransformNode = dagPath.transform()
jointTransformFn = om.MFnTransform(jointTransformNode)
localMatrix = jointTransformFn.transformation()
 
quatRotation  = om.MQuaternion()
quatRotation = localMatrix.rotation()

#jointTransformFn.getRotation(quatRotation)
eulerRotation = quatRotation.asEulerRotation()

print 'Local Rotation ', math.degrees(eulerRotation.x), math.degrees(eulerRotation.y), math.degrees(eulerRotation.z)
	