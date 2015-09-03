import pymel.core as pm
import maya.OpenMaya as om

def bdJointOnSelCenter():
    selection = pm.ls(sl=True,fl=True)

    vtxPosArray = []
    vertices = pm.polyListComponentConversion(selection,toVertex=True)
    pm.select(vertices)
    selection = pm.ls(sl=True,fl=True)
    
    if type(selection[0]).__name__ == 'MeshVertex':
        for sel in selection:
            vtxPos = sel.getPosition(space='world')
            print vtxPos, sel.name() 
            vtxPosArray.append(om.MVector(vtxPos[0],vtxPos[1],vtxPos[2]))
            loc = pm.spaceLocator(p=vtxPos)
            loc.centerPivots()
        #vtx1Pos = selection[0].getPoint(1,space='world')
        #vtxPos.append(om.MVector(vtx1Pos[0],vtx1Pos[1],vtx1Pos[2]))
    
        area = 0
        
        centroids = []
        areas = []
        for i in range(1,len(vtxPosArray)-1):
            area = area + ((vtxPosArray[i] - vtxPosArray[0]) ^ (vtxPosArray[i+1] - vtxPosArray[0])).length()/2.0
            areas.append(((vtxPosArray[i] - vtxPosArray[0]) ^ (vtxPosArray[i+1] - vtxPosArray[0])).length()/2.0)
            centroid = (vtxPosArray[0] + vtxPosArray[i] + vtxPosArray[i+1])/3.0
            centroids.append(centroid)
            loc = pm.spaceLocator(p=[centroid.x,centroid.y,centroid.z])
            loc.centerPivots()            
            
           
        '''
        center = om.MVector(0,0,0)
        
        print len(vtxPos), len(centroids), len(areas), 'MUIE'
        
        for i in range(len(centroids)):
            center = center + (centroids[i]*areas[i])
            
        
        
        center = center/area
        pm.spaceLocator(p=[center.x,center.y,center.z],a=True)
            
        '''
        
        '''
        sumCrossProducts = om.MVector()
        normal = (vtxPos[0]^vtxPos[1]).normal()
        print normal.x,normal.y,normal.z
        for i in range(len(vtxPos)-1):
            sumCrossProducts +=  (vtxPos[i]^vtxPos[i+1])
            
        area = (normal/2.0)*sumCrossProducts
        
        cx= cy = cz = 0
        for i in range(len(vtxPos)-1):
            cx = cx + (vtxPos[i].x + vtxPos[i+1].x)*(vtxPos[i].x*vtxPos[i+1].y - vtxPos[i+1].x*vtxPos[i].y)
            cy = cy + (vtxPos[i].y + vtxPos[i+1].y)*(vtxPos[i].x*vtxPos[i+1].y - vtxPos[i+1].x*vtxPos[i].y)
            cz = cx + (vtxPos[i].z + vtxPos[i+1].z)*(vtxPos[i].x*vtxPos[i+1].z- vtxPos[i+1].x*vtxPos[i].z)
        cx = cx/(6.0*area)
        cy = cy/(6.0*area)
        cz = cz/(6.0*area)
        '''
        
        print area
        #pm.spaceLocator(p=[cx,cy,cz])
    if type(selection[0]).__name__ == 'MeshFace':
        for sel in selection:
            print sel.getArea(),pm.objectCenter(sel)
            center = pm.objectCenter(sel)
            pm.spaceLocator(p=[center[0],center[1],center[2]])
        
        
    
bdJointOnSelCenter()
        