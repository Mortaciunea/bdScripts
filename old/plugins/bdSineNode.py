#test plugin 1

import sys, math

import maya.OpenMayaMPx as omMpx
import maya.OpenMaya as om


kNodeTypeName = 'sineNode'
id =  om.MTypeId(0x00000238)


#data
class sineNode(omMpx.MPxNode):
    sinInput = om.MObject()
    aAmplitude = om.MObject()
    aFrequency = om.MObject()
    sinOutput = om.MObject()
    def __init__(self):
        omMpx.MPxNode.__init__(self)

    def compute(self, plug, data):
        om.MGlobal.displayInfo('Sine Node')
        if plug != sineNode.sinOutput:
            return om.kUnknownParameter
        
        inputValue = data.inputValue(sineNode.sinInput).asFloat()
        frequency = data.inputValue(sineNode.aFrequency).asFloat()
        amplitude = data.inputValue(sineNode.aAmplitude).asFloat()
        
        output = amplitude * math.sin(frequency* inputValue)
        #handle for output
        hOutput = data.outputValue(sineNode.sinOutput)
        hOutput.setFloat(output)
        hOutput.setClean()
        
        data.setClean(plug )
        
        


#creators
def nodeCreator():
    return omMpx.asMPxPtr(sineNode())

def nodeInitializer():
    nAttr = om.MFnNumericAttribute()
    sineNode.sinInput = nAttr.create( "input", "in", om.MFnNumericData.kFloat, 0.0 )
    nAttr.setStorable(1)
    sineNode.addAttribute(sineNode.sinInput)
    
    
    sineNode.sinOutput = nAttr.create( "output", "out", om.MFnNumericData.kFloat, 0.0 )
    nAttr.setWritable(1)
    nAttr.setStorable(1)
    sineNode.addAttribute(sineNode.sinOutput)
    
    sineNode.attributeAffects(sineNode.sinInput,sineNode.sinOutput)
    
    sineNode.aAmplitude= nAttr.create( "amplitude", "am", om.MFnNumericData.kFloat, 0.0 )
    nAttr.setKeyable(1)
    sineNode.addAttribute(sineNode.aAmplitude)
    sineNode.attributeAffects(sineNode.aAmplitude,sineNode.sinOutput)
    
    sineNode.aFrequency= nAttr.create( "frequency", "fr", om.MFnNumericData.kFloat, 0.0 )
    nAttr.setKeyable(1)
    sineNode.addAttribute(sineNode.aFrequency)
    sineNode.attributeAffects(sineNode.aFrequency,sineNode.sinOutput)



def initializePlugin(mobject):
    mplugin = omMpx.MFnPlugin(mobject,'bd','1.0','Any')
    try:
        mplugin.registerNode(kNodeTypeName, id, nodeCreator, nodeInitializer)
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