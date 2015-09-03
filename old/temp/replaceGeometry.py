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

def replaceGeometry():

    fbxPath = os.path.split(fbxFile)[0]
    defaultMeshPath = os.path.join(fbxPath,'blendshapes/')

    meshes = pm.ls(type='mesh')
    meshesShaders = {}

    for m in meshes:
        if 'Orig' not in m.name():
            shader = pm.listConnections(m.name(),s=1,d=1,type = 'shadingEngine')
            if shader:
                meshesShaders[str(m.name())] = str(shader[0].name())

    print meshesShaders

    morphFiles = [f for f in os.listdir(defaultMeshPath) if f.endswith('.obj')]
    print morphFiles 
    if 'default.obj' in morphFiles:
        print 'Found default'

        pm.importFile(defaultMeshPath + 'default.obj',namespace= 'tpose')
        importMeshes = pm.ls('tpose:*',type='mesh')

        for m in importMeshes:
            if 'Orig' not in m.name():
                sourceMesh = m.name().split(':')[1]
                pm.select(m)
                pm.mel.eval('sets -e -forceElement ' + meshesShaders[sourceMesh])
                pm.substituteGeometry(sourceMesh,m)


        removeNamespace()

    meshes = pm.ls(type='mesh')
    meshesShaders = {}

    for m in meshes:
        if 'Orig' not in m.name():
            skinCls = pm.listConnections('%s.inMesh'%m)
            if not skinCls:
                m.rename('replaced_' + m.name())

replaceGeometry()