import maya.OpenMayaMPx as OpenMayaMpx
import maya.OpenMaya as OpenMaya
import math
import pymel.core as pm

class trNode(OpenMayaMpx.MPxNode):
    kPluginNodeId = OpenMaya.MTypeId(0X00001235)
    
    aInTranslation = OpenMaya.MObject()
    aInTranslationX = OpenMaya.MObject()
    aInTranslationY = OpenMaya.MObject()
    aInTranslationZ = OpenMaya.MObject()
    aOffset = OpenMaya.MObject()
    aOutTranslation = OpenMaya.MObject()
    aOutTranslationX = OpenMaya.MObject()
    aOutTranslationY = OpenMaya.MObject()
    aOutTranslationZ = OpenMaya.MObject()
    
    
    def __init__(self):
        OpenMayaMpx.MPxNode.__init__(self)
        
    def compute(self,plug,data):
        if plug != trNode.aOutTranslation:
            return OpenMaya.kUnknownParameter
            

        #get inputs
        offset = data.inputValue(trNode.aOffset).asFloat()
        inTranslate = data.inputValue(trNode.aInTranslation).asFloat3()
        
        outTranslate = [inTranslate[0] +  offset,inTranslate[1] +  offset, inTranslate[2] +  offset]
        
        data.outputValue(trNode.aOutTranslationX).setFloat(outTranslate[0])
        data.outputValue(trNode.aOutTranslationY).setFloat(outTranslate[1])
        data.outputValue(trNode.aOutTranslationZ).setFloat(outTranslate[2])
        data.setClean(plug)

            
            

        


def creator():
    return OpenMayaMpx.asMPxPtr(trNode())


def initialize():
    nAttr = OpenMaya.MFnNumericAttribute()
    
    trNode.aInTranslationX = nAttr.create('inTranslationX','intx',OpenMaya.MFnNumericData.kFloat,0.0)
    nAttr.setStorable(1)
    
    
    trNode.aInTranslationY = nAttr.create('inTranslationY','inty',OpenMaya.MFnNumericData.kFloat,0.0)
    nAttr.setStorable(1)
    
    trNode.aInTranslationZ = nAttr.create('inTranslationZ','intz',OpenMaya.MFnNumericData.kFloat,0.0)
    nAttr.setStorable(1)
    
    trNode.aInTranslation = nAttr.create('inTranslation','intr',trNode.aInTranslationX,trNode.aInTranslationY,trNode.aInTranslationZ)
    nAttr.setStorable(1)
    nAttr.setKeyable(1)
    nAttr.setWritable(1)
    trNode.addAttribute(trNode.aInTranslation)    
    
    trNode.aOffset = nAttr.create('offset','offset',OpenMaya.MFnNumericData.kFloat,0.0)
    nAttr.setStorable(1)
    nAttr.setKeyable(1)
    nAttr.setWritable(1)
    trNode.addAttribute(trNode.aOffset)

    trNode.aOutTranslationX = nAttr.create('outTranslationX','otx',OpenMaya.MFnNumericData.kFloat,0.0)
    nAttr.setStorable(0)
    nAttr.setWritable(0)

    
    trNode.aOutTranslationY = nAttr.create('outTranslationY','oty',OpenMaya.MFnNumericData.kFloat,0.0)
    nAttr.setStorable(0)
    nAttr.setWritable(0)

    
    trNode.aOutTranslationZ = nAttr.create('outTranslationZ','otz',OpenMaya.MFnNumericData.kFloat,0.0)
    nAttr.setStorable(0)
    nAttr.setWritable(0)
    
    trNode.aOutTranslation = nAttr.create('outTranslation','outt',trNode.aOutTranslationX,trNode.aOutTranslationY,trNode.aOutTranslationZ)
    nAttr.setStorable(0)
    nAttr.setKeyable(0)
    nAttr.setWritable(0)
    trNode.addAttribute(trNode.aOutTranslation)    

    
    trNode.attributeAffects(trNode.aInTranslation,trNode.aOutTranslation)
    trNode.attributeAffects(trNode.aOffset,trNode.aOutTranslation)



def initializePlugin(obj):
    fnPlugin = OpenMayaMpx.MFnPlugin(obj,'Bogdan Diaconu','1.0','Any')
    fnPlugin.registerNode('trNode',trNode.kPluginNodeId, creator, initialize)
    
def uninitializePlugin(obj):
    fnPlugin = OpenMayaMpx.MFnPlugin(obj)
    fnPlugin.deregisterNode(trNode.kPluginNodeId)

