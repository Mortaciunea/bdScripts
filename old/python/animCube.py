import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx

kPluginNodeName = "spAnimCube"
kPluginNodeId = OpenMaya.MTypeId(0x8700B)

class animCube(OpenMayaMPx.MPxNode):
    time = OpenMaya.MObject()
    outputMesh = OpenMaya.MObject()

    def __init__(self):
        OpenMayaMPx.MPxNode.__init__(self)

    def createMesh(self, tempTime, outData):
        frame = int(tempTime.asUnits(OpenMaya.MTime.kFilm))
        if frame is 0:
            frame = 1

        cubeSize = 0.5 * float(frame % 10)

        numFaces = 6
        numVertices = 8
        numFaceConnects = 24

        vtx_1 = OpenMaya.MFloatPoint(-cubeSize, -cubeSize, -cubeSize)
        vtx_2 = OpenMaya.MFloatPoint( cubeSize, -cubeSize, -cubeSize)
        vtx_3 = OpenMaya.MFloatPoint( cubeSize, -cubeSize,  cubeSize)
        vtx_4 = OpenMaya.MFloatPoint(-cubeSize, -cubeSize,  cubeSize)
        vtx_5 = OpenMaya.MFloatPoint(-cubeSize,  cubeSize, -cubeSize)
        vtx_6 = OpenMaya.MFloatPoint(-cubeSize,  cubeSize,  cubeSize)
        vtx_7 = OpenMaya.MFloatPoint( cubeSize,  cubeSize,  cubeSize)
        vtx_8 = OpenMaya.MFloatPoint( cubeSize,  cubeSize, -cubeSize)

        points = OpenMaya.MFloatPointArray()
        points.setLength(8)
        points.set(vtx_1, 0)
        points.set(vtx_2, 1)
        points.set(vtx_3, 2)
        points.set(vtx_4, 3)
        points.set(vtx_5, 4)
        points.set(vtx_6, 5)
        points.set(vtx_7, 6)
        points.set(vtx_8, 7)

        faceConnects = OpenMaya.MIntArray()
        faceConnects.setLength(numFaceConnects)
        faceConnects.set(0, 0)
        faceConnects.set(1, 1)
        faceConnects.set(2, 2)
        faceConnects.set(3, 3)
        faceConnects.set(4, 4)
        faceConnects.set(5, 5)
        faceConnects.set(6, 6)
        faceConnects.set(7, 7)
        faceConnects.set(3, 8)
        faceConnects.set(2, 9)
        faceConnects.set(6, 10)
        faceConnects.set(5, 11)
        faceConnects.set(0, 12)
        faceConnects.set(3, 13)
        faceConnects.set(5, 14)
        faceConnects.set(4, 15)
        faceConnects.set(0, 16)
        faceConnects.set(4, 17)
        faceConnects.set(7, 18)
        faceConnects.set(1, 19)
        faceConnects.set(1, 20)
        faceConnects.set(7, 21)
        faceConnects.set(6, 22)
        faceConnects.set(2, 23)

        faceCounts = OpenMaya.MIntArray()
        faceCounts.setLength(6)
        faceCounts.set(4, 0)
        faceCounts.set(4, 1)
        faceCounts.set(4, 2)
        faceCounts.set(4, 3)
        faceCounts.set(4, 4)
        faceCounts.set(4, 5)

        meshFS = OpenMaya.MFnMesh()
        newMesh = meshFS.create(numVertices, numFaces, points, faceCounts, faceConnects, outData)

        return newMesh

    def compute(self, plug, data):
        if plug == animCube.outputMesh:
            timeData = data.inputValue(animCube.time)
            tempTime = timeData.asTime()

            outputHandle = data.outputValue(animCube.outputMesh)

            dataCreator = OpenMaya.MFnMeshData()
            newOutputData = dataCreator.create()

            self.createMesh(tempTime, newOutputData)

            outputHandle.setMObject(newOutputData)
            data.setClean(plug)
        else:
            return OpenMaya.kUnknownParameter

def nodeCreator():
    return OpenMayaMPx.asMPxPtr( animCube() )

def nodeInitializer():
    unitAttr = OpenMaya.MFnUnitAttribute()
    typedAttr = OpenMaya.MFnTypedAttribute()

    animCube.time = unitAttr.create("time", "tm", OpenMaya.MFnUnitAttribute.kTime, 0.0)
    animCube.outputMesh = typedAttr.create("outputMesh", "out", OpenMaya.MFnData.kMesh)

    animCube.addAttribute(animCube.time)
    animCube.addAttribute(animCube.outputMesh)

    animCube.attributeAffects(animCube.time, animCube.outputMesh)


# initialize the script plug-in
def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.registerNode( kPluginNodeName, kPluginNodeId, nodeCreator, nodeInitializer)
    except:
        sys.stderr.write( "Failed to register node: %s" % kPluginNodeName )
        raise

# uninitialize the script plug-in
def uninitializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.deregisterNode( kPluginNodeId )
    except:
        sys.stderr.write( "Failed to deregister node: %s" % kPluginNodeName )
        raise