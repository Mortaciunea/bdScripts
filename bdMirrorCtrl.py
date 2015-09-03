import maya.OpenMaya as om
import maya.OpenMayaAnim as oma
import sys
import math
import pymel.core as pm
import pymel.core.datatypes as dt

def bdMirrorCtrl():
    selection = pm.ls(sl=True)
    if selection:
        try:
            source,target = pm.ls(sl=True)
        except:
            pm.warning('Select source and target controller')
            return
        
        sourceShape = source.getShape()
        if sourceShape.type() != 'nurbsCurve':
            pm.error('Selected source is not nurbs curve')
            return
        
        targetCvsPos =  [ (dt.Point(-x.x, x.y, x.z) ) for x in sourceShape.getCVs(space='world')]
        
        
        targetShape = target.getShape()
        
        if targetShape.type() != 'nurbsCurve':
            pm.error('Selected target is not nurbs curve')
            return        
        targetShape.setCVs(targetCvsPos,space='world')
        targetShape.updateCurve()
        
        
    else:
        print 'Select source and target controller'
    '''
    mDagPath = om.MDagPath()
    mSelList = om.MSelectionList()

    om.MGlobal.getActiveSelectionList(mSelList)
    srcCurvePointAray = om.MPointArray()
    destCurvePointAray = om.MPointArray()
    
    numSel = mSelList.length()
    
    if numSel == 2:
        
        mSelList.getDagPath(0,mDagPath)
        
        if mDagPath.hasFn(om.MFn.kNurbsCurve):
            srcCurveFn = om.MFnNurbsCurve(mDagPath)
            srcCurveFn.getCVs(srcCurvePointAray,om.MSpace.kWorld)
            
            mSelList.getDagPath(1,mDagPath)
            if mDagPath.hasFn(om.MFn.kNurbsCurve):
                destCurveFn = om.MFnNurbsCurve(mDagPath)
                print destCurveFn.name()
                
                iterCurveCVs = om.MItCurveCV( mDagPath)
                while not iterCurveCVs.isDone():
                    mPoint = om.MPoint()
                                        
                    index = iterCurveCVs.index()
                    
                    mPoint.x = -srcCurvePointAray[index][0]
                    mPoint.y = srcCurvePointAray[index][1]
                    mPoint.z = srcCurvePointAray[index][2]
                    #print mPoint.x, mPoint.y, mPoint.z
                    iterCurveCVs.setPosition(mPoint,om.MSpace.kWorld)
                    iterCurveCVs.updateCurve()
                    iterCurveCVs.next()
                    pm.spaceLocator(p=[mPoint.x ,mPoint.y ,mPoint.z ])
    '''
def bdMatchCtrl():
    mDagPath = om.MDagPath()
    mSelList = om.MSelectionList()

    om.MGlobal.getActiveSelectionList(mSelList)
    srcCurvePointAray = om.MPointArray()
    destCurvePointAray = om.MPointArray()
    
    numSel = mSelList.length()
    
    if numSel == 2:
        
        mSelList.getDagPath(0,mDagPath)
        
        if mDagPath.hasFn(om.MFn.kNurbsCurve):
            srcCurveFn = om.MFnNurbsCurve(mDagPath)
            srcCurveFn.getCVs(srcCurvePointAray,om.MSpace.kWorld)
            
            mSelList.getDagPath(1,mDagPath)
            if mDagPath.hasFn(om.MFn.kNurbsCurve):
                destCurveFn = om.MFnNurbsCurve(mDagPath)
                print destCurveFn.name()
                
                iterCurveCVs = om.MItCurveCV( mDagPath)
                while not iterCurveCVs.isDone():
                    mPoint = om.MPoint()
                                        
                    index = iterCurveCVs.index()
                    print index

                    mPoint.x = srcCurvePointAray[index][0]
                    mPoint.y = srcCurvePointAray[index][1]
                    mPoint.z = srcCurvePointAray[index][2]
                    print mPoint.x, mPoint.y, mPoint.z
                    try:
                        iterCurveCVs.setPosition(mPoint,om.MSpace.kWorld )
                    except:
                        mc.warning('Could not move')
                    iterCurveCVs.updateCurve()
                    iterCurveCVs.next()