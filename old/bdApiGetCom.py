import maya.cmds as cmds
import maya.OpenMaya as om


def bdCalculateVolume(vectorArray,pointInsideVec):
    volume = ((vectorArray[0] - pointInsideVec)*((vectorArray[1] - pointInsideVec)^(vectorArray[2] - pointInsideVec)))/6
    return volume
    
def bdCalculateCenter(vectorArray,pointInsideVec):
    center = ((vectorArray[0] - pointInsideVec) + (vectorArray[1] - pointInsideVec) + (vectorArray[2] - pointInsideVec))/4
    return center

def bdGetComMain():
    
    mDagObject = om.MDagPath()
    mSelList = om.MSelectionList()
    mDagPointInside = om.MDagPath()
    
    mSelList.add('pointInsideLoc')
    mSelList.getDagPath(0,mDagPointInside)
    #mDagPointInside.pop()
    mTransformPointInside = om.MFnTransform(mDagPointInside)
    mPointInsideVector = mTransformPointInside.getTranslation(om.MSpace.kWorld)
    
    print mDagPointInside.fullPathName()
    
	
    om.MGlobal.getActiveSelectionList(mSelList)
    
    numSel = mSelList.length()
    
    
    if numSel == 1:
	mSelList.getDagPath(0,mDagObject)
	#print mDagObject.fullPathName()
	if mDagObject.hasFn(om.MFn.kMesh):
	    mFnMesh = om.MFnMesh(mDagObject)
	    volumes = om.MFloatArray()
	    centers = om.MVectorArray()
	    for i in range(mFnMesh.numPolygons()):
		mVertsId = om.MIntArray()
		mFnMesh.getPolygonVertices(i,mVertsId)
		mVertPosArray = om.MVectorArray()
		for vert in mVertsId:
		    mVertPos = om.MPoint()
		    mFnMesh.getPoint(vert,mVertPos)
		    mPointVector = om.MVector(mVertPos)
		    mVertPosArray.append(mPointVector)
		volumes.append(bdCalculateVolume(mVertPosArray,mPointInsideVector))
		centers.append(bdCalculateCenter(mVertPosArray,mPointInsideVector))
	    totalVolume = 0
	    for vol in volumes:
		totalVolume +=vol
	    print 'Total Volume :', totalVolume
	    centerMass = om.MVector()
	    for i in range(mFnMesh.numPolygons()):
		centerMass += centers[i]*volumes[i]
	    centerMass = centerMass / totalVolume
	    print centerMass.x, centerMass.y,centerMass.z
    mSelList.add('comLoc')
    mComLoc = om.MDagPath()
    
    mSelList.getDagPath(1,mComLoc)

    mTransformComLoc = om.MFnTransform(mComLoc)
    print mComLoc.fullPathName()
    mTransformComLoc.translateBy(centerMass,om.MSpace.kWorld)
		

    
bdGetComMain()