import maya.OpenMayaMPx as OpenMayaMpx
import maya.OpenMaya as OpenMaya
import math
import pymel.core as pm

class sePushPullConstraint(OpenMayaMpx.MPxNode):
    kPluginNodeId = OpenMaya.MTypeId(0X00001237)
    
    constTransAttr = OpenMaya.MObject()
    ctAttrX = OpenMaya.MObject()
    ctAttrY = OpenMaya.MObject()
    ctAttrZ = OpenMaya.MObject()
    lastPositionAttr = OpenMaya.MObject()
    lpAttrX = OpenMaya.MObject()
    lpAttrY = OpenMaya.MObject()
    lpAttrZ = OpenMaya.MObject()
    distanceAttr = OpenMaya.MObject()
    inTimeAttr = OpenMaya.MObject()
    startFrameAttr = OpenMaya.MObject()
    targetAttr = OpenMaya.MObject()
    startPositionAttr = OpenMaya.MObject()
    spAttrX = OpenMaya.MObject()
    spAttrY = OpenMaya.MObject()
    spAttrZ = OpenMaya.MObject()
    pullAttr = OpenMaya.MObject()
    pushAttr = OpenMaya.MObject()
    constraintParentAttr = OpenMaya.MObject()
    id = OpenMaya.MObject()
    
    def __init__(self):
        OpenMayaMpx.MPxNode.__init__(self)
        
    def compute(self,plug,data):
        plugRoot = OpenMaya.MPlug()
        if plug.isChild:
            plugRoot = plug.parent()
        else:
            plugRoot = plug
        
        if plugRoot != sePushPullConstraint.constTransAttr:
            return OpenMaya.kUnknownParameter
        
        currentFrame = data.inputValue(sePushPullConstraint.inTimeAttr).asTime()
        startFrame  = data.inputValue(sePushPullConstraint.startFrameAttr).asDouble()
        
        outputHandle = data.outputValue(sePushPullConstraint.constTransAttr)
        
        if currentFrame.value() < startFrame:
            startPos = data.inputValue(sePushPullConstraint.startPositionAttr).asVector()
            lastPosHandle = data.outputValue(lastPositionAttr)
            
            lastPosHandle.setMVector(startPos)
            outputHandle.setMVector(startPos)
            #we are done
            data.setClean(constTransAttr)
            data.setClean(lastPositionAttr)
            return OpenMaya.MStatus.kSuccess
        
        #get the push / pull attribute
        isPullActive = data.inputValue(sePushPullConstraint.pullAttr).asBool()
        isPushActive = data.inputValue(sePushPullConstraint.pushAttr).asBool()
        
        if not isPullActive and not isPushActive:
            data.setClean(sePushPullConstraint.constTransAttr)
            return OpenMaya.MStatus.kSuccess
        
        lp = data.inputValue(sePushPullConstraint.lastPositionAttr).asVector()
        lastPosition = OpenMaya.MPoint(lp)
        
        targetMat = data.inputValue(sePushPullConstraint.targetAttr).asMatrix()
        targetPos = OpenMaya.MPoint(targetMat[3][0], targetMat[3][1], targetMat[3][2])
        
        dist = data.inputValue(sePushPullConstraint.distanceAttr).asDouble()
        
        constraintParentMat = data.inputValue(sePushPullConstraint.constraintParentAttr).asMatrix()
        
        relativePos = OpenMaya.MVector((lastPosition * constraintParentMat) - targetPos)
        
        currentDistance =  relativePos.length()
            
        if (isPullActive and (currentDistance > dist)) or (isPushActive and currentDistance < dist):
            relativePos.normalize()
            relativePos *= dist
            newPosition = OpenMaya.MPoint(targetPos + relativePos)
            
            localPos = OpenMaya.MVector(newPosition * constraintParentMat.inverse())
            
            outputHandle.setMVector(localPos)
            
            lastPosOutHandle = data.outputValue(sePushPullConstraint.lastPositionAttr);
            lastPosOutHandle.setMVector(localPos);
        
            data.setClean(lastPositionAttr)        
        
def creator():
    return OpenMayaMpx.asMPxPtr(sePushPullConstraint())


def initialize():
    nAttr = OpenMaya.MFnNumericAttribute()
    unitAttr = OpenMaya.MFnUnitAttribute()
    matrixAttr = OpenMaya.MFnMatrixAttribute()
    
    #output
    sePushPullConstraint.ctAttrX = nAttr.create("constraintTranslateX", "ctx", OpenMaya.MFnNumericData.kDouble,0.0)
    sePushPullConstraint.ctAttrY = nAttr.create("constraintTranslateY", "cty", OpenMaya.MFnNumericData.kDouble,0.0)
    sePushPullConstraint.ctAttrZ = nAttr.create("constraintTranslateZ", "ctz", OpenMaya.MFnNumericData.kDouble,0.0)
    sePushPullConstraint.constTransAttr = nAttr.create("constraintTranslate", "ct", ctAttrX, ctAttrY, ctAttrZ)
    nAttr.setWritable(0)
    sePushPullConstraint.addAttribute(sePushPullConstraint.constTransAttr)
    
    #inputs
    sePushPullConstraint.inTimeAttr = unitAttr.create("inTime", "it",  OpenMaya.MFnNumericData.kTime, 1.0)
    unitAttr.setStorable(0)
    unitAttr.setKeyable(0)
    unitAttr.setHidden(1)
    sePushPullConstraint.addAttribute(inTimeAttr)
    sePushPullConstraint.attributeAffects(sePushPullConstraint.inTimeAttr, sePushPullConstraint.constTransAttr)
    
    sePushPullConstraint.startFrameAttr = nAttr.create("inTime", "it", OpenMaya.MFnNumericData.kDouble,0.0)
    nAttr.setKeyable(1)
    sePushPullConstraint.addAttribute(sePushPullConstraint.startFrameAttr)
    sePushPullConstraint.attributeAffects(sePushPullConstraint.startFrameAttr,sePushPullConstraint.constTransAttr)
    
    #create the distance attribute
    sePushPullConstraint.distanceAttr = nAttr.create("distance", "dist",  OpenMaya.MFnNumericData.kDouble)
    nAttr.setKeyable(True)
    nAttr.setMin(0.0)
    sePushPullConstraint.addAttribute(sePushPullConstraint.distanceAttr)
    sePushPullConstraint.attributeAffects(sePushPullConstraint.distanceAttr, sePushPullConstraint.constTransAttr)
    
    #create the target world matrix attribute
    sePushPullConstraint.targetAttr = matrixAttr.create("targetWorldMatrix", "twm", OpenMaya.MFnNumericData.kDouble)
    matrixAttr.setStorable(False)
    sePushPullConstraint.addAttribute(sePushPullConstraint.targetAttr)
    attributeAffects(sePushPullConstraint.targetAttr, sePushPullConstraint.constTransAttr)
    
    #create the constraint parent matrix attribute    
    sePushPullConstraint.constraintParentAttr = matrixAttr.create("constraintParentMatrix", "cpm", OpenMaya.MFnNumericData.kDouble)
    matrixAttr.setStorable(False)
    sePushPullConstraint.addAttribute(sePushPullConstraint.constraintParentAttr)
    sePushPullConstraint.attributeAffects(sePushPullConstraint.constraintParentAttr, sePushPullConstraint.constTransAttr)
    
    #create the start position attribute
    spAttrX = nAttr.create("startPositionX", "spx",OpenMaya.MFnNumericData.kDouble, 0.0)
    spAttrY = nAttr.create("startPositionY", "spy", OpenMaya.MFnNumericData.kDouble, 0.0)
    spAttrZ = nAttr.create("startPositionZ", "spz", OpenMaya.MFnNumericData.kDouble, 0.0)    
    startPositionAttr = nAttr.create("startPosition", "sp", spAttrX, spAttrY, spAttrZ)
    nAttr.setKeyable(True)
    sePushPullConstraint.addAttribute(sePushPullConstraint.startPositionAttr)
    sePushPullConstraint.attributeAffects(sePushPullConstraint.startPositionAttr, sePushPullConstraint.constTransAttr)

    #create the push bool attribute
    sePushPullConstraint.pushAttr = nAttr.create("push", "psh", OpenMaya.MFnNumericData.kBoolean)
    nAttr.setKeyable(True)
    nAttr.setDefault(True)
    sePushPullConstraint.addAttribute(falsepushAttr)
    sePushPullConstraint.attributeAffects(pushAttr, constTransAttr)

    #create the push bool attribute
    pullAttr = nAttr.create("pull", "pll", OpenMaya.MFnNumericData.kBoolean)
    nAttr.setKeyable(True)
    nAttr.setDefault(True)
    addAttribute(pullAttr)
    sePushPullConstraint.attributeAffects(sePushPullConstraint.pullAttr, sePushPullConstraint.constTransAttr)

    #create the last position attribute for internal uses
    sePushPullConstraint.lpAttrX = nAttr.create("lastPositionX", "lpx", OpenMaya.MFnNumericData.kDouble, 0.0)
    sePushPullConstraint.lpAttrY = nAttr.create("lastPositionY", "lpy", OpenMaya.MFnNumericData.kDouble, 0.0)
    sePushPullConstraint.lpAttrZ = nAttr.create("lastPositionZ", "lpz", OpenMaya.MFnNumericData.kDouble, 0.0)
    lastPositionAttr = nAttr.create("lastPosition", "lp", sePushPullConstraint.lpAttrX, sePushPullConstraint.lpAttrY, sePushPullConstraint.lpAttrZ)
    nAttr.setHidden(True)
    sePushPullConstraint.addAttribute(sePushPullConstraint.lastPositionAttr)    


def initializePlugin(obj):
    fnPlugin = OpenMayaMpx.MFnPlugin(obj,'Bogdan Diaconu','1.0','Any')
    fnPlugin.registerNode('sePushPullConstraint',sePushPullConstraint.kPluginNodeId, creator, initialize)
    
def uninitializePlugin(obj):
    fnPlugin = OpenMayaMpx.MFnPlugin(obj)
    fnPlugin.deregisterNode(sePushPullConstraint.kPluginNodeId)