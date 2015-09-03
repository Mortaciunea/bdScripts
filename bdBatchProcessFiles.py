import os,fnmatch
path = 'P:/omnom/working_project/scenes/characters/omnom/07_animation/01_wip/omnelle_candy'

allFiles = []

if os.path.isdir(path):
    for root, dirnames, filenames in os.walk(path):
        for filename in fnmatch.filter(filenames, '*.mb'):
            #finalAnimations.append(os.path.join(root, filename))
            allFiles.append(os.path.join(root, filename))


for f in allFiles:
    pm.openFile(f,f=1)
    print f

    unknown = pm.ls(type='unknown')
    if unknown :
        for node in unknown :
            lockStatus = pm.lockNode( node, q=True )
            if node:
                pm.lockNode( node, lock=False )
        pm.delete(unknown)
        
    eyelashes = pm.ls('*:*eyelash*CTL')
    for eyelash in eyelashes:
        pm.cutKey(eyelash)
        eyelash.translateX.set(0)
        eyelash.translateY.set(0)
        eyelash.translateZ.set(0)

        eyelash.rotateX.set(0)
        eyelash.rotateY.set(0)
        eyelash.rotateZ.set(0)
    upperEyelids = pm.ls('*:*eyelidTop*CTL')
    for eyelid in upperEyelids :
        val = pm.keyframe(eyelid,q=1,at='rotateX',vc=1)
        times = pm.keyframe(eyelid,q=1,at='rotateX')
        for i in range(len(val)):
            if val[i] > 90:
                print val[i]
                pm.setKeyframe(eyelid,at = 'rotateX',v=40,time=times[i])

    pm.saveAs(f,type='mayaAscii',f=1)