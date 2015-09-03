import pymel.core as pm
import pymel.core.datatypes as dt


def bdJointOnSelCenter():
    selection = pm.ls(sl=True,fl=True)

    vertices = pm.polyListComponentConversion(selection,toVertex=True)
    pm.select(vertices)
    selection = pm.ls(sl=True,fl=True)
    averagePos = dt.Vector(0,0,0)
    if type(selection[0]).__name__ == 'MeshVertex':
        numSel  = len(selection)
        for sel in selection:
            vtxPos = sel.getPosition(space='world')
            averagePos =  averagePos + vtxPos

           
        averagePos = averagePos/numSel
        pm.select(cl=True)
        joint = pm.joint(p=[averagePos.x,averagePos.y,averagePos.z],radius = 0.2)
        #pm.parent(joint,world=True)

        
        
    
bdJointOnSelCenter()
        