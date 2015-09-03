import maya.OpenMayaMPx as OpenMayaMpx
import maya.OpenMaya as OpenMaya
import math

class varfkNode(OpenMayaMpx.MPxNode):
    kPluginNodeId = OpenMaya.MTypeId(0X00001234)
    
    aOutRotMult = OpenMaya.MObject()
    aCtrlPosition = OpenMaya.MObject()
    aJntPosition = OpenMaya.MObject()
    aFalloff = OpenMaya.MObject()

    
    def __init__(self):
        OpenMayaMpx.MPxNode.__init__(self)
        
    def compute(self,plug,data):
        if plug != varfkNode.aOutRotation:
            return OpenMaya.kUnknownParameter
        
        rotMult = 0.0
        #get inputs
        ctrlPos = data.inputValue(self.aCtrlPosition).asFloat()
        jntPos = data.inputValue(self.aJntPosition).asFloat()
        falloff = data.inputValue(self.aFalloff).asFloat()
        
        distance = math.fabs(ctrlPos-jntPos)

        if falloff != 0:
            if distance / falloff < 1:
                rotMult = 1.0 - distance / falloff
            
        
        output = data.outputValue(varfkNode.aOutRotation)
        output.setFloat( rotMult )
        data.setClean( plug )
        


def creator():
    return OpenMayaMpx.asMPxPtr(varfkNode())


def initialize():
    nAttr = OpenMaya.MFnNumericAttribute()
    compoundAttr = OpenMaya.MFnCompoundAttribute()

    varfkNode.aCtrlPosition = nAttr.create('ctrlPosition','ctrlpos',OpenMaya.MFnNumericData.kFloat,0.0)
    nAttr.setKeyable(1)
    nAttr.setMin(0.0)
    nAttr.setMax(1.0)
    varfkNode.addAttribute(varfkNode.aCtrlPosition)

    varfkNode.aJntPosition = nAttr.create('jointPosition','jntpos',OpenMaya.MFnNumericData.kFloat,0.0)
    nAttr.setKeyable(1)
    nAttr.setMin(0.0)
    nAttr.setMax(1.0)
    varfkNode.addAttribute(varfkNode.aJntPosition)
    
    varfkNode.aFalloff = nAttr.create('falloff','f',OpenMaya.MFnNumericData.kFloat,0.0)
    nAttr.setKeyable(1)
    nAttr.setMin(0.0)
    nAttr.setMax(1.0)
    varfkNode.addAttribute(varfkNode.aFalloff)
    
    
    varfkNode.aOutRotMult = nAttr.create('outRotationMultiplier','orm',OpenMaya.MFnNumericData.kFloat,0.0)
    nAttr.setWritable(0)
    nAttr.setStorable(0)
    varfkNode.addAttribute(varfkNode.aOutRotMult)
    
    varfkNode.attributeAffects(varfkNode.aCtrlPosition,varfkNode.aOutRotMult)
    varfkNode.attributeAffects(varfkNode.aJntPosition,varfkNode.aOutRotMult)
    varfkNode.attributeAffects(varfkNode.aFalloff,varfkNode.aOutRotMult)
    


def initializePlugin(obj):
    fnPlugin = OpenMayaMpx.MFnPlugin(obj,'Bogdan Diaconu','1.0','Any')
    fnPlugin.registerNode('varfkNode',varfkNode.kPluginNodeId, creator, initialize)
    
def uninitializePlugin(obj):
    fnPlugin = OpenMayaMpx.MFnPlugin(obj)
    fnPlugin.deregisterNode(varfkNode.kPluginNodeId)

