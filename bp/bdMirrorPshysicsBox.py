import pymel.core as pm

def mirrorPhysicsBox():
    selection = pm.ls(sl=1)
    if len(selection) != 2:
        pm.warning('Select the source and target boxes!')
        return
    else:
        srcBox = selection[0]
        destBox = selection[1]
        
        srcBoxVtx = pm.ls(srcBox.vtx,fl=1)
        destBoxVtx = pm.ls(destBox.vtx,fl=1)
        
        if len(srcBoxVtx) == len(destBoxVtx):
            for vtx in srcBoxVtx:
                srcPos = vtx.getPosition(space='world')
                index = srcBoxVtx.index(vtx)
                destPos = [-1 * srcPos [0],srcPos [1],srcPos [2]]
                destBoxVtx[index].setPosition(destPos,space='world')
        
        
    
    