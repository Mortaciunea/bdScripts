import maya.OpenMayaMPx as OpenMayaMpx
import maya.OpenMaya as OpenMaya
import math

class varfkNode(OpenMayaMpx.MPxNode):
    kPluginNodeId = OpenMaya.MTypeId(0X00001234)
    
    #aOutRotMult = OpenMaya.MObject()
    aCtrlPosition = OpenMaya.MObject()
    aJntPosition = OpenMaya.MObject()
    aFalloff = OpenMaya.MObject()
    aInRotation = OpenMaya.MObject()
    aInRotationX = OpenMaya.MObject()
    aInRotationY = OpenMaya.MObject()
    aInRotationZ = OpenMaya.MObject()

    aOutRotation = OpenMaya.MObject()
    aOutRotationX = OpenMaya.MObject()
    aOutRotationY = OpenMaya.MObject()
    aOutRotationZ = OpenMaya.MObject()
    
    def __init__(self):
        OpenMayaMpx.MPxNode.__init__(self)
        
    def compute(self,plug,data):
        if plug != varfkNode.aOutRotation or plug != varfkNode.aOutRotationX or plug != varfkNode.aOutRotationY or plug != varfkNode.aOutRotationZ:
            return OpenMaya.kUnknownParameter
        
        rotMult = 0.0
        #get inputs
        ctrlPos = data.inputValue(self.aCtrlPosition).asFloat()
        jntPos = data.inputValue(self.aJntPosition).asFloat()
        falloff = data.inputValue(self.aFalloff).asFloat()
        inRot = data.inputValue(self.inRot).asVector()
        
        distance = math.fabs(ctrlPos-jntPos)

        if falloff != 0:
            if distance / falloff < 1:
                rotMult = 1.0 - distance / falloff
                
        outRot = [inRot.x*rotMult,inRot.y*rotMult,inRot.z*rotMult]
        data.outputValue(self.aOutRotation).set(20, outRot[1],outRot[2])
        data.outputValue(self.aOutRotation).setClean()
            

        


def creator():
    return OpenMayaMpx.asMPxPtr(varfkNode())


def initialize():
    nAttr = OpenMaya.MFnNumericAttribute()
    compoundAttr = OpenMaya.MFnCompoundAttribute()
    
    varfkNode.aInRotationX = nAttr.create('inRotationX','inrx',OpenMaya.MFnNumericData.kFloat,0.0)
    nAttr.setStorable(1)
    nAttr.setKeyable(1)
    nAttr.setWritable(1)
    varfkNode.addAttribute(varfkNode.aInRotationX)
    
    varfkNode.aInRotationY = nAttr.create('inRotationY','inry',OpenMaya.MFnNumericData.kFloat,0.0)
    nAttr.setStorable(1)
    nAttr.setKeyable(1)
    nAttr.setWritable(1)
    varfkNode.addAttribute(varfkNode.aInRotationY)
    
    varfkNode.aInRotationZ = nAttr.create('inRotationZ','inrz',OpenMaya.MFnNumericData.kFloat,0.0)
    nAttr.setStorable(1)
    nAttr.setKeyable(1)
    nAttr.setWritable(1)
    varfkNode.addAttribute(varfkNode.aInRotationZ)    
    
    varfkNode.aInRotation = compoundAttr.create('inRotation','inr')
    compoundAttr.setStorable(1)
    compoundAttr.setKeyable(1)
    nAttr.setWritable(1)
    compoundAttr.addChild(varfkNode.aInRotationX)
    compoundAttr.addChild(varfkNode.aInRotationY)
    compoundAttr.addChild(varfkNode.aInRotationZ)
    compoundAttr.setArray(1)
    varfkNode.addAttribute(varfkNode.aInRotation)    
    
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
    
    varfkNode.aOutRotationX = nAttr.create('outRotationX','outrx',OpenMaya.MFnNumericData.kFloat,0.0)
    nAttr.setStorable(0)
    nAttr.setKeyable(0)
    nAttr.setWritable(0)
    varfkNode.addAttribute(varfkNode.aOutRotationX)
    
    varfkNode.aOutRotationY = nAttr.create('outRotationY','outry',OpenMaya.MFnNumericData.kFloat,0.0)
    nAttr.setStorable(0)
    nAttr.setKeyable(0)
    nAttr.setWritable(0)
    varfkNode.addAttribute(varfkNode.aOutRotationY)
    
    varfkNode.aOutRotationZ = nAttr.create('outRotationZ','outrz',OpenMaya.MFnNumericData.kFloat,0.0)
    nAttr.setStorable(0)
    nAttr.setKeyable(0)
    nAttr.setWritable(0)
    varfkNode.addAttribute(varfkNode.aOutRotationZ)   
    
    varfkNode.aOutRotation = compoundAttr.create('outRotation','outr')
    compoundAttr.setStorable(0)
    compoundAttr.setKeyable(0)
    compoundAttr.setWritable(0)
    compoundAttr.addChild(varfkNode.aOutRotationX)
    compoundAttr.addChild(varfkNode.aOutRotationY)
    compoundAttr.addChild(varfkNode.aOutRotationZ)
    compoundAttr.setArray(1)
    varfkNode.addAttribute(varfkNode.aOutRotation)

    
    varfkNode.attributeAffects(varfkNode.aInRotation,varfkNode.aOutRotation)
    varfkNode.attributeAffects(varfkNode.aCtrlPosition,varfkNode.aOutRotation)
    varfkNode.attributeAffects(varfkNode.aJntPosition,varfkNode.aOutRotation)
    varfkNode.attributeAffects(varfkNode.aFalloff,varfkNode.aOutRotation)
    


def initializePlugin(obj):
    fnPlugin = OpenMayaMpx.MFnPlugin(obj,'Bogdan Diaconu','1.0','Any')
    fnPlugin.registerNode('varfkNode',varfkNode.kPluginNodeId, creator, initialize)
    
def uninitializePlugin(obj):
    fnPlugin = OpenMayaMpx.MFnPlugin(obj)
    fnPlugin.deregisterNode(varfkNode.kPluginNodeId)

