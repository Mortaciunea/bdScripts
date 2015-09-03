import os
fbxFile = 'p:/mixamo_character/working_project/incoming/fuse_girl/fuse_girl.fbx'

def removeNamespace():
    sceneNS = pm.namespaceInfo(lon=True,r=True)
    importNS = []
    mayaNS = set([u'UI', u'shared'])
    for ns in sceneNS:
        if ns not in mayaNS:
            importNS.append(ns)
    importNS.reverse()

    for ns in importNS:
        pm.namespace( rm = ns,mergeNamespaceWithRoot=True)

def addObjMorphs():
    morphPath = os.path.join(os.path.split(fbxFile)[0], 'blendshapes/')
    morphFiles = [f for f in os.listdir(morphPath) if f.endswith('.obj') and 'default' not in f ]
    meshesVtxCount = {}
    meshes = pm.ls(type='mesh')
    for m in meshes:
        if 'Orig' not in m.name() and 'rg' not in m.name():
            meshesVtxCount[m.name()] = pm.polyEvaluate(m,v=1)
    print meshesVtxCount
    
    if morphFiles:

        bsNode = ''
        bsCreated = 0
        bsEntry =0
        
        for obj in morphFiles:
            speakName = obj.split('.')[0]
            speakName = 'speak_' + speakName
            pm.importFile(morphPath + obj,namespace= 'morph')
            morph = pm.ls('morph:*',type='mesh')[0]
            morph.rename(speakName)
            morphVtxCount = pm.polyEvaluate(morph,v=1)
            
            
            for mesh, count in meshesVtxCount.iteritems():
                print mesh, count
                if count == morphVtxCount:
                    rigMesh = [pm.ls(mesh,type='mesh')[0].getParent()]
                    skinCls = pm.listConnections('%s.inMesh'%rigMesh[0].getShape())[0]

                    
                    if not bsCreated:
                        print 'creating blendshape'
                        bsNode = pm.blendShape(rigMesh,name='speak_BS')[0].name()
                        pm.reorderDeformers(skinCls.name(),bsNode,rigMesh[0].name())
                        pm.blendShape(bsNode,e=1,t=(rigMesh[0].name(), bsEntry , morph.name(), 1))
                        bsCreated = 1
                    else:
                        print 'adding blendshape'
                        pm.blendShape(bsNode,e=1,t=(rigMesh[0].name(), bsEntry , morph.name(), 1))
            pm.delete(morph)
            bsEntry += 1



            removeNamespace()


addObjMorphs()