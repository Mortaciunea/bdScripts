#test plugin 1

import sys, math

import maya.OpenMayaMPx as omMpx
import maya.OpenMaya as om


kNodeTypeName = 'blendMeshNode'
id =  om.MTypeId(0x00000239)


#data
class blendMesh(omMpx.MPxDeformerNode):
    aBlendMesh = om.MObject()
    aBlendWeight = om.MObject()
    def __init__(self):
        omMpx.MPxDeformerNode.__init__(self)

    def deform(self,dataBlock,geomIter,matrix,multiIndex):
        hBlendMesh = dataBlock.inputValue(self.aBlendMesh)
        oBlendMesh = hBlendMesh.asMesh()

        if oBlendMesh.isNull():
            return

        fnMesh = om.MFnMesh(oBlendMesh)
        blendPoints = om.MPointArray()
        fnMesh.getPoints(blendPoints,om.MSpace.kWorld)


        blendWeightValue = dataBlock.inputValue(blendMesh.aBlendWeight).asFloat()
        envelope = omMpx.cvar.MPxDeformerNode_envelope
        envelopeHandle = dataBlock.inputValue( envelope )
        envelopeValue = envelopeHandle.asFloat()
        
        point = om.MPoint()
        while geomIter.isDone() == False:
            point = geomIter.position()
            
            point += (blendPoints[geomIter.index()] - point) * blendWeightValue * envelopeValue
            
            geomIter.setPosition(point)
            
            geomIter.next()



#creators
def nodeCreator():
    return omMpx.asMPxPtr(blendMesh())

def nodeInitializer():
    nAttr = om.MFnNumericAttribute()
    tAttr = om.MFnTypedAttribute()

    blendMesh.aBlendMesh = tAttr.create('blendMesh','blendMesh',om.MFnData.kMesh)
    blendMesh.addAttribute(blendMesh.aBlendMesh)
    outputGeom = omMpx.cvar.MPxDeformerNode_outputGeom
    blendMesh.attributeAffects(blendMesh.aBlendMesh,outputGeom)

    blendMesh.aBlendWeight = nAttr.create('blendValue','blendValue',om.MFnNumericData.kFloat)
    nAttr.setKeyable(1)
    nAttr.setMin(0.0)
    nAttr.setMax(1.0)
    blendMesh.addAttribute(blendMesh.aBlendWeight)
    blendMesh.attributeAffects(blendMesh.aBlendWeight,outputGeom)





def initializePlugin(mobject):
    mplugin = omMpx.MFnPlugin(mobject,'bd','1.0','Any')
    try:
        mplugin.registerNode(kNodeTypeName, id, nodeCreator, nodeInitializer, omMpx.MPxNode.kDeformerNode )
    except:
        sys.stderr.write("Failed to register node : %s \n" % kNodeTypeName)
        raise

def uninitializePlugin(mobject):
    mplugin = omMpx.MFnPlugin(mobject)
    try:
        mplugin.deregisterNode(id)
    except:
        sys.stderr.write("Failed to unregister node: %s\n" % kNodeTypeName)
        raise