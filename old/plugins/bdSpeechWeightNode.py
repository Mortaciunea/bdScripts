#test plugin 1

import sys, math

import maya.OpenMayaMPx as omMpx
import maya.OpenMaya as om


kNodeTypeName = 'speechMaterial'
kNodeClassify = "shader/surface"
id =  om.MTypeId(0x00000240)


#data
class speechMaterial(omMpx.MPxNode):
    inputWeight = om.MObject()
    aNeutral = om.MObject()

    aJawDown = om.MObject()
    aJawUp = om.MObject()
    aWide= om.MObject()
    aNarrow= om.MObject()
    aLipsOpen = om.MObject()
    aLipsClosed = om.MObject()

    outputColor = om.MObject()

    
    def __init__(self):
        omMpx.MPxNode.__init__(self)

    def compute(self, plug, data):
        
        if plug == speechMaterial.outputColor or plug.parent() == speechMaterial.outputColor:
        

            resultColor = om.MFloatVector(0.0,0.0,0.0)
            
            try:
                speechWeightHandle = data.inputValue(speechMaterial.inputWeight)
            except:
                sys.stderr.write( "Failed to get speech weight" )
                raise
            speechWeightValue = speechWeightHandle.asInt()
            
            try:
                neutralColorHandle = data.inputValue(speechMaterial.aNeutral)
            except:
                sys.stderr.write( "Failed to get neutral color" )
                raise            
            neutralColor = neutralColorHandle.asFloatVector()

            jawDownColor = data.inputValue(speechMaterial.aJawDown).asFloatVector()
            jawUpColor = data.inputValue(speechMaterial.aJawUp).asFloatVector()
            wideColor = data.inputValue(speechMaterial.aWide).asFloatVector()
            narrowColor = data.inputValue(speechMaterial.aNarrow).asFloatVector()
            lipsOpenColor = data.inputValue(speechMaterial.aLipsOpen).asFloatVector()
            lipsClosedColor = data.inputValue(speechMaterial.aLipsClosed).asFloatVector()

            
            
            if speechWeightValue == 6:
                resultColor = neutralColor
            elif speechWeightValue == 5:
                resultColor = jawUpColor
            elif speechWeightValue == 4:
                resultColor = jawDownColor
            elif speechWeightValue == 3:
                resultColor = lipsOpenColor
            elif speechWeightValue == 2:
                resultColor = lipsClosedColor
            elif speechWeightValue == 1:
                resultColor = narrowColor
            elif speechWeightValue == 0:
                resultColor = wideColor


            
            outColorHandle = data.outputValue(speechMaterial.outputColor)
            outColorHandle.setMFloatVector(resultColor)        
            outColorHandle.setClean()
        else:
            sys.stderr.write("fail compute")
            return om.kUnknownParameter

#creators
def nodeCreator():
    return omMpx.asMPxPtr(speechMaterial())

def nodeInitializer():
    nAttr = om.MFnNumericAttribute()
    
    speechMaterial.inputWeight = nAttr.create('speechWeight','speechWeight',om.MFnNumericData.kInt)
    nAttr.setStorable(1)
    nAttr.setKeyable(1)
    nAttr.setMin(0)
    nAttr.setMax(6)
    speechMaterial.addAttribute(speechMaterial.inputWeight)
    
    
    speechMaterial.outputColor = nAttr.createColor('outColor','oc')
    nAttr.setStorable(0)
    nAttr.setReadable(1)
    nAttr.setWritable(0)
    speechMaterial.addAttribute(speechMaterial.outputColor)
    
    speechMaterial.aNeutral = nAttr.createColor('neutralFile','n')
    nAttr.setStorable(1)
    nAttr.setKeyable(1)
    nAttr.setDefault(0.0, 0.0, 0.0)
    nAttr.setUsedAsColor(1)
    speechMaterial.addAttribute(speechMaterial.aNeutral)


    speechMaterial.aJawDown = nAttr.createColor('jawDownFile','jd')
    nAttr.setStorable(1)
    nAttr.setKeyable(1)
    nAttr.setDefault(0.0, 0.0, 0.0)
    nAttr.setUsedAsColor(1)
    speechMaterial.addAttribute(speechMaterial.aJawDown)
    
    speechMaterial.aJawUp = nAttr.createColor('jawUpFile','ju')
    nAttr.setStorable(1)
    nAttr.setKeyable(1)
    nAttr.setDefault(0.0, 0.0, 0.0)
    nAttr.setUsedAsColor(1)
    speechMaterial.addAttribute(speechMaterial.aJawUp)
    
    speechMaterial.aWide = nAttr.createColor('wideFile','w')
    nAttr.setStorable(1)
    nAttr.setKeyable(1)
    nAttr.setDefault(0.0, 0.0, 0.0)
    nAttr.setUsedAsColor(1)
    speechMaterial.addAttribute(speechMaterial.aWide)
    
    speechMaterial.aNarrow = nAttr.createColor('narrowFile','na')
    nAttr.setStorable(1)
    nAttr.setKeyable(1)
    nAttr.setDefault(0.0, 0.0, 0.0)
    nAttr.setUsedAsColor(1)
    speechMaterial.addAttribute(speechMaterial.aNarrow)

    speechMaterial.aLipsOpen = nAttr.createColor('lipsOpenFile','lo')
    nAttr.setStorable(1)
    nAttr.setKeyable(1)
    nAttr.setDefault(0.0, 0.0, 0.0)
    speechMaterial.addAttribute(speechMaterial.aLipsOpen)
    
    speechMaterial.aLipsClosed = nAttr.createColor('lipsClosedFile','lc')
    nAttr.setStorable(1)
    nAttr.setKeyable(1)
    nAttr.setDefault(0.0, 0.0, 0.0)
    nAttr.setUsedAsColor(1)
    speechMaterial.addAttribute(speechMaterial.aLipsClosed)

    speechMaterial.attributeAffects(speechMaterial.inputWeight,speechMaterial.outputColor)

    speechMaterial.attributeAffects(speechMaterial.aNeutral,speechMaterial.outputColor)
    speechMaterial.attributeAffects(speechMaterial.aJawUp,speechMaterial.outputColor)
    speechMaterial.attributeAffects(speechMaterial.aJawDown,speechMaterial.outputColor)
    speechMaterial.attributeAffects(speechMaterial.aWide,speechMaterial.outputColor)
    speechMaterial.attributeAffects(speechMaterial.aNarrow,speechMaterial.outputColor)    
    speechMaterial.attributeAffects(speechMaterial.aLipsOpen,speechMaterial.outputColor)
    speechMaterial.attributeAffects(speechMaterial.aLipsClosed,speechMaterial.outputColor)    


def initializePlugin(mobject):
    mplugin = omMpx.MFnPlugin(mobject,'bd','1.0','Any')
    try:
        mplugin.registerNode(kNodeTypeName, id, nodeCreator, nodeInitializer,omMpx.MPxNode.kDependNode)
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