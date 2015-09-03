import maya.cmds as cmds
import maya.OpenMaya as om



def bdGetComMain():
    locators = cmds.ls('locator*')
    if locators:
    	cmds.delete(locators)
    mDagObject = om.MDagPath()
    mSelList = om.MSelectionList()
	
    om.MGlobal.getActiveSelectionList(mSelList)
    
    centerMass = om.MPoint(0,0,0)

    mSelList.getDagPath(0,mDagObject)

    print centerMass.x, centerMass.y, centerMass.z
    
    if mSelList.length():
	if mDagObject.hasFn(om.MFn.kMesh):
	    mFnMesh = om.MFnMesh(mDagObject)
    
	    for i in range(mFnMesh.numVertices()):
		mVertPos = om.MPoint()
		mFnMesh.getPoint(i,mVertPos,om.MSpace.kWorld)
		print i
		print mVertPos.x, mVertPos.y,mVertPos.z
		
		centerMass += om.MVector(mVertPos)
		print centerMass.x, centerMass.y,centerMass.z
		cmds.spaceLocator(p=[mVertPos.x,mVertPos.y,mVertPos.z])
	    
	    print mFnMesh.numVertices()
	    centerMass = centerMass / (mFnMesh.numVertices())

	    cmds.spaceLocator(p=[centerMass.x,centerMass.y,centerMass.z])

    
bdGetComMain()