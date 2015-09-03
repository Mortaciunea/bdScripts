'''
    \file       nrMixamoLib.py
    \author     nielsr
    \date       03/11/14

    \brief      Collection of rigging functions for Mixamo rigs. www.nielsr.org

    \b History:
    \code
    03/02/15    nielsr    added root joint for rig scaling.
    28/01/15    nielsr    initial version.
    \endcode

'''

#!/usr/bin/env python

try:
    import maya.cmds as mc
    import maya.mel as mel
except:
    print "Couldn't load maya.cmds"

#=============================================================================
# FUNCTIONS
#=============================================================================
def convertToZoobeRig():
    '''
    Takes a standard Mixamo rig and converts it into a Zoobe rig.
    Expects an autorigged FBX in original pose to be downloaded from the website and imported into the current Maya scene.
    First executes the original Mixamo python script to create controls.
    Adds eye aim controls, centers eye joints, creates speak blendShapes etc.

    \code
    import nrMixamoLib
    nrMixamoLib.convertToZoobeRig()
    \endcode
    '''

    # Mixamo Setup

    #setupControls_function
    global DJB_CharacterInstance
    DJB_CharacterInstance = None
    DJB_populatePythonSpaceWithCharacter()
    if not DJB_CharacterInstance:
        joints = mayac.ls(type = "joint")
        if not joints:
            OpenMaya.MGlobal.displayError("There must be a Mixamo Autorigged character in the scene.")
        else:
            print ('DJB_CharacterInstance.append(DJB_Character(hulaOption_ = True))')
            DJB_CharacterInstance.append(DJB_Character(hulaOption_ = True))
            print('DJB_CharacterInstance[len(DJB_CharacterInstance)-1].fixArmsAndLegs()')
            DJB_CharacterInstance[len(DJB_CharacterInstance)-1].fixArmsAndLegs()
            
            print('DJB_CharacterInstance[len(DJB_CharacterInstance)-1].makeAnimDataJoints()')
            DJB_CharacterInstance[len(DJB_CharacterInstance)-1].makeAnimDataJoints()
            
            print('DJB_CharacterInstance[len(DJB_CharacterInstance)-1].makeControls()')
            DJB_CharacterInstance[len(DJB_CharacterInstance)-1].makeControls()
            
            print('DJB_CharacterInstance[len(DJB_CharacterInstance)-1].hookUpControls()')
            DJB_CharacterInstance[len(DJB_CharacterInstance)-1].hookUpControls()
            
            print('DJB_CharacterInstance[len(DJB_CharacterInstance)-1].writeInfoNode()')
            DJB_CharacterInstance[len(DJB_CharacterInstance)-1].writeInfoNode()
    
    # add eye rig, speak shapes auto-blink and scale
    mc.setAttr('global_CTRL.s', 1, 1, 1)
    buildFaceShapes('Facial_Blends')
    hookupEyesAimRig()

    # add zoobe attrs
    mc.addAttr('Mesh_GRP',  ln="zoobe_char_model_grp", dt="string")
    #mc.addAttr('Bind_Root', ln="zoobe_char_root_joint", dt="string")

    # scale whole rig to .1 as it is too large. scale should be on main ctl for easy bind pose restoration
    mc.select(d=1)
    rootJnt = mc.joint(position=[0, 0, 0], absolute=1, n='root')
    mc.parent('Bind_Root', rootJnt)
    mc.connectAttr('global_CTRL.s', '%s.s' % rootJnt, f=1)
    mc.setAttr('%s.v' % rootJnt, 0)
    mc.setAttr('global_CTRL.s', .1, .1, .1)
    # add zoobe attrs
    mc.addAttr(rootJnt, ln="zoobe_char_root_joint", dt="string")
    

def hookupEyesAimRig():
    '''
    Build aim rigs for left and right eyeball, hook them up.
    '''
    lEyeJnt = 'mixamorig:LeftEye'
    rEyeJnt = 'mixamorig:RightEye'
    eyeGeo = 'Mesh_Eyes'
    #lEyeGeo = mc.ls(bodyGeo+'.vtx[2570:2951]')
    #rEyeGeo = mc.ls(bodyGeo+'.vtx[2952:3333]')
    lEyeGeo = mc.ls(eyeGeo+'.vtx[94:475]')
    rEyeGeo = mc.ls(eyeGeo+'.vtx[476:763]', eyeGeo+'.vtx[0:93]')

    dataL = buildEyeAimRig(lEyeGeo, eyeGeo, lEyeJnt)
    dataR = buildEyeAimRig(rEyeGeo, eyeGeo, rEyeJnt)

    # set eye limits do prevent them from rotating into the eye cavity
    mc.transformLimits('Bind_LeftEye', rx=[-5.3, 10], enableRotationX=[1, 1])
    mc.transformLimits('Bind_LeftEye', ry=[-10, 20],  enableRotationY=[1, 1])
    mc.transformLimits('Bind_LeftEye', rz=[-45, 45],  enableRotationZ=[1, 1])

    mc.transformLimits('Bind_RightEye', rx=[-5.3, 10], enableRotationX=[1, 1])
    mc.transformLimits('Bind_RightEye', ry=[-20, 10],  enableRotationY=[1, 1])
    mc.transformLimits('Bind_RightEye', rz=[-45, 45],  enableRotationZ=[1, 1])

    mc.namespace(rm='mixamorig:')


    # center control
    con = mc.circle(name='C_eyeAim_CTRL', ch=0, normal=(0, 0, 1), radius=8)
    mc.xform(con, relative=1, scale=[1, 0.8, 1])
    mc.makeIdentity(con, apply=1, t=1, r=1, s=1, n=0, pn=1)
    for a in 'xyz':
        mc.setAttr('%s.s%s' % (con[0], a), l=1, k=0)
    conGrp = mc.group(con, name='C_eyeAimCtl_GRP')
    mc.delete(mc.parentConstraint(dataL[1], dataR[1], conGrp))
    mc.parent(dataL[1], dataR[1], con)

    # import facial con curve
    path = 'P:/happywow/working_project/scenes/characters/01_jane/03_rigging/01_wip/facialCtlTemplate.ma'
    mc.file(path, i=True, type='mayaAscii', mergeNamespacesOnClash=0, rpr='test', options='v=0;', preserveReferences=1)
    mc.setAttr("facialCtl_GRP.translateX", 30)
    mc.setAttr("facialCtl_GRP.translateY", 190)

    # connect blink con
    mc.connectAttr('facial_CTRL.eyelid_L_upper', 'Facial_Blends.Blink_Left')
    mc.connectAttr('facial_CTRL.eyelid_R_upper', 'Facial_Blends.Blink_Right')

    # clean up scene
    mc.parent('facialCtl_GRP', 'Root_CTRL')
    mc.parent(conGrp, 'global_CTRL')

    # add cons to con set
    mc.sets(con, dataL[0], dataR[0], 'facial_CTRL', add='Controls_SelectSet')

    # animate blink
    keyframesLoopborders = [[101, 0], [250, 0]]
    keyframesBlink = [[0, 0], [2, .5], [3, 1], [6, 1.1], [9, 0]]
    blinkStartTimes = [109, 171, 210]

    eyeLidAttrs = ['eyelid_L_upper', 'eyelid_R_upper'] # facial_CTRL
    browAttrs = ['BrowsUp_Left', 'BrowsUp_Right'] # Facial_Blends
    keyedNodes = ['facial_CTRL', 'Facial_Blends']

    for klb in keyframesLoopborders:
        for ela in eyeLidAttrs:
            mc.setKeyframe(keyedNodes[0], attribute=ela, time=klb[0], value=klb[1], inTangentType='auto', outTangentType='auto')
        for ba in browAttrs:
            mc.setKeyframe(keyedNodes[1], attribute=ba, time=klb[0], value=klb[1], inTangentType='auto', outTangentType='auto')
 
    for i in range(0, len(blinkStartTimes)):
        for k in range(0, len(keyframesBlink)):
            for ela in eyeLidAttrs: # offset the blink for each of the blink start times and key the attr
                mc.setKeyframe(keyedNodes[0], attribute=ela, time=keyframesBlink[k][0]+blinkStartTimes[i], value=keyframesBlink[k][1], inTangentType='auto', outTangentType='auto')
            for ba in browAttrs: # offset the blink and modify to use as fleshy animation on brows
                mc.setKeyframe(keyedNodes[1], attribute=ba, time=keyframesBlink[k][0]+blinkStartTimes[i]+1, value=keyframesBlink[k][1]*-0.1, inTangentType='auto', outTangentType='auto')
        
    mc.setInfinity(keyedNodes, preInfinite='cycle', postInfinite='cycle')


def buildEyeAimRig(eyeVerts, eyeGeo='Body', eyeJoint='mixamorig:LeftEye'):
    '''
    Mixamo Rig: Select eye verts, centers joint to verts, builds simple aim eye rig.

    Returns the eye control and its group.
    \code
        buildEyeAimRig(mc.ls(sl=1))
    \endCode
    '''
    worldUpObject = 'Bind_HeadTop_End'
    import maya.mel as mel

    baseName = eyeJoint.replace('mixamorig:', '')

    # rename eye joints to match the rest of the mixamo rig
    eyeJoint = mc.rename(eyeJoint, eyeJoint.replace('mixamorig:', 'Bind_'))

    # center joint to eye ball geo
    center = getCenterAverage(eyeVerts)
    mc.select(eyeGeo, r=1)
    mel.eval('moveJointsMode 1;')
    mc.xform(eyeJoint, ws=1, t=center)
    mel.eval('moveJointsMode 0;')

    # create aim group for joint to aim at
    targetGrp = mc.group(n='%sAimTarget_GRP' %baseName, em=1)
    mc.parent(targetGrp, eyeJoint)
    mc.xform(targetGrp, os=1, t=[0, 0, 40], ro=[0, 0, 0])
    mc.parent(targetGrp, w=1)

    # create aim offset eye hierarchy
    driverJnt = mc.duplicate(eyeJoint, n='%sDriver_JNT' % baseName)
    aimGrp = mc.group(n='%sAim_GRP' %baseName, em=1)
    mc.parent(aimGrp, eyeJoint)
    mc.xform(aimGrp, os=1, t=[0, 0, 0], ro=[0, 0, 0])
    mc.parent(aimGrp, w=1)    
    offsetGrp = mc.duplicate(aimGrp, n='%sOffset_GRP' % baseName)

    # connect
    mc.parent(driverJnt, offsetGrp)
    mc.parent(offsetGrp, aimGrp)
    mc.aimConstraint(targetGrp, aimGrp, n=aimGrp.replace('_GRP', '_AIC'), aimVector=[0, 0, 1], worldUpType='objectrotation', worldUpObject=worldUpObject)

    # for a in 'trs':
    #    mc.connectAttr('%s.%s' %(driverJnt[0], a), '%s.%s' %(baseName, a))
    mc.parentConstraint(driverJnt[0], eyeJoint, n=baseName+'_PAC')
    mc.scaleConstraint (driverJnt[0], eyeJoint, n=baseName+'_SAC')

    # cleanup
    mc.parent(aimGrp, 'Head_CTRL')

    # create controls
    con = mc.circle(name='%s_CTRL' %baseName, ch=0, normal=(0, 0, 1), radius=3)
    for a in 'xyz':
        mc.setAttr('%s.s%s' % (con[0], a), l=1, k=0)

    conGrp = mc.group(con, name='%sCtl_GRP' %baseName)
    mc.delete(mc.parentConstraint(targetGrp, conGrp))
    mc.parent(targetGrp, con)
    return [con, conGrp]

def getCenterAverage(objectsOrComponents):
    '''
    Calculates the center of an array of objects or components by calculating their average
    and returns it.

    \code
        print(getCenterAverage(mc.ls(sl=True)))   # print center of selection
        
        center = getCenterAverage(mc.ls(sl=True)) # create locator at selection center
        mc.spaceLocator()
        mc.xform(ws=1,t=center)
    \endCode
    '''
    pos = []
    if mc.nodeType(objectsOrComponents[0]) == 'transform' or mc.nodeType(objectsOrComponents[0]) == 'joint':
        for i in range(0, len(objectsOrComponents)):
            tmp = mc.xform(objectsOrComponents[i], q=1, t=1, ws=1)
            for j in tmp:
                pos.append(j)
    else:
        pos = mc.xform(objectsOrComponents, q=1, t=1, ws=1)
    center = [0, 0, 0]
    count = len(pos)/3
    for v in range(0, count):
        center[0] += pos[v*3+0]
        center[1] += pos[v*3+1]
        center[2] += pos[v*3+2]
    center[0] /= count
    center[1] /= count
    center[2] /= count
    return center

def buildFaceShapes(blsNode='Facial_Blends'):
    '''
    Mixamo Rig: Create a Zoobe BLS set by blending Mixamo shapes.
   \code
        buildFaceShapes('Facial_Blends')
    \endCode
    '''
    # Array of needed shapes
    shapes = []
    shapes.append(['speak_jaw_down',     ['MouthOpen', 0.8], ['JawBackward', 0.8]])
    shapes.append(['speak_mouth_narrow', ['MouthOpen', 0.1], ['JawBackward', 0.2], ['MouthNarrow_Left', 0.5],  ['MouthNarrow_Right', 0.5]])
    shapes.append(['speak_mouth_wide',   ['MouthOpen', 0.25], ['JawBackward', 0.2], ['MouthNarrow_Left', -0.4],  ['MouthNarrow_Right', -0.4], ['Smile_Left', 0.2],  ['Smile_Right', 0.2]])
    shapes.append(['smile', ['Midmouth_Left', 0.15], ['MouthNarrow_Left', -0.1], ['MouthNarrow_Right', -0.1],  ['NoseScrunch_Left', 0.1], ['NoseScrunch_Right', 0.1],  ['Smile_Left', 0.5],  ['Smile_Right', 0.5],  ['Squint_Left', 0.5],  ['Squint_Right', 0.5]])

    setBlsPose(blsNode, shapes)
    secondaryBlsNodes = ['Facial_Blends_ncl1_1', 'Facial_Blends_ncl1_2']
    setBlsPose(secondaryBlsNodes[0], shapes) # secondary nodes need to have addl shapes so smile shape also moves eye lashes
    setBlsPose(secondaryBlsNodes[1], shapes)
   
    # connect face target nodes to each other
    targets = mc.listAttr('%s.w' % blsNode, m=1) # gets target alias names
    for sbn in secondaryBlsNodes:
        for t in targets:
            try:
                mc.connectAttr('%s.%s' %(blsNode, t), '%s.%s' %(sbn, t), f=1)
            except:
                print 'Couldn\'t connect "%s.%s".' %(sbn, t)

    # clean up target shape group
    shapesGrp = mc.group(em=1, n= 'shapes_GRP')
    mc.parent(shapesGrp, 'Character')
    targetShapes = []
    Mesh_GRPChildren = mc.listRelatives('Mesh_GRP')
    for c in Mesh_GRPChildren:
        if mc.getAttr('%s.v' % c) == 0:
            targetShapes.append(c)

    mc.parent(targetShapes, shapesGrp)

def setBlsPose(blsNode, blsValueArray):
    '''
    get blsNode and set all its channels to 0 and then set blsValueArray channels to provided values
   \code
        setBlsPose('Facial_Blends', [['speak_jaw_down', ['MouthOpen', 0.8], ['JawBackward', 0.8]]])
    \endCode
    '''
    sel = mc.ls(sl=1)
    # set target values according to given array
    for s in blsValueArray: # go through configurations
        # zero bls targets
        targets = mc.listAttr('%s.w' % blsNode, m=1) # gets target alias names
        # mc.blendShape(blsNode, q=1, target=1) gets target geo names
        for t in targets:
            mc.setAttr('%s.%s' % (blsNode, t), 0)

        shape = s[0]
        shapeValuePairs = s[1:]

        for svp in shapeValuePairs: # go through shapes
            mc.setAttr('%s.%s' % (blsNode, svp[0]), svp[1])

        # save configuration as new target shape
        bakeBlsBase(blsNode, shape)

    # zero bls targets
    targets = mc.listAttr('%s.w' % blsNode, m=1)
    for t in targets:
        mc.setAttr('%s.%s' % (blsNode, t), 0)
    if len(sel):
        mc.select(sel, r=1)

def bakeBlsBase(blsNode, targetName):
    '''
    Bake the current base shape into a new target called targetName and assign it to the blendShape node
    Useful for combining a number of generic targets into a new target for speak animation
    \code
        bakeBlsBase('Facial_Blends', 'speak_jaw_down')
    \endCode
    '''
    baseShape = mc.blendShape(blsNode, q=1, geometry=1)
    newShape = mc.duplicate(baseShape, rr=1)

    # make sure shape can be named correctly by grouping it
    grp = mc.group(newShape)
    newShape = mc.rename(newShape, targetName)

    # get number of existing shapes
    num = len(mc.listAttr('%s.w' % blsNode, m=1)) # gets target geo names

    # add the new shape as the next free slot
    mc.blendShape(blsNode, edit=True, t=(''+baseShape[0], num, newShape, 1.0))
    mc.setAttr('%s.v' % newShape, l=0)
    mc.setAttr('%s.v' % newShape, 0)

    # ungroup shape
    mc.ungroup(grp)

    return newShape

#=============================================================================
# MIXAMO FUNCTIONS
#=============================================================================
DJB_ABOUT_TEXT = """
MIXAMO Maya Auto Control Rig      
www.mixamo.com/c/maya-auto-control-rig   
Copyright Mixamo www.mixamo.com 2012 Created by Dan Babcock
    Additional code by Paolo Dominici: Thanks for letting us integrate ZV Dynamics!

This script automatically creates a no-bake-necessary control rig for 
    editing MIXAMO motions and/or keyframing animation

    
Notes:
    Autodesk Maya 2009 or higher is required.
    Requires a character Autorigged by Mixamo

To Use:
    Run the script.

Noted Features:
    FK/IK legs and arms that follow animation data with no baking
    Keyable AnimDataMult attributes that exaggerate or ignore animation data
    The ability to bake animation to controls at any point in time
    The ability to clear controls at any point in time, preserving animation
    IK legs and arms can follow body motion
    Hands and Feet custom attributes
    Export baked FK skeleton
    Dynamic Joints / Joint Chains
"""

Mixamo_AutoControlRig_Version = "1.5.0"

DJB_CHANGELOG_TEXT = """
Changes in 1.5.0:
    Fixed bug with mesh export
    Blendshape animation now exports with "Export with Mesh" 
        *Only works on non-referenced rigs - needs to disconnect and reconnect attributes
    Fixed bug in IK creation
    Removed extraneous code
    Added option to remove end joints on export
Changes in 1.04d:
    Fix for no finger joints at all
Changes in 1.04c:
    Added support for characters with only one spine joint
    Fixed some namespace issues
    Extra Joints exports now have translates unlocked
Changes in 1.04b:
    Added handling of meshes (usually blendshapes) where 
      the shape node had the same name as the transform
Changes in 1.04a:
    Added support for dynamic joints and joint chains! 
      (integrated ZV Dynamics by Paolo Dominici)
    Added utilities for recreating infonodes 
    Fixed application of namespace on export joints when 
      namespace is not present in the scene
    Reworked UI
    Batching functionality
"""

    
import maya.cmds as mayac
import maya.mel as mel
import maya.OpenMaya as OpenMaya
import math
import sys
import re
import cPickle
import os
mel.eval("source channelBoxCommand.mel;")
mel.eval("cycleCheck -e off")

FBXpluginLoaded = mayac.pluginInfo("fbxmaya", query = True, loaded = True)
if not FBXpluginLoaded:
    mayac.loadPlugin( "fbxmaya")

ERRORCHECK = 0
JOINT_NAMESPACE = ""
proportionCheckTolerance = .03
DJB_Character_ProportionOverrideCube = ""




#assorted functions
def goToWebpage(page):
    if page == "mixamo":
        mayac.showHelp( 'http://www.mixamo.com', absolute = True)
    elif page == "autoRigger":
        mayac.showHelp( 'http://www.mixamo.com/c/auto-rigger', absolute = True)
    elif page == "motions":
        mayac.showHelp( 'http://www.mixamo.com/motions', absolute = True)
    elif page == "autoControlRig":
        mayac.showHelp( 'http://www.mixamo.com/c/auto-control-rig-for-maya', absolute = True)
    elif page == "community":
        mayac.showHelp( 'https://community.mixamo.com', absolute = True)
    elif page == "tutorials":
        mayac.showHelp( 'https://community.mixamo.com/hc/en-us/sections/200559213-Maya', absolute = True)
    else:
        OpenMaya.MGlobal.displayError("Webpage Call Invalid")

def DJB_BrowserWindow(filter_ = None, caption_ = "Browse", fileMode_ = "directory"):
    multipleFilters = None
    filtersOld = None
    if filter_ == "Maya":
        multipleFilters = "Maya Files (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb)"
        filtersOld = None
    elif filter_ == "Maya_FBX":
        multipleFilters = "Maya Files (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb);;FBX (*.fbx);;All Files (*.*)"
    elif filter_ == "FBX":
        multipleFilters = "FBX (*.fbx);;All Files (*.*)"
    else:
        multipleFilters = ""
    window = None    
    version = mel.eval("float $ver = `getApplicationVersionAsFloat`;")
    if version <= 2011.0:
        if fileMode_ == "directory":
            window = mayac.fileBrowserDialog(dialogStyle = 2, windowTitle = caption_, fileType = "directory")
    else: #new style dialog window
        if fileMode_ == "directory":
            window = mayac.fileDialog2(fileFilter=multipleFilters, dialogStyle=2, caption = caption_, fileMode = 3, okCaption = "Select")
        else:
            window = mayac.fileDialog2(fileFilter=multipleFilters, dialogStyle=2, caption = caption_, fileMode = 4, okCaption = "Select")
    if window:
        return window[0]
    else:
        return window

def DJB_LockNHide(node, tx = True, ty = True, tz = True, rx = True, ry = True, rz = True, s = True, v = True, other = None):
    if tx:
        mayac.setAttr("%s.tx" % (node), lock = True, keyable = False, channelBox  = False)
    if ty:
        mayac.setAttr("%s.ty" % (node), lock = True, keyable = False, channelBox  = False)
    if tz:
        mayac.setAttr("%s.tz" % (node), lock = True, keyable = False, channelBox  = False)
    if rx:
        mayac.setAttr("%s.rx" % (node), lock = True, keyable = False, channelBox  = False)
    if ry:
        mayac.setAttr("%s.ry" % (node), lock = True, keyable = False, channelBox  = False)
    if rz:
        mayac.setAttr("%s.rz" % (node), lock = True, keyable = False, channelBox  = False)
    if s:
        mayac.setAttr("%s.sx" % (node), lock = True, keyable = False, channelBox  = False)
        mayac.setAttr("%s.sy" % (node), lock = True, keyable = False, channelBox  = False)
        mayac.setAttr("%s.sz" % (node), lock = True, keyable = False, channelBox  = False)
    if v:
        mayac.setAttr("%s.v" % (node), lock = True, keyable = False, channelBox  = False)
    if other:
        for att in other:
            if mayac.objExists("%s.%s" % (node, att)):
                mayac.setAttr("%s.%s" % (node, att), lock = True, keyable = False, channelBox  = False)
        
        
def DJB_Unlock(node, tx = True, ty = True, tz = True, rx = True, ry = True, rz = True, s = True, v = True):
    if tx:
        mayac.setAttr("%s.tx" % (node), lock = False, keyable = True)
    if ty:
        mayac.setAttr("%s.ty" % (node), lock = False, keyable = True)
    if tz:
        mayac.setAttr("%s.tz" % (node), lock = False, keyable = True)
    if rx:
        mayac.setAttr("%s.rx" % (node), lock = False, keyable = True)
    if ry:
        mayac.setAttr("%s.ry" % (node), lock = False, keyable = True)
    if rz:
        mayac.setAttr("%s.rz" % (node), lock = False, keyable = True)
    if s:
        mayac.setAttr("%s.sx" % (node), lock = False, keyable = True)
        mayac.setAttr("%s.sy" % (node), lock = False, keyable = True)
        mayac.setAttr("%s.sz" % (node), lock = False, keyable = True)
    if v:
        mayac.setAttr("%s.v" % (node), lock = False, keyable = True)
 
 
def DJB_Unlock_Connect_Lock(att1, att2):
    mayac.setAttr(att2, lock = False, keyable = True)
    mayac.connectAttr(att1, att2)
    mayac.setAttr(att2, lock = True, keyable = False) 
    
def DJB_ConnectAll(xform1, xform2):
    mayac.connectAttr("%s.tx"%(xform1), "%s.tx"%(xform2))
    mayac.connectAttr("%s.ty"%(xform1), "%s.ty"%(xform2))
    mayac.connectAttr("%s.tz"%(xform1), "%s.tz"%(xform2))
    mayac.connectAttr("%s.rx"%(xform1), "%s.rx"%(xform2))
    mayac.connectAttr("%s.ry"%(xform1), "%s.ry"%(xform2))
    mayac.connectAttr("%s.rz"%(xform1), "%s.rz"%(xform2))

def DJB_parentShape(master, slaveGRP):
    mayac.parent(slaveGRP, master)
    mayac.makeIdentity(slaveGRP, apply = True, t=1, r=1, s=1, n=0) 
    shapes = mayac.listRelatives(slaveGRP, shapes = True)
    for shape in shapes:
        mayac.parent(shape, master, relative = True, shape = True)
    mayac.delete(slaveGRP)

def DJB_createGroup(transform = None, suffix = None, fullName = None, pivotFrom = "self"):
    Grp = 0
    if suffix:
        Grp = mayac.group(empty = True, name = (transform + suffix))
    elif fullName:
        Grp = mayac.group(empty = True, name = fullName)
    else:
        Grp = mayac.group(empty = True, name = (transform + "GRP"))
    if pivotFrom == "self":
        mayac.delete(mayac.parentConstraint(transform, Grp))
    else:
        mayac.delete(mayac.parentConstraint(pivotFrom, Grp))
    if transform:
        mayac.parent(transform, Grp)
    return Grp

def DJB_movePivotToObject(moveMe, toHere, posOnly = False):
    POS = mayac.xform(toHere, query=True, absolute=True, worldSpace=True ,rp=True)
    mayac.move(POS[0], POS[1], POS[2], (moveMe + ".rotatePivot"), (moveMe + ".scalePivot"), absolute=True, worldSpace=True)
    if not posOnly:
        mayac.parent(moveMe, toHere)
        DJB_cleanGEO(moveMe)
        mayac.parent(moveMe, world=True)
         

def DJB_findBeforeSeparator(object, separatedWith):
    latestSeparator = object.rfind(separatedWith)
    return object[0:latestSeparator+1]
    
def DJB_findAfterSeperator(object, separatedWith):
    latestSeparator = object.rfind(separatedWith)
    return object[latestSeparator+1:len(object)]
    
    
def DJB_addNameSpace(namespace, string):
    if string == None:
        return None
    elif namespace == None:
        return string
    else:
        return namespace + string
    
def DJB_cleanGEO(mesh):
    mayac.setAttr("%s.tx" % (mesh), lock = False, keyable = True)
    mayac.setAttr("%s.ty" % (mesh), lock = False, keyable = True)
    mayac.setAttr("%s.tz" % (mesh), lock = False, keyable = True)
    mayac.setAttr("%s.rx" % (mesh), lock = False, keyable = True)
    mayac.setAttr("%s.ry" % (mesh), lock = False, keyable = True)
    mayac.setAttr("%s.rz" % (mesh), lock = False, keyable = True)
    mayac.setAttr("%s.sx" % (mesh), lock = False, keyable = True)
    mayac.setAttr("%s.sy" % (mesh), lock = False, keyable = True)
    mayac.setAttr("%s.sz" % (mesh), lock = False, keyable = True)
    mayac.setAttr("%s.visibility" % (mesh), lock = False, keyable = True)
    mayac.makeIdentity(mesh, apply = True, t=1, r=1, s=1, n=0)
    mayac.delete(mesh, constructionHistory = True)
    return mesh    


def DJB_ZeroOut(transform):
    if transform:
        if not mayac.getAttr("%s.tx" % (transform),lock=True):
            mel.eval('CBdeleteConnection "%s.tx";'%(transform))
            mayac.setAttr("%s.tx" % (transform), 0)
        if not mayac.getAttr("%s.ty" % (transform),lock=True):
            mel.eval('CBdeleteConnection "%s.ty";'%(transform))
            mayac.setAttr("%s.ty" % (transform), 0)
        if not mayac.getAttr("%s.tz" % (transform),lock=True):
            mel.eval('CBdeleteConnection "%s.tz";'%(transform))
            mayac.setAttr("%s.tz" % (transform), 0)
        if not mayac.getAttr("%s.rx" % (transform),lock=True):
            mel.eval('CBdeleteConnection "%s.rx";'%(transform))
            mayac.setAttr("%s.rx" % (transform), 0)
        if not mayac.getAttr("%s.ry" % (transform),lock=True):
            mel.eval('CBdeleteConnection "%s.ry";'%(transform))
            mayac.setAttr("%s.ry" % (transform), 0)
        if not mayac.getAttr("%s.rz" % (transform),lock=True):
            mel.eval('CBdeleteConnection "%s.rz";'%(transform))
            mayac.setAttr("%s.rz" % (transform), 0)


def DJB_ZeroOutAtt(att, value = 0):
    if mayac.objExists("%s" % (att)):
        mel.eval('CBdeleteConnection %s;'%(att))
        mayac.setAttr("%s" % (att), value)


def DJB_ChangeDisplayColor(object, color = None):
    colorNum = 0
    if color == "red1":
        colorNum = 12
    elif color == "red2":
        colorNum = 10
    elif color == "red3":
        colorNum = 24
    elif color == "blue1":
        colorNum = 15
    elif color == "blue2":
        colorNum = 29
    elif color == "blue3":
        colorNum = 28
    elif color == "yellow":
        colorNum = 17
    elif color == "white":
        colorNum = 16
    else:    #default is black
        colorNum = 1
    if object:
        mayac.setAttr('%s.overrideEnabled' % (object), 1)
        mayac.setAttr('%s.overrideColor' % (object), colorNum)


def DJB_CheckAngle(object1, object2, object3, axis = "z", multiplier = 1): #axis can be "x", "y", or "z"
    obj1POS = mayac.xform(object1, query = True, worldSpace = True, absolute = True, translation = True)
    obj3POS = mayac.xform(object3, query = True, worldSpace = True, absolute = True, translation = True)
    rotOrig = mayac.getAttr("%s.rotate%s" % (object2, axis.upper()))
    distOrig = math.sqrt((obj3POS[0]-obj1POS[0])*(obj3POS[0]-obj1POS[0]) + (obj3POS[1]-obj1POS[1])*(obj3POS[1]-obj1POS[1]) + (obj3POS[2]-obj1POS[2])*(obj3POS[2]-obj1POS[2]))
    mayac.setAttr("%s.rotate%s" % (object2, axis.upper()), rotOrig + .5*multiplier)
    obj1POS = mayac.xform(object1, query = True, worldSpace = True, absolute = True, translation = True)
    obj3POS = mayac.xform(object3, query = True, worldSpace = True, absolute = True, translation = True)
    distBack = math.sqrt((obj3POS[0]-obj1POS[0])*(obj3POS[0]-obj1POS[0]) + (obj3POS[1]-obj1POS[1])*(obj3POS[1]-obj1POS[1]) + (obj3POS[2]-obj1POS[2])*(obj3POS[2]-obj1POS[2]))
    mayac.setAttr("%s.rotate%s" % (object2, axis.upper()), rotOrig)
    if distOrig < distBack:
        return True
    else:
        return False


def pyToAttr(objAttr, data):
    obj, attr = objAttr.split('.')
    if not mayac.objExists(objAttr):
        mayac.addAttr(obj, longName=attr, dataType='string')
    if mayac.getAttr(objAttr, type=True) != 'string':
        raise Exception("Object '%s' already has an attribute called '%s', but it isn't type 'string'"%(obj,attr))

    stringData = cPickle.dumps(data)
    mayac.setAttr(objAttr, stringData, type='string')


def attrToPy(objAttr):
    if mayac.objExists(objAttr):
        stringAttrData = str(mayac.getAttr(objAttr))
        loadedData = cPickle.loads(stringAttrData)
        return loadedData
    else:
        return None
        
        
        
def makeUnique(object, keyword):
    if "|" in object: #and geo[geo.rfind("|")+1:] == parent[parent.rfind("|")+1]:
        object = mayac.rename(object, object[object.rfind("|")+1:] + keyword)
        object = makeUnique(object, keyword)
    return object
    
    
###################### Portion of ZV Dynamics 2.0 by Paolo Dominici ##########################

def particleMethod(obj, weight=0.5, conserve=1.0, transfShapes=False):
    return _particleDyn(obj, weight, conserve, transfShapes, False)

def nParticleMethod(obj, weight=0.5, conserve=1.0, transfShapes=False):
    return _particleDyn(obj, weight, conserve, transfShapes, True)

def _particleDyn(obj, weight, conserve, transfShapes, nucleus):
    "Metodo generico di dinamica basata sulla particella"
    c = obj
    
    cNoPath = c[c.rfind("|")+1:]
    dynName = cNoPath + "_DYN"
    partName = cNoPath + "_INIT"
    dynLocName = cNoPath + "_DYN_LOC"
    statLocName = cNoPath + "_STAT_LOC"
    revName = cNoPath + "_REV"
    exprName = cNoPath + "_Expression"
    octName = cNoPath + "Oct"
    
    # leggo la posizione dell'oggetto
    pos = mayac.xform(c, q=True, rp=True, ws=True)
    
    # creo la particella
    if nucleus:
        partic, partShape = mayac.nParticle(n=partName, p=pos)
    else:
        partic, partShape = mayac.particle(n=partName, p=pos)
    
    partShape = "%s|%s" % (partic, partShape)
    
    # sposto il pivot
    mayac.xform(partic, piv=pos, ws=True)
    # aggiungo uno shape alla particella
    octName = drawOct(octName, r=0.25, pos=pos)
    octShapeName = mayac.listRelatives(octName, s=True, pa=True)[0]
    
    mayac.setAttr(octShapeName + ".overrideEnabled", True)
    mayac.setAttr(octShapeName + ".overrideColor", 13)
    mayac.parent([octShapeName, partic], s=True, r=True)
    mayac.delete(octName)
    
    # creo i locator
    statLocGrp = mayac.group("|" + mayac.spaceLocator(n=statLocName)[0], n="g_" + statLocName)
    dynLocGrp = mayac.group("|" + mayac.spaceLocator(n=dynLocName)[0], n="g_" + dynLocName)
    mayac.setAttr("|%s|%s.overrideEnabled" % (dynLocGrp, dynLocName), True)
    mayac.setAttr("|%s|%s.overrideColor" % (dynLocGrp, dynLocName), 6)
    
    # se e' attivo transfer shapes uso un gruppo invece di creare il cubetto
    if transfShapes:
        dyn = mayac.group(n=dynName, em=True)
    else:
        # cubetto colorato di blu orientato secondo l'oggetto
        dyn = drawCube(dynName, l=0.5)
        cubeShape = mayac.listRelatives(dyn, s=True, pa=True)[0]
        mayac.setAttr(cubeShape + ".overrideEnabled", True)        # colore
        mayac.setAttr(cubeShape + ".overrideColor", 6)
    
    # ruoto il cubetto e i locator (molto + carino)
    mayac.xform(["|" + statLocGrp, "|" + dynLocGrp, dyn], ro=mayac.xform(c, q=True, ro=True, ws=True), ws=True)
    mayac.xform(["|" + statLocGrp, "|" + dynLocGrp, dyn], t=pos, ws=True)
    dyn = mayac.parent([dyn, c])[0]
    mayac.makeIdentity(dyn, apply=True)                        # in questo modo il cubo assume le coordinate dell'oggetto pur essendo posizionato nel suo pivot
    
    # parento dyn allo stesso parente dell'oggetto
    parentObj = mayac.listRelatives(c, p=True, pa=True)
    if parentObj:
        dyn = mayac.parent([dyn, parentObj[0]])[0]
    else:
        dyn = mayac.parent(dyn, w=True)[0]
    c = mayac.parent([c, dyn])[0]
    
    mayac.parent(["|" + statLocGrp, "|" + dynLocGrp, dyn])
    
    # aggiorna i nomi con i percorsi
    statLocGrp = "%s|%s" % (dyn, statLocGrp)
    dynLocGrp = "%s|%s" % (dyn, dynLocGrp)
    statLoc = "%s|%s" % (statLocGrp, statLocName)
    dynLoc = "%s|%s" % (dynLocGrp, dynLocName)
    
    # goal particella-loc statico
    mayac.goal(partic, g=statLoc, utr=True, w=weight)
    
    # nascondo locator
    mayac.hide([statLocGrp, dynLocGrp])
    
    # rendo template la particella
    mayac.setAttr(partShape + '.template', True)
    
    # aggiungo l'attributo di velocita'
    mayac.addAttr(c, ln="info", at="enum", en=" ", keyable=True)
    mayac.setAttr(c + ".info", l=True)
    mayac.addAttr(c, ln="velocity", at="double3")
    mayac.addAttr(c, ln="velocityX", at="double", p="velocity", k=True)
    mayac.addAttr(c, ln="velocityY", at="double", p="velocity", k=True)
    mayac.addAttr(c, ln="velocityZ", at="double", p="velocity", k=True)

    # point oggetto tra i locator statico e dinamico
    pc = mayac.pointConstraint(statLoc, dynLoc, c, n=cNoPath + "_PC")[0]
    mayac.addAttr(dyn, ln="settings", at="enum", en=" ", keyable=True)
    mayac.setAttr(dyn + ".settings", l=True)
    mayac.addAttr(dyn, ln="dynamicsBlend", at="double", min=0.0, max=1.0, dv=1.0, keyable=True)
    mayac.addAttr(dyn, ln="weight", at="double", min=0.0, max=1.0, dv=weight, keyable=True)
    mayac.addAttr(dyn, ln="conserve", at="double", min=0.0, max=1.0, dv=conserve, keyable=True)
    rev = mayac.createNode("reverse", n=revName)
    mayac.connectAttr(dyn + ".dynamicsBlend", pc + ".w1")
    mayac.connectAttr(dyn + ".dynamicsBlend", rev + ".inputX")
    mayac.connectAttr(rev + ".outputX", pc + ".w0")
    mayac.connectAttr(dyn + ".weight", partShape + ".goalWeight[0]")
    mayac.connectAttr(dyn + ".conserve", partShape + ".conserve")
    # locco il point constraint
    [mayac.setAttr("%s.%s" % (pc, s), l=True) for s in ["offsetX", "offsetY", "offsetZ", "w0", "w1", "nodeState"]]
    # locco il reverse
    [mayac.setAttr("%s.%s" % (revName, s), l=True) for s in ["inputX", "inputY", "inputZ"]]
    
    # nParticle
    if nucleus:
        nucleusNode = mayac.listConnections(partShape + ".currentState")[0]
        mayac.setAttr(nucleusNode + '.gravity', 0.0)
        
        expr = """// rename if needed
string $dynHandle = "%s";
string $particleObject = "%s";
string $dynLocator = "%s";

undoInfo -swf 0;
$ast = `playbackOptions -q -ast`;
if (`currentTime -q` - $ast < 2) {
//    %s.startFrame = $ast;                        // remove it if you don't want to change nucleus start time
    $destPiv = `xform -q -rp -ws $dynHandle`;
    $origPiv = `xform -q -rp -ws $particleObject`;
    xform -t ($destPiv[0]-$origPiv[0]) ($destPiv[1]-$origPiv[1]) ($destPiv[2]-$origPiv[2]) -r -ws $particleObject;
}

$zvPos = `getParticleAttr -at worldPosition ($particleObject + ".pt[0]")`;
$currUnit = `currentUnit -q -linear`;
if ($currUnit != "cm") {
    $zvPos[0] = `convertUnit -f "cm" -t $currUnit ((string)$zvPos[0])`;
    $zvPos[1] = `convertUnit -f "cm" -t $currUnit ((string)$zvPos[1])`;
    $zvPos[2] = `convertUnit -f "cm" -t $currUnit ((string)$zvPos[2])`;
}
xform -a -ws -t $zvPos[0] $zvPos[1] $zvPos[2] $dynLocator;
$zvVel = `getParticleAttr -at velocity ($particleObject + ".pt[0]")`;        // velocity relative to the particleObject
%s.velocityX = $zvVel[0];
%s.velocityY = $zvVel[1];
%s.velocityZ = $zvVel[2];
undoInfo -swf 1;""" % (dyn, partic, dynLocName, nucleusNode, c, c, c)
    
    # particella standard
    else:
        mayac.setAttr(partic + ".visibility", False)
        expr = """// rename if needed
string $dynHandle = "%s";
string $particleObject = "%s";
string $dynLocator = "%s";

undoInfo -swf 0;
$ast = `playbackOptions -q -ast`;
if (`currentTime -q` - $ast < 2) {
    %s.startFrame = $ast;
    $destPiv = `xform -q -rp -ws $dynHandle`;
    $origPiv = `xform -q -rp -ws $particleObject`;
    xform -t ($destPiv[0]-$origPiv[0]) ($destPiv[1]-$origPiv[1]) ($destPiv[2]-$origPiv[2]) -r -ws $particleObject;
}

$zvPos = `getParticleAttr -at worldPosition ($particleObject + ".pt[0]")`;
$currUnit = `currentUnit -q -linear`;
if ($currUnit != "cm") {
    $zvPos[0] = `convertUnit -f "cm" -t $currUnit ((string)$zvPos[0])`;
    $zvPos[1] = `convertUnit -f "cm" -t $currUnit ((string)$zvPos[1])`;
    $zvPos[2] = `convertUnit -f "cm" -t $currUnit ((string)$zvPos[2])`;
}
xform -a -ws -t $zvPos[0] $zvPos[1] $zvPos[2] $dynLocator;
$zvVel = `getParticleAttr -at velocity ($particleObject + ".pt[0]")`;        // velocity relative to the particleObject
%s.velocityX = $zvVel[0];
%s.velocityY = $zvVel[1];
%s.velocityZ = $zvVel[2];
undoInfo -swf 1;""" % (dyn, partic, dynLocName, partShape, c, c, c)
    
    # crea l'espressione
    mayac.expression(n=exprName, s=expr)
    
    # se il check e' attivo trasferisci le geometrie nel nodo dinamico
    if transfShapes:
        shapes = mayac.listRelatives(c, s=True, pa=True)
        if shapes:
            mayac.parent(shapes + [dyn], r=True, s=True)
    
    # locks
    [mayac.setAttr(partic + s, k=False, cb=True) for s in [".tx", ".ty", ".tz", ".rx", ".ry", ".rz", ".sx", ".sy", ".sz", ".v", ".startFrame"]]
    
    return dyn

def drawOct(name, r=1.0, pos=(0.0, 0.0, 0.0)):
    p = [(s[0]+pos[0], s[1]+pos[1], s[2]+pos[2]) for s in [(0, 0, r), (r, 0, 0), (0, 0, -r), (-r, 0, 0), (0, -r, 0), (r, 0, 0), (0, r, 0), (-r, 0, 0), (0, 0, r), (0, r, 0), (0, 0, -r), (0, -r, 0), (0, 0, r)]]
    return mayac.rename(mayac.curve(d=1, p=p), name)

def drawCube(name, l=1.0, pos=(0.0, 0.0, 0.0)):
    r = l*0.5
    p = [(s[0]+pos[0], s[1]+pos[1], s[2]+pos[2]) for s in [(-r, r, r,), (r, r, r,), (r, r, -r,), (-r, r, -r,), (-r, -r, -r,), (r, -r, -r,), (r, -r, r,), (-r, -r, r,), (-r, r, r,), (-r, r, -r,), (-r, -r, -r,), (-r, -r, r,), (r, -r, r,), (r, r, r,), (r, r, -r,), (r, -r, -r,)]]
    return mayac.rename(mayac.curve(d=1, p=p), name)


###################### End of portion used of ZV Dynamics 2.0 by Paolo Dominici ##########################




class blendShapeAttrTracker(object):
    def __init__(self, blendShapeNode, attr, meshOrig):
        self.blendShapeNode = blendShapeNode
        self.attr = attr
        self.meshOrig = meshOrig
        self.attrFull = "%s.%s"%(self.blendShapeNode,self.attr)
        self.connection = mayac.listConnections(self.attrFull,plugs=True)
        if self.connection:
            self.connection = self.connection[0]
    def deleteConnection(self):
        if self.connection:
            mayac.disconnectAttr(self.connection, self.attrFull)
    def reconnect(self, blendShapeNodeOrigTempName = None):
        self.blendShapeNodeOrigTempName = blendShapeNodeOrigTempName
        if self.connection:
            mayac.connectAttr(self.connection, "%s.%s"%(self.blendShapeNodeOrigTempName,self.attr))
    def off(self):
        mayac.setAttr(self.attrFull, 0.0)
    def on(self):
        mayac.setAttr(self.attrFull, 1.0)
    def duplicateGeo(self):
        self.newGeo = mayac.duplicate(self.meshOrig, returnRootsOnly=True)[0]
        shapes = mayac.listRelatives(self.newGeo, children=True, shapes=True, fullPath=True)
        for shape in shapes:
            connections = mayac.listConnections(shape, connections=True, plugs=True, type='shadingEngine')
            if connections:
                i=0
                while i<len(connections):
                    verifyConnection = mayac.listConnections(connections[i], s=True, plugs=True, type='shadingEngine')
                    if verifyConnection:
                        try:
                            mayac.disconnectAttr(connections[i],verifyConnection[0])
                        except:
                            pass
                    i+=2
        
        self.newGeo = mayac.parent(self.newGeo, world=True)[0]
        self.newGeo = mayac.rename(self.newGeo, self.attr)
        mayac.setAttr("%s.visibility"%self.newGeo, lock=False, keyable=True)
        mayac.setAttr("%s.visibility"%self.newGeo, 0)
        
    def connectNewBlendShape(self, newBlendshapeNode):
        self.newBlendShapeNode = newBlendshapeNode
        #ensure naming of attr is good
        if self.newGeo != self.attr:
            mayac.aliasAttr(self.attr, "%s.%s"%(self.newBlendShapeNode,self.newGeo))
        mayac.connectAttr("%s.%s"%(self.blendShapeNodeOrigTempName,self.attr), "%s.%s"%(self.newBlendShapeNode,self.attr))

class blendShapeTracker(object):
    def __init__(self, blendShapeNodeOrig, meshOrig):
        self.blendShapeNodeOrig = blendShapeNodeOrig
        self.meshOrig = meshOrig
        self.shapesOrig = mayac.aliasAttr(self.blendShapeNodeOrig, q=True)[::2]
        self.blendShapeAttrTrackers = []
        #create trackers and delete connections
        for attr in self.shapesOrig:
            if attr != "envelope":
                attrTracker = blendShapeAttrTracker(self.blendShapeNodeOrig, attr, self.meshOrig)
                attrTracker.deleteConnection()
                self.blendShapeAttrTrackers.append(attrTracker)
                attrTracker.off()
        
    def duplicate(self, newMesh):
        self.newMesh = newMesh
        #duplicate off blends as is
        for attrTracker in self.blendShapeAttrTrackers:
            for offAttr in self.blendShapeAttrTrackers:
                offAttr.off()
            attrTracker.on()
            attrTracker.duplicateGeo()
            attrTracker.off()
        #create new blendshape node and hook up attrs for baking
        self.blendShapeNodeOrigTempName = mayac.rename(self.blendShapeNodeOrig, "BACKUP_%s"%self.blendShapeNodeOrig)
        blendShapeCreationSelection = []
        for attrTracker in self.blendShapeAttrTrackers:
            blendShapeCreationSelection.append(attrTracker.newGeo)
        blendShapeCreationSelection.append(self.newMesh)
        self.blendShapeNodeNew = mayac.blendShape(blendShapeCreationSelection, name=self.blendShapeNodeOrig, frontOfChain=True)[0]
        for attrTracker in self.blendShapeAttrTrackers:
            attrTracker.reconnect(blendShapeNodeOrigTempName = self.blendShapeNodeOrigTempName)
        for attrTracker in self.blendShapeAttrTrackers:
            attrTracker.connectNewBlendShape(self.blendShapeNodeNew)
        self.bakeAttrs = []
        for attrTracker in self.blendShapeAttrTrackers:
            self.bakeAttrs.append(attrTracker.attrFull)
            
    
    def restoreScene(self):
        mayac.rename(self.blendShapeNodeOrigTempName, self.blendShapeNodeOrig)
        try:
            mayac.setAttr("%s.envelope"%self.blendShapeNodeOrig, 1.0)
        except:
            pass
        
        
        
class DJB_CharacterNode():
    def __init__(self, joint_name_, infoNode_ = None, optional_ = 0, hasIK_ = 0, parent = None, nameSpace_ = "", actAsRoot_ = 0, alias_ = None, dynamic_ = None, twistJoint_ = False, translateOpen_ = False):
        self.characterNameSpace = nameSpace_
        self.infoNode = None
        if infoNode_:
            self.infoNode = self.characterNameSpace + infoNode_
        self.nodeName = joint_name_
        self.children = []
        self.AnimData_Joint = None
        self.Bind_Joint = None
        self.Export_Joint = None
        self.origPosX = None
        self.origPosY = None
        self.origPosZ = None
        self.origRotX = None
        self.origRotY = None
        self.origRotZ = None
        self.FK_Joint =  None
        self.IK_Joint = None
        self.IK_Dummy_Joint = None
        self.templateGeo = None
        self.FK_CTRL = None
        self.FK_CTRL_COLOR = None
        self.FK_CTRL_inRig_CONST_GRP = None
        self.FK_CTRL_animData_CONST_GRP = None
        self.FK_CTRL_animData_MultNode = None
        self.FK_CTRL_animData_MultNode_Trans = None
        self.FK_CTRL_POS_GRP = None
        self.IK_CTRL = None
        self.IK_CTRL_COLOR = None
        self.IK_CTRL_inRig_CONST_GRP = None
        self.IK_CTRL_animData_CONST_GRP = None
        self.IK_CTRL_animData_MultNode = None
        self.IK_CTRL_POS_GRP = None
        self.IK_CTRL_ReorientGRP = None
        
        self.IK_CTRL_parent_animData_CONST_GRP = None
        self.IK_CTRL_parent_animData_MultNode = None
        self.IK_CTRL_parent_POS_GRP = None
        
        self.IK_CTRL_grandparent_inRig_CONST_GRP = None
        self.IK_CTRL_grandparent_animData_CONST_GRP = None
        self.IK_CTRL_grandparent_animData_MultNode = None
        self.IK_CTRL_grandparent_POS_GRP = None
        
        self.Inherit_Rotation_GRP = None
        self.Inherit_Rotation_Constraint = None
        self.Inherit_Rotation_Reverse = None
        self.Constraint = None
        self.FK_Constraint = None
        self.IK_Constraint = None
        self.IK_Handle = None
        self.IK_EndEffector = None
        self.PV_Constraint = None
        self.Guide_Curve = None
        self.Guide_Curve_Cluster1 = None
        self.Guide_Curve_Cluster2 = None
        self.Options_CTRL = None
        self.Options_CTRL_COLOR = None
        
        self.IK_CTRL_parent_Global_POS_GRP = None
        self.IK_CTRL_grandparent_Global_POS_GRP = None
        self.grandparent_Global_Constraint = None
        self.grandparent_Global_Constraint_Reverse = None
        self.parent_Global_Constraint = None
        self.parent_Global_Constraint_Reverse = None
        
        self.follow_extremity_Constraint = None
        self.follow_extremity_Constraint_Reverse = None
        
        self.locator = None
        self.locatorConstraint = None
        self.locator1 = None
        self.locatorConstraint1 = None
        self.locator2 = None
        self.locatorConstraint2 = None
        self.locator3 = None
        self.locatorConstraint3 = None
        self.footRotateLOC = None
        self.Follow_Foot_GRP = None
        self.Follow_Knee_GRP = None
        self.Follow_Knee_Constraint = None
        self.Follow_Foot_Constraint = None
        self.IK_BakingLOC = None
        self.actAsRoot = actAsRoot_
        self.rotOrder = None
        self.alias = alias_
        self.twistJoint = twistJoint_
        
        self.dynamic = dynamic_
        self.Dyn_Joint = None
        self.DynMult_Joint = None
        self.Dyn_Mult = None
        self.Dyn_CTRL = None
        self.Dyn_CTRL_COLOR = None
        self.Dyn_Node = None
        self.translateOpen = translateOpen_
        self.parent = parent
        
        
        
        
        if not self.infoNode:
            if not self.Bind_Joint:
                self.Bind_Joint = self.validateExistance(str(JOINT_NAMESPACE) + joint_name_)
            if not self.Bind_Joint and self.alias:
                for alias in self.alias:
                    self.Bind_Joint = self.validateExistance(str(JOINT_NAMESPACE) + alias)
                    if self.Bind_Joint:
                        break
            if not self.Bind_Joint and not optional_:
                OpenMaya.MGlobal.displayError("ERROR: %s cannot be found and is necessary for the autorigger to complete process" % (str(JOINT_NAMESPACE) + joint_name_))
                sys.exit()
            
            if self.Bind_Joint:
                self.Bind_Joint = mayac.rename(self.Bind_Joint, 'Bind_' + joint_name_)
                mel.eval('CBdeleteConnection "%s.tx";'%(self.Bind_Joint))
                mel.eval('CBdeleteConnection "%s.ty";'%(self.Bind_Joint))
                mel.eval('CBdeleteConnection "%s.tz";'%(self.Bind_Joint))
                mel.eval('CBdeleteConnection "%s.rx";'%(self.Bind_Joint))
                mel.eval('CBdeleteConnection "%s.ry";'%(self.Bind_Joint))
                mel.eval('CBdeleteConnection "%s.rz";'%(self.Bind_Joint))
                self.rotOrder = mayac.getAttr("%s.rotateOrder" %(self.Bind_Joint))
            if not self.Bind_Joint:
                return None
            self.parent = parent
            if self.parent:
                self.parent.children.append(self)
       
        #recreate from an infoNode
        else:              
            self.parent = parent
            if self.parent:
                self.parent.children.append(self)
            try:
                self.Bind_Joint = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.Bind_Joint" % (self.infoNode)))
            except:
                version = mel.eval("float $ver = `getApplicationVersionAsFloat`;")
                if version == 2010.0:
                    OpenMaya.MGlobal.displayError("The Auto-Control Setup requires namespaces in Maya 2010.")
                return None
            if not self.nodeName:
                self.nodeName = attrToPy("%s.nodeName" % (self.infoNode))
                if not self.nodeName:
                    self.nodeName = self.Bind_Joint[5:]
            self.AnimData_Joint = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.AnimData_Joint" % (self.infoNode)))
            self.rotOrder = attrToPy("%s.rotOrder" % (self.infoNode))
            self.origPosX = attrToPy("%s.origPosX" % (self.infoNode))
            self.origPosY = attrToPy("%s.origPosY" % (self.infoNode))
            self.origPosZ = attrToPy("%s.origPosZ" % (self.infoNode))
            self.origRotX = attrToPy("%s.origRotX" % (self.infoNode))
            self.origRotY = attrToPy("%s.origRotY" % (self.infoNode))
            self.origRotZ = attrToPy("%s.origRotZ" % (self.infoNode))
            self.FK_Joint =  DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.FK_Joint" % (self.infoNode)))
            self.IK_Joint = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.IK_Joint" % (self.infoNode)))
            self.IK_Dummy_Joint = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.IK_Dummy_Joint" % (self.infoNode)))
            self.Export_Joint = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.Export_Joint" % (self.infoNode)))
            self.templateGeo = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.templateGeo" % (self.infoNode)))
            self.FK_CTRL = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.FK_CTRL" % (self.infoNode)))
            self.FK_CTRL_COLOR = attrToPy("%s.FK_CTRL_COLOR" % (self.infoNode))
            self.FK_CTRL_inRig_CONST_GRP = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.FK_CTRL_inRig_CONST_GRP" % (self.infoNode)))
            self.FK_CTRL_animData_CONST_GRP = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.FK_CTRL_animData_CONST_GRP" % (self.infoNode)))
            self.FK_CTRL_animData_MultNode = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.FK_CTRL_animData_MultNode" % (self.infoNode)))
            self.FK_CTRL_animData_MultNode_Trans = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.FK_CTRL_animData_MultNode_Trans" % (self.infoNode)))
            self.FK_CTRL_POS_GRP = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.FK_CTRL_POS_GRP" % (self.infoNode)))
            self.IK_CTRL = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.IK_CTRL" % (self.infoNode)))
            self.IK_CTRL_COLOR = attrToPy("%s.IK_CTRL_COLOR" % (self.infoNode))
            self.IK_CTRL_inRig_CONST_GRP = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.IK_CTRL_inRig_CONST_GRP" % (self.infoNode)))
            self.IK_CTRL_animData_CONST_GRP = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.IK_CTRL_animData_CONST_GRP" % (self.infoNode)))
            self.IK_CTRL_animData_MultNode = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.IK_CTRL_animData_MultNode" % (self.infoNode)))
            self.IK_CTRL_POS_GRP = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.IK_CTRL_POS_GRP" % (self.infoNode)))
            self.IK_CTRL_ReorientGRP = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.IK_CTRL_ReorientGRP" % (self.infoNode)))
            
            self.IK_CTRL_parent_animData_CONST_GRP = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.IK_CTRL_parent_animData_CONST_GRP" % (self.infoNode)))
            self.IK_CTRL_parent_animData_MultNode = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.IK_CTRL_parent_animData_MultNode" % (self.infoNode)))
            self.IK_CTRL_parent_POS_GRP = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.IK_CTRL_parent_POS_GRP" % (self.infoNode)))
            
            self.IK_CTRL_grandparent_inRig_CONST_GRP = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.IK_CTRL_parent_POS_GRP" % (self.infoNode)))
            self.IK_CTRL_grandparent_animData_CONST_GRP = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.IK_CTRL_grandparent_animData_CONST_GRP" % (self.infoNode)))
            self.IK_CTRL_grandparent_animData_MultNode = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.IK_CTRL_grandparent_animData_MultNode" % (self.infoNode)))
            self.IK_CTRL_grandparent_POS_GRP = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.IK_CTRL_grandparent_POS_GRP" % (self.infoNode)))
            
            self.Inherit_Rotation_GRP = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.Inherit_Rotation_GRP" % (self.infoNode)))
            self.Inherit_Rotation_Constraint = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.Inherit_Rotation_Constraint" % (self.infoNode)))
            self.Inherit_Rotation_Reverse = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.Inherit_Rotation_Reverse" % (self.infoNode)))
            self.Constraint = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.Constraint" % (self.infoNode)))
            self.FK_Constraint = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.FK_Constraint" % (self.infoNode)))
            self.IK_Constraint = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.IK_Constraint" % (self.infoNode)))
            self.IK_Handle = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.IK_Handle" % (self.infoNode)))
            self.IK_EndEffector = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.IK_EndEffector" % (self.infoNode)))
            self.PV_Constraint = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.PV_Constraint" % (self.infoNode)))
            self.Guide_Curve = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.Guide_Curve" % (self.infoNode)))
            self.Guide_Curve_Cluster1 = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.Guide_Curve_Cluster1" % (self.infoNode)))
            self.Guide_Curve_Cluster2 = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.Guide_Curve_Cluster2" % (self.infoNode)))
            self.Options_CTRL = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.Options_CTRL" % (self.infoNode)))
            self.Options_CTRL_COLOR = attrToPy("%s.Options_CTRL_COLOR" % (self.infoNode))
            
            self.IK_CTRL_parent_Global_POS_GRP = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.IK_CTRL_parent_Global_POS_GRP" % (self.infoNode)))
            self.IK_CTRL_grandparent_Global_POS_GRP = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.IK_CTRL_grandparent_Global_POS_GRP" % (self.infoNode)))
            self.grandparent_Global_Constraint = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.grandparent_Global_Constraint" % (self.infoNode)))
            self.grandparent_Global_Constraint_Reverse = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.grandparent_Global_Constraint_Reverse" % (self.infoNode)))
            self.parent_Global_Constraint = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.parent_Global_Constraint" % (self.infoNode)))
            self.parent_Global_Constraint_Reverse = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.parent_Global_Constraint_Reverse" % (self.infoNode)))
            
            self.follow_extremity_Constraint = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.follow_extremity_Constraint" % (self.infoNode)))
            self.follow_extremity_Constraint_Reverse = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.follow_extremity_Constraint_Reverse" % (self.infoNode)))
            
            self.locator = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.locator" % (self.infoNode)))
            self.locatorConstraint = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.locator" % (self.infoNode)))
            self.locator1 = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.locator1" % (self.infoNode)))
            self.locatorConstraint1 = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.locatorConstraint1" % (self.infoNode)))
            self.footRotateLOC = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.footRotateLOC" % (self.infoNode)))
            self.Follow_Foot_GRP = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.Follow_Foot_GRP" % (self.infoNode)))
            self.Follow_Knee_GRP = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.Follow_Knee_GRP" % (self.infoNode)))
            self.Follow_Knee_Constraint = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.Follow_Knee_Constraint" % (self.infoNode)))
            self.Follow_Foot_Constraint = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.Follow_Knee_Constraint" % (self.infoNode)))
            self.IK_BakingLOC = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.IK_BakingLOC" % (self.infoNode)))

            self.dynamic = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.dynamic" % (self.infoNode)))
            self.Dyn_Joint = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.Dyn_Joint" % (self.infoNode)))
            self.Dyn_CTRL = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.Dyn_CTRL" % (self.infoNode)))
            self.Dyn_CTRL_COLOR = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.Dyn_CTRL_COLOR" % (self.infoNode)))
            self.Dyn_Node = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.Dyn_Node" % (self.infoNode)))
            self.DynMult_Joint = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.Dyn_Node" % (self.infoNode)))
            self.Dyn_Mult = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.Dyn_Mult" % (self.infoNode)))
            self.translateOpen = attrToPy("%s.translateOpen" % (self.infoNode))
            self.twistJoint = attrToPy("%s.twistJoint" % (self.infoNode))
        
        
    def writeInfoNode(self):
        self.infoNode = mayac.createNode("transform", name = "MIXAMO_CHARACTER_%s_infoNode" % (self.nodeName))
        
        pyToAttr("%s.nodeName" % (self.infoNode), self.nodeName)
        if self.parent:
            pyToAttr("%s.parent" % (self.infoNode), self.parent.nodeName)
        else:
            pyToAttr("%s.parent" % (self.infoNode), None)
        pyToAttr("%s.Bind_Joint" % (self.infoNode), self.Bind_Joint)
        pyToAttr("%s.AnimData_Joint" % (self.infoNode), self.AnimData_Joint)
        pyToAttr("%s.rotOrder" % (self.infoNode), self.rotOrder)
        pyToAttr("%s.origPosX" % (self.infoNode), self.origPosX)
        pyToAttr("%s.origPosY" % (self.infoNode), self.origPosY)
        pyToAttr("%s.origPosZ" % (self.infoNode), self.origPosZ)
        pyToAttr("%s.origRotX" % (self.infoNode), self.origRotX)
        pyToAttr("%s.origRotY" % (self.infoNode), self.origRotY)
        pyToAttr("%s.origRotZ" % (self.infoNode), self.origRotZ)
        pyToAttr("%s.FK_Joint" % (self.infoNode), self.FK_Joint)
        pyToAttr("%s.IK_Joint" % (self.infoNode), self.IK_Joint)
        pyToAttr("%s.IK_Dummy_Joint" % (self.infoNode), self.IK_Dummy_Joint)
        pyToAttr("%s.Export_Joint" % (self.infoNode), self.Export_Joint)
        pyToAttr("%s.templateGeo" % (self.infoNode), self.templateGeo)
        pyToAttr("%s.FK_CTRL" % (self.infoNode), self.FK_CTRL)
        pyToAttr("%s.FK_CTRL_COLOR" % (self.infoNode), self.FK_CTRL_COLOR)
        pyToAttr("%s.FK_CTRL_inRig_CONST_GRP" % (self.infoNode), self.FK_CTRL_inRig_CONST_GRP)
        pyToAttr("%s.FK_CTRL_animData_CONST_GRP" % (self.infoNode), self.FK_CTRL_animData_CONST_GRP)
        pyToAttr("%s.FK_CTRL_animData_MultNode" % (self.infoNode), self.FK_CTRL_animData_MultNode)
        pyToAttr("%s.FK_CTRL_animData_MultNode_Trans" % (self.infoNode), self.FK_CTRL_animData_MultNode_Trans)
        pyToAttr("%s.FK_CTRL_POS_GRP" % (self.infoNode), self.FK_CTRL_POS_GRP)
        pyToAttr("%s.IK_CTRL" % (self.infoNode), self.IK_CTRL)
        pyToAttr("%s.IK_CTRL_COLOR" % (self.infoNode), self.IK_CTRL_COLOR)
        pyToAttr("%s.IK_CTRL_inRig_CONST_GRP" % (self.infoNode), self.IK_CTRL_inRig_CONST_GRP)
        pyToAttr("%s.IK_CTRL_animData_CONST_GRP" % (self.infoNode), self.IK_CTRL_animData_CONST_GRP)
        pyToAttr("%s.IK_CTRL_animData_MultNode" % (self.infoNode), self.IK_CTRL_animData_MultNode)
        pyToAttr("%s.IK_CTRL_POS_GRP" % (self.infoNode), self.IK_CTRL_POS_GRP)
        pyToAttr("%s.IK_CTRL_ReorientGRP" % (self.infoNode), self.IK_CTRL_ReorientGRP)
        pyToAttr("%s.IK_CTRL_parent_animData_CONST_GRP" % (self.infoNode), self.IK_CTRL_parent_animData_CONST_GRP)
        pyToAttr("%s.IK_CTRL_parent_animData_MultNode" % (self.infoNode), self.IK_CTRL_parent_animData_MultNode)
        pyToAttr("%s.IK_CTRL_parent_POS_GRP" % (self.infoNode), self.IK_CTRL_parent_POS_GRP)
        pyToAttr("%s.IK_CTRL_grandparent_inRig_CONST_GRP" % (self.infoNode), self.IK_CTRL_grandparent_inRig_CONST_GRP)
        pyToAttr("%s.IK_CTRL_grandparent_animData_CONST_GRP" % (self.infoNode), self.IK_CTRL_grandparent_animData_CONST_GRP)
        pyToAttr("%s.IK_CTRL_grandparent_animData_MultNode" % (self.infoNode), self.IK_CTRL_grandparent_animData_MultNode)
        pyToAttr("%s.IK_CTRL_grandparent_POS_GRP" % (self.infoNode), self.IK_CTRL_grandparent_POS_GRP)
        pyToAttr("%s.Inherit_Rotation_GRP" % (self.infoNode), self.Inherit_Rotation_GRP)
        pyToAttr("%s.Inherit_Rotation_Constraint" % (self.infoNode), self.Inherit_Rotation_Constraint)
        pyToAttr("%s.Inherit_Rotation_Reverse" % (self.infoNode), self.Inherit_Rotation_Reverse)
        pyToAttr("%s.Constraint" % (self.infoNode), self.Constraint)
        pyToAttr("%s.FK_Constraint" % (self.infoNode), self.FK_Constraint)
        pyToAttr("%s.IK_Constraint" % (self.infoNode), self.IK_Constraint)
        pyToAttr("%s.IK_Handle" % (self.infoNode), self.IK_Handle)
        pyToAttr("%s.IK_EndEffector" % (self.infoNode), self.IK_EndEffector)
        pyToAttr("%s.PV_Constraint" % (self.infoNode), self.PV_Constraint)
        pyToAttr("%s.Guide_Curve" % (self.infoNode), self.Guide_Curve)
        pyToAttr("%s.Guide_Curve_Cluster1" % (self.infoNode), self.Guide_Curve_Cluster1)
        pyToAttr("%s.Guide_Curve_Cluster2" % (self.infoNode), self.Guide_Curve_Cluster2)
        pyToAttr("%s.Options_CTRL" % (self.infoNode), self.Options_CTRL)
        pyToAttr("%s.Options_CTRL_COLOR" % (self.infoNode), self.Options_CTRL_COLOR)
        pyToAttr("%s.IK_CTRL_parent_Global_POS_GRP" % (self.infoNode), self.IK_CTRL_parent_Global_POS_GRP)
        pyToAttr("%s.IK_CTRL_grandparent_Global_POS_GRP" % (self.infoNode), self.IK_CTRL_grandparent_Global_POS_GRP)
        pyToAttr("%s.grandparent_Global_Constraint" % (self.infoNode), self.grandparent_Global_Constraint)
        pyToAttr("%s.grandparent_Global_Constraint_Reverse" % (self.infoNode), self.grandparent_Global_Constraint_Reverse)
        pyToAttr("%s.parent_Global_Constraint" % (self.infoNode), self.parent_Global_Constraint)
        pyToAttr("%s.parent_Global_Constraint_Reverse" % (self.infoNode), self.parent_Global_Constraint_Reverse)
        pyToAttr("%s.follow_extremity_Constraint" % (self.infoNode), self.follow_extremity_Constraint)
        pyToAttr("%s.follow_extremity_Constraint_Reverse" % (self.infoNode), self.follow_extremity_Constraint_Reverse)
        pyToAttr("%s.locator" % (self.infoNode), self.locator)
        pyToAttr("%s.locatorConstraint" % (self.infoNode), self.locatorConstraint)
        pyToAttr("%s.locator1" % (self.infoNode), self.locator1)
        pyToAttr("%s.locatorConstraint1" % (self.infoNode), self.locatorConstraint1)
        pyToAttr("%s.footRotateLOC" % (self.infoNode), self.footRotateLOC)
        pyToAttr("%s.Follow_Foot_GRP" % (self.infoNode), self.Follow_Foot_GRP)
        pyToAttr("%s.Follow_Knee_GRP" % (self.infoNode), self.Follow_Knee_GRP)
        pyToAttr("%s.Follow_Knee_Constraint" % (self.infoNode), self.Follow_Knee_Constraint)
        pyToAttr("%s.Follow_Foot_Constraint" % (self.infoNode), self.Follow_Foot_Constraint)
        pyToAttr("%s.IK_BakingLOC" % (self.infoNode), self.IK_BakingLOC)
        
        #Dynamics
        pyToAttr("%s.dynamic" % (self.infoNode), self.dynamic)
        pyToAttr("%s.Dyn_Joint" % (self.infoNode), self.Dyn_Joint)
        pyToAttr("%s.Dyn_CTRL" % (self.infoNode), self.Dyn_CTRL)
        pyToAttr("%s.Dyn_CTRL_COLOR" % (self.infoNode), self.Dyn_CTRL_COLOR)
        pyToAttr("%s.Dyn_Node" % (self.infoNode), self.Dyn_Node)
        pyToAttr("%s.DynMult_Joint" % (self.infoNode), self.DynMult_Joint)
        pyToAttr("%s.Dyn_Mult" % (self.infoNode), self.Dyn_Mult)
        pyToAttr("%s.translateOpen" % (self.infoNode), self.translateOpen)
        pyToAttr("%s.twistJoint" % (self.infoNode), self.twistJoint)
        
        return self.infoNode
        
     
     
    def fixAllLayerOverrides(self, layer):
        if self.FK_CTRL:
            self.fixLayerOverrides(self.FK_CTRL, self.FK_CTRL_COLOR, layer)
        if self.IK_CTRL:
            self.fixLayerOverrides(self.IK_CTRL, self.IK_CTRL_COLOR, layer)
        if self.Options_CTRL:
            self.fixLayerOverrides(self.Options_CTRL, self.Options_CTRL_COLOR, layer)
        if self.Dyn_CTRL:
            self.fixLayerOverrides(self.Dyn_CTRL, self.Dyn_CTRL_COLOR, layer)
        
           
    def fixLayerOverrides(self, control, color, layer, referenceAlways = False):
        if mayac.listConnections( "%s.drawOverride" % (control)):
            mayac.disconnectAttr("%s.drawInfo" % (layer), "%s.drawOverride" % (control))
        mayac.connectAttr("%s.levelOfDetail" % (layer), "%s.overrideLevelOfDetail" % (control), force = True)
        mayac.connectAttr("%s.shading" % (layer), "%s.overrideShading" % (control), force = True)
        mayac.connectAttr("%s.texturing" % (layer), "%s.overrideTexturing" % (control), force = True)
        mayac.connectAttr("%s.playback" % (layer), "%s.overridePlayback" % (control), force = True)
        mayac.connectAttr("%s.visibility" % (layer), "%s.overrideVisibility" % (control), force = True)
        DJB_ChangeDisplayColor(control, color = color)
        if referenceAlways:
            mayac.setAttr("%s.overrideDisplayType" % (control), 2)
        else:
            mayac.connectAttr("%s.displayType" % (layer), "%s.overrideDisplayType" % (control), force = True)
        shapes = mayac.listRelatives(control, children = True, shapes = True)
        if shapes:
            for shape in shapes:
                self.fixLayerOverrides(shape, color, layer, referenceAlways)
    
        
    def validateExistance(self, object):
        if mayac.objExists(object):
            return object
        else:
            return None

    def duplicateJoint(self, type, parent_ = "UseSelf", jointNamespace = None):
        if self.Bind_Joint:
            if type == "AnimData":
                self.AnimData_Joint = mayac.duplicate(self.Bind_Joint, parentOnly = True, name = "AnimData_" + self.nodeName)[0]
            elif type == "FK":
                self.FK_Joint = mayac.duplicate(self.Bind_Joint, parentOnly = True, name = "FK_" + self.nodeName)[0]
            elif type == "IK":
                self.IK_Joint = mayac.duplicate(self.Bind_Joint, parentOnly = True, name = "IK_" + self.nodeName)[0]
            elif type == "IK_Dummy":
                self.IK_Dummy_Joint = mayac.duplicate(self.Bind_Joint, parentOnly = True, name = "IK_Dummy_" + self.nodeName)[0]
            elif type == "ExportSkeleton":
                if jointNamespace:
                    if not mayac.namespace(exists = jointNamespace):
                        mayac.namespace(add=jointNamespace[0:len(jointNamespace)-1])
                    self.Export_Joint = mayac.duplicate(self.Bind_Joint, parentOnly = True, inputConnections=False, name = jointNamespace + self.nodeName)[0]
                else:
                    temp = mayac.duplicate(self.Bind_Joint, parentOnly = True, name = self.nodeName)
                    self.Export_Joint = temp[0]
                try:
                    connections = mayac.listConnections("%s.drawOverride"%self.Export_Joint, s=True, plugs=True)
                    if connections:
                        mayac.disconnectAttr(connections[0], "%s.drawOverride"%self.Export_Joint)
                    connections = mayac.listConnections("%s.instObjGroups[0]"%self.Export_Joint, d=True, plugs=True)
                    if connections:
                        mayac.disconnectAttr("%s.instObjGroups[0]"%self.Export_Joint, connections[0])
                    
                    mayac.parent(self.Export_Joint, world = True)
                except:
                    pass
            elif type == "ZV":
                self.Dyn_Joint = mayac.duplicate(self.Bind_Joint, parentOnly = True, name = "DYN_" + self.nodeName)[0]
                self.DynMult_Joint = mayac.duplicate(self.Bind_Joint, parentOnly = True, name = "DynMult_" + self.nodeName)[0]
            if parent_ == "UseSelf" and self.parent:
                if type == "AnimData":
                    mayac.parent(self.AnimData_Joint, self.parent.AnimData_Joint)
                if type == "FK":
                    mayac.parent(self.FK_Joint, self.parent.FK_Joint)
                if type == "IK":
                    mayac.parent(self.IK_Joint, self.parent.IK_Joint)
                if type == "IK_Dummy":
                    mayac.parent(self.IK_Dummy_Joint, self.parent.IK_Dummy_Joint)
                if type == "ZV":
                    mayac.parent(self.Dyn_Joint, self.parent.Dyn_Joint)
                    mayac.parent(self.DynMult_Joint, self.parent.DynMult_Joint)
                if type == "ExportSkeleton":
                    mayac.parent(self.Export_Joint, self.parent.Export_Joint)
                    if jointNamespace and self.Export_Joint != (jointNamespace + self.nodeName):
                        #add namespace to scene if should have it but doesn't
                        if not mayac.namespace(exists = jointNamespace):
                            mayac.namespace(add=jointNamespace[0:len(jointNamespace)-1])
                        self.Export_Joint = mayac.rename(self.Export_Joint, (jointNamespace + self.nodeName))
                            
                    
                    
    def createGuideCurve(self, group_, optionsCTRL = None):
        pos1 = mayac.xform(self.IK_CTRL, query = True, absolute = True, worldSpace = True, translation = True)
        pos2 = mayac.xform(self.IK_Joint, query = True, absolute = True, worldSpace = True, translation = True)
        self.Guide_Curve = mayac.curve(degree = 1, name = "%s_GuideCurve" % (self.IK_CTRL),
                                      point = [(pos1[0], pos1[1], pos1[2]), (pos2[0], pos2[1], pos2[2])],
                                      knot = [0,1])
        mayac.xform(self.Guide_Curve, centerPivots = True)
        mayac.select("%s.cv[0]" % (self.Guide_Curve), replace = True) ;
        temp = mayac.cluster(name = "%s_Cluster1" % (self.Guide_Curve))
        self.Guide_Curve_Cluster1 = temp[1]
        mayac.select("%s.cv[1]" % (self.Guide_Curve), replace = True) ;
        temp = mayac.cluster(name = "%s_Cluster2" % (self.Guide_Curve))
        self.Guide_Curve_Cluster2 = temp[1]
        mayac.parent(self.Guide_Curve_Cluster1, self.IK_CTRL)
        mayac.parent(self.Guide_Curve_Cluster2, self.IK_Joint)
        mayac.parent(self.Guide_Curve, group_)
        mayac.setAttr("%s.visibility" % (self.Guide_Curve_Cluster1),0)
        mayac.setAttr("%s.visibility" % (self.Guide_Curve_Cluster2),0)
        mayac.setAttr("%s.overrideEnabled" % (self.Guide_Curve), 1)
        mayac.setAttr("%s.overrideDisplayType" % (self.Guide_Curve), 1)
        multDiv = mayac.createNode( 'multiplyDivide', n=self.Guide_Curve + "_Visibility_MultNode")
        mayac.addAttr(self.IK_CTRL, longName='GuideCurve', defaultValue=1.0, min = 0.0, max = 1.0, keyable = True)
        mayac.connectAttr("%s.GuideCurve" %(self.IK_CTRL), "%s.input2X" %(multDiv), force = True)
        if optionsCTRL:
            mayac.connectAttr("%s.FK_IK" %(optionsCTRL), "%s.input1X" %(multDiv), force = True)
        mayac.connectAttr("%s.outputX" %(multDiv), "%s.visibility" %(self.Guide_Curve), force = True)
        DJB_LockNHide(self.Guide_Curve)
        DJB_LockNHide(self.Guide_Curve_Cluster1)
        DJB_LockNHide(self.Guide_Curve_Cluster2)



    def createControl(self, type, rigType = "AutoRig", style = "circle", partialConstraint = 0, scale = (0.1,0.1,0.1), rotate = (0,0,0), offset = (0,0,0), estimateSize = True, color_ = None, name_ = None, flipFingers = False):
        control = 0 
        if style == "circle":
            if estimateSize:
                control = mayac.circle(constructionHistory = 0)
                control = control[0]
                mayac.rotate(0, 90, 90)
                if "Root" not in self.nodeName and "Spine" not in self.nodeName and "Hips" not in self.nodeName and rigType == "World":
                    mayac.rotate(rotate[0], rotate[1], rotate[2], control, absolute = True) #override for world-oriented rigs
                if rigType == "Dyn":
                    mayac.rotate(rotate[0], rotate[1], rotate[2], control, relative = True)
                mayac.scale(scale[0],scale[1],scale[2])
                mayac.move(offset[0], offset[1], offset[2], "%s.cv[0:7]" % (control), relative = True)
                mayac.makeIdentity(control, apply = True, t=1, r=1, s=1, n=0)
            else:
                print "exactSizeNotFunctionalYet"

        elif style == "box":
            if estimateSize:
                control = mayac.curve(degree = 1,
                                      point = [(0.5, 0.5, 0.5),
                                          (0.5, 0.5, -0.5),
                                          (-0.5, 0.5, -0.5),
                                          (-0.5, -0.5, -0.5),
                                          (0.5, -0.5, -0.5),
                                          (0.5, 0.5, -0.5),
                                          (-0.5, 0.5, -0.5),
                                          (-0.5, 0.5, 0.5),
                                          (0.5, 0.5, 0.5),
                                          (0.5, -0.5, 0.5),
                                          (0.5, -0.5, -0.5),
                                          (-0.5, -0.5, -0.5),
                                          (-0.5, -0.5, 0.5),
                                          (0.5, -0.5, 0.5),
                                          (-0.5, -0.5, 0.5),
                                          (-0.5, 0.5, 0.5)],
                                      knot = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15])                                                                            
                mayac.move(0, -.2, 0, "%s.cv[0]" % (control), "%s.cv[7:8]" % (control), "%s.cv[15]" % (control), relative = True)
                mayac.scale(1.3, 1.3, 1.3, "%s.cv[3:4]" % (control), "%s.cv[9:12]" % (control), "%s.cv[13:14]" % (control))       
                mayac.scale(scale[0], scale[1], scale[2], control)
                mayac.rotate(rotate[0], rotate[1], rotate[2], control, relative = True)
                mayac.move(offset[0], offset[1], offset[2],  "%s.cv[0:15]" % (control), relative = True)
                mayac.makeIdentity(control, apply = True, t=1, r=1, s=1, n=0)
            else:
                print "exactSizeNotFunctionalYet"
                
        elif style == "box1":
            if estimateSize:
                control = mayac.curve(degree = 1,
                                      point = [(0.5, 0.5, 0.5),
                                          (0.5, 0.5, -0.5),
                                          (-0.5, 0.5, -0.5),
                                          (-0.5, -0.5, -0.5),
                                          (0.5, -0.5, -0.5),
                                          (0.5, 0.5, -0.5),
                                          (-0.5, 0.5, -0.5),
                                          (-0.5, 0.5, 0.5),
                                          (0.5, 0.5, 0.5),
                                          (0.5, -0.5, 0.5),
                                          (0.5, -0.5, -0.5),
                                          (-0.5, -0.5, -0.5),
                                          (-0.5, -0.5, 0.5),
                                          (0.5, -0.5, 0.5),
                                          (-0.5, -0.5, 0.5),
                                          (-0.5, 0.5, 0.5)],
                                      knot = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15])                                                                                  
                mayac.scale(scale[0], scale[1], scale[2], control)
                mayac.rotate(rotate[0], rotate[1], rotate[2], control, relative = True)
                mayac.move(offset[0], offset[1], offset[2],  "%s.cv[0:15]" % (control), relative = True)
                mayac.makeIdentity(control, apply = True, t=1, r=1, s=1, n=0)
            else:
                print "exactSizeNotFunctionalYet"
                
                
        elif style == "footBox":
            if estimateSize:
                control = mayac.curve(degree = 1,
                                      point = [(0.5, 0.5, 0.5),
                                          (0.5, 0.5, -0.5),
                                          (-0.5, 0.5, -0.5),
                                          (-0.5, -0.5, -0.5),
                                          (0.5, -0.5, -0.5),
                                          (0.5, 0.5, -0.5),
                                          (-0.5, 0.5, -0.5),
                                          (-0.5, 0.5, 0.5),
                                          (0.5, 0.5, 0.5),
                                          (0.5, -0.5, 0.5),
                                          (0.5, -0.5, -0.5),
                                          (-0.5, -0.5, -0.5),
                                          (-0.5, -0.5, 0.5),
                                          (0.5, -0.5, 0.5),
                                          (-0.5, -0.5, 0.5),
                                          (-0.5, 0.5, 0.5)],
                                      knot = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15])                                                                            
                mayac.move(0, -.4, .1, "%s.cv[1:2]" % (control), "%s.cv[5:6]" % (control), relative = True)
                mayac.move(0, .1, 0, "%s.cv[3:4]" % (control), "%s.cv[10:11]" % (control), relative = True)
                mayac.move(0, .3, 0, "%s.cv[0]" % (control), "%s.cv[7:8]" % (control), "%s.cv[15]" % (control), relative = True)
                mayac.scale(1.0, .75, 1.0, "%s.cv[1:6]" % (control), "%s.cv[10:11]" % (control))      
                mayac.scale(scale[0], scale[1], scale[2], control)
                mayac.rotate(rotate[0], rotate[1], rotate[2], control, relative = True)
                mayac.move(offset[0], offset[1], offset[2],  "%s.cv[0:15]" % (control), relative = True)
                mayac.makeIdentity(control, apply = True, t=1, r=1, s=1, n=0)
            else:
                print "exactSizeNotFunctionalYet"
                

                
        elif style == "circleWrapped":
            if estimateSize:
                control = mayac.circle(constructionHistory = 0)
                control = control[0]
                mayac.move(0, 0, 1.0, "%s.cv[3]" % (control), "%s.cv[7]" % (control), relative = True)
                mayac.move(0, 0, -1.0, "%s.cv[1]" % (control), "%s.cv[5]" % (control), relative = True)
                mayac.scale(scale[0],scale[1],scale[2])
                mayac.rotate(rotate[0], rotate[1], rotate[2], control, relative = True) #override for world-oriented rigs
                mayac.move(offset[0], offset[1], offset[2], "%s.cv[0:7]" % (control), relative = True)
                mayac.makeIdentity(control, apply = True, t=1, r=1, s=1, n=0)
            else:
                print "exactSizeNotFunctionalYet"
            
            
        elif style == "pin":
            if estimateSize:
                control = mayac.circle(constructionHistory = 0)
                control = control[0]
                mayac.scale(1.0, 0.0, 0.0, "%s.cv[1:5]" % (control))
                mayac.move(-2.891806, 0, 0, "%s.cv[3]" % (control), relative = True)
                mayac.move(4.0, 0, 0, "%s.cv[0:7]" % (control), relative = True)
                mayac.rotate(180, 0, 180, control)
                mayac.scale(scale[0], scale[1], scale[2], control)
                mayac.rotate(rotate[0], rotate[1], rotate[2], control, relative = True) #override for world-oriented rigs
                mayac.move(offset[0], offset[1], offset[2], "%s.cv[0:7]" % (control), relative = True)
                mayac.makeIdentity(control, apply = True, t=1, r=1, s=1, n=0)
            else:
                print "exactSizeNotFunctionalYet"
                
        elif style == "pin1" or style == "pin2":
            if estimateSize:
                control = mayac.circle(constructionHistory = 0)
                control = control[0]
                mayac.scale(1.0, 0.0, 0.0, "%s.cv[1:5]" % (control))
                mayac.move(-2.891806, 0, 0, "%s.cv[3]" % (control), relative = True)
                mayac.move(4.0, 0, 0, "%s.cv[0:7]" % (control), relative = True)
                mayac.scale(scale[0], scale[1], scale[2], control)
                if flipFingers:
                    mayac.rotate(rotate[0], 180, rotate[2], control, relative = True) #flip fingers
                else:
                    mayac.rotate(rotate[0], rotate[1], rotate[2], control, relative = True) #override for world-oriented rigs
                mayac.move(offset[0], offset[1], offset[2], "%s.cv[0:7]" % (control), relative = True)
                mayac.makeIdentity(control, apply = True, t=1, r=1, s=1, n=0)
            else:
                print "exactSizeNotFunctionalYet"       
        

        elif style == "options":
            if estimateSize:
                control = mayac.curve(degree = 1,
                                      point = [(-1.03923, 0.0, 0.6),
                                          (1.03923, 0.0, 0.6),
                                          (0.0, 0.0, -1.2),
                                          (-1.03923, 0.0, 0.6)],
                                      knot = [0,1,2,3])    
                mayac.scale(scale[0], scale[1], scale[2], control)
                mayac.rotate(rotate[0], rotate[1], rotate[2], control, relative = True)
                mayac.rotate(rotate[0], rotate[1], rotate[2], control, relative = True) #override for world-oriented rigs
                mayac.move(offset[0], offset[1], offset[2],  "%s.cv[0:15]" % (control), relative = True)
                mayac.makeIdentity(control, apply = True, t=1, r=1, s=1, n=0)
            else:
                print "exactSizeNotFunctionalYet"
            
            
        elif style == "hula":
            if estimateSize:
                control = mayac.circle(constructionHistory = 0)
                control = control[0]
                mayac.move(0, 0, -0.5, "%s.cv[0]" % (control), "%s.cv[2]" % (control), "%s.cv[4]" % (control), "%s.cv[6]" % (control), relative = True)
                mayac.move(0, 0, 0.3, "%s.cv[1]" % (control), "%s.cv[3]" % (control), "%s.cv[5]" % (control), "%s.cv[7]" % (control), relative = True)
                mayac.rotate(0, 90, 90, control)
                mayac.scale(scale[0], scale[1], scale[2], control)
                mayac.move(offset[0], offset[1], offset[2], "%s.cv[0:7]" % (control), relative = True)
                mayac.makeIdentity(control, apply = True, t=1, r=1, s=1, n=0)
            else:
                print "exactSizeNotFunctionalYet"
                
                
        elif style == "PoleVector":
            if estimateSize:
                control = mayac.curve(degree = 1,
                                      point = [(0.0, 2.0, 0.0),
                                          (1.0, 0.0, -1.0),
                                          (-1.0, 0.0, -1.0),
                                          (0.0, 2.0, 0.0),
                                          (-1.0, 0.0, 1.0),
                                          (1.0, 0.0, 1.0),
                                          (0.0, 2.0, 0.0),
                                          (1.0, 0.0, -1.0),
                                          (1.0, 0.0, 1.0),
                                          (-1.0, 0.0, 1.0),
                                          (-1.0, 0.0, -1.0)],
                                      knot = [0,1,2,3,4,5,6,7,8,9,10])
                mayac.rotate(90, 0, 0, control)
                mayac.rotate(rotate[0], rotate[1], rotate[2], control, relative = True)                                                                                          
                mayac.scale(scale[0], scale[1], scale[2], control)
                mayac.move(offset[0], offset[1], offset[2],  "%s.cv[0:9]" % (control), relative = True)
                mayac.makeIdentity(control, apply = True, t=1, r=1, s=1, n=0)
            else:
                print "exactSizeNotFunctionalYet"


        #set color
        DJB_ChangeDisplayColor(control, color = color_)
        #place control
        if not partialConstraint:
            mayac.delete(mayac.parentConstraint(self.Bind_Joint, control))
        elif partialConstraint == 2:
            mayac.delete(mayac.parentConstraint(self.Bind_Joint, control, sr=["x"]))
        elif partialConstraint == 1:
            mayac.delete(mayac.pointConstraint(self.Bind_Joint, control))
            mayac.makeIdentity(control, apply = True, t=1, r=1, s=1, n=0)
            mayac.xform(control, cp = True)
            mayac.scale(1,-1,1, control)
            mayac.makeIdentity(control, apply = True, t=1, r=1, s=1, n=0)
            cvPos = mayac.xform("%s.cv[0]" % (control), query = True, worldSpace = True, translation = True)
            pivPosY = mayac.getAttr("%s.rotatePivotY" % (control))
            mayac.setAttr("%s.translateY" % (control), cvPos[1] - pivPosY)
            DJB_movePivotToObject(control, self.Bind_Joint, posOnly = True)
            mayac.delete(mayac.aimConstraint(self.children[0].Bind_Joint, control, skip = ["x", "z"], weight = 1, aimVector = (0,0,1), worldUpType = "vector", upVector = (0,1,0)))

        if style == "pin1":
            mayac.delete(mayac.orientConstraint(self.Bind_Joint, control, offset = (0,-90,90)))
        if type == "FK":
            self.FK_CTRL = mayac.rename(control, DJB_findAfterSeperator(self.nodeName, ":") + "_FK_CTRL")
            self.FK_CTRL_COLOR = color_ 
        elif type == "IK":
            self.IK_CTRL = mayac.rename(control, DJB_findAfterSeperator(self.nodeName, ":") + "_IK_CTRL")
            self.IK_CTRL_COLOR = color_
        elif type == "options":
            if not name_:
                self.Options_CTRL = mayac.rename(control, DJB_findAfterSeperator(self.nodeName, ":") + "_Options")
            else:
                self.Options_CTRL = mayac.rename(control, name_)
            self.Options_CTRL_COLOR = color_
        elif type == "Dyn":
            if not name_:
                self.Dyn_CTRL = mayac.rename(control, DJB_findAfterSeperator(self.nodeName, ":") + "_Dyn_CTRL")
            else:
                self.Dyn_CTRL = mayac.rename(control, name_)
            self.Dyn_CTRL_COLOR = color_
        elif type == "normal":
            if "Hips" in self.nodeName:
                if self.actAsRoot:
                    self.FK_CTRL = mayac.rename(control, "Root_CTRL")
                else:
                    self.FK_CTRL = mayac.rename(control, "Pelvis_CTRL")
            else:
                self.FK_CTRL = mayac.rename(control, DJB_findAfterSeperator(self.nodeName, ":") + "_CTRL")
            self.FK_CTRL_COLOR = color_
     
     
     
        
    def zeroToOrig(self, transform):
        if transform:
            if not mayac.getAttr("%s.tx" % (transform),lock=True):
                mel.eval('CBdeleteConnection "%s.tx";'%(transform))
                mayac.setAttr("%s.tx" % (transform), self.origPosX)
            if not mayac.getAttr("%s.ty" % (transform),lock=True):
                mel.eval('CBdeleteConnection "%s.ty";'%(transform))
                mayac.setAttr("%s.ty" % (transform), self.origPosY)
            if not mayac.getAttr("%s.tz" % (transform),lock=True):
                mel.eval('CBdeleteConnection "%s.tz";'%(transform))
                mayac.setAttr("%s.tz" % (transform), self.origPosZ)
            if not mayac.getAttr("%s.rx" % (transform),lock=True):
                mel.eval('CBdeleteConnection "%s.rx";'%(transform))
                mayac.setAttr("%s.rx" % (transform), self.origRotX)
            if not mayac.getAttr("%s.ry" % (transform),lock=True):
                mel.eval('CBdeleteConnection "%s.ry";'%(transform))
                mayac.setAttr("%s.ry" % (transform), self.origRotY)
            if not mayac.getAttr("%s.rz" % (transform),lock=True):
                mel.eval('CBdeleteConnection "%s.rz";'%(transform))
                mayac.setAttr("%s.rz" % (transform), self.origRotZ)




    def finalizeCTRLs(self, parent = "UseSelf"):   
        #find type of chains
        print('#find type of chains')
        switchName = ""
        if self.FK_Joint and self.IK_Joint:
            switchName = "FK_IK"
        elif self.FK_Joint and self.Dyn_Joint:
            switchName = "FK_Dyn"
        #record original positions, rotations
        print('#record original positions, rotations')
        self.origPosX = mayac.getAttr("%s.translateX" % (self.Bind_Joint))
        self.origPosY = mayac.getAttr("%s.translateY" % (self.Bind_Joint))
        self.origPosZ = mayac.getAttr("%s.translateZ" % (self.Bind_Joint))
        self.origRotX = mayac.getAttr("%s.rotateX" % (self.Bind_Joint))
        self.origRotY = mayac.getAttr("%s.rotateY" % (self.Bind_Joint))
        self.origRotZ = mayac.getAttr("%s.rotateZ" % (self.Bind_Joint))
        #hook up control
        print('# FK_CTRL hook up control')
        if self.FK_CTRL:
            #place control
            print('#place control')
            temp = mayac.duplicate(self.Bind_Joint, parentOnly = True, name = "UnRotate" + self.nodeName)
            mayac.parent(self.FK_CTRL, temp[0])
            mayac.rotate(0,0,0, temp[0])
            mayac.parent(self.FK_CTRL, world = True)
            DJB_movePivotToObject(self.FK_CTRL, temp[0])
            mayac.delete(temp[0])
            #add attributes  
            print('#add attributes  ')
            mayac.addAttr(self.FK_CTRL, longName='AnimDataMult', defaultValue=1.0, keyable = True)
            self.FK_CTRL_inRig_CONST_GRP = DJB_createGroup(transform = self.FK_CTRL, fullName = self.FK_CTRL + "_In_Rig_CONST_GRP")
            self.FK_CTRL_animData_CONST_GRP = DJB_createGroup(transform = self.FK_CTRL_inRig_CONST_GRP, fullName = self.FK_CTRL + "_AnimData_CONST_GRP")
            self.FK_CTRL_animData_MultNode = mayac.createNode( 'multiplyDivide', n=self.FK_CTRL + "_AnimData_MultNode")
            self.FK_CTRL_POS_GRP = DJB_createGroup(transform = self.FK_CTRL_animData_CONST_GRP, fullName = self.FK_CTRL + "_POS_GRP")
            
            #set rotation orders
            print('#set rotation orders')
            mayac.setAttr("%s.rotateOrder" % (self.FK_CTRL), self.rotOrder)
            mayac.setAttr("%s.rotateOrder" % (self.FK_CTRL_inRig_CONST_GRP), self.rotOrder)
            mayac.setAttr("%s.rotateOrder" % (self.FK_CTRL_animData_CONST_GRP), self.rotOrder)
            mayac.setAttr("%s.rotateOrder" % (self.FK_CTRL_POS_GRP), self.rotOrder)
            
            #place in hierarchy
            print('#place in hierarchy')
            if parent == "UseSelf" and self.parent:
                mayac.parent(self.FK_CTRL_POS_GRP, self.parent.FK_CTRL)
            elif parent != "UseSelf":
                mayac.parent(self.FK_CTRL_POS_GRP, parent)
                
            if "Head" in self.nodeName:
                mayac.addAttr(self.FK_CTRL, longName='InheritRotation', defaultValue=1.0, min = 0, max = 1.0, keyable = True)
                self.Inherit_Rotation_GRP = DJB_createGroup(transform = None, fullName = self.FK_CTRL + "_Inherit_Rotation_GRP", pivotFrom = self.FK_CTRL)
                mayac.parent(self.Inherit_Rotation_GRP, self.FK_CTRL_animData_CONST_GRP)
                mayac.setAttr("%s.inheritsTransform" % (self.Inherit_Rotation_GRP), 0)
                temp = mayac.orientConstraint(self.FK_CTRL_animData_CONST_GRP, self.FK_CTRL_inRig_CONST_GRP, maintainOffset = True)
                self.Inherit_Rotation_Constraint = temp[0]
                mayac.orientConstraint(self.Inherit_Rotation_GRP, self.FK_CTRL_inRig_CONST_GRP, maintainOffset = True)
                self.Inherit_Rotation_Constraint_Reverse = mayac.createNode( 'reverse', n="Head_Inherit_Rotation_Constraint_Reverse")
                mayac.connectAttr("%s.InheritRotation" %(self.FK_CTRL), "%s.inputX" %(self.Inherit_Rotation_Constraint_Reverse))
                mayac.connectAttr("%s.InheritRotation" %(self.FK_CTRL), "%s.%sW0" %(self.Inherit_Rotation_Constraint, self.FK_CTRL_animData_CONST_GRP))
                mayac.connectAttr("%s.outputX" %(self.Inherit_Rotation_Constraint_Reverse), "%s.%sW1" %(self.Inherit_Rotation_Constraint, self.Inherit_Rotation_GRP))
                mayac.setAttr("%s.interpType" %(self.Inherit_Rotation_Constraint), 2)
                
        
        
        
            #hook up CTRLs
            print('#hook up CTRLs')
            mayac.connectAttr("%s.rotateX" %(self.AnimData_Joint), "%s.input1X" %(self.FK_CTRL_animData_MultNode), force = True)
            mayac.connectAttr("%s.AnimDataMult" %(self.FK_CTRL), "%s.input2X" %(self.FK_CTRL_animData_MultNode), force = True)
            mayac.connectAttr("%s.rotateY" %(self.AnimData_Joint), "%s.input1Y" %(self.FK_CTRL_animData_MultNode), force = True)
            mayac.connectAttr("%s.AnimDataMult" %(self.FK_CTRL), "%s.input2Y" %(self.FK_CTRL_animData_MultNode), force = True)
            mayac.connectAttr("%s.rotateZ" %(self.AnimData_Joint), "%s.input1Z" %(self.FK_CTRL_animData_MultNode), force = True)
            mayac.connectAttr("%s.AnimDataMult" %(self.FK_CTRL), "%s.input2Z" %(self.FK_CTRL_animData_MultNode), force = True)
            
            mayac.connectAttr("%s.outputX" %(self.FK_CTRL_animData_MultNode), "%s.rotateX" %(self.FK_CTRL_animData_CONST_GRP), force = True)
            mayac.connectAttr("%s.outputY" %(self.FK_CTRL_animData_MultNode), "%s.rotateY" %(self.FK_CTRL_animData_CONST_GRP), force = True)
            mayac.connectAttr("%s.outputZ" %(self.FK_CTRL_animData_MultNode), "%s.rotateZ" %(self.FK_CTRL_animData_CONST_GRP), force = True)
            if not self.FK_Joint:
                if self.actAsRoot:
                    mayac.addAttr(self.FK_CTRL, longName='AnimDataMultTrans', defaultValue=1.0, keyable = True)
                    self.FK_CTRL_animData_MultNode_Trans = mayac.createNode( 'multiplyDivide', n=self.FK_CTRL + "_AnimData_MultNode_Trans")
                    temp = mayac.parentConstraint(self.FK_CTRL, self.Bind_Joint, mo = True, name = "%s_Constraint" %(self.nodeName))
                    self.Constraint = temp[0]
                    
                    mayac.connectAttr("%s.translateX" %(self.AnimData_Joint), "%s.input1X" %(self.FK_CTRL_animData_MultNode_Trans), force = True)
                    mayac.connectAttr("%s.AnimDataMultTrans" %(self.FK_CTRL), "%s.input2X" %(self.FK_CTRL_animData_MultNode_Trans), force = True)
                    mayac.connectAttr("%s.translateY" %(self.AnimData_Joint), "%s.input1Y" %(self.FK_CTRL_animData_MultNode_Trans), force = True)
                    mayac.connectAttr("%s.AnimDataMultTrans" %(self.FK_CTRL), "%s.input2Y" %(self.FK_CTRL_animData_MultNode_Trans), force = True)
                    mayac.connectAttr("%s.translateZ" %(self.AnimData_Joint), "%s.input1Z" %(self.FK_CTRL_animData_MultNode_Trans), force = True)
                    mayac.connectAttr("%s.AnimDataMultTrans" %(self.FK_CTRL), "%s.input2Z" %(self.FK_CTRL_animData_MultNode_Trans), force = True)
                    
                    mayac.connectAttr("%s.outputX" %(self.FK_CTRL_animData_MultNode_Trans), "%s.translateX" %(self.FK_CTRL_POS_GRP), force = True)
                    mayac.connectAttr("%s.outputY" %(self.FK_CTRL_animData_MultNode_Trans), "%s.translateY" %(self.FK_CTRL_POS_GRP), force = True)
                    mayac.connectAttr("%s.outputZ" %(self.FK_CTRL_animData_MultNode_Trans), "%s.translateZ" %(self.FK_CTRL_POS_GRP), force = True)
                    mayac.connectAttr("%s.outputX" %(self.FK_CTRL_animData_MultNode_Trans), "%s.translateX" %(self.IK_Dummy_Joint), force = True)
                    mayac.connectAttr("%s.outputY" %(self.FK_CTRL_animData_MultNode_Trans), "%s.translateY" %(self.IK_Dummy_Joint), force = True)
                    mayac.connectAttr("%s.outputZ" %(self.FK_CTRL_animData_MultNode_Trans), "%s.translateZ" %(self.IK_Dummy_Joint), force = True)
                elif self.translateOpen:
                    temp = mayac.parentConstraint(self.FK_CTRL, self.Bind_Joint, mo = True, name = "%s_Constraint" %(self.nodeName))
                    self.Constraint = temp[0]
                    mayac.setAttr("%s.offsetX" % (self.Constraint), 0)
                    mayac.setAttr("%s.offsetY" % (self.Constraint), 0)
                    mayac.setAttr("%s.offsetZ" % (self.Constraint), 0)
                else:
                    temp = mayac.orientConstraint(self.FK_CTRL, self.Bind_Joint, mo = True, name = "%s_Constraint" %(self.nodeName))
                    self.Constraint = temp[0]
                    mayac.setAttr("%s.offsetX" % (self.Constraint), 0)
                    mayac.setAttr("%s.offsetY" % (self.Constraint), 0)
                    mayac.setAttr("%s.offsetZ" % (self.Constraint), 0)
            elif self.translateOpen:
                temp= mayac.parentConstraint(self.FK_CTRL, self.FK_Joint, mo = True, name = "%s_FK_Constraint" %(self.nodeName))
                self.FK_Constraint = temp[0]
                temp = mayac.parentConstraint(self.FK_Joint, self.Bind_Joint, mo = True, name = "%s_%s_Constraint" %(self.nodeName, switchName))
                self.Constraint = temp[0]
            else:
                temp= mayac.orientConstraint(self.FK_CTRL, self.FK_Joint, mo = True, name = "%s_FK_Constraint" %(self.nodeName))
                self.FK_Constraint = temp[0]
                temp = mayac.orientConstraint(self.FK_Joint, self.Bind_Joint, mo = True, name = "%s_%s_Constraint" %(self.nodeName, switchName))
                self.Constraint = temp[0]
                mayac.setAttr("%s.offsetX" % (self.Constraint), 0)
                mayac.setAttr("%s.offsetY" % (self.Constraint), 0)
                mayac.setAttr("%s.offsetZ" % (self.Constraint), 0)
        
        if self.IK_Dummy_Joint:
            mayac.connectAttr("%s.rotateX" %(self.AnimData_Joint), "%s.rotateX" %(self.IK_Dummy_Joint), force = True)
            mayac.connectAttr("%s.rotateY" %(self.AnimData_Joint), "%s.rotateY" %(self.IK_Dummy_Joint), force = True)
            mayac.connectAttr("%s.rotateZ" %(self.AnimData_Joint), "%s.rotateZ" %(self.IK_Dummy_Joint), force = True)

        if self.IK_CTRL:
            #place control
            print('# IK_CTRL place control')
            if "Foot" in self.nodeName:
                self.footRotateLOC = mayac.spaceLocator(n = self.IK_CTRL + "_footRotateLOC")
                self.footRotateLOC = self.footRotateLOC[0]
                DJB_movePivotToObject(self.footRotateLOC, self.IK_Joint)
                mayac.delete(mayac.orientConstraint(self.IK_CTRL, self.footRotateLOC))
                mayac.setAttr("%s.rotateOrder" % (self.footRotateLOC), self.rotOrder)

                
                
            temp = mayac.duplicate(self.Bind_Joint, parentOnly = True, name = "UnRotate" + self.nodeName)
            mayac.parent(self.IK_CTRL, temp[0])
            mayac.rotate(0,0,0, temp[0])
            mayac.parent(self.IK_CTRL, world = True)
            DJB_movePivotToObject(self.IK_CTRL, temp[0])
            mayac.delete(temp[0])
            #add attributes  
            print('#add attributes  ')
            mayac.addAttr(self.IK_CTRL, longName='AnimDataMult', defaultValue=1.0, keyable = True)
            mayac.addAttr(self.IK_CTRL, longName='FollowBody', defaultValue=1.0, minValue = 0, maxValue = 1.0, keyable = True)
            if "Foot" in self.nodeName:
                self.IK_CTRL_ReorientGRP = DJB_createGroup(transform = self.IK_CTRL, fullName = self.IK_CTRL + "_Reorient_GRP")
                self.IK_CTRL_inRig_CONST_GRP = DJB_createGroup(transform = self.IK_CTRL_ReorientGRP, fullName = self.IK_CTRL + "_In_Rig_CONST_GRP")
                DJB_movePivotToObject(self.IK_CTRL, self.footRotateLOC)
                DJB_movePivotToObject(self.IK_CTRL_ReorientGRP, self.footRotateLOC)
                mayac.setAttr("%s.rotateOrder" % (self.IK_CTRL_ReorientGRP), self.rotOrder)
                mayac.setAttr("%s.rotateOrder" % (self.IK_CTRL_inRig_CONST_GRP), self.rotOrder)
                #mayac.delete(self.footRotateLOC)
                mayac.parent(self.IK_CTRL_ReorientGRP, self.IK_CTRL_inRig_CONST_GRP)
                mayac.parent(self.IK_CTRL, self.IK_CTRL_ReorientGRP)
            else:
                self.IK_CTRL_inRig_CONST_GRP = DJB_createGroup(transform = self.IK_CTRL, fullName = self.IK_CTRL + "_In_Rig_CONST_GRP")
            self.IK_CTRL_animData_CONST_GRP = DJB_createGroup(transform = self.IK_CTRL_inRig_CONST_GRP, fullName = self.IK_CTRL + "_AnimData_CONST_GRP")
            self.IK_CTRL_animData_MultNode = mayac.createNode( 'multiplyDivide', n=self.IK_CTRL + "_AnimData_MultNode")
            self.IK_CTRL_POS_GRP = DJB_createGroup(transform = self.IK_CTRL_animData_CONST_GRP, fullName = self.IK_CTRL + "_POS_GRP")
            
            #set rotation orders
            print('#set rotation orders')
            mayac.setAttr("%s.rotateOrder" % (self.IK_CTRL), self.rotOrder)
            mayac.setAttr("%s.rotateOrder" % (self.IK_CTRL_inRig_CONST_GRP), self.rotOrder)
            mayac.setAttr("%s.rotateOrder" % (self.IK_CTRL_animData_CONST_GRP), self.rotOrder)
            mayac.setAttr("%s.rotateOrder" % (self.IK_CTRL_POS_GRP), self.rotOrder)
            
            #place in hierarchy
            #hook up CTRLs
            print('#place in hierarchy, #hook up CTRLs')
            mayac.connectAttr("%s.rotateX" %(self.AnimData_Joint), "%s.input1X" %(self.IK_CTRL_animData_MultNode), force = True)
            mayac.connectAttr("%s.AnimDataMult" %(self.IK_CTRL), "%s.input2X" %(self.IK_CTRL_animData_MultNode), force = True)
            mayac.connectAttr("%s.rotateY" %(self.AnimData_Joint), "%s.input1Y" %(self.IK_CTRL_animData_MultNode), force = True)
            mayac.connectAttr("%s.AnimDataMult" %(self.IK_CTRL), "%s.input2Y" %(self.IK_CTRL_animData_MultNode), force = True)
            mayac.connectAttr("%s.rotateZ" %(self.AnimData_Joint), "%s.input1Z" %(self.IK_CTRL_animData_MultNode), force = True)
            mayac.connectAttr("%s.AnimDataMult" %(self.IK_CTRL), "%s.input2Z" %(self.IK_CTRL_animData_MultNode), force = True)
            
            mayac.connectAttr("%s.outputX" %(self.IK_CTRL_animData_MultNode), "%s.rotateX" %(self.IK_CTRL_animData_CONST_GRP), force = True)
            mayac.connectAttr("%s.outputY" %(self.IK_CTRL_animData_MultNode), "%s.rotateY" %(self.IK_CTRL_animData_CONST_GRP), force = True)
            mayac.connectAttr("%s.outputZ" %(self.IK_CTRL_animData_MultNode), "%s.rotateZ" %(self.IK_CTRL_animData_CONST_GRP), force = True)
            
            if "Hand" in self.nodeName or "ForeArm" in self.nodeName or "Foot" in self.nodeName or "Leg" in self.nodeName:
                self.IK_CTRL_parent_animData_CONST_GRP = DJB_createGroup(transform = self.IK_CTRL_POS_GRP, fullName = self.IK_CTRL + "_parent_AnimData_CONST_GRP")
                
                #place parent GRP
                print('#place parent GRP')
                temp = mayac.duplicate(self.parent.Bind_Joint, parentOnly = True, name = "UnRotate" + self.nodeName)
                mayac.parent(self.IK_CTRL_parent_animData_CONST_GRP, temp[0])
                mayac.rotate(0,0,0, temp[0])
                mayac.parent(self.IK_CTRL_POS_GRP, world = True)
                mayac.parent(self.IK_CTRL_parent_animData_CONST_GRP, world = True)
                DJB_movePivotToObject(self.IK_CTRL_parent_animData_CONST_GRP, temp[0])
                mayac.delete(temp[0])
                mayac.parent(self.IK_CTRL_POS_GRP, self.IK_CTRL_parent_animData_CONST_GRP)
                
                self.IK_CTRL_parent_animData_MultNode = mayac.createNode( 'multiplyDivide', n=self.IK_CTRL + "_parent_AnimData_MultNode")
                self.IK_CTRL_parent_Global_POS_GRP = DJB_createGroup(transform = self.IK_CTRL_parent_animData_CONST_GRP, fullName = self.IK_CTRL + "_parent_Global_POS_GRP")
                self.IK_CTRL_parent_POS_GRP = DJB_createGroup(transform = self.IK_CTRL_parent_Global_POS_GRP, fullName = self.IK_CTRL + "_parent_POS_GRP")

                #set rotation orders
                print('#set rotation orders')
                mayac.setAttr("%s.rotateOrder" % (self.IK_CTRL_parent_animData_CONST_GRP), self.parent.rotOrder)
                mayac.setAttr("%s.rotateOrder" % (self.IK_CTRL_parent_Global_POS_GRP), self.parent.rotOrder)
                mayac.setAttr("%s.rotateOrder" % (self.IK_CTRL_parent_POS_GRP), self.parent.rotOrder)

                mayac.connectAttr("%s.rotateX" %(self.parent.AnimData_Joint), "%s.input1X" %(self.IK_CTRL_parent_animData_MultNode), force = True)
                mayac.connectAttr("%s.AnimDataMult" %(self.IK_CTRL), "%s.input2X" %(self.IK_CTRL_parent_animData_MultNode), force = True)
                mayac.connectAttr("%s.rotateY" %(self.parent.AnimData_Joint), "%s.input1Y" %(self.IK_CTRL_parent_animData_MultNode), force = True)
                mayac.connectAttr("%s.AnimDataMult" %(self.IK_CTRL), "%s.input2Y" %(self.IK_CTRL_parent_animData_MultNode), force = True)
                mayac.connectAttr("%s.rotateZ" %(self.parent.AnimData_Joint), "%s.input1Z" %(self.IK_CTRL_parent_animData_MultNode), force = True)
                mayac.connectAttr("%s.AnimDataMult" %(self.IK_CTRL), "%s.input2Z" %(self.IK_CTRL_parent_animData_MultNode), force = True)
                
                mayac.connectAttr("%s.outputX" %(self.IK_CTRL_parent_animData_MultNode), "%s.rotateX" %(self.IK_CTRL_parent_animData_CONST_GRP), force = True)
                mayac.connectAttr("%s.outputY" %(self.IK_CTRL_parent_animData_MultNode), "%s.rotateY" %(self.IK_CTRL_parent_animData_CONST_GRP), force = True)
                mayac.connectAttr("%s.outputZ" %(self.IK_CTRL_parent_animData_MultNode), "%s.rotateZ" %(self.IK_CTRL_parent_animData_CONST_GRP), force = True)
                
                mayac.addAttr(self.IK_CTRL, longName='ParentToGlobal', defaultValue=0.0, minValue = 0, maxValue = 1.0, keyable = True)

                if "ForeArm" in self.nodeName:
                    mayac.addAttr(self.IK_CTRL, longName='FollowHand', defaultValue=0.0, minValue = 0, maxValue = 1.0, keyable = True)
                    #if "Left" in self.nodeName:
                        #mayac.aimConstraint(self.IK_Joint, self.IK_CTRL, upVector = (0,1,0), aimVector = (-1,0,0))
                    #elif "Right" in self.nodeName:
                        #mayac.aimConstraint(self.IK_Joint, self.IK_CTRL, upVector = (0,1,0), aimVector = (1,0,0))
                        
                    #IK elbow bakingLOCs
                    print('#IK elbow bakingLOCs')
                    temp = mayac.spaceLocator(name = "%s_IK_BakingLOC" % (self.nodeName))
                    self.IK_BakingLOC = temp[0]
                    mayac.parent(self.IK_BakingLOC, self.Bind_Joint)
                    DJB_ZeroOut(self.IK_BakingLOC)
                    mayac.setAttr("%s.rotateOrder" % (self.IK_BakingLOC), self.rotOrder)
                    
                    
                
                        
                if "Leg" in self.nodeName:
                    mayac.addAttr(self.IK_CTRL, longName='FollowFoot', defaultValue=0.0, minValue = 0, maxValue = 1.0, keyable = True)
                    #mayac.aimConstraint(self.IK_Joint, self.IK_CTRL, upVector = (0,1,0), aimVector = (0,0,-1))
                    
                    #groups for follow foot Attr
                    print('#groups for follow foot Attr')
                    self.Follow_Knee_GRP = DJB_createGroup(transform = None, fullName = self.IK_CTRL + "_Follow_Knee_GRP", pivotFrom = self.FK_CTRL)
                    self.Follow_Foot_GRP = DJB_createGroup(transform = self.Follow_Knee_GRP, fullName = self.IK_CTRL + "_Follow_Foot_GRP", pivotFrom = self.FK_CTRL)
                    #set rotation orders
                    print('#set rotation orders')
                    mayac.setAttr("%s.rotateOrder" % (self.Follow_Knee_GRP), self.rotOrder)
                    mayac.setAttr("%s.rotateOrder" % (self.Follow_Foot_GRP), self.rotOrder)

                    mayac.parent(self.Follow_Foot_GRP, self.IK_CTRL_animData_CONST_GRP)
                    selfPOS = mayac.xform(self.Bind_Joint, query = True, absolute = True, worldSpace = True, translation = True)
                    parentPOS = mayac.xform(self.parent.Bind_Joint, query = True, absolute = True, worldSpace = True, translation = True)
                    tempDistance = math.sqrt((selfPOS[0]-parentPOS[0])*(selfPOS[0]-parentPOS[0]) + (selfPOS[1]-parentPOS[1])*(selfPOS[1]-parentPOS[1]) + (selfPOS[2]-parentPOS[2])*(selfPOS[2]-parentPOS[2]))
                    mayac.setAttr("%s.translateZ" % (self.Follow_Knee_GRP), tempDistance / 2)
                    temp = mayac.pointConstraint(self.IK_Joint, self.Follow_Knee_GRP, sk = ("x", "y"), mo = True)
                    self.Follow_Knee_Constraint = temp[0]
                    
                    #IK knee bakingLOCs
                    print('#IK knee bakingLOCs')
                    temp = mayac.spaceLocator(name = "%s_IK_BakingLOC" % (self.nodeName))
                    self.IK_BakingLOC = temp[0]
                    mayac.parent(self.IK_BakingLOC, self.Bind_Joint)
                    DJB_ZeroOut(self.IK_BakingLOC)
                    mayac.setAttr("%s.rotateOrder" % (self.IK_BakingLOC), self.rotOrder)

                    if "Left" in self.nodeName:
                        mayac.setAttr("%s.translateZ" % (self.IK_BakingLOC), tempDistance / 2)
                        #mayac.setAttr("%s.translateX" % (self.IK_BakingLOC), -2.017)
                    elif "Right" in self.nodeName:
                        mayac.setAttr("%s.translateZ" % (self.IK_BakingLOC), tempDistance / 2)
                    

                if "Hand" in self.nodeName or "Foot" in self.nodeName:
                    self.IK_CTRL_grandparent_inRig_CONST_GRP = DJB_createGroup(transform = self.IK_CTRL_parent_POS_GRP, fullName = self.IK_CTRL + "_grandparent_inRig_CONST_GRP", pivotFrom = self.parent.parent.Bind_Joint)
                    
                    
                    #place parent GRP
                    print('#place parent GRP')
                    temp = mayac.duplicate(self.parent.parent.Bind_Joint, parentOnly = True, name = "UnRotate" + self.nodeName)
                    mayac.parent(self.IK_CTRL_grandparent_inRig_CONST_GRP, temp[0])
                    mayac.rotate(0,0,0, temp[0])
                    mayac.parent(self.IK_CTRL_parent_POS_GRP, world = True)
                    mayac.parent(self.IK_CTRL_grandparent_inRig_CONST_GRP, world = True)
                    DJB_movePivotToObject(self.IK_CTRL_grandparent_inRig_CONST_GRP, temp[0])
                    mayac.delete(temp[0])
                    mayac.parent(self.IK_CTRL_parent_POS_GRP, self.IK_CTRL_grandparent_inRig_CONST_GRP)
                
                    self.IK_CTRL_grandparent_animData_CONST_GRP = DJB_createGroup(transform = self.IK_CTRL_grandparent_inRig_CONST_GRP, fullName = self.IK_CTRL + "_grandparent_AnimData_CONST_GRP")
                    self.IK_CTRL_grandparent_animData_MultNode = mayac.createNode( 'multiplyDivide', n=self.IK_CTRL + "_grandparent_AnimData_MultNode")
                    self.IK_CTRL_grandparent_Global_POS_GRP = DJB_createGroup(transform = self.IK_CTRL_grandparent_animData_CONST_GRP, fullName = self.IK_CTRL + "_grandparent_Global_POS_GRP")
                    self.IK_CTRL_grandparent_POS_GRP = DJB_createGroup(transform = self.IK_CTRL_grandparent_Global_POS_GRP, fullName = self.IK_CTRL + "_grandparent_POS_GRP")
                    
                    #set rotation orders
                    mayac.setAttr("%s.rotateOrder" % (self.IK_CTRL_grandparent_inRig_CONST_GRP), self.parent.parent.rotOrder)
                    mayac.setAttr("%s.rotateOrder" % (self.IK_CTRL_grandparent_animData_CONST_GRP), self.parent.parent.rotOrder)
                    mayac.setAttr("%s.rotateOrder" % (self.IK_CTRL_grandparent_Global_POS_GRP), self.parent.parent.rotOrder)
                    mayac.setAttr("%s.rotateOrder" % (self.IK_CTRL_grandparent_POS_GRP), self.parent.parent.rotOrder)
                    
                    mayac.connectAttr("%s.rotateX" %(self.parent.parent.AnimData_Joint), "%s.input1X" %(self.IK_CTRL_grandparent_animData_MultNode), force = True)
                    mayac.connectAttr("%s.AnimDataMult" %(self.IK_CTRL), "%s.input2X" %(self.IK_CTRL_grandparent_animData_MultNode), force = True)
                    mayac.connectAttr("%s.rotateY" %(self.parent.parent.AnimData_Joint), "%s.input1Y" %(self.IK_CTRL_grandparent_animData_MultNode), force = True)
                    mayac.connectAttr("%s.AnimDataMult" %(self.IK_CTRL), "%s.input2Y" %(self.IK_CTRL_grandparent_animData_MultNode), force = True)
                    mayac.connectAttr("%s.rotateZ" %(self.parent.parent.AnimData_Joint), "%s.input1Z" %(self.IK_CTRL_grandparent_animData_MultNode), force = True)
                    mayac.connectAttr("%s.AnimDataMult" %(self.IK_CTRL), "%s.input2Z" %(self.IK_CTRL_grandparent_animData_MultNode), force = True)
                    
                    mayac.connectAttr("%s.outputX" %(self.IK_CTRL_grandparent_animData_MultNode), "%s.rotateX" %(self.IK_CTRL_grandparent_animData_CONST_GRP), force = True)
                    mayac.connectAttr("%s.outputY" %(self.IK_CTRL_grandparent_animData_MultNode), "%s.rotateY" %(self.IK_CTRL_grandparent_animData_CONST_GRP), force = True)
                    mayac.connectAttr("%s.outputZ" %(self.IK_CTRL_grandparent_animData_MultNode), "%s.rotateZ" %(self.IK_CTRL_grandparent_animData_CONST_GRP), force = True)
                    
                    temp = mayac.ikHandle( n="%s_IK_Handle" % (self.nodeName), sj= self.parent.parent.IK_Joint, ee= self.IK_Joint, solver = "ikRPsolver", weight = 1)
                    self.IK_Handle = temp[0]
                    mayac.setAttr("%s.visibility" % (self.IK_Handle), 0)
                    self.IK_EndEffector = temp[1]
                    temp = mayac.poleVectorConstraint( self.parent.IK_CTRL, self.IK_Handle )
                    self.PV_Constraint = temp[0]
                    if "Foot" in self.nodeName:
                        temp = mayac.orientConstraint(self.IK_CTRL_inRig_CONST_GRP, self.IK_Joint)
                        self.IK_Constraint = temp[0]
                    else:
                        temp = mayac.orientConstraint(self.IK_CTRL, self.IK_Joint)
                        self.IK_Constraint = temp[0]
                                     
                    
                    if "Hand" in self.nodeName:
                        mayac.parent(self.IK_Handle, self.IK_CTRL)
                        DJB_LockNHide(self.IK_Handle)
                        DJB_LockNHide(self.IK_EndEffector)
                    if "Foot" in self.nodeName:
                        mayac.addAttr(self.IK_CTRL, longName='FootControls', defaultValue=0.0, hidden = False, keyable = True)
                        mayac.setAttr("%s.FootControls" % (self.IK_CTRL), lock = True)
                        mayac.addAttr(self.IK_CTRL, longName='FootRoll', defaultValue=0.0, hidden = False, keyable = True)
                        mayac.addAttr(self.IK_CTRL, longName='ToeTap', defaultValue=0.0, hidden = False, keyable = True)
                        mayac.addAttr(self.IK_CTRL, longName='ToeSideToSide', defaultValue=0.0, hidden = False, keyable = True)
                        mayac.addAttr(self.IK_CTRL, longName='ToeRotate', defaultValue=0.0, hidden = False, keyable = True)
                        mayac.addAttr(self.IK_CTRL, longName='ToeRoll', defaultValue=0.0, hidden = False, keyable = True)
                        mayac.addAttr(self.IK_CTRL, longName='HipPivot', defaultValue=0.0, hidden = False, keyable = True)
                        mayac.addAttr(self.IK_CTRL, longName='BallPivot', defaultValue=0.0, hidden = False, keyable = True)
                        mayac.addAttr(self.IK_CTRL, longName='ToePivot', defaultValue=0.0, hidden = False, keyable = True)
                        mayac.addAttr(self.IK_CTRL, longName='HipSideToSide', defaultValue=0.0, hidden = False, keyable = True)
                        mayac.addAttr(self.IK_CTRL, longName='HipBackToFront', defaultValue=0.0, hidden = False, keyable = True)
                        
                        #Foot IK Baking LOCs
                        print('#Foot IK Baking LOCs')
                        temp = mayac.spaceLocator(n = "%s_IK_BakingLOC" % (self.nodeName))
                        self.IK_BakingLOC = temp[0]
                        mayac.setAttr("%s.visibility"%(self.IK_BakingLOC), 0)
                        mayac.parent(self.IK_BakingLOC, self.Bind_Joint)
                        mayac.delete(mayac.parentConstraint(self.IK_CTRL, self.IK_BakingLOC))
                        
            
            mayac.orientConstraint(self.IK_Joint, self.Bind_Joint, mo = True)
        if not self.IK_CTRL and self.IK_Joint and not self.translateOpen:
            mayac.orientConstraint(self.IK_Joint, self.Bind_Joint, mo = True)
        elif not self.IK_CTRL and self.IK_Joint and self.translateOpen:
            mayac.parentConstraint(self.IK_Joint, self.Bind_Joint, mo = True)
        if self.Dyn_Joint:
            if not self.translateOpen:
                mayac.orientConstraint(self.DynMult_Joint, self.Bind_Joint, mo = True)
            else:
                mayac.parentConstraint(self.DynMult_Joint, self.Bind_Joint, mo = True)
                self.Dyn_Mult1 = mayac.createNode( 'multiplyDivide', n="%s_MultNodeTrans" %(self.nodeName))
                mayac.connectAttr("%s.translate"%(self.Dyn_Joint), "%s.input1"%(self.Dyn_Mult1))
                mayac.connectAttr("%s.output"%(self.Dyn_Mult1), "%s.translate"%(self.DynMult_Joint))
            self.Dyn_Mult = mayac.createNode( 'multiplyDivide', n="%s_MultNode" %(self.nodeName))
            mayac.connectAttr("%s.rotate"%(self.Dyn_Joint), "%s.input1"%(self.Dyn_Mult))
            mayac.connectAttr("%s.output"%(self.Dyn_Mult), "%s.rotate"%(self.DynMult_Joint))
        if self.Dyn_CTRL:
            mayac.addAttr(self.Dyn_CTRL, longName='weight', defaultValue=1.0, min = 0.0, max = 1.0, keyable = True)
            mayac.addAttr(self.Dyn_CTRL, longName='conserve', defaultValue=1.0, min = 0.0, max = 1.0, keyable = True)
            mayac.addAttr(self.Dyn_CTRL, longName='multiplier', defaultValue=1.0, min = 0.0, keyable = True)
            
        if self.Options_CTRL:
            #place control
            DJB_movePivotToObject(self.Options_CTRL, self.Bind_Joint)
            mayac.parentConstraint(self.Bind_Joint, self.Options_CTRL, mo = True, name = "%s_Constraint" %(self.Options_CTRL))
            #add attributes  
            mayac.addAttr(self.Options_CTRL, longName=switchName, defaultValue=0.0, min = 0.0, max = 1.0, keyable = True)
            mayac.setAttr("%s.rotateOrder" % (self.Options_CTRL), self.rotOrder)
            if "Hand" in self.nodeName:
                mayac.addAttr(self.Options_CTRL, longName='FingerControls', defaultValue=0.0, hidden = False, keyable = True)
                mayac.setAttr("%s.FingerControls" % (self.Options_CTRL), lock = True)
                mayac.addAttr(self.Options_CTRL, longName='ThumbCurl', defaultValue=0.0, min = -10.0, max = 10.0, hidden = False, keyable = True)
                mayac.addAttr(self.Options_CTRL, longName='IndexCurl', defaultValue=0.0, min = -10.0, max = 10.0, hidden = False, keyable = True)
                mayac.addAttr(self.Options_CTRL, longName='MiddleCurl', defaultValue=0.0, min = -10.0, max = 10.0, hidden = False, keyable = True)
                mayac.addAttr(self.Options_CTRL, longName='RingCurl', defaultValue=0.0, min = -10.0, max = 10.0, hidden = False, keyable = True)
                mayac.addAttr(self.Options_CTRL, longName='PinkyCurl', defaultValue=0.0, min = -10.0, max = 10.0, hidden = False, keyable = True)
                mayac.addAttr(self.Options_CTRL, longName='Sway', defaultValue=0.0, min = -10.0, max = 10.0, hidden = False, keyable = True)
                mayac.addAttr(self.Options_CTRL, longName='Spread', defaultValue=0.0, min = -10.0, max = 10.0, hidden = False, keyable = True)
                
            
            
        
    def lockUpCTRLs(self):    
        #lock and hide attributes
        if self.Dyn_CTRL:
            DJB_LockNHide(self.Dyn_CTRL)
        if self.FK_CTRL:
            if self.nodeName == "Root":
                DJB_LockNHide(self.FK_CTRL, tx = False, ty = False, tz = False, rx = False, ry = False, rz = False)
            elif self.nodeName == "Hips" and self.actAsRoot:
                DJB_LockNHide(self.FK_CTRL, tx = False, ty = False, tz = False, rx = False, ry = False, rz = False)
            elif self.translateOpen:
                DJB_LockNHide(self.FK_CTRL, tx = False, ty = False, tz = False, rx = False, ry = False, rz = False)
            else:
                DJB_LockNHide(self.FK_CTRL, rx = False, ry = False, rz = False)
            DJB_LockNHide(self.FK_CTRL_inRig_CONST_GRP)
            DJB_LockNHide(self.FK_CTRL_animData_CONST_GRP)
            DJB_LockNHide(self.FK_CTRL_POS_GRP)
            
        if self.IK_CTRL:
            #lock and hide channels
            DJB_LockNHide(self.IK_CTRL, tx = False, ty = False, tz = False, rx = False, ry = False, rz = False)
            DJB_LockNHide(self.IK_CTRL_inRig_CONST_GRP)
            DJB_LockNHide(self.IK_CTRL_animData_CONST_GRP)
            DJB_LockNHide(self.IK_CTRL_POS_GRP)
            if self.IK_CTRL_grandparent_inRig_CONST_GRP:
                DJB_LockNHide(self.IK_CTRL_grandparent_inRig_CONST_GRP)
            if self.IK_CTRL_parent_POS_GRP:
                DJB_LockNHide(self.IK_CTRL_parent_POS_GRP)
                DJB_LockNHide(self.IK_CTRL_parent_Global_POS_GRP)
                DJB_LockNHide(self.IK_CTRL_parent_animData_CONST_GRP)
                if self.IK_CTRL_grandparent_POS_GRP:
                    DJB_LockNHide(self.IK_CTRL_grandparent_POS_GRP)
                    DJB_LockNHide(self.IK_CTRL_grandparent_Global_POS_GRP)
                    DJB_LockNHide(self.IK_CTRL_grandparent_animData_CONST_GRP)
            if self.IK_CTRL_ReorientGRP:
                DJB_LockNHide(self.IK_CTRL_ReorientGRP)
            if self.IK_Handle:
                DJB_LockNHide(self.IK_Handle)
            if "ForeArm" in self.nodeName or "LeftLeg" in self.nodeName or "RightLeg" in self.nodeName:
                DJB_LockNHide(self.IK_CTRL, tx = False, ty = False, tz = False, rx = True, ry = True, rz = True)
                mayac.setAttr("%s.visibility" % (self.IK_BakingLOC), 0)
            
        if self.Options_CTRL:
            DJB_LockNHide(self.Options_CTRL)
            
        


class DJB_Character():
    def __init__(self, infoNode_ = None, hulaOption_ = 0, name_ = "Character"):
        self.characterNameSpace = None
        self.name = None
        self.joints = None
        self.original_Mesh_Names = None
        self.mesh = None
        self.jointNamespace = None
        self.BoundingBox = None
        self.Root = None
        self.Hips = None
        self.Spine = None
        self.Spine1 = None
        self.Spine2 = None
        self.Spine3 = None
        self.Neck = None
        self.Neck1 = None
        self.Head = None
        self.HeadTop_End = None
        self.LeftShoulder = None
        self.LeftArm = None
        self.LeftForeArm = None
        self.LeftHand = None
        self.LeftHandThumb1 = None
        self.LeftHandThumb2 = None
        self.LeftHandThumb3 = None
        self.LeftHandThumb4 = None
        self.LeftHandIndex1 = None
        self.LeftHandIndex2 = None
        self.LeftHandIndex3 = None
        self.LeftHandIndex4 = None
        self.LeftHandMiddle1 = None
        self.LeftHandMiddle2 = None
        self.LeftHandMiddle3 = None
        self.LeftHandMiddle4 = None
        self.LeftHandRing1 = None
        self.LeftHandRing2 = None
        self.LeftHandRing3 = None
        self.LeftHandRing4 = None
        self.LeftHandPinky1 = None
        self.LeftHandPinky2 = None
        self.LeftHandPinky3 = None
        self.LeftHandPinky4 = None
        self.RightShoulder = None
        self.RightArm = None
        self.RightForeArm = None
        self.RightHand = None
        self.RightHandThumb1 = None
        self.RightHandThumb2 = None
        self.RightHandThumb3 = None
        self.RightHandThumb4 = None
        self.RightHandIndex1 = None
        self.RightHandIndex2 = None
        self.RightHandIndex3 = None
        self.RightHandIndex4 = None
        self.RightHandMiddle1 = None
        self.RightHandMiddle2 = None
        self.RightHandMiddle3 = None
        self.RightHandMiddle4 = None
        self.RightHandRing1 = None
        self.RightHandRing2 = None
        self.RightHandRing3 = None
        self.RightHandRing4 = None
        self.RightHandPinky1 = None
        self.RightHandPinky2 = None
        self.RightHandPinky3 = None
        self.RightHandPinky4 = None
        self.LeftUpLeg = None
        self.LeftLeg = None
        self.LeftFoot = None
        self.LeftToeBase = None
        self.LeftToe_End = None
        self.RightUpLeg = None
        self.RightLeg = None
        self.RightFoot = None
        self.RightToeBase = None
        self.RightToe_End = None
        self.bodyParts = None
        self.proportions = {}
        self.defaultControlScale = 0
        self.Character_GRP = None
        self.global_CTRL = None
        self.CTRL_GRP = None
        self.Joint_GRP = None
        self.AnimData_Joint_GRP = None
        self.Bind_Joint_GRP = None
        self.Mesh_GRP = None
        self.Misc_GRP = None
        self.LeftArm_Switch_Reverse = None
        self.RightArm_Switch_Reverse = None
        self.LeftLeg_Switch_Reverse = None
        self.RightLeg_Switch_Reverse = None
        self.Bind_Joint_SelectSet = None
        self.AnimData_Joint_SelectSet = None
        self.Controls_SelectSet = None
        self.Geo_SelectSet = None
        self.Left_Toe_IK_AnimData_GRP = None
        self.Left_Toe_IK_CTRL = None
        self.Left_ToeBase_IK_AnimData_GRP = None
        self.Left_IK_ToeBase_animData_MultNode = None
        self.Left_ToeBase_IK_CTRL = None
        self.Left_Ankle_IK_AnimData_GRP = None
        self.Left_Ankle_IK_CTRL = None
        self.Left_ToeBase_IkHandle = None
        self.Left_ToeEnd_IkHandle = None
        self.Right_Toe_IK_AnimData_GRP = None
        self.Right_Toe_IK_CTRL = None
        self.Right_ToeBase_IK_AnimData_GRP = None
        self.Right_IK_ToeBase_animData_MultNode = None
        self.Right_ToeBase_IK_CTRL = None
        self.Right_Ankle_IK_AnimData_GRP = None
        self.Right_Ankle_IK_CTRL = None
        self.Right_ToeBase_IkHandle = None
        self.Right_ToeEnd_IkHandle = None
        self.LeftHand_CTRLs_GRP = None
        self.RightHand_CTRLs_GRP = None
        self.LeftFoot_FootRoll_MultNode = None
        self.LeftFoot_ToeRoll_MultNode = None
        self.RightFoot_FootRoll_MultNode = None
        self.RightFoot_ToeRoll_MultNode = None
        self.RightFoot_HipPivot_MultNode = None
        self.RightFoot_BallPivot_MultNode = None
        self.RightFoot_ToePivot_MultNode = None
        self.RightFoot_HipSideToSide_MultNode = None
        self.RightFoot_ToeRotate_MultNode = None
        self.IK_Dummy_Joint_GRP = None
        self.LeftHand_grandparent_Constraint = None
        self.LeftHand_grandparent_Constraint_Reverse = None
        self.RightHand_grandparent_Constraint = None
        self.RightHand_grandparent_Constraint_Reverse = None
        self.LeftForeArm_grandparent_Constraint = None
        self.LeftForeArm_grandparent_Constraint_Reverse = None
        self.RightForeArm_grandparent_Constraint = None
        self.RightForeArm_grandparent_Constraint_Reverse = None
        self.origAnim = None
        self.origAnimation_Layer = None
        self.Mesh_Layer = None
        self.Control_Layer = None
        self.Bind_Joint_Layer = None
        self.infoNode = infoNode_
        self.rigType = None
        self.blendShapeTrackers = None
        
        
        self.ExtraJoints = None
        self.numExtraJointChains = 0
        self.Dyn_CTRL = None
        
        self.hulaOption = hulaOption_
        self.exportList = None
        
        if not self.infoNode:
            self.name = name_
            mayac.currentTime(1)
            self.joints = mayac.ls(type = "joint")
            locators = mayac.ls(et = "locator")
            if locators:
                mayac.delete(locators)
            global JOINT_NAMESPACE
            self.mesh = []
            temp = mayac.ls(geometry = True)
            self.original_Mesh_Names = []
            shapes = []
            for geo in temp:
                #Shape22Orig, ShapeOrig, should make a better test
                if "Orig" not in geo and "Bounding_Box_Override_Cube" not in geo:
                    shapes.append(geo)
                    transform = mayac.listRelatives(geo, parent = True)[0]
                    self.original_Mesh_Names.append(transform)
            for geo in shapes:
                parent = mayac.listRelatives(geo, parent = True, path = True)[0]
                if "|" in geo:
                    geo = makeUnique(geo, "Shape")
                parent = mayac.listRelatives(geo, parent = True, path = True)[0]
                DJB_Unlock(parent)
                parent = mayac.rename(parent, "Mesh_%s" % (DJB_findAfterSeperator(parent, ":")))
                self.mesh.append(mayac.listRelatives(parent, children = True, type = "shape", path = True)[0])
                
            self.jointNamespace = JOINT_NAMESPACE = DJB_findBeforeSeparator(self.joints[1], ':') #changed from 0 for one special case - zombie lores
            
            #override box gets proportions if it exists
            global DJB_Character_ProportionOverrideCube
            if DJB_Character_ProportionOverrideCube:
                if mayac.objExists(DJB_Character_ProportionOverrideCube):
                    self.BoundingBox = mayac.exactWorldBoundingBox(DJB_Character_ProportionOverrideCube)
                    mayac.delete(DJB_Character_ProportionOverrideCube)
                else:
                    DJB_Character_ProportionOverrideCube = ""
                    self.BoundingBox = mayac.exactWorldBoundingBox(self.mesh)
            else:
                self.BoundingBox = mayac.exactWorldBoundingBox(self.mesh)
            
            if self.hulaOption:              
                self.Root = DJB_CharacterNode("Root", actAsRoot_ = 1, optional_ = 1)
                if not self.Root.Bind_Joint:
                    mayac.duplicate(self.jointNamespace + "Hips", parentOnly = True, name = self.jointNamespace + "Root")
                    self.Root = DJB_CharacterNode("Root", actAsRoot_ = 1)
                self.Hips = DJB_CharacterNode("Hips", parent = self.Root)
                self.Spine = DJB_CharacterNode("Spine", parent = self.Root)
                mayac.parent(self.Hips.Bind_Joint, self.Spine.Bind_Joint, self.Root.Bind_Joint)
            else:
                self.Root = DJB_CharacterNode("Root", optional_ = 1)
                if self.Root.Bind_Joint:
                    self.Hips = DJB_CharacterNode("Hips")
                    self.hulaOption = True
                else:
                    self.Hips = DJB_CharacterNode("Hips", actAsRoot_ = 1)
                self.Spine = DJB_CharacterNode("Spine", parent = self.Hips)
                
            self.Spine1 = DJB_CharacterNode("Spine1", parent = self.Spine)
            self.Spine2 = DJB_CharacterNode("Spine2", parent = self.Spine1, optional_ = 1)
            if self.Spine2.Bind_Joint:
                self.Spine3 = DJB_CharacterNode("Spine3", parent = self.Spine2, optional_ = 1)
                if self.Spine3.Bind_Joint:
                    self.Neck = DJB_CharacterNode("Neck", parent = self.Spine3)
                else:
                    self.Neck = DJB_CharacterNode("Neck", parent = self.Spine2)
                self.Neck1 = DJB_CharacterNode("Neck1", parent = self.Neck, optional_ = 1)
                if self.Neck1.Bind_Joint:
                    self.Head = DJB_CharacterNode("Head", parent = self.Neck1)
                else:
                    self.Head = DJB_CharacterNode("Head", parent = self.Neck)
                self.HeadTop_End = DJB_CharacterNode("HeadTop_End", parent = self.Head, alias_ = ["Head_End", "Head_END"])
                if self.Spine3.Bind_Joint:
                    self.LeftShoulder = DJB_CharacterNode("LeftShoulder", parent = self.Spine3)
                else:
                    self.LeftShoulder = DJB_CharacterNode("LeftShoulder", parent = self.Spine2)
            else:
                #going to put in a blank spine3 just to mitigate errors, TODO: better handling
                self.Spine3 = DJB_CharacterNode("Spine3", parent = self.Spine1, optional_ = 1)
                self.Neck = DJB_CharacterNode("Neck", parent = self.Spine1)
                self.Neck1 = DJB_CharacterNode("Neck1", parent = self.Neck, optional_ = 1)
                if self.Neck1.Bind_Joint:
                    self.Head = DJB_CharacterNode("Head", parent = self.Neck1)
                else:
                    self.Head = DJB_CharacterNode("Head", parent = self.Neck)
                self.HeadTop_End = DJB_CharacterNode("HeadTop_End", parent = self.Head, alias_ = ["Head_End", "Head_END"])
                self.LeftShoulder = DJB_CharacterNode("LeftShoulder", parent = self.Spine1)
            self.LeftArm = DJB_CharacterNode("LeftArm", parent = self.LeftShoulder)
            self.LeftForeArm = DJB_CharacterNode("LeftForeArm", parent = self.LeftArm)
            self.LeftHand = DJB_CharacterNode("LeftHand", parent = self.LeftForeArm)
            self.LeftHandThumb1 = DJB_CharacterNode("LeftHandThumb1", optional_ = 1, parent = self.LeftHand)
            self.LeftHandThumb2 = DJB_CharacterNode("LeftHandThumb2", optional_ = 1, parent = self.LeftHandThumb1)
            self.LeftHandThumb3 = DJB_CharacterNode("LeftHandThumb3", optional_ = 1, parent = self.LeftHandThumb2)
            self.LeftHandThumb4 = DJB_CharacterNode("LeftHandThumb4", optional_ = 1, parent = self.LeftHandThumb3)
            self.LeftHandIndex1 = DJB_CharacterNode("LeftHandIndex1", optional_ = 1,parent = self.LeftHand)
            self.LeftHandIndex2 = DJB_CharacterNode("LeftHandIndex2", optional_ = 1, parent = self.LeftHandIndex1)
            self.LeftHandIndex3 = DJB_CharacterNode("LeftHandIndex3", optional_ = 1, parent = self.LeftHandIndex2)
            self.LeftHandIndex4 = DJB_CharacterNode("LeftHandIndex4", optional_ = 1, parent = self.LeftHandIndex3)
            self.LeftHandMiddle1 = DJB_CharacterNode("LeftHandMiddle1", optional_ = 1, parent = self.LeftHand)
            self.LeftHandMiddle2 = DJB_CharacterNode("LeftHandMiddle2", optional_ = 1, parent = self.LeftHandMiddle1)
            self.LeftHandMiddle3 = DJB_CharacterNode("LeftHandMiddle3", optional_ = 1, parent = self.LeftHandMiddle2)
            self.LeftHandMiddle4 = DJB_CharacterNode("LeftHandMiddle4", optional_ = 1, parent = self.LeftHandMiddle3)
            self.LeftHandRing1 = DJB_CharacterNode("LeftHandRing1", optional_ = 1, parent = self.LeftHand)
            self.LeftHandRing2 = DJB_CharacterNode("LeftHandRing2", optional_ = 1, parent = self.LeftHandRing1)
            self.LeftHandRing3 = DJB_CharacterNode("LeftHandRing3", optional_ = 1, parent = self.LeftHandRing2)
            self.LeftHandRing4 = DJB_CharacterNode("LeftHandRing4", optional_ = 1, parent = self.LeftHandRing3)
            self.LeftHandPinky1 = DJB_CharacterNode("LeftHandPinky1", optional_ = 1, parent = self.LeftHand)
            self.LeftHandPinky2 = DJB_CharacterNode("LeftHandPinky2", optional_ = 1, parent = self.LeftHandPinky1)
            self.LeftHandPinky3 = DJB_CharacterNode("LeftHandPinky3", optional_ = 1, parent = self.LeftHandPinky2)
            self.LeftHandPinky4 = DJB_CharacterNode("LeftHandPinky4", optional_ = 1, parent = self.LeftHandPinky3)
            if self.Spine2.Bind_Joint:
                if self.Spine3.Bind_Joint:
                    self.RightShoulder = DJB_CharacterNode("RightShoulder", parent = self.Spine3)
                else:
                    self.RightShoulder = DJB_CharacterNode("RightShoulder", parent = self.Spine2)
            else:
                self.RightShoulder = DJB_CharacterNode("RightShoulder", parent = self.Spine1)
            self.RightArm = DJB_CharacterNode("RightArm", parent = self.RightShoulder)
            self.RightForeArm = DJB_CharacterNode("RightForeArm", parent = self.RightArm)
            self.RightHand = DJB_CharacterNode("RightHand", parent = self.RightForeArm)
            self.RightHandThumb1 = DJB_CharacterNode("RightHandThumb1", optional_ = 1, parent = self.RightHand)
            self.RightHandThumb2 = DJB_CharacterNode("RightHandThumb2", optional_ = 1, parent = self.RightHandThumb1)
            self.RightHandThumb3 = DJB_CharacterNode("RightHandThumb3", optional_ = 1, parent = self.RightHandThumb2)
            self.RightHandThumb4 = DJB_CharacterNode("RightHandThumb4", optional_ = 1, parent = self.RightHandThumb3)
            self.RightHandIndex1 = DJB_CharacterNode("RightHandIndex1", optional_ = 1, parent = self.RightHand)
            self.RightHandIndex2 = DJB_CharacterNode("RightHandIndex2", optional_ = 1, parent = self.RightHandIndex1)
            self.RightHandIndex3 = DJB_CharacterNode("RightHandIndex3", optional_ = 1, parent = self.RightHandIndex2)
            self.RightHandIndex4 = DJB_CharacterNode("RightHandIndex4", optional_ = 1, parent = self.RightHandIndex3)
            self.RightHandMiddle1 = DJB_CharacterNode("RightHandMiddle1", optional_ = 1, parent = self.RightHand)
            self.RightHandMiddle2 = DJB_CharacterNode("RightHandMiddle2", optional_ = 1, parent = self.RightHandMiddle1)
            self.RightHandMiddle3 = DJB_CharacterNode("RightHandMiddle3", optional_ = 1, parent = self.RightHandMiddle2)
            self.RightHandMiddle4 = DJB_CharacterNode("RightHandMiddle4", optional_ = 1, parent = self.RightHandMiddle3)
            self.RightHandRing1 = DJB_CharacterNode("RightHandRing1", optional_ = 1, parent = self.RightHand)
            self.RightHandRing2 = DJB_CharacterNode("RightHandRing2", optional_ = 1, parent = self.RightHandRing1)
            self.RightHandRing3 = DJB_CharacterNode("RightHandRing3", optional_ = 1, parent = self.RightHandRing2)
            self.RightHandRing4 = DJB_CharacterNode("RightHandRing4", optional_ = 1, parent = self.RightHandRing3)
            self.RightHandPinky1 = DJB_CharacterNode("RightHandPinky1", optional_ = 1, parent = self.RightHand)
            self.RightHandPinky2 = DJB_CharacterNode("RightHandPinky2", optional_ = 1, parent = self.RightHandPinky1)
            self.RightHandPinky3 = DJB_CharacterNode("RightHandPinky3", optional_ = 1, parent = self.RightHandPinky2)
            self.RightHandPinky4 = DJB_CharacterNode("RightHandPinky4", optional_ = 1, parent = self.RightHandPinky3)
            self.LeftUpLeg = DJB_CharacterNode("LeftUpLeg", parent = self.Hips)
            self.LeftLeg = DJB_CharacterNode("LeftLeg", parent = self.LeftUpLeg)
            self.LeftFoot = DJB_CharacterNode("LeftFoot", parent = self.LeftLeg)
            self.LeftToeBase = DJB_CharacterNode("LeftToeBase", parent = self.LeftFoot)
            self.LeftToe_End = DJB_CharacterNode("LeftToe_End", parent = self.LeftToeBase, alias_ = ["toe_L", "LeftFootToeBase_End"])
            self.RightUpLeg = DJB_CharacterNode("RightUpLeg", parent = self.Hips)
            self.RightLeg = DJB_CharacterNode("RightLeg", parent = self.RightUpLeg)
            self.RightFoot = DJB_CharacterNode("RightFoot", parent = self.RightLeg)
            self.RightToeBase = DJB_CharacterNode("RightToeBase", parent = self.RightFoot)
            self.RightToe_End = DJB_CharacterNode("RightToe_End", parent = self.RightToeBase, alias_ = ["toe_R", "RightFootToeBase_End"])
            
            #educated guess with 2 samples for rig type
            if mayac.getAttr("%s.jointOrient" % self.LeftUpLeg.Bind_Joint)[0] == (0,0,0) and mayac.getAttr("%s.jointOrient" % self.RightArm.Bind_Joint)[0] == (0,0,0):
                self.rigType = "World"
            else:
                self.rigType = "AutoRig"
            
            #educated guess for fingerFlip
            if self.LeftHandIndex1.Bind_Joint:
                jox = mayac.getAttr("%s.jointOrientX" % (self.LeftHandIndex1.Bind_Joint))
                if jox < -100 or jox > 100:
                    self.fingerFlip = False
                else:
                    self.fingerFlip = True
            
        #there is an infoNode for this Character
        else:
            
            self.characterNameSpace = DJB_findBeforeSeparator(self.infoNode, ':')
            self.jointNamespace = attrToPy("%s.jointNamespace" % (self.infoNode))
            #filmbox attrs
            self.name = attrToPy("%s.name" % (self.infoNode))
            
            
            
            self.mesh = attrToPy("%s.mesh" % (self.infoNode))
            self.original_Mesh_Names = attrToPy("%s.original_Mesh_Names" % (self.infoNode))
            self.BoundingBox = attrToPy("%s.BoundingBox" % (self.infoNode))
            self.rigType = attrToPy("%s.rigType" % (self.infoNode))
            #####################
            self.hulaOption = attrToPy("%s.hulaOption" % (self.infoNode))
            
            self.Root = DJB_CharacterNode("Root", infoNode_ = attrToPy("%s.Root" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            if self.hulaOption:
                if not self.Root.Bind_Joint:
                    return None
                self.Hips = DJB_CharacterNode("Hips", parent = self.Root, infoNode_ = attrToPy("%s.Hips" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
                self.Spine = DJB_CharacterNode("Spine", parent = self.Root, infoNode_ = attrToPy("%s.Spine" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            else:
                self.Hips = DJB_CharacterNode("Hips", infoNode_ = attrToPy("%s.Hips" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
                self.Spine = DJB_CharacterNode("Spine", parent = self.Hips, infoNode_ = attrToPy("%s.Spine" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            self.Spine1 = DJB_CharacterNode("Spine1", parent = self.Spine, infoNode_ = attrToPy("%s.Spine1" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            self.Spine2 = DJB_CharacterNode("Spine2", parent = self.Spine1, optional_ = 1, infoNode_ = attrToPy("%s.Spine2" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            if self.Spine2.Bind_Joint:
                self.Spine3 = DJB_CharacterNode("Spine3", parent = self.Spine2, optional_ = 1, infoNode_ = attrToPy("%s.Spine3" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
                if self.Spine3.Bind_Joint:
                    self.Neck = DJB_CharacterNode("Neck", parent = self.Spine3, infoNode_ = attrToPy("%s.Neck" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
                else:
                    self.Neck = DJB_CharacterNode("Neck", parent = self.Spine2, infoNode_ = attrToPy("%s.Neck" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            else:
                self.Spine3 = DJB_CharacterNode("Spine3", parent = self.Spine1, optional_ = 1, infoNode_ = attrToPy("%s.Spine3" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
                self.Neck = DJB_CharacterNode("Neck", parent = self.Spine1, infoNode_ = attrToPy("%s.Neck" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            self.Neck1 = DJB_CharacterNode("Neck1", parent = self.Neck, optional_ = 1, infoNode_ = attrToPy("%s.Neck1" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            if self.Neck1.Bind_Joint:
                self.Head = DJB_CharacterNode("Head", parent = self.Neck1, infoNode_ = attrToPy("%s.Head" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            else:
                self.Head = DJB_CharacterNode("Head", parent = self.Neck, infoNode_ = attrToPy("%s.Head" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            self.HeadTop_End = DJB_CharacterNode("HeadTop_End", parent = self.Head, infoNode_ = attrToPy("%s.HeadTop_End" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            if self.Spine2.Bind_Joint:
                if self.Spine3.Bind_Joint:
                    self.LeftShoulder = DJB_CharacterNode("LeftShoulder", parent = self.Spine3, infoNode_ = attrToPy("%s.LeftShoulder" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
                else:
                    self.LeftShoulder = DJB_CharacterNode("LeftShoulder", parent = self.Spine2, infoNode_ = attrToPy("%s.LeftShoulder" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            else:
                self.LeftShoulder = DJB_CharacterNode("LeftShoulder", parent = self.Spine1, infoNode_ = attrToPy("%s.LeftShoulder" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            self.LeftArm = DJB_CharacterNode("LeftArm", parent = self.LeftShoulder, infoNode_ = attrToPy("%s.LeftArm" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            self.LeftForeArm = DJB_CharacterNode("LeftForeArm", parent = self.LeftArm, infoNode_ = attrToPy("%s.LeftForeArm" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            self.LeftHand = DJB_CharacterNode("LeftHand", parent = self.LeftForeArm, infoNode_ = attrToPy("%s.LeftHand" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            self.LeftHandThumb1 = DJB_CharacterNode("LeftHandThumb1", optional_ = 1, parent = self.LeftHand, infoNode_ = attrToPy("%s.LeftHandThumb1" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            self.LeftHandThumb2 = DJB_CharacterNode("LeftHandThumb2", optional_ = 1, parent = self.LeftHandThumb1, infoNode_ = attrToPy("%s.LeftHandThumb2" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            self.LeftHandThumb3 = DJB_CharacterNode("LeftHandThumb3", optional_ = 1, parent = self.LeftHandThumb2, infoNode_ = attrToPy("%s.LeftHandThumb3" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            self.LeftHandThumb4 = DJB_CharacterNode("LeftHandThumb4", optional_ = 1, parent = self.LeftHandThumb3, infoNode_ = attrToPy("%s.LeftHandThumb4" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            self.LeftHandIndex1 = DJB_CharacterNode("LeftHandIndex1", optional_ = 1, parent = self.LeftHand, infoNode_ = attrToPy("%s.LeftHandIndex1" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            self.LeftHandIndex2 = DJB_CharacterNode("LeftHandIndex2", optional_ = 1, parent = self.LeftHandIndex1, infoNode_ = attrToPy("%s.LeftHandIndex2" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            self.LeftHandIndex3 = DJB_CharacterNode("LeftHandIndex3", optional_ = 1, parent = self.LeftHandIndex2, infoNode_ = attrToPy("%s.LeftHandIndex3" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            self.LeftHandIndex4 = DJB_CharacterNode("LeftHandIndex4", optional_ = 1, parent = self.LeftHandIndex3, infoNode_ = attrToPy("%s.LeftHandIndex4" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            self.LeftHandMiddle1 = DJB_CharacterNode("LeftHandMiddle1", optional_ = 1, parent = self.LeftHand, infoNode_ = attrToPy("%s.LeftHandMiddle1" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            self.LeftHandMiddle2 = DJB_CharacterNode("LeftHandMiddle2", optional_ = 1, parent = self.LeftHandMiddle1, infoNode_ = attrToPy("%s.LeftHandMiddle2" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            self.LeftHandMiddle3 = DJB_CharacterNode("LeftHandMiddle3", optional_ = 1, parent = self.LeftHandMiddle2, infoNode_ = attrToPy("%s.LeftHandMiddle3" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            self.LeftHandMiddle4 = DJB_CharacterNode("LeftHandMiddle4", optional_ = 1, parent = self.LeftHandMiddle3, infoNode_ = attrToPy("%s.LeftHandMiddle4" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            self.LeftHandRing1 = DJB_CharacterNode("LeftHandRing1", optional_ = 1, parent = self.LeftHand, infoNode_ = attrToPy("%s.LeftHandRing1" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            self.LeftHandRing2 = DJB_CharacterNode("LeftHandRing2", optional_ = 1, parent = self.LeftHandRing1, infoNode_ = attrToPy("%s.LeftHandRing2" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            self.LeftHandRing3 = DJB_CharacterNode("LeftHandRing3", optional_ = 1, parent = self.LeftHandRing2, infoNode_ = attrToPy("%s.LeftHandRing3" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            self.LeftHandRing4 = DJB_CharacterNode("LeftHandRing4", optional_ = 1, parent = self.LeftHandRing3, infoNode_ = attrToPy("%s.LeftHandRing4" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            self.LeftHandPinky1 = DJB_CharacterNode("LeftHandPinky1", optional_ = 1, parent = self.LeftHand, infoNode_ = attrToPy("%s.LeftHandPinky1" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            self.LeftHandPinky2 = DJB_CharacterNode("LeftHandPinky2", optional_ = 1, parent = self.LeftHandPinky1, infoNode_ = attrToPy("%s.LeftHandPinky2" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            self.LeftHandPinky3 = DJB_CharacterNode("LeftHandPinky3", optional_ = 1, parent = self.LeftHandPinky2, infoNode_ = attrToPy("%s.LeftHandPinky3" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            self.LeftHandPinky4 = DJB_CharacterNode("LeftHandPinky4", optional_ = 1, parent = self.LeftHandPinky3, infoNode_ = attrToPy("%s.LeftHandPinky4" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            if self.Spine2.Bind_Joint:
                if self.Spine3.Bind_Joint:
                    self.RightShoulder = DJB_CharacterNode("RightShoulder", parent = self.Spine3, infoNode_ = attrToPy("%s.RightShoulder" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
                else:
                    self.RightShoulder = DJB_CharacterNode("RightShoulder", parent = self.Spine2, infoNode_ = attrToPy("%s.RightShoulder" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            else:
                self.RightShoulder = DJB_CharacterNode("RightShoulder", parent = self.Spine1, infoNode_ = attrToPy("%s.RightShoulder" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            self.RightArm = DJB_CharacterNode("RightArm", parent = self.RightShoulder, infoNode_ = attrToPy("%s.RightArm" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            self.RightForeArm = DJB_CharacterNode("RightForeArm", parent = self.RightArm, infoNode_ = attrToPy("%s.RightForeArm" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            self.RightHand = DJB_CharacterNode("RightHand", parent = self.RightForeArm, infoNode_ = attrToPy("%s.RightHand" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            self.RightHandThumb1 = DJB_CharacterNode("RightHandThumb1", optional_ = 1, parent = self.RightHand, infoNode_ = attrToPy("%s.RightHandThumb1" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            self.RightHandThumb2 = DJB_CharacterNode("RightHandThumb2", optional_ = 1, parent = self.RightHandThumb1, infoNode_ = attrToPy("%s.RightHandThumb2" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            self.RightHandThumb3 = DJB_CharacterNode("RightHandThumb3", optional_ = 1, parent = self.RightHandThumb2, infoNode_ = attrToPy("%s.RightHandThumb3" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            self.RightHandThumb4 = DJB_CharacterNode("RightHandThumb4", optional_ = 1, parent = self.RightHandThumb3, infoNode_ = attrToPy("%s.RightHandThumb4" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            self.RightHandIndex1 = DJB_CharacterNode("RightHandIndex1", optional_ = 1, parent = self.RightHand, infoNode_ = attrToPy("%s.RightHandIndex1" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            self.RightHandIndex2 = DJB_CharacterNode("RightHandIndex2", optional_ = 1, parent = self.RightHandIndex1, infoNode_ = attrToPy("%s.RightHandIndex2" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            self.RightHandIndex3 = DJB_CharacterNode("RightHandIndex3", optional_ = 1, parent = self.RightHandIndex2, infoNode_ = attrToPy("%s.RightHandIndex3" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            self.RightHandIndex4 = DJB_CharacterNode("RightHandIndex4", optional_ = 1, parent = self.RightHandIndex3, infoNode_ = attrToPy("%s.RightHandIndex4" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            self.RightHandMiddle1 = DJB_CharacterNode("RightHandMiddle1", optional_ = 1, parent = self.RightHand, infoNode_ = attrToPy("%s.RightHandMiddle1" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            self.RightHandMiddle2 = DJB_CharacterNode("RightHandMiddle2", optional_ = 1, parent = self.RightHandMiddle1, infoNode_ = attrToPy("%s.RightHandMiddle2" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            self.RightHandMiddle3 = DJB_CharacterNode("RightHandMiddle3", optional_ = 1, parent = self.RightHandMiddle2, infoNode_ = attrToPy("%s.RightHandMiddle3" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            self.RightHandMiddle4 = DJB_CharacterNode("RightHandMiddle4", optional_ = 1, parent = self.RightHandMiddle3, infoNode_ = attrToPy("%s.RightHandMiddle4" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            self.RightHandRing1 = DJB_CharacterNode("RightHandRing1", optional_ = 1, parent = self.RightHand, infoNode_ = attrToPy("%s.RightHandRing1" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            self.RightHandRing2 = DJB_CharacterNode("RightHandRing2", optional_ = 1, parent = self.RightHandRing1, infoNode_ = attrToPy("%s.RightHandRing2" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            self.RightHandRing3 = DJB_CharacterNode("RightHandRing3", optional_ = 1, parent = self.RightHandRing2, infoNode_ = attrToPy("%s.RightHandRing3" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            self.RightHandRing4 = DJB_CharacterNode("RightHandRing4", optional_ = 1, parent = self.RightHandRing3, infoNode_ = attrToPy("%s.RightHandRing4" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            self.RightHandPinky1 = DJB_CharacterNode("RightHandPinky1", optional_ = 1, parent = self.RightHand, infoNode_ = attrToPy("%s.RightHandPinky1" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            self.RightHandPinky2 = DJB_CharacterNode("RightHandPinky2", optional_ = 1, parent = self.RightHandPinky1, infoNode_ = attrToPy("%s.RightHandPinky2" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            self.RightHandPinky3 = DJB_CharacterNode("RightHandPinky3", optional_ = 1, parent = self.RightHandPinky2, infoNode_ = attrToPy("%s.RightHandPinky3" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            self.RightHandPinky4 = DJB_CharacterNode("RightHandPinky4", optional_ = 1, parent = self.RightHandPinky3, infoNode_ = attrToPy("%s.RightHandPinky4" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            self.LeftUpLeg = DJB_CharacterNode("LeftUpLeg", parent = self.Hips, infoNode_ = attrToPy("%s.LeftUpLeg" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            self.LeftLeg = DJB_CharacterNode("LeftLeg", parent = self.LeftUpLeg, infoNode_ = attrToPy("%s.LeftLeg" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            self.LeftFoot = DJB_CharacterNode("LeftFoot", parent = self.LeftLeg, infoNode_ = attrToPy("%s.LeftFoot" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            self.LeftToeBase = DJB_CharacterNode("LeftToeBase", parent = self.LeftFoot, infoNode_ = attrToPy("%s.LeftToeBase" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            self.LeftToe_End = DJB_CharacterNode("LeftToe_End", parent = self.LeftToeBase, infoNode_ = attrToPy("%s.LeftToe_End" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            self.RightUpLeg = DJB_CharacterNode("RightUpLeg", parent = self.Hips, infoNode_ = attrToPy("%s.RightUpLeg" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            self.RightLeg = DJB_CharacterNode("RightLeg", parent = self.RightUpLeg, infoNode_ = attrToPy("%s.RightLeg" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            self.RightFoot = DJB_CharacterNode("RightFoot", parent = self.RightLeg, infoNode_ = attrToPy("%s.RightFoot" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            self.RightToeBase = DJB_CharacterNode("RightToeBase", parent = self.RightFoot, infoNode_ = attrToPy("%s.RightToeBase" % (self.infoNode)), nameSpace_ = self.characterNameSpace)
            self.RightToe_End = DJB_CharacterNode("RightToe_End", parent = self.RightToeBase, infoNode_ = attrToPy("%s.RightToe_End" % (self.infoNode)), nameSpace_ = self.characterNameSpace)

            ##############################################
            self.proportions = attrToPy("%s.proportions" % (self.infoNode))
            self.defaultControlScale = attrToPy("%s.defaultControlScale" % (self.infoNode))
            self.Character_GRP = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.Character_GRP" % (self.infoNode)))
            self.global_CTRL = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.global_CTRL" % (self.infoNode)))
            self.CTRL_GRP = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.CTRL_GRP" % (self.infoNode)))
            self.Joint_GRP = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.Joint_GRP" % (self.infoNode)))
            self.AnimData_Joint_GRP = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.AnimData_Joint_GRP" % (self.infoNode)))
            self.Bind_Joint_GRP = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.Bind_Joint_GRP" % (self.infoNode)))
            self.Mesh_GRP = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.Mesh_GRP" % (self.infoNode)))
            self.Misc_GRP = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.Misc_GRP" % (self.infoNode)))
            self.LeftArm_Switch_Reverse = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.Misc_GRP" % (self.infoNode)))
            self.RightArm_Switch_Reverse = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.RightArm_Switch_Reverse" % (self.infoNode)))
            self.LeftLeg_Switch_Reverse = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.LeftLeg_Switch_Reverse" % (self.infoNode)))
            self.RightLeg_Switch_Reverse = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.RightLeg_Switch_Reverse" % (self.infoNode)))
            self.Bind_Joint_SelectSet = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.Bind_Joint_SelectSet" % (self.infoNode)))
            self.AnimData_Joint_SelectSet = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.AnimData_Joint_SelectSet" % (self.infoNode)))
            self.Controls_SelectSet = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.Controls_SelectSet" % (self.infoNode)))
            self.Geo_SelectSet = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.Geo_SelectSet" % (self.infoNode)))
            self.Left_Toe_IK_AnimData_GRP = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.Left_Toe_IK_AnimData_GRP" % (self.infoNode)))
            self.Left_Toe_IK_CTRL = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.Left_Toe_IK_CTRL" % (self.infoNode)))
            self.Left_ToeBase_IK_AnimData_GRP = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.Left_ToeBase_IK_AnimData_GRP" % (self.infoNode)))
            self.Left_IK_ToeBase_animData_MultNode = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.Left_IK_ToeBase_animData_MultNode" % (self.infoNode)))
            self.Left_ToeBase_IK_CTRL = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.Left_ToeBase_IK_CTRL" % (self.infoNode)))
            self.Left_Ankle_IK_AnimData_GRP = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.Left_Ankle_IK_AnimData_GRP" % (self.infoNode)))
            self.Left_Ankle_IK_CTRL = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.Left_Ankle_IK_CTRL" % (self.infoNode)))
            self.Left_ToeBase_IkHandle = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.Left_ToeBase_IkHandle" % (self.infoNode)))
            self.Left_ToeEnd_IkHandle = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.Left_ToeEnd_IkHandle" % (self.infoNode)))
            self.Right_Toe_IK_AnimData_GRP = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.Right_Toe_IK_AnimData_GRP" % (self.infoNode)))
            self.Right_Toe_IK_CTRL = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.Right_Toe_IK_CTRL" % (self.infoNode)))
            self.Right_ToeBase_IK_AnimData_GRP = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.Right_ToeBase_IK_AnimData_GRP" % (self.infoNode)))
            self.Right_IK_ToeBase_animData_MultNode = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.Right_IK_ToeBase_animData_MultNode" % (self.infoNode)))
            self.Right_ToeBase_IK_CTRL = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.Right_ToeBase_IK_CTRL" % (self.infoNode)))
            self.Right_Ankle_IK_AnimData_GRP = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.Right_Ankle_IK_AnimData_GRP" % (self.infoNode)))
            self.Right_Ankle_IK_CTRL = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.Right_Ankle_IK_AnimData_GRP" % (self.infoNode)))
            self.Right_ToeBase_IkHandle = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.Right_ToeBase_IkHandle" % (self.infoNode)))
            self.Right_ToeEnd_IkHandle = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.Right_ToeEnd_IkHandle" % (self.infoNode)))
            self.LeftHand_CTRLs_GRP = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.LeftHand_CTRLs_GRP" % (self.infoNode)))
            self.RightHand_CTRLs_GRP = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.RightHand_CTRLs_GRP" % (self.infoNode)))
            self.LeftFoot_FootRoll_MultNode = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.LeftFoot_FootRoll_MultNode" % (self.infoNode)))
            self.LeftFoot_ToeRoll_MultNode = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.LeftFoot_ToeRoll_MultNode" % (self.infoNode)))
            self.RightFoot_FootRoll_MultNode = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.RightFoot_FootRoll_MultNode" % (self.infoNode)))
            self.RightFoot_ToeRoll_MultNode = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.RightFoot_ToeRoll_MultNode" % (self.infoNode)))
            self.RightFoot_HipPivot_MultNode = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.RightFoot_HipPivot_MultNode" % (self.infoNode)))
            self.RightFoot_BallPivot_MultNode = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.RightFoot_BallPivot_MultNode" % (self.infoNode)))
            self.RightFoot_ToePivot_MultNode = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.RightFoot_ToePivot_MultNode" % (self.infoNode)))
            self.RightFoot_HipSideToSide_MultNode = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.RightFoot_HipSideToSide_MultNode" % (self.infoNode)))
            self.RightFoot_ToeRotate_MultNode = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.RightFoot_ToeRotate_MultNode" % (self.infoNode)))
            self.IK_Dummy_Joint_GRP = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.IK_Dummy_Joint_GRP" % (self.infoNode)))
            self.LeftHand_grandparent_Constraint = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.LeftHand_grandparent_Constraint" % (self.infoNode)))
            self.LeftHand_grandparent_Constraint_Reverse = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.LeftHand_grandparent_Constraint_Reverse" % (self.infoNode)))
            self.RightHand_grandparent_Constraint = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.RightHand_grandparent_Constraint" % (self.infoNode)))
            self.RightHand_grandparent_Constraint_Reverse = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.RightHand_grandparent_Constraint_Reverse" % (self.infoNode)))
            self.LeftForeArm_grandparent_Constraint = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.LeftForeArm_grandparent_Constraint" % (self.infoNode)))
            self.LeftForeArm_grandparent_Constraint_Reverse = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.LeftForeArm_grandparent_Constraint_Reverse" % (self.infoNode)))
            self.RightForeArm_grandparent_Constraint = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.RightForeArm_grandparent_Constraint" % (self.infoNode)))
            self.RightForeArm_grandparent_Constraint_Reverse = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.RightForeArm_grandparent_Constraint_Reverse" % (self.infoNode)))
            self.exportList = attrToPy("%s.exportList" % (self.infoNode))
            
            if attrToPy("%s.origAnim" % (self.infoNode)):
                if mayac.objExists(DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.origAnim" % (self.infoNode)))):
                    self.origAnim = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.origAnim" % (self.infoNode)))
                    self.origAnimation_Layer = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.origAnimation_Layer" % (self.infoNode)))
                else:
                    self.origAnim = attrToPy("%s.origAnim" % (self.infoNode))
                    self.origAnimation_Layer = attrToPy("%s.origAnimation_Layer" % (self.infoNode))
            self.Mesh_Layer = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.Mesh_Layer" % (self.infoNode)))
            #self.Control_Layer = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.Control_Layer" % (self.infoNode)))
            self.Bind_Joint_Layer = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.Bind_Joint_Layer" % (self.infoNode)))
            self.fingerFlip = attrToPy("%s.fingerFlip" % (self.infoNode))
            
            
            
            
            
        
        
           
        self.bodyParts = []
        for bodyPart in (self.Root, self.Hips, self.Spine, self.Spine1, self.Spine2, self.Spine3, self.Neck, self.Neck1, self.Head, self.HeadTop_End, self.LeftShoulder, 
                              self.LeftArm, self.LeftForeArm, self.LeftHand, self.LeftHandThumb1, self.LeftHandThumb2, self.LeftHandThumb3, 
                              self.LeftHandThumb4, self.LeftHandIndex1, self.LeftHandIndex2, self.LeftHandIndex3, self.LeftHandIndex4,
                              self.LeftHandMiddle1, self.LeftHandMiddle2, self.LeftHandMiddle3, self.LeftHandMiddle4, self.LeftHandRing1,
                              self.LeftHandRing2, self.LeftHandRing3, self.LeftHandRing4, self.LeftHandPinky1, self.LeftHandPinky2, 
                              self.LeftHandPinky3, self.LeftHandPinky4, self.RightShoulder, self.RightArm, self.RightForeArm, 
                              self.RightHand, self.RightHandThumb1, self.RightHandThumb2, self.RightHandThumb3, 
                              self.RightHandThumb4, self.RightHandIndex1, self.RightHandIndex2, self.RightHandIndex3, self.RightHandIndex4,
                              self.RightHandMiddle1, self.RightHandMiddle2, self.RightHandMiddle3, self.RightHandMiddle4, self.RightHandRing1,
                              self.RightHandRing2, self.RightHandRing3, self.RightHandRing4, self.RightHandPinky1, self.RightHandPinky2, 
                              self.RightHandPinky3, self.RightHandPinky4, self.LeftUpLeg, self.LeftLeg, self.LeftFoot, self.LeftToeBase,
                              self.LeftToe_End, self.RightUpLeg, self.RightLeg, self.RightFoot, self.RightToeBase, self.RightToe_End):
            if bodyPart and bodyPart.Bind_Joint:
                self.bodyParts.append(bodyPart)
                
        #Dynamics
        if self.infoNode:
            self.Dyn_CTRL = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.Dyn_CTRL" % (self.infoNode)))
            self.numExtraJointChains = attrToPy("%s.numExtraJointChains" % (self.infoNode))
            self.ExtraJoints = []
            extraJointInfoNodes = attrToPy("%s.ExtraJoints" % (self.infoNode))
            if extraJointInfoNodes:
                for extraJointInfoNode in extraJointInfoNodes:
                    extraJointInfoNode = DJB_addNameSpace(self.characterNameSpace, extraJointInfoNode)
                    extraJointName = DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.nodeName" % (extraJointInfoNode)))
                    if not extraJointName:
                        print self.nodeName
                        extraJointName = attrToPy("%s.Bind_Joint" % (extraJointInfoNode))[5:]
                    nodesParent = None
                    parentShouldBe = attrToPy("%s.parent" % (extraJointInfoNode))
                    if not parentShouldBe:
                        parentShouldBe = mayac.listRelatives(DJB_addNameSpace(self.characterNameSpace, attrToPy("%s.Bind_Joint" % (extraJointInfoNode))), parent = True)[0]
                        parentShouldBe = DJB_findAfterSeperator(parentShouldBe, ":")[5:]
                    for bodyPart in self.bodyParts:
                        if bodyPart.nodeName == parentShouldBe:
                            nodesParent = bodyPart
                    if not nodesParent:
                        for bodyPart in self.ExtraJoints:
                            if bodyPart.nodeName == parentShouldBe:
                                nodesParent = bodyPart
                    if not nodesParent:
                        for bodyPart in self.ExtraJoints:
                            parentShouldBeNamespaced = DJB_addNameSpace(self.characterNameSpace, parentShouldBe)
                            if bodyPart.nodeName == parentShouldBeNamespaced:
                                nodesParent = bodyPart
                    extraJointInfoNode = DJB_findAfterSeperator(extraJointInfoNode, ":")
                    self.ExtraJoints.append(DJB_CharacterNode(extraJointName, parent = nodesParent, infoNode_ = extraJointInfoNode, nameSpace_ = self.characterNameSpace))
            else:
                self.ExtraJoints = None  
        
        
        
        mayac.select(clear = True)
        

    
    def fixArmsAndLegs(self):
        LAnklePosStart = mayac.xform(self.LeftFoot.Bind_Joint, query = True, worldSpace = True, absolute = True, translation = True)
        RAnklePosStart = mayac.xform(self.RightFoot.Bind_Joint, query = True, worldSpace = True, absolute = True, translation = True)
        
        if self.rigType == "World":
            value = -1
            while not DJB_CheckAngle(self.LeftUpLeg.Bind_Joint, self.LeftLeg.Bind_Joint, self.LeftFoot.Bind_Joint, axis = "x", multiplier = -1):
                mayac.rotate(value, 0, 0, self.LeftUpLeg.Bind_Joint, relative = True)
                mayac.rotate(value*-1, 0, 0, self.LeftLeg.Bind_Joint, relative = True)
                mayac.refresh()
            mayac.rotate(-45, 0, 0, self.LeftUpLeg.Bind_Joint, relative = True)
            mayac.rotate(90, 0, 0, self.LeftLeg.Bind_Joint, relative = True)
            mayac.joint(self.LeftUpLeg.Bind_Joint, edit = True, setPreferredAngles=True, children=True)
            mayac.rotate(45, 0, 0, self.LeftUpLeg.Bind_Joint, relative = True)
            mayac.rotate(-90, 0, 0, self.LeftLeg.Bind_Joint, relative = True)
              
            value = -1
            while not DJB_CheckAngle(self.RightUpLeg.Bind_Joint, self.RightLeg.Bind_Joint, self.RightFoot.Bind_Joint, axis = "x", multiplier = -1):
                mayac.rotate(value, 0, 0, self.RightUpLeg.Bind_Joint, relative = True)
                mayac.rotate(value*-1, 0, 0, self.RightLeg.Bind_Joint, relative = True)
                mayac.refresh()
            mayac.rotate(-45, 0, 0, self.RightUpLeg.Bind_Joint, relative = True)
            mayac.rotate(90, 0, 0, self.RightLeg.Bind_Joint, relative = True)
            mayac.joint( self.RightUpLeg.Bind_Joint, edit = True, setPreferredAngles=True, children=True)
            mayac.rotate(45, 0, 0, self.RightUpLeg.Bind_Joint, relative = True)
            mayac.rotate(-90, 0, 0, self.RightLeg.Bind_Joint, relative = True)
            
            value = -1
            while not DJB_CheckAngle(self.LeftArm.Bind_Joint, self.LeftForeArm.Bind_Joint, self.LeftHand.Bind_Joint, axis = "y", multiplier = 1):
                mayac.rotate(0, value, 0, self.LeftForeArm.Bind_Joint, relative = True)
                mayac.refresh()
            tempRotData = mayac.getAttr("%s.rotate" %(self.LeftArm.Bind_Joint))
            mayac.rotate(0, 0, 0, self.LeftArm.Bind_Joint, absolute = True)
            mayac.rotate(0, -90, 0, self.LeftForeArm.Bind_Joint, relative = True)
            mayac.joint( self.LeftArm.Bind_Joint, edit = True, setPreferredAngles=True, children=True)
            mayac.setAttr("%s.rotate" %(self.LeftArm.Bind_Joint), tempRotData[0][0], tempRotData[0][1], tempRotData[0][2], type = "double3")
            mayac.rotate(0, 90, 0, self.LeftForeArm.Bind_Joint, relative = True)
                
            value = 1
            while not DJB_CheckAngle(self.RightArm.Bind_Joint, self.RightForeArm.Bind_Joint, self.RightHand.Bind_Joint, axis = "y", multiplier = -1):
                mayac.rotate(0, value, 0, self.RightForeArm.Bind_Joint, relative = True)
                mayac.refresh()
            tempRotData = mayac.getAttr("%s.rotate" %(self.RightArm.Bind_Joint))
            mayac.rotate(0, 0, 0, self.RightArm.Bind_Joint, absolute = True)
            mayac.rotate(0, 90, 0, self.RightForeArm.Bind_Joint, relative = True)
            mayac.joint( self.RightArm.Bind_Joint, edit = True, setPreferredAngles=True, children=True)
            mayac.setAttr("%s.rotate" %(self.RightArm.Bind_Joint), tempRotData[0][0], tempRotData[0][1], tempRotData[0][2], type = "double3")
            mayac.rotate(0, -90, 0, self.RightForeArm.Bind_Joint, relative = True)
        
        elif self.rigType =="AutoRig":
            value = 1
            while not DJB_CheckAngle(self.LeftUpLeg.Bind_Joint, self.LeftLeg.Bind_Joint, self.LeftFoot.Bind_Joint, axis = "x", multiplier = 1):
                mayac.rotate(value, 0, 0, self.LeftUpLeg.Bind_Joint, relative = True)
                mayac.rotate(value*-1, 0, 0, self.LeftLeg.Bind_Joint, relative = True)
                mayac.refresh()
            mayac.rotate(45, 0, 0, self.LeftUpLeg.Bind_Joint, relative = True)
            mayac.rotate(-90, 0, 0, self.LeftLeg.Bind_Joint, relative = True)
            mayac.joint(self.LeftUpLeg.Bind_Joint, edit = True, setPreferredAngles=True, children=True)
            mayac.rotate(-45, 0, 0, self.LeftUpLeg.Bind_Joint, relative = True)
            mayac.rotate(90, 0, 0, self.LeftLeg.Bind_Joint, relative = True)
              
            value = 1
            while not DJB_CheckAngle(self.RightUpLeg.Bind_Joint, self.RightLeg.Bind_Joint, self.RightFoot.Bind_Joint, axis = "x", multiplier = 1):
                mayac.rotate(value, 0, 0, self.RightUpLeg.Bind_Joint, relative = True)
                mayac.rotate(value*-1, 0, 0, self.RightLeg.Bind_Joint, relative = True)
                mayac.refresh()
            mayac.rotate(45, 0, 0, self.RightUpLeg.Bind_Joint, relative = True)
            mayac.rotate(-90, 0, 0, self.RightLeg.Bind_Joint, relative = True)
            mayac.joint( self.RightUpLeg.Bind_Joint, edit = True, setPreferredAngles=True, children=True)
            mayac.rotate(-45, 0, 0, self.RightUpLeg.Bind_Joint, relative = True)
            mayac.rotate(90, 0, 0, self.RightLeg.Bind_Joint, relative = True)
            
            value = 1
            while not DJB_CheckAngle(self.LeftArm.Bind_Joint, self.LeftForeArm.Bind_Joint, self.LeftHand.Bind_Joint, axis = "z", multiplier = -1):
                mayac.rotate(0, 0, value, self.LeftForeArm.Bind_Joint, relative = True)
                mayac.refresh()
            tempRotData = mayac.getAttr("%s.rotate" %(self.LeftArm.Bind_Joint))
            mayac.rotate(0, 0, 0, self.LeftArm.Bind_Joint, absolute = True)
            mayac.rotate(0, 0, 90, self.LeftForeArm.Bind_Joint, relative = True)
            mayac.joint( self.LeftArm.Bind_Joint, edit = True, setPreferredAngles=True, children=True)
            mayac.setAttr("%s.rotate" %(self.LeftArm.Bind_Joint), tempRotData[0][0], tempRotData[0][1], tempRotData[0][2], type = "double3")
            mayac.rotate(0, 0, -90, self.LeftForeArm.Bind_Joint, relative = True)
                
            value = -1
            while not DJB_CheckAngle(self.RightArm.Bind_Joint, self.RightForeArm.Bind_Joint, self.RightHand.Bind_Joint, axis = "z", multiplier = 1):
                mayac.rotate(0, 0, value, self.RightForeArm.Bind_Joint, relative = True)
                mayac.refresh()
            tempRotData = mayac.getAttr("%s.rotate" %(self.RightArm.Bind_Joint))
            mayac.rotate(0, 0, 0, self.RightArm.Bind_Joint, absolute = True)
            mayac.rotate(0, 0, -90, self.RightForeArm.Bind_Joint, relative = True)
            mayac.joint( self.RightArm.Bind_Joint, edit = True, setPreferredAngles=True, children=True)
            mayac.setAttr("%s.rotate" %(self.RightArm.Bind_Joint), tempRotData[0][0], tempRotData[0][1], tempRotData[0][2], type = "double3")
            mayac.rotate(0, 0, 90, self.RightForeArm.Bind_Joint, relative = True)
        
        LAnklePosEnd = mayac.xform(self.LeftFoot.Bind_Joint, query = True, worldSpace = True, absolute = True, translation = True)
        RAnklePosEnd = mayac.xform(self.RightFoot.Bind_Joint, query = True, worldSpace = True, absolute = True, translation = True)
        AvgDiff = (LAnklePosStart[1]-LAnklePosEnd[1] + RAnklePosStart[1] - RAnklePosEnd[1]) / 2
        
        if self.hulaOption:
            mayac.move(0,AvgDiff,0, self.Root.Bind_Joint, relative = True)
        else:
            mayac.move(0,AvgDiff,0, self.Hips.Bind_Joint, relative = True)
        
        
        
    def makeAnimDataJoints(self):
        for bodyPart in self.bodyParts:
            bodyPart.duplicateJoint("AnimData")
        mayac.select(clear = True)
        
        #IK dummy joints
        if self.Root.Bind_Joint:
            self.Root.duplicateJoint("IK_Dummy")
        self.Hips.duplicateJoint("IK_Dummy")
        self.Spine.duplicateJoint("IK_Dummy")
        self.Spine1.duplicateJoint("IK_Dummy")
        self.Spine2.duplicateJoint("IK_Dummy")
        if self.Spine3 and self.Spine3.Bind_Joint:
            self.Spine3.duplicateJoint("IK_Dummy")
        self.LeftShoulder.duplicateJoint("IK_Dummy")
        self.RightShoulder.duplicateJoint("IK_Dummy")
            
    def makeControls(self, estimateSize = True):
    
        if len(self.mesh):
            bbox = self.BoundingBox
            
            self.proportions["highPoint"] = bbox[4]
            self.proportions["lowPoint"] = bbox[1]
            self.proportions["height"] = bbox[4]-bbox[1]
            self.proportions["front"] = bbox[5]
            self.proportions["back"] = bbox[2]
            self.proportions["depth"] = bbox[5]-bbox[2]
            self.proportions["depthMidpoint"] = ((bbox[5]-bbox[2])/2) + bbox[2]
            self.proportions["left"] = bbox[0]
            self.proportions["right"] = bbox[3]
            self.proportions["width"] = bbox[3]-bbox[0]
            self.proportions["widthMidpoint"] = ((bbox[3]-bbox[0])/2) + bbox[0]
            
        #global   
        temp = mayac.circle(
                        radius = (self.proportions["width"]+self.proportions["depth"])*.35,
                        constructionHistory = False,
                        name = "global_CTRL")
        self.global_CTRL = temp[0]
        mayac.move(self.proportions["widthMidpoint"], self.proportions["lowPoint"], self.proportions["depthMidpoint"], absolute = True, worldSpace = True)
        mayac.rotate(90,0,0, self.global_CTRL)
        DJB_cleanGEO(self.global_CTRL)
        DJB_ChangeDisplayColor(self.global_CTRL)
        
        
        
        if self.rigType == "AutoRig":  
            #root
            if self.Root.Bind_Joint:
                self.Root.createControl(type = "normal", 
                                    style = "circle", 
                                    scale = (self.proportions["depth"]*0.8, self.proportions["depth"]*0.8, self.proportions["depth"]*0.8), 
                                    offset = (0,0,0), 
                                    estimateSize = estimateSize)
            
                #hips
                self.Hips.createControl(type = "normal", 
                                        style = "hula", 
                                        scale = (self.proportions["depth"]*0.75, self.proportions["depth"]*0.75, self.proportions["depth"]*0.75),
                                        offset = (0,-.01*self.proportions["height"],0), 
                                        estimateSize = estimateSize,
                                        color_ = "yellow")
            else:
                #hips
                self.Hips.createControl(type = "normal", 
                                    style = "circle", 
                                    scale = (self.proportions["depth"]*0.8, self.proportions["depth"]*0.8, self.proportions["depth"]*0.8), 
                                    offset = (0,0,0), 
                                    estimateSize = estimateSize)
            #spine
            self.Spine.createControl(type = "normal", 
                                    style = "circle", 
                                    scale = (self.proportions["depth"]*0.7, self.proportions["depth"]*0.7, self.proportions["depth"]*0.7),
                                    offset = (0,0,self.proportions["depth"]*0.1), 
                                    estimateSize = estimateSize,
                                    color_ = "yellow")
            
            #spine1
            if self.Spine2.Bind_Joint:
                self.Spine1.createControl(type = "normal", 
                                        style = "circle", 
                                        scale = (self.proportions["depth"]*0.6, self.proportions["depth"]*0.6, self.proportions["depth"]*0.6),
                                        offset = (0,0,self.proportions["depth"]*0.15), 
                                        estimateSize = estimateSize,
                                        color_ = "yellow")
                #spine2
                if self.Spine3.Bind_Joint:
                    self.Spine2.createControl(type = "normal", 
                                        style = "circle", 
                                        scale = (self.proportions["depth"]*0.6, self.proportions["depth"]*0.6, self.proportions["depth"]*0.6),
                                        offset = (0,0,self.proportions["depth"]*0.15), 
                                        estimateSize = estimateSize,
                                        color_ = "yellow")
                    self.Spine3.createControl(type = "normal", 
                                        style = "box", 
                                        scale = (self.proportions["depth"]*0.7, self.proportions["depth"]*0.7, (self.proportions["depth"])*0.8), 
                                        offset = (0,self.proportions["depth"]*.2,self.proportions["depth"]*0.1), 
                                        estimateSize = estimateSize,
                                        color_ = "yellow")
                else:
                    self.Spine2.createControl(type = "normal", 
                                        style = "box", 
                                        scale = (self.proportions["depth"]*0.7, self.proportions["depth"]*0.7, (self.proportions["depth"])*0.8), 
                                        offset = (0,self.proportions["depth"]*.2,self.proportions["depth"]*0.1), 
                                        estimateSize = estimateSize,
                                        color_ = "yellow")
            else:
                self.Spine1.createControl(type = "normal", 
                                        style = "box", 
                                        scale = (self.proportions["depth"]*0.7, self.proportions["depth"]*0.7, (self.proportions["depth"])*0.8), 
                                        offset = (0,self.proportions["depth"]*.2,self.proportions["depth"]*0.1), 
                                        estimateSize = estimateSize,
                                        color_ = "yellow")
                                    
            #neck
            self.Neck.createControl(type = "normal", 
                                    style = "pin1", 
                                    scale = (self.proportions["depth"]*-0.18, self.proportions["depth"]*0.18, self.proportions["depth"]*0.18),
                                    offset = (self.proportions["height"]*0.033, 0, self.proportions["height"]*-0.04),  
                                    estimateSize = estimateSize,
                                    color_ = "yellow")
            if self.Neck1.Bind_Joint:
                self.Neck1.createControl(type = "normal", 
                                    style = "pin1", 
                                    scale = (self.proportions["depth"]*-0.18, self.proportions["depth"]*0.18, self.proportions["depth"]*0.18),
                                    offset = (self.proportions["height"]*0.033, 0, self.proportions["height"]*-0.04),  
                                    estimateSize = estimateSize,
                                    color_ = "yellow")
                                    
            #head
            self.Head.createControl(type = "normal", 
                                    style = "box", 
                                    scale = (self.proportions["depth"]*0.4, self.proportions["height"]*0.13, (self.proportions["depth"])*0.5), 
                                    offset = (0,self.proportions["height"]*.08,self.proportions["depth"]*0.1), 
                                    estimateSize = estimateSize,
                                    color_ = "yellow")
                              
            #LeftShoulder
            self.LeftShoulder.createControl(type = "normal", 
                                    style = "circleWrapped", 
                                    scale = (self.proportions["depth"]*0.4, self.proportions["depth"]*0.15, self.proportions["depth"]*0.15), 
                                    offset = (0,self.proportions["depth"]*0.3,self.proportions["height"]*-0.04),  
                                    estimateSize = estimateSize,
                                    color_ = "blue1")
                                    
            #RightShoulder
            self.RightShoulder.createControl(type = "normal", 
                                    style = "circleWrapped", 
                                    scale = (self.proportions["depth"]*0.4, self.proportions["depth"]*0.15, self.proportions["depth"]*0.15), 
                                    offset = (0,self.proportions["depth"]*0.3,self.proportions["height"]*-0.04),  
                                    estimateSize = estimateSize,
                                    color_ = "red1")
            
            #LeftArm
            self.LeftArm.createControl(type = "FK", 
                                    style = "circle", 
                                    scale = (self.proportions["depth"]*0.25, self.proportions["depth"]*0.25, self.proportions["depth"]*0.25),
                                    offset = (0, 0, 0),  
                                    estimateSize = estimateSize,
                                    color_ = "blue1")
            
            #RightArm
            self.RightArm.createControl(type = "FK", 
                                    style = "circle", 
                                    scale = (self.proportions["depth"]*0.25, self.proportions["depth"]*0.25, self.proportions["depth"]*0.25),
                                    offset = (0, 0, 0),  
                                    estimateSize = estimateSize,
                                    color_ = "red1")
            
            #LeftForeArm
            self.LeftForeArm.createControl(type = "FK", 
                                    style = "circle", 
                                    scale = (self.proportions["depth"]*0.25, self.proportions["depth"]*0.25, self.proportions["depth"]*0.25),
                                    offset = (0, 0, 0),  
                                    estimateSize = estimateSize,
                                    color_ = "blue1")
            
            self.LeftForeArm.createControl(type = "IK", 
                                    style = "PoleVector", 
                                    scale = (self.proportions["depth"]*0.1, self.proportions["depth"]*0.2, self.proportions["depth"]*0.1),
                                    offset = (0, 0, 0),
                                    rotate = (0, 90, 0),  
                                    estimateSize = estimateSize,
                                    color_ = "blue2")
            
            #RightForeArm
            self.RightForeArm.createControl(type = "FK", 
                                    style = "circle", 
                                    scale = (self.proportions["depth"]*0.25, self.proportions["depth"]*0.25, self.proportions["depth"]*0.25),
                                    offset = (0, 0, 0),  
                                    estimateSize = estimateSize,
                                    color_ = "red1")
            
            self.RightForeArm.createControl(type = "IK", 
                                    style = "PoleVector", 
                                    scale = (self.proportions["depth"]*0.1, self.proportions["depth"]*0.2, self.proportions["depth"]*0.1),
                                    offset = (0, 0, 0),  
                                    rotate = (0, -90, 0),
                                    estimateSize = estimateSize,
                                    color_ = "red2")
            
            #LeftHand
            self.LeftHand.createControl(type = "FK", 
                                    style = "circle", 
                                    scale = (self.proportions["depth"]*0.2, self.proportions["depth"]*0.2, self.proportions["depth"]*0.2),
                                    offset = (0, 0, 0),  
                                    estimateSize = estimateSize,
                                    color_ = "blue1")
            
            self.LeftHand.createControl(type = "IK", 
                                    style = "box", 
                                    scale = (self.proportions["depth"]*0.2, self.proportions["depth"]*0.3, self.proportions["depth"]*0.2),
                                    offset = (0, self.proportions["depth"]*0.3, 0),  
                                    estimateSize = estimateSize,
                                    color_ = "blue2")
            
            #RightHand
            self.RightHand.createControl(type = "FK", 
                                    style = "circle", 
                                    scale = (self.proportions["depth"]*0.2, self.proportions["depth"]*0.2, self.proportions["depth"]*0.2),
                                    offset = (0, 0, 0),  
                                    estimateSize = estimateSize,
                                    color_ = "red1")
            
            self.RightHand.createControl(type = "IK", 
                                    style = "box", 
                                    scale = (self.proportions["depth"]*0.2, self.proportions["depth"]*0.3, self.proportions["depth"]*0.2),
                                    offset = (0, self.proportions["depth"]*0.3, 0),  
                                    estimateSize = estimateSize,
                                    color_ = "red2")
                                    
                                    
            #LeftUpLeg
            self.LeftUpLeg.createControl(type = "FK", 
                                    style = "pin", 
                                    scale = (self.proportions["depth"]*0.1, self.proportions["depth"]*0.1, self.proportions["depth"]*0.1),
                                    offset = (0, 0, 0),  
                                    estimateSize = estimateSize,
                                    color_ = "blue1")
                                    
            #LeftLeg
            self.LeftLeg.createControl(type = "FK", 
                                    style = "pin", 
                                    scale = (self.proportions["depth"]*0.09, self.proportions["depth"]*0.09, self.proportions["depth"]*0.09),
                                    offset = (0, 0, 0),  
                                    estimateSize = estimateSize,
                                    color_ = "blue1")
                                    
            self.LeftLeg.createControl(type = "IK", 
                                    style = "PoleVector", 
                                    scale = (self.proportions["depth"]*0.1, self.proportions["depth"]*0.2, self.proportions["depth"]*0.1),
                                    offset = (0, 0, 0),  
                                    estimateSize = estimateSize,
                                    color_ = "blue2")
            
            #LeftFoot
            self.LeftFoot.createControl(type = "FK", 
                                    style = "pin", 
                                    scale = (self.proportions["depth"]*0.08, self.proportions["depth"]*0.08, self.proportions["depth"]*0.08),
                                    offset = (0, 0, 0),  
                                    estimateSize = estimateSize,
                                    color_ = "blue1")
            
            self.LeftFoot.createControl(type = "IK", 
                                    style = "footBox", 
                                    scale = (self.proportions["depth"]*0.4, self.proportions["depth"]*0.7, self.proportions["depth"]*-0.4),
                                    offset = (0, self.proportions["depth"]*0.1, self.proportions["depth"]*0.1),
                                    rotate = (90, 0, 0),  
                                    partialConstraint = 1,
                                    estimateSize = estimateSize,
                                    color_ = "blue2")
            mayac.move(self.proportions["lowPoint"], "%s.scalePivot" % (self.LeftFoot.IK_CTRL),  "%s.rotatePivot" % (self.LeftFoot.IK_CTRL),  y = True)
    
            #LeftToeBase
            self.LeftToeBase.createControl(type = "FK", 
                                    style = "pin", 
                                    scale = (self.proportions["depth"]*0.07, self.proportions["depth"]*0.07, self.proportions["depth"]*0.07),
                                    offset = (0, 0, 0),  
                                    estimateSize = estimateSize,
                                    color_ = "blue1")
                                    
                                    
            #RightUpLeg
            self.RightUpLeg.createControl(type = "FK", 
                                    style = "pin", 
                                    scale = (self.proportions["depth"]*-0.1, self.proportions["depth"]*0.1, self.proportions["depth"]*0.1),
                                    offset = (0, 0, 0),  
                                    estimateSize = estimateSize,
                                    color_ = "red1")
                                    
            #RightLeg
            self.RightLeg.createControl(type = "FK", 
                                    style = "pin", 
                                    scale = (self.proportions["depth"]*-0.09, self.proportions["depth"]*0.09, self.proportions["depth"]*0.09),
                                    offset = (0, 0, 0),  
                                    estimateSize = estimateSize,
                                    color_ = "red1")
            
            self.RightLeg.createControl(type = "IK", 
                                    style = "PoleVector", 
                                    scale = (self.proportions["depth"]*0.1, self.proportions["depth"]*0.2, self.proportions["depth"]*0.1),
                                    offset = (0, 0, 0),  
                                    estimateSize = estimateSize,
                                    color_ = "red2")
                                    
            #RightFoot
            self.RightFoot.createControl(type = "FK", 
                                    style = "pin", 
                                    scale = (self.proportions["depth"]*-0.08, self.proportions["depth"]*0.08, self.proportions["depth"]*0.08),
                                    offset = (0, 0, 0),  
                                    estimateSize = estimateSize,
                                    color_ = "red1")
            
            self.RightFoot.createControl(type = "IK", 
                                    style = "footBox", 
                                    scale = (self.proportions["depth"]*0.4, self.proportions["depth"]*0.7, self.proportions["depth"]*-0.4),
                                    offset = (0, self.proportions["depth"]*0.1, self.proportions["depth"]*0.1),
                                    rotate = (90, 0, 0),
                                    partialConstraint = 1,  
                                    estimateSize = estimateSize,
                                    color_ = "red2")
            mayac.move(self.proportions["lowPoint"], "%s.scalePivot" % (self.RightFoot.IK_CTRL),  "%s.rotatePivot" % (self.RightFoot.IK_CTRL),  y = True)
    
            #RightToeBase
            self.RightToeBase.createControl(type = "FK", 
                                    style = "pin", 
                                    scale = (self.proportions["depth"]*-0.07, self.proportions["depth"]*0.07, self.proportions["depth"]*0.07),
                                    offset = (0, 0, 0),  
                                    estimateSize = estimateSize,
                                    color_ = "red1")
            
            #fingers
            if self.LeftHandThumb1.Bind_Joint:
                self.LeftHandThumb1.createControl(type = "normal", 
                                    style = "pin1", 
                                    scale = (self.proportions["depth"]*0.02, self.proportions["depth"]*0.02, self.proportions["depth"]*0.02),
                                    offset = (0, 0, 0),  
                                    estimateSize = estimateSize,
                                    flipFingers = self.fingerFlip,
                                    color_ = "blue2")
                self.LeftHandThumb2.createControl(type = "normal", 
                                    style = "pin1", 
                                    scale = (self.proportions["depth"]*0.016, self.proportions["depth"]*0.016, self.proportions["depth"]*0.016),
                                    offset = (0, 0, 0),  
                                    estimateSize = estimateSize,
                                    flipFingers = self.fingerFlip,
                                    color_ = "blue2")
                self.LeftHandThumb3.createControl(type = "normal", 
                                    style = "pin1", 
                                    scale = (self.proportions["depth"]*0.012, self.proportions["depth"]*0.012, self.proportions["depth"]*0.012),
                                    offset = (0, 0, 0),  
                                    estimateSize = estimateSize,
                                    flipFingers = self.fingerFlip,
                                    color_ = "blue2")
            if self.LeftHandIndex1.Bind_Joint:
                self.LeftHandIndex1.createControl(type = "normal", 
                                    style = "pin1", 
                                    scale = (self.proportions["depth"]*0.02, self.proportions["depth"]*0.02, self.proportions["depth"]*0.02),
                                    offset = (0, 0, 0),  
                                    estimateSize = estimateSize,
                                    flipFingers = self.fingerFlip,
                                    color_ = "blue2")
                self.LeftHandIndex2.createControl(type = "normal", 
                                    style = "pin1", 
                                    scale = (self.proportions["depth"]*0.016, self.proportions["depth"]*0.016, self.proportions["depth"]*0.016),
                                    offset = (0, 0, 0),  
                                    estimateSize = estimateSize,
                                    flipFingers = self.fingerFlip,
                                    color_ = "blue2")
                self.LeftHandIndex3.createControl(type = "normal", 
                                    style = "pin1", 
                                    scale = (self.proportions["depth"]*0.012, self.proportions["depth"]*0.012, self.proportions["depth"]*0.012),
                                    offset = (0, 0, 0),  
                                    estimateSize = estimateSize,
                                    flipFingers = self.fingerFlip,
                                    color_ = "blue2")
            if self.LeftHandMiddle1.Bind_Joint:
                self.LeftHandMiddle1.createControl(type = "normal", 
                                    style = "pin1", 
                                    scale = (self.proportions["depth"]*0.02, self.proportions["depth"]*0.02, self.proportions["depth"]*0.02),
                                    offset = (0, 0, 0),  
                                    estimateSize = estimateSize,
                                    flipFingers = self.fingerFlip,
                                    color_ = "blue2")
                self.LeftHandMiddle2.createControl(type = "normal", 
                                    style = "pin1", 
                                    scale = (self.proportions["depth"]*0.016, self.proportions["depth"]*0.016, self.proportions["depth"]*0.016),
                                    offset = (0, 0, 0),  
                                    estimateSize = estimateSize,
                                    flipFingers = self.fingerFlip,
                                    color_ = "blue2")
                self.LeftHandMiddle3.createControl(type = "normal", 
                                    style = "pin1", 
                                    scale = (self.proportions["depth"]*0.012, self.proportions["depth"]*0.012, self.proportions["depth"]*0.012),
                                    offset = (0, 0, 0),  
                                    estimateSize = estimateSize,
                                    flipFingers = self.fingerFlip,
                                    color_ = "blue2")
            if self.LeftHandRing1.Bind_Joint:
                self.LeftHandRing1.createControl(type = "normal", 
                                    style = "pin1", 
                                    scale = (self.proportions["depth"]*0.02, self.proportions["depth"]*0.02, self.proportions["depth"]*0.02),
                                    offset = (0, 0, 0),  
                                    estimateSize = estimateSize,
                                    flipFingers = self.fingerFlip,
                                    color_ = "blue2")
                self.LeftHandRing2.createControl(type = "normal", 
                                    style = "pin1", 
                                    scale = (self.proportions["depth"]*0.016, self.proportions["depth"]*0.016, self.proportions["depth"]*0.016),
                                    offset = (0, 0, 0),  
                                    estimateSize = estimateSize,
                                    flipFingers = self.fingerFlip,
                                    color_ = "blue2")
                self.LeftHandRing3.createControl(type = "normal", 
                                    style = "pin1", 
                                    scale = (self.proportions["depth"]*0.012, self.proportions["depth"]*0.012, self.proportions["depth"]*0.012),
                                    offset = (0, 0, 0),  
                                    estimateSize = estimateSize,
                                    flipFingers = self.fingerFlip,
                                    color_ = "blue2")
            if self.LeftHandPinky1.Bind_Joint:
                self.LeftHandPinky1.createControl(type = "normal", 
                                    style = "pin1", 
                                    scale = (self.proportions["depth"]*0.02, self.proportions["depth"]*0.02, self.proportions["depth"]*0.02),
                                    offset = (0, 0, 0),  
                                    estimateSize = estimateSize,
                                    flipFingers = self.fingerFlip,
                                    color_ = "blue2")
                self.LeftHandPinky2.createControl(type = "normal", 
                                    style = "pin1", 
                                    scale = (self.proportions["depth"]*0.016, self.proportions["depth"]*0.016, self.proportions["depth"]*0.016),
                                    offset = (0, 0, 0),  
                                    estimateSize = estimateSize,
                                    flipFingers = self.fingerFlip,
                                    color_ = "blue2")
                self.LeftHandPinky3.createControl(type = "normal", 
                                    style = "pin1", 
                                    scale = (self.proportions["depth"]*0.012, self.proportions["depth"]*0.012, self.proportions["depth"]*0.012),
                                    offset = (0, 0, 0),  
                                    estimateSize = estimateSize,
                                    flipFingers = self.fingerFlip,
                                    color_ = "blue2")
                
            if self.RightHandThumb1.Bind_Joint:
                self.RightHandThumb1.createControl(type = "normal", 
                                    style = "pin1", 
                                    scale = (self.proportions["depth"]*0.02, self.proportions["depth"]*0.02, self.proportions["depth"]*0.02),
                                    offset = (0, 0, 0),  
                                    estimateSize = estimateSize,
                                    flipFingers = self.fingerFlip,
                                    color_ = "red2")
                self.RightHandThumb2.createControl(type = "normal", 
                                    style = "pin1", 
                                    scale = (self.proportions["depth"]*0.016, self.proportions["depth"]*0.016, self.proportions["depth"]*0.016),
                                    offset = (0, 0, 0),  
                                    estimateSize = estimateSize,
                                    flipFingers = self.fingerFlip,
                                    color_ = "red2")
                self.RightHandThumb3.createControl(type = "normal", 
                                    style = "pin1", 
                                    scale = (self.proportions["depth"]*0.012, self.proportions["depth"]*0.012, self.proportions["depth"]*0.012),
                                    offset = (0, 0, 0),  
                                    estimateSize = estimateSize,
                                    flipFingers = self.fingerFlip,
                                    color_ = "red2")
            if self.RightHandIndex1.Bind_Joint:
                self.RightHandIndex1.createControl(type = "normal", 
                                    style = "pin1", 
                                    scale = (self.proportions["depth"]*0.02, self.proportions["depth"]*0.02, self.proportions["depth"]*0.02),
                                    offset = (0, 0, 0),  
                                    estimateSize = estimateSize,
                                    flipFingers = self.fingerFlip,
                                    color_ = "red2")
                self.RightHandIndex2.createControl(type = "normal", 
                                    style = "pin1", 
                                    scale = (self.proportions["depth"]*0.016, self.proportions["depth"]*0.016, self.proportions["depth"]*0.016),
                                    offset = (0, 0, 0),  
                                    estimateSize = estimateSize,
                                    flipFingers = self.fingerFlip,
                                    color_ = "red2")
                self.RightHandIndex3.createControl(type = "normal", 
                                    style = "pin1", 
                                    scale = (self.proportions["depth"]*0.012, self.proportions["depth"]*0.012, self.proportions["depth"]*0.012),
                                    offset = (0, 0, 0),  
                                    estimateSize = estimateSize,
                                    flipFingers = self.fingerFlip,
                                    color_ = "red2")
            if self.RightHandMiddle1.Bind_Joint:
                self.RightHandMiddle1.createControl(type = "normal", 
                                    style = "pin1", 
                                    scale = (self.proportions["depth"]*0.02, self.proportions["depth"]*0.02, self.proportions["depth"]*0.02),
                                    offset = (0, 0, 0),  
                                    estimateSize = estimateSize,
                                    flipFingers = self.fingerFlip,
                                    color_ = "red2")
                self.RightHandMiddle2.createControl(type = "normal", 
                                    style = "pin1", 
                                    scale = (self.proportions["depth"]*0.016, self.proportions["depth"]*0.016, self.proportions["depth"]*0.016),
                                    offset = (0, 0, 0),  
                                    estimateSize = estimateSize,
                                    flipFingers = self.fingerFlip,
                                    color_ = "red2")
                self.RightHandMiddle3.createControl(type = "normal", 
                                    style = "pin1", 
                                    scale = (self.proportions["depth"]*0.012, self.proportions["depth"]*0.012, self.proportions["depth"]*0.012),
                                    offset = (0, 0, 0),  
                                    estimateSize = estimateSize,
                                    flipFingers = self.fingerFlip,
                                    color_ = "red2")
            if self.RightHandRing1.Bind_Joint:
                self.RightHandRing1.createControl(type = "normal", 
                                    style = "pin1", 
                                    scale = (self.proportions["depth"]*0.02, self.proportions["depth"]*0.02, self.proportions["depth"]*0.02),
                                    offset = (0, 0, 0),  
                                    estimateSize = estimateSize,
                                    flipFingers = self.fingerFlip,
                                    color_ = "red2")
                self.RightHandRing2.createControl(type = "normal", 
                                    style = "pin1", 
                                    scale = (self.proportions["depth"]*0.016, self.proportions["depth"]*0.016, self.proportions["depth"]*0.016),
                                    offset = (0, 0, 0),  
                                    estimateSize = estimateSize,
                                    flipFingers = self.fingerFlip,
                                    color_ = "red2")
                self.RightHandRing3.createControl(type = "normal", 
                                    style = "pin1", 
                                    scale = (self.proportions["depth"]*0.012, self.proportions["depth"]*0.012, self.proportions["depth"]*0.012),
                                    offset = (0, 0, 0),  
                                    estimateSize = estimateSize,
                                    flipFingers = self.fingerFlip,
                                    color_ = "red2")
            if self.RightHandPinky1.Bind_Joint:
                self.RightHandPinky1.createControl(type = "normal", 
                                    style = "pin1", 
                                    scale = (self.proportions["depth"]*0.02, self.proportions["depth"]*0.02, self.proportions["depth"]*0.02),
                                    offset = (0, 0, 0),  
                                    estimateSize = estimateSize,
                                    flipFingers = self.fingerFlip,
                                    color_ = "red2")
                self.RightHandPinky2.createControl(type = "normal", 
                                    style = "pin1", 
                                    scale = (self.proportions["depth"]*0.016, self.proportions["depth"]*0.016, self.proportions["depth"]*0.016),
                                    offset = (0, 0, 0),  
                                    estimateSize = estimateSize,
                                    flipFingers = self.fingerFlip,
                                    color_ = "red2")
                self.RightHandPinky3.createControl(type = "normal", 
                                    style = "pin1", 
                                    scale = (self.proportions["depth"]*0.012, self.proportions["depth"]*0.012, self.proportions["depth"]*0.012),
                                    offset = (0, 0, 0),  
                                    estimateSize = estimateSize,
                                    flipFingers = self.fingerFlip,
                                    color_ = "red2")
                
            #Options
            self.LeftFoot.createControl(type = "options", 
                                    style = "options", 
                                    scale = (self.proportions["depth"]*0.12, self.proportions["depth"]*0.12, self.proportions["depth"]*-0.12),
                                    offset = (0, 0, self.proportions["depth"]*-0.4),  
                                    estimateSize = estimateSize,
                                    partialConstraint = 2,
                                    color_ = "black")
            
            self.RightFoot.createControl(type = "options", 
                                    style = "options", 
                                    scale = (self.proportions["depth"]*0.12, self.proportions["depth"]*0.12, self.proportions["depth"]*-0.12),
                                    offset = (0, 0, self.proportions["depth"]*-0.4),  
                                    estimateSize = estimateSize,
                                    partialConstraint = 2,
                                    color_ = "black")
            
            self.LeftHand.createControl(type = "options", 
                                    style = "options", 
                                    scale = (self.proportions["depth"]*0.12, self.proportions["depth"]*0.12, self.proportions["depth"]*-0.12),
                                    offset = (0, self.proportions["depth"]*0.3, self.proportions["depth"]*-0.3),  
                                    estimateSize = estimateSize,
                                    color_ = "black")
            
            self.RightHand.createControl(type = "options", 
                                    style = "options", 
                                    scale = (self.proportions["depth"]*0.12, self.proportions["depth"]*0.12, self.proportions["depth"]*-0.12),
                                    offset = (0, self.proportions["depth"]*0.3, self.proportions["depth"]*-0.3),  
                                    estimateSize = estimateSize,
                                    color_ = "black")
        
        
        elif self.rigType == "World":     
            #root
            if self.Root.Bind_Joint:
                self.Root.createControl(type = "normal", 
                                    style = "circle", 
                                    scale = (self.proportions["depth"]*0.8, self.proportions["depth"]*0.8, self.proportions["depth"]*0.8), 
                                    offset = (0,0,0), 
                                    estimateSize = estimateSize)
            
                #hips
                self.Hips.createControl(type = "normal", 
                                        style = "hula", 
                                        scale = (self.proportions["depth"]*0.75, self.proportions["depth"]*0.75, self.proportions["depth"]*0.75),
                                        offset = (0,-.01*self.proportions["height"],0), 
                                        estimateSize = estimateSize,
                                        color_ = "yellow")
            else:
                #hips
                self.Hips.createControl(type = "normal", 
                                    style = "circle", 
                                    scale = (self.proportions["depth"]*0.8, self.proportions["depth"]*0.8, self.proportions["depth"]*0.8), 
                                    offset = (0,0,0), 
                                    estimateSize = estimateSize)
            #spine
            self.Spine.createControl(type = "normal", 
                                    style = "circle", 
                                    scale = (self.proportions["depth"]*0.7, self.proportions["depth"]*0.7, self.proportions["depth"]*0.7),
                                    offset = (0,0,0), 
                                    estimateSize = estimateSize,
                                    color_ = "yellow")
            
            #spine1
            self.Spine1.createControl(type = "normal", 
                                    style = "circle", 
                                    scale = (self.proportions["depth"]*0.6, self.proportions["depth"]*0.6, self.proportions["depth"]*0.6),
                                    offset = (0,0,0), 
                                    estimateSize = estimateSize,
                                    color_ = "yellow")
            #spine2
            if self.Spine3.Bind_Joint:
                self.Spine2.createControl(type = "normal", 
                                    style = "circle", 
                                    scale = (self.proportions["depth"]*0.6, self.proportions["depth"]*0.6, self.proportions["depth"]*0.6),
                                    offset = (0,0,0), 
                                    estimateSize = estimateSize,
                                    color_ = "yellow")
                self.Spine3.createControl(type = "normal", 
                                    style = "box", 
                                    scale = (self.proportions["depth"]*0.7, self.proportions["depth"]*0.7, (self.proportions["depth"])*0.8), 
                                    offset = (0,self.proportions["depth"]*.2,0), 
                                    estimateSize = estimateSize,
                                    color_ = "yellow")
            else:
                self.Spine2.createControl(type = "normal", 
                                    style = "box", 
                                    scale = (self.proportions["depth"]*0.7, self.proportions["depth"]*0.7, (self.proportions["depth"])*0.8), 
                                    offset = (0,self.proportions["depth"]*.2,0), 
                                    estimateSize = estimateSize,
                                    color_ = "yellow")
                                    
            #neck
            self.Neck.createControl(type = "normal", 
                                    style = "pin1", 
                                    scale = (self.proportions["depth"]*-0.18, self.proportions["depth"]*0.18, self.proportions["depth"]*0.18),
                                    offset = (self.proportions["height"]*0.033, 0, self.proportions["height"]*-0.04),  
                                    estimateSize = estimateSize,
                                    color_ = "yellow")
            if self.Neck1.Bind_Joint:
                self.Neck1.createControl(type = "normal", 
                                    style = "pin1", 
                                    scale = (self.proportions["depth"]*-0.18, self.proportions["depth"]*0.18, self.proportions["depth"]*0.18),
                                    offset = (self.proportions["height"]*0.033, 0, self.proportions["height"]*-0.04),  
                                    estimateSize = estimateSize,
                                    color_ = "yellow")
                                    
            #head
            self.Head.createControl(type = "normal", 
                                    style = "box", 
                                    scale = (self.proportions["depth"]*0.4, self.proportions["height"]*0.13, (self.proportions["depth"])*0.5), 
                                    offset = (0,self.proportions["height"]*.06,self.proportions["depth"]*0.1), 
                                    estimateSize = estimateSize,
                                    color_ = "yellow")
                               
            #LeftShoulder
            self.LeftShoulder.createControl(type = "normal", 
                                    style = "circleWrapped", 
                                    scale = (self.proportions["depth"]*0.4, self.proportions["depth"]*0.15, self.proportions["depth"]*0.15), 
                                    offset = (self.proportions["height"]*0.04, self.proportions["depth"]*0.3, 0), 
                                    rotate = (0, -90, 90), 
                                    estimateSize = estimateSize,
                                    color_ = "blue1")
                                    
            #RightShoulder
            self.RightShoulder.createControl(type = "normal", 
                                    style = "circleWrapped", 
                                    scale = (self.proportions["depth"]*0.4, self.proportions["depth"]*0.15, self.proportions["depth"]*0.15), 
                                    offset = (self.proportions["height"]*-0.04, self.proportions["depth"]*0.3, 0), 
                                    rotate = (0, -90, 90),  
                                    estimateSize = estimateSize,
                                    color_ = "red1")
            
            #LeftArm
            self.LeftArm.createControl(type = "FK", 
                                    style = "circle", 
                                    scale = (self.proportions["depth"]*0.25, self.proportions["depth"]*0.25, self.proportions["depth"]*0.25),
                                    offset = (0, 0, 0),
                                    rotate = (0, 90, 0), 
                                    rigType = "World",
                                    estimateSize = estimateSize,
                                    color_ = "blue1")
            
            #RightArm
            self.RightArm.createControl(type = "FK", 
                                    style = "circle", 
                                    scale = (self.proportions["depth"]*0.25, self.proportions["depth"]*0.25, self.proportions["depth"]*0.25),
                                    offset = (0, 0, 0),
                                    rotate = (0, 90, 0), 
                                    rigType = "World",
                                    estimateSize = estimateSize,
                                    color_ = "red1")
            
            #LeftForeArm
            self.LeftForeArm.createControl(type = "FK", 
                                    style = "circle", 
                                    scale = (self.proportions["depth"]*0.25, self.proportions["depth"]*0.25, self.proportions["depth"]*0.25),
                                    offset = (0, 0, 0),
                                    rotate = (0, 90, 0),  
                                    rigType = "World",
                                    estimateSize = estimateSize,
                                    color_ = "blue1")
            
            self.LeftForeArm.createControl(type = "IK", 
                                    style = "PoleVector", 
                                    scale = (self.proportions["depth"]*0.1, self.proportions["depth"]*0.2, self.proportions["depth"]*0.1),
                                    offset = (0, 0, 0),
                                    rotate = (0, 180, 0),  
                                    estimateSize = estimateSize,
                                    color_ = "blue2")
            
            #RightForeArm
            self.RightForeArm.createControl(type = "FK", 
                                    style = "circle", 
                                    scale = (self.proportions["depth"]*0.25, self.proportions["depth"]*0.25, self.proportions["depth"]*0.25),
                                    offset = (0, 0, 0),
                                    rotate = (0, 90, 0), 
                                    rigType = "World", 
                                    estimateSize = estimateSize,
                                    color_ = "red1")
            
            self.RightForeArm.createControl(type = "IK", 
                                    style = "PoleVector", 
                                    scale = (self.proportions["depth"]*0.1, self.proportions["depth"]*0.2, self.proportions["depth"]*0.1),
                                    offset = (0, 0, 0),  
                                    rotate = (0, 180, 0),
                                    estimateSize = estimateSize,
                                    color_ = "red2")
            
            #LeftHand
            self.LeftHand.createControl(type = "FK", 
                                    style = "circle", 
                                    scale = (self.proportions["depth"]*0.2, self.proportions["depth"]*0.2, self.proportions["depth"]*0.2),
                                    offset = (0, 0, 0), 
                                    rotate = (0, 90, 0), 
                                    rigType = "World",
                                    estimateSize = estimateSize,
                                    color_ = "blue1")
            
            self.LeftHand.createControl(type = "IK", 
                                    style = "box", 
                                    scale = (self.proportions["depth"]*0.2, self.proportions["depth"]*0.3, self.proportions["depth"]*0.2),
                                    offset = (self.proportions["depth"]*0.3, 0, 0),  
                                    rotate = (0, -90, -90),
                                    estimateSize = estimateSize,
                                    color_ = "blue2")
            
            #RightHand
            self.RightHand.createControl(type = "FK", 
                                    style = "circle", 
                                    scale = (self.proportions["depth"]*0.2, self.proportions["depth"]*0.2, self.proportions["depth"]*0.2),
                                    offset = (0, 0, 0),
                                    rotate = (0, 90, 0),
                                    rigType = "World",
                                    estimateSize = estimateSize,
                                    color_ = "red1")
            
            self.RightHand.createControl(type = "IK", 
                                    style = "box", 
                                    scale = (self.proportions["depth"]*0.2, self.proportions["depth"]*0.3, self.proportions["depth"]*0.2),
                                    offset = (self.proportions["depth"]*-0.3, 0, 0), 
                                    rotate = (0, 90, 90), 
                                    estimateSize = estimateSize,
                                    color_ = "red2")
                                    
                                    
            #LeftUpLeg
            self.LeftUpLeg.createControl(type = "FK", 
                                    style = "pin", 
                                    scale = (self.proportions["depth"]*0.1, self.proportions["depth"]*0.1, self.proportions["depth"]*0.1),
                                    offset = (0, 0, 0),
                                    rotate = (0, 180, 0), 
                                    estimateSize = estimateSize,
                                    color_ = "blue1")
                                    
            #LeftLeg
            self.LeftLeg.createControl(type = "FK", 
                                    style = "pin", 
                                    scale = (self.proportions["depth"]*0.09, self.proportions["depth"]*0.09, self.proportions["depth"]*0.09),
                                    offset = (0, 0, 0),
                                    rotate = (0, 180, 0),
                                    estimateSize = estimateSize,
                                    color_ = "blue1")
                                    
            self.LeftLeg.createControl(type = "IK", 
                                    style = "PoleVector", 
                                    scale = (self.proportions["depth"]*0.1, self.proportions["depth"]*0.2, self.proportions["depth"]*0.1),
                                    offset = (0, 0, 0), 
                                    estimateSize = estimateSize,
                                    color_ = "blue2")
            
            #LeftFoot
            self.LeftFoot.createControl(type = "FK", 
                                    style = "pin", 
                                    scale = (self.proportions["depth"]*0.08, self.proportions["depth"]*0.08, self.proportions["depth"]*0.08),
                                    offset = (0, 0, 0),
                                    rotate = (0, 180, 0),  
                                    estimateSize = estimateSize,
                                    color_ = "blue1")
            
            self.LeftFoot.createControl(type = "IK", 
                                    style = "footBox", 
                                    scale = (self.proportions["depth"]*0.4, self.proportions["depth"]*0.7, self.proportions["depth"]*-0.4),
                                    offset = (0, self.proportions["depth"]*0.1, self.proportions["depth"]*0.1),
                                    rotate = (90, 0, 0),  
                                    partialConstraint = 1,
                                    estimateSize = estimateSize,
                                    color_ = "blue2")
            mayac.move(self.proportions["lowPoint"], "%s.scalePivot" % (self.LeftFoot.IK_CTRL),  "%s.rotatePivot" % (self.LeftFoot.IK_CTRL),  y = True)
    
            #LeftToeBase
            self.LeftToeBase.createControl(type = "FK", 
                                    style = "pin", 
                                    scale = (self.proportions["depth"]*0.07, self.proportions["depth"]*0.07, self.proportions["depth"]*0.07),
                                    offset = (0, 0, 0),
                                    rotate = (0, 180, 0),   
                                    estimateSize = estimateSize,
                                    color_ = "blue1")
                                    
                                    
            #RightUpLeg
            self.RightUpLeg.createControl(type = "FK", 
                                    style = "pin", 
                                    scale = (self.proportions["depth"]*-0.1, self.proportions["depth"]*0.1, self.proportions["depth"]*0.1),
                                    offset = (0, 0, 0),
                                    rotate = (0, 180, 0), 
                                    estimateSize = estimateSize,
                                    color_ = "red1")
                                    
            #RightLeg
            self.RightLeg.createControl(type = "FK", 
                                    style = "pin", 
                                    scale = (self.proportions["depth"]*-0.09, self.proportions["depth"]*0.09, self.proportions["depth"]*0.09),
                                    offset = (0, 0, 0),
                                    rotate = (0, 180, 0),  
                                    estimateSize = estimateSize,
                                    color_ = "red1")
            
            self.RightLeg.createControl(type = "IK", 
                                    style = "PoleVector", 
                                    scale = (self.proportions["depth"]*0.1, self.proportions["depth"]*0.2, self.proportions["depth"]*0.1),
                                    offset = (0, 0, 0),  
                                    estimateSize = estimateSize,
                                    color_ = "red2")
                                    
            #RightFoot
            self.RightFoot.createControl(type = "FK", 
                                    style = "pin", 
                                    scale = (self.proportions["depth"]*-0.08, self.proportions["depth"]*0.08, self.proportions["depth"]*0.08),
                                    offset = (0, 0, 0),  
                                    rotate = (0, 180, 0), 
                                    estimateSize = estimateSize,
                                    color_ = "red1")
            
            self.RightFoot.createControl(type = "IK", 
                                    style = "footBox", 
                                    scale = (self.proportions["depth"]*0.4, self.proportions["depth"]*0.7, self.proportions["depth"]*-0.4),
                                    offset = (0, self.proportions["depth"]*0.1, self.proportions["depth"]*0.1),
                                    rotate = (90, 0, 0),
                                    partialConstraint = 1,  
                                    estimateSize = estimateSize,
                                    color_ = "red2")
            mayac.move(self.proportions["lowPoint"], "%s.scalePivot" % (self.RightFoot.IK_CTRL),  "%s.rotatePivot" % (self.RightFoot.IK_CTRL),  y = True)
    
            #RightToeBase
            self.RightToeBase.createControl(type = "FK", 
                                    style = "pin", 
                                    scale = (self.proportions["depth"]*-0.07, self.proportions["depth"]*0.07, self.proportions["depth"]*0.07),
                                    offset = (0, 0, 0),
                                    rotate = (0, 180, 0), 
                                    estimateSize = estimateSize,
                                    color_ = "red1")
            
            #fingers
            if self.LeftHandThumb1.Bind_Joint:
                self.LeftHandThumb1.createControl(type = "normal", 
                                    style = "pin1", 
                                    scale = (self.proportions["depth"]*0.02, self.proportions["depth"]*0.02, self.proportions["depth"]*0.02),
                                    offset = (0, 0, 0),
                                    rotate = (0, 90, 0), 
                                    estimateSize = estimateSize,
                                    color_ = "blue2")
                self.LeftHandThumb2.createControl(type = "normal", 
                                    style = "pin1", 
                                    scale = (self.proportions["depth"]*0.016, self.proportions["depth"]*0.016, self.proportions["depth"]*0.016),
                                    offset = (0, 0, 0),
                                    rotate = (0, 90, 0),  
                                    estimateSize = estimateSize,
                                    color_ = "blue2")
                self.LeftHandThumb3.createControl(type = "normal", 
                                    style = "pin1", 
                                    scale = (self.proportions["depth"]*0.012, self.proportions["depth"]*0.012, self.proportions["depth"]*0.012),
                                    offset = (0, 0, 0),
                                    rotate = (0, 90, 0),  
                                    estimateSize = estimateSize,
                                    color_ = "blue2")
            if self.LeftHandIndex1.Bind_Joint:
                self.LeftHandIndex1.createControl(type = "normal", 
                                    style = "pin1", 
                                    scale = (self.proportions["depth"]*0.02, self.proportions["depth"]*0.02, self.proportions["depth"]*0.02),
                                    offset = (0, 0, 0), 
                                    rotate = (0, 90, 0),  
                                    estimateSize = estimateSize,
                                    color_ = "blue2")
                self.LeftHandIndex2.createControl(type = "normal", 
                                    style = "pin1", 
                                    scale = (self.proportions["depth"]*0.016, self.proportions["depth"]*0.016, self.proportions["depth"]*0.016),
                                    offset = (0, 0, 0),  
                                    rotate = (0, 90, 0), 
                                    estimateSize = estimateSize,
                                    color_ = "blue2")
                self.LeftHandIndex3.createControl(type = "normal", 
                                    style = "pin1", 
                                    scale = (self.proportions["depth"]*0.012, self.proportions["depth"]*0.012, self.proportions["depth"]*0.012),
                                    offset = (0, 0, 0),  
                                    rotate = (0, 90, 0), 
                                    estimateSize = estimateSize,
                                    color_ = "blue2")
            if self.LeftHandMiddle1.Bind_Joint:
                self.LeftHandMiddle1.createControl(type = "normal", 
                                    style = "pin1", 
                                    scale = (self.proportions["depth"]*0.02, self.proportions["depth"]*0.02, self.proportions["depth"]*0.02),
                                    offset = (0, 0, 0),  
                                    rotate = (0, 90, 0), 
                                    estimateSize = estimateSize,
                                    color_ = "blue2")
                self.LeftHandMiddle2.createControl(type = "normal", 
                                    style = "pin1", 
                                    scale = (self.proportions["depth"]*0.016, self.proportions["depth"]*0.016, self.proportions["depth"]*0.016),
                                    offset = (0, 0, 0),  
                                    rotate = (0, 90, 0), 
                                    estimateSize = estimateSize,
                                    color_ = "blue2")
                self.LeftHandMiddle3.createControl(type = "normal", 
                                    style = "pin1", 
                                    scale = (self.proportions["depth"]*0.012, self.proportions["depth"]*0.012, self.proportions["depth"]*0.012),
                                    offset = (0, 0, 0), 
                                    rotate = (0, 90, 0),  
                                    estimateSize = estimateSize,
                                    color_ = "blue2")
            if self.LeftHandRing1.Bind_Joint:
                self.LeftHandRing1.createControl(type = "normal", 
                                    style = "pin1", 
                                    scale = (self.proportions["depth"]*0.02, self.proportions["depth"]*0.02, self.proportions["depth"]*0.02),
                                    offset = (0, 0, 0),  
                                    rotate = (0, 90, 0), 
                                    estimateSize = estimateSize,
                                    color_ = "blue2")
                self.LeftHandRing2.createControl(type = "normal", 
                                    style = "pin1", 
                                    scale = (self.proportions["depth"]*0.016, self.proportions["depth"]*0.016, self.proportions["depth"]*0.016),
                                    offset = (0, 0, 0),  
                                    rotate = (0, 90, 0), 
                                    estimateSize = estimateSize,
                                    color_ = "blue2")
                self.LeftHandRing3.createControl(type = "normal", 
                                    style = "pin1", 
                                    scale = (self.proportions["depth"]*0.012, self.proportions["depth"]*0.012, self.proportions["depth"]*0.012),
                                    offset = (0, 0, 0),  
                                    rotate = (0, 90, 0), 
                                    estimateSize = estimateSize,
                                    color_ = "blue2")
            if self.LeftHandPinky1.Bind_Joint:
                self.LeftHandPinky1.createControl(type = "normal", 
                                    style = "pin1", 
                                    scale = (self.proportions["depth"]*0.02, self.proportions["depth"]*0.02, self.proportions["depth"]*0.02),
                                    offset = (0, 0, 0), 
                                    rotate = (0, 90, 0),  
                                    estimateSize = estimateSize,
                                    color_ = "blue2")
                self.LeftHandPinky2.createControl(type = "normal", 
                                    style = "pin1", 
                                    scale = (self.proportions["depth"]*0.016, self.proportions["depth"]*0.016, self.proportions["depth"]*0.016),
                                    offset = (0, 0, 0), 
                                    rotate = (0, 90, 0),  
                                    estimateSize = estimateSize,
                                    color_ = "blue2")
                self.LeftHandPinky3.createControl(type = "normal", 
                                    style = "pin1", 
                                    scale = (self.proportions["depth"]*0.012, self.proportions["depth"]*0.012, self.proportions["depth"]*0.012),
                                    offset = (0, 0, 0),  
                                    rotate = (0, 90, 0), 
                                    estimateSize = estimateSize,
                                    color_ = "blue2")
                
            if self.RightHandThumb1.Bind_Joint:
                self.RightHandThumb1.createControl(type = "normal", 
                                    style = "pin1", 
                                    scale = (self.proportions["depth"]*0.02, self.proportions["depth"]*0.02, self.proportions["depth"]*0.02),
                                    offset = (0, 0, 0), 
                                    rotate = (0, 90, 0),  
                                    estimateSize = estimateSize,
                                    color_ = "red2")
                self.RightHandThumb2.createControl(type = "normal", 
                                    style = "pin1", 
                                    scale = (self.proportions["depth"]*0.016, self.proportions["depth"]*0.016, self.proportions["depth"]*0.016),
                                    offset = (0, 0, 0),  
                                    rotate = (0, 90, 0), 
                                    estimateSize = estimateSize,
                                    color_ = "red2")
                self.RightHandThumb3.createControl(type = "normal", 
                                    style = "pin1", 
                                    scale = (self.proportions["depth"]*0.012, self.proportions["depth"]*0.012, self.proportions["depth"]*0.012),
                                    offset = (0, 0, 0),  
                                    rotate = (0, 90, 0), 
                                    estimateSize = estimateSize,
                                    color_ = "red2")
            if self.RightHandIndex1.Bind_Joint:
                self.RightHandIndex1.createControl(type = "normal", 
                                    style = "pin1", 
                                    scale = (self.proportions["depth"]*0.02, self.proportions["depth"]*0.02, self.proportions["depth"]*0.02),
                                    offset = (0, 0, 0), 
                                    rotate = (0, 90, 0),  
                                    estimateSize = estimateSize,
                                    color_ = "red2")
                self.RightHandIndex2.createControl(type = "normal", 
                                    style = "pin1", 
                                    scale = (self.proportions["depth"]*0.016, self.proportions["depth"]*0.016, self.proportions["depth"]*0.016),
                                    offset = (0, 0, 0),  
                                    rotate = (0, 90, 0), 
                                    estimateSize = estimateSize,
                                    color_ = "red2")
                self.RightHandIndex3.createControl(type = "normal", 
                                    style = "pin1", 
                                    scale = (self.proportions["depth"]*0.012, self.proportions["depth"]*0.012, self.proportions["depth"]*0.012),
                                    offset = (0, 0, 0), 
                                    rotate = (0, 90, 0),  
                                    estimateSize = estimateSize,
                                    color_ = "red2")
            if self.RightHandMiddle1.Bind_Joint:
                self.RightHandMiddle1.createControl(type = "normal", 
                                    style = "pin1", 
                                    scale = (self.proportions["depth"]*0.02, self.proportions["depth"]*0.02, self.proportions["depth"]*0.02),
                                    offset = (0, 0, 0),  
                                    rotate = (0, 90, 0), 
                                    estimateSize = estimateSize,
                                    color_ = "red2")
                self.RightHandMiddle2.createControl(type = "normal", 
                                    style = "pin1", 
                                    scale = (self.proportions["depth"]*0.016, self.proportions["depth"]*0.016, self.proportions["depth"]*0.016),
                                    offset = (0, 0, 0), 
                                    rotate = (0, 90, 0),  
                                    estimateSize = estimateSize,
                                    color_ = "red2")
                self.RightHandMiddle3.createControl(type = "normal", 
                                    style = "pin1", 
                                    scale = (self.proportions["depth"]*0.012, self.proportions["depth"]*0.012, self.proportions["depth"]*0.012),
                                    offset = (0, 0, 0),  
                                    rotate = (0, 90, 0), 
                                    estimateSize = estimateSize,
                                    color_ = "red2")
            if self.RightHandRing1.Bind_Joint:
                self.RightHandRing1.createControl(type = "normal", 
                                    style = "pin1", 
                                    scale = (self.proportions["depth"]*0.02, self.proportions["depth"]*0.02, self.proportions["depth"]*0.02),
                                    offset = (0, 0, 0),  
                                    rotate = (0, 90, 0), 
                                    estimateSize = estimateSize,
                                    color_ = "red2")
                self.RightHandRing2.createControl(type = "normal", 
                                    style = "pin1", 
                                    scale = (self.proportions["depth"]*0.016, self.proportions["depth"]*0.016, self.proportions["depth"]*0.016),
                                    offset = (0, 0, 0),  
                                    rotate = (0, 90, 0), 
                                    estimateSize = estimateSize,
                                    color_ = "red2")
                self.RightHandRing3.createControl(type = "normal", 
                                    style = "pin1", 
                                    scale = (self.proportions["depth"]*0.012, self.proportions["depth"]*0.012, self.proportions["depth"]*0.012),
                                    offset = (0, 0, 0),  
                                    rotate = (0, 90, 0), 
                                    estimateSize = estimateSize,
                                    color_ = "red2")
            if self.RightHandPinky1.Bind_Joint:
                self.RightHandPinky1.createControl(type = "normal", 
                                    style = "pin1", 
                                    scale = (self.proportions["depth"]*0.02, self.proportions["depth"]*0.02, self.proportions["depth"]*0.02),
                                    offset = (0, 0, 0),  
                                    rotate = (0, 90, 0), 
                                    estimateSize = estimateSize,
                                    color_ = "red2")
                self.RightHandPinky2.createControl(type = "normal", 
                                    style = "pin1", 
                                    scale = (self.proportions["depth"]*0.016, self.proportions["depth"]*0.016, self.proportions["depth"]*0.016),
                                    offset = (0, 0, 0),  
                                    rotate = (0, 90, 0), 
                                    estimateSize = estimateSize,
                                    color_ = "red2")
                self.RightHandPinky3.createControl(type = "normal", 
                                    style = "pin1", 
                                    scale = (self.proportions["depth"]*0.012, self.proportions["depth"]*0.012, self.proportions["depth"]*0.012),
                                    offset = (0, 0, 0),  
                                    rotate = (0, 90, 0), 
                                    estimateSize = estimateSize,
                                    color_ = "red2")
        
            #Options
            self.LeftFoot.createControl(type = "options", 
                                    style = "options", 
                                    scale = (self.proportions["depth"]*0.12, self.proportions["depth"]*0.12, self.proportions["depth"]*-0.12),
                                    offset = (0, 0, self.proportions["depth"]*-0.4),  
                                    estimateSize = estimateSize,
                                    partialConstraint = 2,
                                    color_ = "black")
            
            self.RightFoot.createControl(type = "options", 
                                    style = "options", 
                                    scale = (self.proportions["depth"]*0.12, self.proportions["depth"]*0.12, self.proportions["depth"]*-0.12),
                                    offset = (0, 0, self.proportions["depth"]*-0.4),  
                                    estimateSize = estimateSize,
                                    partialConstraint = 2,
                                    color_ = "black")
            
            self.LeftHand.createControl(type = "options", 
                                    style = "options", 
                                    scale = (self.proportions["depth"]*0.12, self.proportions["depth"]*0.12, self.proportions["depth"]*-0.12),
                                    offset = (self.proportions["depth"]*0.3, self.proportions["depth"]*0.3, 0),  
                                    rotate = (-90, 0, -90),  
                                    estimateSize = estimateSize,
                                    color_ = "black")
            
            self.RightHand.createControl(type = "options", 
                                    style = "options", 
                                    scale = (self.proportions["depth"]*0.12, self.proportions["depth"]*0.12, self.proportions["depth"]*-0.12),
                                    offset = (self.proportions["depth"]*-0.3, self.proportions["depth"]*0.3, 0),  
                                    rotate = (-90, 0, -90), 
                                    estimateSize = estimateSize,
                                    color_ = "black")
                                
                
                
    def hookUpControls(self):
        #Groupings
        print ('Grouping')
        self.Character_GRP = mayac.group(em = True, name = "Character")
        DJB_movePivotToObject(self.Character_GRP, self.global_CTRL)
        self.CTRL_GRP = mayac.group(em = True, name = "CTRL_GRP")
        DJB_movePivotToObject(self.CTRL_GRP, self.global_CTRL)
        mayac.parent(self.global_CTRL, self.CTRL_GRP)
        mayac.parent(self.CTRL_GRP, self.Character_GRP)
        self.Joint_GRP = mayac.group(em = True, name = "Joint_GRP")
        DJB_movePivotToObject(self.Joint_GRP, self.global_CTRL)
        mayac.parent(self.Joint_GRP, self.Character_GRP)
        self.AnimData_Joint_GRP = mayac.group(em = True, name = "AnimData_Joint_GRP")
        DJB_movePivotToObject(self.AnimData_Joint_GRP, self.global_CTRL)
        mayac.parent(self.AnimData_Joint_GRP, self.Joint_GRP)
        if self.hulaOption:
            mayac.parent(self.Root.AnimData_Joint, self.AnimData_Joint_GRP)
        else:
            mayac.parent(self.Hips.AnimData_Joint, self.AnimData_Joint_GRP)
        self.Bind_Joint_GRP = mayac.group(em = True, name = "Bind_Joint_GRP")
        DJB_movePivotToObject(self.Bind_Joint_GRP, self.global_CTRL)
        mayac.parent(self.Bind_Joint_GRP, self.Joint_GRP)
        if self.hulaOption:
            mayac.parent(self.Root.Bind_Joint, self.Bind_Joint_GRP)
        else:
            mayac.parent(self.Hips.Bind_Joint, self.Bind_Joint_GRP)
        self.Mesh_GRP = mayac.group(em = True, name = "Mesh_GRP")
        DJB_movePivotToObject(self.Mesh_GRP, self.global_CTRL)
        tempTransList =[]
        for geo in self.mesh:
            transform = mayac.listRelatives(geo, parent = True)
            if mayac.objectType(transform) == "transform" and transform not in tempTransList:
                mayac.parent(transform, self.Mesh_GRP)
                DJB_LockNHide(transform[0])
                tempTransList.append(transform)
        mayac.parent(self.Mesh_GRP, self.Character_GRP)

        #get rid of any limitations
        print('get rid of any limitations')
        for bodyPart in self.bodyParts:
            if bodyPart.Bind_Joint:
                mayac.transformLimits(bodyPart.Bind_Joint, rm = True)
        
        #create FK and IK Joints
        print ("create FK and IK Joints")
        self.LeftArm.duplicateJoint("FK", parent_ = "Bind_Joint")
        self.LeftForeArm.duplicateJoint("FK")
        self.LeftHand.duplicateJoint("FK")
        self.RightArm.duplicateJoint("FK", parent_ = "Bind_Joint")
        self.RightForeArm.duplicateJoint("FK")
        self.RightHand.duplicateJoint("FK")
        self.LeftUpLeg.duplicateJoint("FK", parent_ = "Bind_Joint")
        self.LeftLeg.duplicateJoint("FK")
        self.LeftFoot.duplicateJoint("FK")
        self.LeftToeBase.duplicateJoint("FK")
        self.LeftToe_End.duplicateJoint("FK")
        self.RightUpLeg.duplicateJoint("FK", parent_ = "Bind_Joint")
        self.RightLeg.duplicateJoint("FK")
        self.RightFoot.duplicateJoint("FK")
        self.RightToeBase.duplicateJoint("FK")
        self.RightToe_End.duplicateJoint("FK")
        
        self.LeftArm.duplicateJoint("IK", parent_ = "Bind_Joint")
        self.LeftForeArm.duplicateJoint("IK")
        self.LeftHand.duplicateJoint("IK")
        self.RightArm.duplicateJoint("IK", parent_ = "Bind_Joint")
        self.RightForeArm.duplicateJoint("IK")
        self.RightHand.duplicateJoint("IK")
        self.LeftUpLeg.duplicateJoint("IK", parent_ = "Bind_Joint")
        self.LeftLeg.duplicateJoint("IK")
        self.LeftFoot.duplicateJoint("IK")
        self.LeftToeBase.duplicateJoint("IK")
        self.LeftToe_End.duplicateJoint("IK")
        self.RightUpLeg.duplicateJoint("IK", parent_ = "Bind_Joint")
        self.RightLeg.duplicateJoint("IK")
        self.RightFoot.duplicateJoint("IK")
        self.RightToeBase.duplicateJoint("IK")
        self.RightToe_End.duplicateJoint("IK")
        
        #finalize CTRLs
        print ('finalize CTRLs')
        for bodyPart in self.bodyParts:
            bodyPart.finalizeCTRLs()
            
        #Left Arm IK BakingLOC Positions
        print('#Left Arm IK BakingLOC Positions')
        selfPOS = mayac.xform(self.LeftForeArm.Bind_Joint, query = True, absolute = True, worldSpace = True, translation = True)
        parentPOS = mayac.xform(self.LeftForeArm.parent.Bind_Joint, query = True, absolute = True, worldSpace = True, translation = True)
        tempDistance = math.sqrt((selfPOS[0]-parentPOS[0])*(selfPOS[0]-parentPOS[0]) + (selfPOS[1]-parentPOS[1])*(selfPOS[1]-parentPOS[1]) + (selfPOS[2]-parentPOS[2])*(selfPOS[2]-parentPOS[2]))
        if self.rigType == "AutoRig":
            mayac.setAttr("%s.translateX" % (self.LeftForeArm.IK_BakingLOC), tempDistance / 2)
        elif self.rigType == "World":  
            mayac.setAttr("%s.translateZ" % (self.LeftForeArm.IK_BakingLOC), tempDistance / -2)
            
        #Right Arm IK BakingLOC Positions
        print("#Right Arm IK BakingLOC Positions")
        selfPOS = mayac.xform(self.RightForeArm.Bind_Joint, query = True, absolute = True, worldSpace = True, translation = True)
        parentPOS = mayac.xform(self.RightForeArm.parent.Bind_Joint, query = True, absolute = True, worldSpace = True, translation = True)
        tempDistance = math.sqrt((selfPOS[0]-parentPOS[0])*(selfPOS[0]-parentPOS[0]) + (selfPOS[1]-parentPOS[1])*(selfPOS[1]-parentPOS[1]) + (selfPOS[2]-parentPOS[2])*(selfPOS[2]-parentPOS[2]))
        if self.rigType == "AutoRig":
            mayac.setAttr("%s.translateX" % (self.RightForeArm.IK_BakingLOC), tempDistance / -2)
        elif self.rigType == "World":  
            mayac.setAttr("%s.translateZ" % (self.RightForeArm.IK_BakingLOC), tempDistance / -2)
            
        #more groupings
        print('#more groupings')
        self.LeftHand_CTRLs_GRP = mayac.group(em = True, name = "LeftHand_CTRLs_GRP")
        self.RightHand_CTRLs_GRP = mayac.group(em = True, name = "RightHand_CTRLs_GRP")
        DJB_movePivotToObject(self.LeftHand_CTRLs_GRP, self.LeftHand.Bind_Joint)
        DJB_movePivotToObject(self.RightHand_CTRLs_GRP, self.RightHand.Bind_Joint)
        #set rotation orders
        print('#set rotation orders')
        mayac.setAttr("%s.rotateOrder" % (self.LeftHand_CTRLs_GRP), self.LeftHand.rotOrder)
        mayac.setAttr("%s.rotateOrder" % (self.RightHand_CTRLs_GRP), self.RightHand.rotOrder)

        mayac.parent(self.LeftHand_CTRLs_GRP, self.RightHand_CTRLs_GRP, self.global_CTRL)
        if self.LeftHandIndex1.Bind_Joint:
            mayac.parent(self.LeftHandIndex1.FK_CTRL_POS_GRP, self.LeftHand_CTRLs_GRP)
        if self.LeftHandThumb1.Bind_Joint:
            mayac.parent(self.LeftHandThumb1.FK_CTRL_POS_GRP, self.LeftHand_CTRLs_GRP)
        if self.LeftHandMiddle1.Bind_Joint:
            mayac.parent(self.LeftHandMiddle1.FK_CTRL_POS_GRP, self.LeftHand_CTRLs_GRP)
        if self.LeftHandRing1.Bind_Joint:
            mayac.parent(self.LeftHandRing1.FK_CTRL_POS_GRP, self.LeftHand_CTRLs_GRP)
        if self.LeftHandPinky1.Bind_Joint:
            mayac.parent(self.LeftHandPinky1.FK_CTRL_POS_GRP, self.LeftHand_CTRLs_GRP)
        if self.RightHandIndex1.Bind_Joint:
            mayac.parent(self.RightHandIndex1.FK_CTRL_POS_GRP, self.RightHand_CTRLs_GRP)    
        if self.RightHandThumb1.Bind_Joint:
            mayac.parent(self.RightHandThumb1.FK_CTRL_POS_GRP, self.RightHand_CTRLs_GRP)
        if self.RightHandMiddle1.Bind_Joint:
            mayac.parent(self.RightHandMiddle1.FK_CTRL_POS_GRP, self.RightHand_CTRLs_GRP)
        if self.RightHandRing1.Bind_Joint:
            mayac.parent(self.RightHandRing1.FK_CTRL_POS_GRP, self.RightHand_CTRLs_GRP)
        if self.RightHandPinky1.Bind_Joint:
            mayac.parent(self.RightHandPinky1.FK_CTRL_POS_GRP, self.RightHand_CTRLs_GRP)

        mayac.parentConstraint(self.LeftHand.Bind_Joint, self.LeftHand_CTRLs_GRP, name = "%s_Constraint" %(self.LeftHand_CTRLs_GRP))
        mayac.parentConstraint(self.RightHand.Bind_Joint, self.RightHand_CTRLs_GRP, name = "%s_Constraint" %(self.RightHand_CTRLs_GRP))
        DJB_LockNHide(self.LeftHand_CTRLs_GRP)
        DJB_LockNHide(self.RightHand_CTRLs_GRP)
        
        mayac.parent(self.LeftFoot.Options_CTRL, self.RightFoot.Options_CTRL, self.LeftHand.Options_CTRL, self.RightHand.Options_CTRL, self.global_CTRL)
        if self.hulaOption:
            mayac.parent(self.Root.FK_CTRL_POS_GRP, self.global_CTRL)
        else:
            mayac.parent(self.Hips.FK_CTRL_POS_GRP, self.global_CTRL)
        mayac.parent(self.LeftForeArm.IK_CTRL_parent_POS_GRP, self.global_CTRL)
        mayac.parent(self.LeftHand.IK_CTRL_grandparent_POS_GRP, self.global_CTRL)
        mayac.parent(self.RightForeArm.IK_CTRL_parent_POS_GRP, self.global_CTRL)
        mayac.parent(self.RightHand.IK_CTRL_grandparent_POS_GRP, self.global_CTRL)
        mayac.parent(self.LeftLeg.IK_CTRL_parent_POS_GRP, self.global_CTRL)
        mayac.parent(self.LeftFoot.IK_CTRL_grandparent_POS_GRP, self.global_CTRL)
        mayac.parent(self.RightLeg.IK_CTRL_parent_POS_GRP, self.global_CTRL)
        mayac.parent(self.RightFoot.IK_CTRL_grandparent_POS_GRP, self.global_CTRL)
        
        self.IK_Dummy_Joint_GRP = mayac.group(em = True, name = "IK_Dummy_Joint_GRP")
        if self.hulaOption:
            mayac.parent(self.Root.IK_Dummy_Joint, self.IK_Dummy_Joint_GRP)
        else:
            mayac.parent(self.Hips.IK_Dummy_Joint, self.IK_Dummy_Joint_GRP)
        mayac.parent(self.IK_Dummy_Joint_GRP, self.global_CTRL)
        
        #IKFK follow body
        #arms
        temp = mayac.parentConstraint(self.LeftShoulder.IK_Dummy_Joint, self.LeftHand.IK_CTRL_grandparent_POS_GRP, maintainOffset = True)
        self.LeftHand_grandparent_Constraint = temp[0]
        mayac.parentConstraint(self.LeftShoulder.Bind_Joint, self.LeftHand.IK_CTRL_grandparent_POS_GRP, maintainOffset = True)
        self.LeftHand_grandparent_Constraint_Reverse = mayac.createNode( 'reverse', n="LeftHand_grandparent_Constraint_Reverse")
        mayac.connectAttr("%s.FollowBody" %(self.LeftHand.IK_CTRL), "%s.inputX" %(self.LeftHand_grandparent_Constraint_Reverse))
        mayac.connectAttr("%s.FollowBody" %(self.LeftHand.IK_CTRL), "%s.%sW1" %(self.LeftHand_grandparent_Constraint, self.LeftShoulder.Bind_Joint))
        mayac.connectAttr("%s.outputX" %(self.LeftHand_grandparent_Constraint_Reverse), "%s.%sW0" %(self.LeftHand_grandparent_Constraint, self.LeftShoulder.IK_Dummy_Joint))
        mayac.setAttr("%s.interpType" %(self.LeftHand_grandparent_Constraint), 2)
        
        temp = mayac.parentConstraint(self.RightShoulder.IK_Dummy_Joint, self.RightHand.IK_CTRL_grandparent_POS_GRP, maintainOffset = True)
        self.RightHand_grandparent_Constraint = temp[0]
        mayac.parentConstraint(self.RightShoulder.Bind_Joint, self.RightHand.IK_CTRL_grandparent_POS_GRP, maintainOffset = True)
        self.RightHand_grandparent_Constraint_Reverse = mayac.createNode( 'reverse', n="RightHand_grandparent_Constraint_Reverse")
        mayac.connectAttr("%s.FollowBody" %(self.RightHand.IK_CTRL), "%s.inputX" %(self.RightHand_grandparent_Constraint_Reverse))
        mayac.connectAttr("%s.FollowBody" %(self.RightHand.IK_CTRL), "%s.%sW1" %(self.RightHand_grandparent_Constraint, self.RightShoulder.Bind_Joint))
        mayac.connectAttr("%s.outputX" %(self.RightHand_grandparent_Constraint_Reverse), "%s.%sW0" %(self.RightHand_grandparent_Constraint, self.RightShoulder.IK_Dummy_Joint))
        mayac.setAttr("%s.interpType" %(self.RightHand_grandparent_Constraint), 2)
        
        temp = mayac.parentConstraint(self.LeftShoulder.IK_Dummy_Joint, self.LeftForeArm.IK_CTRL_parent_POS_GRP, maintainOffset = True)
        self.LeftForeArm_parent_Constraint = temp[0]
        mayac.parentConstraint(self.LeftShoulder.Bind_Joint, self.LeftForeArm.IK_CTRL_parent_POS_GRP, maintainOffset = True)
        self.LeftForeArm_parent_Constraint_Reverse = mayac.createNode( 'reverse', n="LeftForeArm_parent_Constraint_Reverse")
        mayac.connectAttr("%s.FollowBody" %(self.LeftForeArm.IK_CTRL), "%s.inputX" %(self.LeftForeArm_parent_Constraint_Reverse))
        mayac.connectAttr("%s.FollowBody" %(self.LeftForeArm.IK_CTRL), "%s.%sW1" %(self.LeftForeArm_parent_Constraint, self.LeftShoulder.Bind_Joint))
        mayac.connectAttr("%s.outputX" %(self.LeftForeArm_parent_Constraint_Reverse), "%s.%sW0" %(self.LeftForeArm_parent_Constraint, self.LeftShoulder.IK_Dummy_Joint))
        mayac.setAttr("%s.interpType" %(self.LeftForeArm_parent_Constraint), 2)
        
        temp = mayac.parentConstraint(self.RightShoulder.IK_Dummy_Joint, self.RightForeArm.IK_CTRL_parent_POS_GRP, maintainOffset = True)
        self.RightForeArm_parent_Constraint = temp[0]
        mayac.parentConstraint(self.RightShoulder.Bind_Joint, self.RightForeArm.IK_CTRL_parent_POS_GRP, maintainOffset = True)
        self.RightForeArm_parent_Constraint_Reverse = mayac.createNode( 'reverse', n="RightForeArm_parent_Constraint_Reverse")
        mayac.connectAttr("%s.FollowBody" %(self.RightForeArm.IK_CTRL), "%s.inputX" %(self.RightForeArm_parent_Constraint_Reverse))
        mayac.connectAttr("%s.FollowBody" %(self.RightForeArm.IK_CTRL), "%s.%sW1" %(self.RightForeArm_parent_Constraint, self.RightShoulder.Bind_Joint))
        mayac.connectAttr("%s.outputX" %(self.RightForeArm_parent_Constraint_Reverse), "%s.%sW0" %(self.RightForeArm_parent_Constraint, self.RightShoulder.IK_Dummy_Joint))
        mayac.setAttr("%s.interpType" %(self.RightForeArm_parent_Constraint), 2)
        
        #legs
        temp = mayac.parentConstraint(self.Hips.IK_Dummy_Joint, self.LeftFoot.IK_CTRL_grandparent_POS_GRP, maintainOffset = True)
        self.LeftFoot_grandparent_Constraint = temp[0]
        mayac.parentConstraint(self.Hips.Bind_Joint, self.LeftFoot.IK_CTRL_grandparent_POS_GRP, maintainOffset = True)
        self.LeftFoot_grandparent_Constraint_Reverse = mayac.createNode( 'reverse', n="LeftFoot_grandparent_Constraint_Reverse")
        mayac.connectAttr("%s.FollowBody" %(self.LeftFoot.IK_CTRL), "%s.inputX" %(self.LeftFoot_grandparent_Constraint_Reverse))
        mayac.connectAttr("%s.FollowBody" %(self.LeftFoot.IK_CTRL), "%s.%sW1" %(self.LeftFoot_grandparent_Constraint, self.Hips.Bind_Joint))
        mayac.connectAttr("%s.outputX" %(self.LeftFoot_grandparent_Constraint_Reverse), "%s.%sW0" %(self.LeftFoot_grandparent_Constraint, self.Hips.IK_Dummy_Joint))
        mayac.setAttr("%s.interpType" %(self.LeftFoot_grandparent_Constraint), 2)
        
        temp = mayac.parentConstraint(self.Hips.IK_Dummy_Joint, self.RightFoot.IK_CTRL_grandparent_POS_GRP, maintainOffset = True)
        self.RightFoot_grandparent_Constraint = temp[0]
        mayac.parentConstraint(self.Hips.Bind_Joint, self.RightFoot.IK_CTRL_grandparent_POS_GRP, maintainOffset = True)
        self.RightFoot_grandparent_Constraint_Reverse = mayac.createNode( 'reverse', n="RightFoot_grandparent_Constraint_Reverse")
        mayac.connectAttr("%s.FollowBody" %(self.RightFoot.IK_CTRL), "%s.inputX" %(self.RightFoot_grandparent_Constraint_Reverse))
        mayac.connectAttr("%s.FollowBody" %(self.RightFoot.IK_CTRL), "%s.%sW1" %(self.RightFoot_grandparent_Constraint, self.Hips.Bind_Joint))
        mayac.connectAttr("%s.outputX" %(self.RightFoot_grandparent_Constraint_Reverse), "%s.%sW0" %(self.RightFoot_grandparent_Constraint, self.Hips.IK_Dummy_Joint))
        mayac.setAttr("%s.interpType" %(self.RightFoot_grandparent_Constraint), 2)
        
        temp = mayac.parentConstraint(self.Hips.IK_Dummy_Joint, self.LeftLeg.IK_CTRL_parent_POS_GRP, maintainOffset = True)
        self.LeftLeg_parent_Constraint = temp[0]
        mayac.parentConstraint(self.Hips.Bind_Joint, self.LeftLeg.IK_CTRL_parent_POS_GRP, maintainOffset = True)
        self.LeftLeg_parent_Constraint_Reverse = mayac.createNode( 'reverse', n="LeftLeg_parent_Constraint_Reverse")
        mayac.connectAttr("%s.FollowBody" %(self.LeftLeg.IK_CTRL), "%s.inputX" %(self.LeftLeg_parent_Constraint_Reverse))
        mayac.connectAttr("%s.FollowBody" %(self.LeftLeg.IK_CTRL), "%s.%sW1" %(self.LeftLeg_parent_Constraint, self.Hips.Bind_Joint))
        mayac.connectAttr("%s.outputX" %(self.LeftLeg_parent_Constraint_Reverse), "%s.%sW0" %(self.LeftLeg_parent_Constraint, self.Hips.IK_Dummy_Joint))
        mayac.setAttr("%s.interpType" %(self.LeftLeg_parent_Constraint), 2)
        
        temp = mayac.parentConstraint(self.Hips.IK_Dummy_Joint, self.RightLeg.IK_CTRL_parent_POS_GRP, maintainOffset = True)
        self.RightLeg_parent_Constraint = temp[0]
        mayac.parentConstraint(self.Hips.Bind_Joint, self.RightLeg.IK_CTRL_parent_POS_GRP, maintainOffset = True)
        self.RightLeg_parent_Constraint_Reverse = mayac.createNode( 'reverse', n="RightLeg_parent_Constraint_Reverse")
        mayac.connectAttr("%s.FollowBody" %(self.RightLeg.IK_CTRL), "%s.inputX" %(self.RightLeg_parent_Constraint_Reverse))
        mayac.connectAttr("%s.FollowBody" %(self.RightLeg.IK_CTRL), "%s.%sW1" %(self.RightLeg_parent_Constraint, self.Hips.Bind_Joint))
        mayac.connectAttr("%s.outputX" %(self.RightLeg_parent_Constraint_Reverse), "%s.%sW0" %(self.RightLeg_parent_Constraint, self.Hips.IK_Dummy_Joint))
        mayac.setAttr("%s.interpType" %(self.RightLeg_parent_Constraint), 2)
        
        
        
        #IK Legs and Arms to Global
        temp = mayac.parentConstraint(self.LeftFoot.IK_CTRL_grandparent_POS_GRP, self.LeftFoot.IK_CTRL_grandparent_Global_POS_GRP, maintainOffset = True)
        self.LeftFoot.grandparent_Global_Constraint = temp[0]
        mayac.parentConstraint(self.global_CTRL, self.LeftFoot.IK_CTRL_grandparent_Global_POS_GRP, maintainOffset = True)
        self.LeftFoot.grandparent_Global_Constraint_Reverse = mayac.createNode( 'reverse', n="LeftFoot_grandparent_Global_Constraint_Reverse")
        mayac.connectAttr("%s.ParentToGlobal" %(self.LeftFoot.IK_CTRL), "%s.inputX" %(self.LeftFoot.grandparent_Global_Constraint_Reverse))
        mayac.connectAttr("%s.ParentToGlobal" %(self.LeftFoot.IK_CTRL), "%s.%sW1" %(self.LeftFoot.grandparent_Global_Constraint, self.global_CTRL))
        mayac.connectAttr("%s.outputX" %(self.LeftFoot.grandparent_Global_Constraint_Reverse), "%s.%sW0" %(self.LeftFoot.grandparent_Global_Constraint, self.LeftFoot.IK_CTRL_grandparent_POS_GRP))
        mayac.setAttr("%s.interpType" %(self.LeftFoot.grandparent_Global_Constraint), 0)
        
        temp = mayac.parentConstraint(self.RightFoot.IK_CTRL_grandparent_POS_GRP, self.RightFoot.IK_CTRL_grandparent_Global_POS_GRP, maintainOffset = True)
        self.RightFoot.grandparent_Global_Constraint = temp[0]
        mayac.parentConstraint(self.global_CTRL, self.RightFoot.IK_CTRL_grandparent_Global_POS_GRP, maintainOffset = True)
        self.RightFoot.grandparent_Global_Constraint_Reverse = mayac.createNode( 'reverse', n="RightFoot_grandparent_Global_Constraint_Reverse")
        mayac.connectAttr("%s.ParentToGlobal" %(self.RightFoot.IK_CTRL), "%s.inputX" %(self.RightFoot.grandparent_Global_Constraint_Reverse))
        mayac.connectAttr("%s.ParentToGlobal" %(self.RightFoot.IK_CTRL), "%s.%sW1" %(self.RightFoot.grandparent_Global_Constraint, self.global_CTRL))
        mayac.connectAttr("%s.outputX" %(self.RightFoot.grandparent_Global_Constraint_Reverse), "%s.%sW0" %(self.RightFoot.grandparent_Global_Constraint, self.RightFoot.IK_CTRL_grandparent_POS_GRP))
        mayac.setAttr("%s.interpType" %(self.RightFoot.grandparent_Global_Constraint), 2)
        
        temp = mayac.parentConstraint(self.LeftHand.IK_CTRL_grandparent_POS_GRP, self.LeftHand.IK_CTRL_grandparent_Global_POS_GRP, maintainOffset = True)
        self.LeftHand.grandparent_Global_Constraint = temp[0]
        mayac.parentConstraint(self.global_CTRL, self.LeftHand.IK_CTRL_grandparent_Global_POS_GRP, maintainOffset = True)
        self.LeftHand.grandparent_Global_Constraint_Reverse = mayac.createNode( 'reverse', n="LeftHand_grandparent_Global_Constraint_Reverse")
        mayac.connectAttr("%s.ParentToGlobal" %(self.LeftHand.IK_CTRL), "%s.inputX" %(self.LeftHand.grandparent_Global_Constraint_Reverse))
        mayac.connectAttr("%s.ParentToGlobal" %(self.LeftHand.IK_CTRL), "%s.%sW1" %(self.LeftHand.grandparent_Global_Constraint, self.global_CTRL))
        mayac.connectAttr("%s.outputX" %(self.LeftHand.grandparent_Global_Constraint_Reverse), "%s.%sW0" %(self.LeftHand.grandparent_Global_Constraint, self.LeftHand.IK_CTRL_grandparent_POS_GRP))
        mayac.setAttr("%s.interpType" %(self.LeftHand.grandparent_Global_Constraint), 2)
        
        temp = mayac.parentConstraint(self.RightHand.IK_CTRL_grandparent_POS_GRP, self.RightHand.IK_CTRL_grandparent_Global_POS_GRP, maintainOffset = True)
        self.RightHand.grandparent_Global_Constraint = temp[0]
        mayac.parentConstraint(self.global_CTRL, self.RightHand.IK_CTRL_grandparent_Global_POS_GRP, maintainOffset = True)
        self.RightHand.grandparent_Global_Constraint_Reverse = mayac.createNode( 'reverse', n="RightHand_grandparent_Global_Constraint_Reverse")
        mayac.connectAttr("%s.ParentToGlobal" %(self.RightHand.IK_CTRL), "%s.inputX" %(self.RightHand.grandparent_Global_Constraint_Reverse))
        mayac.connectAttr("%s.ParentToGlobal" %(self.RightHand.IK_CTRL), "%s.%sW1" %(self.RightHand.grandparent_Global_Constraint, self.global_CTRL))
        mayac.connectAttr("%s.outputX" %(self.RightHand.grandparent_Global_Constraint_Reverse), "%s.%sW0" %(self.RightHand.grandparent_Global_Constraint, self.RightHand.IK_CTRL_grandparent_POS_GRP))
        mayac.setAttr("%s.interpType" %(self.RightHand.grandparent_Global_Constraint), 2)
        

        ''' self.IK_CTRL_inRig_CONST_GRP = None
        self.follow_extremity_Constraint = None
        self.follow_extremity_Constraint_Reverse = None'''
        
        #IK Elbows and Knees to Global
        temp = mayac.parentConstraint(self.LeftLeg.IK_CTRL_parent_POS_GRP, self.LeftLeg.IK_CTRL_parent_Global_POS_GRP, maintainOffset = True)
        self.LeftLeg.parent_Global_Constraint = temp[0]
        mayac.parentConstraint(self.global_CTRL, self.LeftLeg.IK_CTRL_parent_Global_POS_GRP, maintainOffset = True)
        self.LeftLeg.parent_Global_Constraint_Reverse = mayac.createNode( 'reverse', n="LeftLeg_parent_Global_Constraint_Reverse")
        mayac.connectAttr("%s.ParentToGlobal" %(self.LeftLeg.IK_CTRL), "%s.inputX" %(self.LeftLeg.parent_Global_Constraint_Reverse))
        mayac.connectAttr("%s.ParentToGlobal" %(self.LeftLeg.IK_CTRL), "%s.%sW1" %(self.LeftLeg.parent_Global_Constraint, self.global_CTRL))
        mayac.connectAttr("%s.outputX" %(self.LeftLeg.parent_Global_Constraint_Reverse), "%s.%sW0" %(self.LeftLeg.parent_Global_Constraint, self.LeftLeg.IK_CTRL_parent_POS_GRP))
        mayac.setAttr("%s.interpType" %(self.LeftLeg.parent_Global_Constraint), 2)
        
        temp = mayac.parentConstraint(self.RightLeg.IK_CTRL_parent_POS_GRP, self.RightLeg.IK_CTRL_parent_Global_POS_GRP, maintainOffset = True)
        self.RightLeg.parent_Global_Constraint = temp[0]
        mayac.parentConstraint(self.global_CTRL, self.RightLeg.IK_CTRL_parent_Global_POS_GRP, maintainOffset = True)
        self.RightLeg.parent_Global_Constraint_Reverse = mayac.createNode( 'reverse', n="RightLeg_parent_Global_Constraint_Reverse")
        mayac.connectAttr("%s.ParentToGlobal" %(self.RightLeg.IK_CTRL), "%s.inputX" %(self.RightLeg.parent_Global_Constraint_Reverse))
        mayac.connectAttr("%s.ParentToGlobal" %(self.RightLeg.IK_CTRL), "%s.%sW1" %(self.RightLeg.parent_Global_Constraint, self.global_CTRL))
        mayac.connectAttr("%s.outputX" %(self.RightLeg.parent_Global_Constraint_Reverse), "%s.%sW0" %(self.RightLeg.parent_Global_Constraint, self.RightLeg.IK_CTRL_parent_POS_GRP))
        mayac.setAttr("%s.interpType" %(self.RightLeg.parent_Global_Constraint), 2)
        
        temp = mayac.parentConstraint(self.LeftForeArm.IK_CTRL_parent_POS_GRP, self.LeftForeArm.IK_CTRL_parent_Global_POS_GRP, maintainOffset = True)
        self.LeftForeArm.parent_Global_Constraint = temp[0]
        mayac.parentConstraint(self.global_CTRL, self.LeftForeArm.IK_CTRL_parent_Global_POS_GRP, maintainOffset = True)
        self.LeftForeArm.parent_Global_Constraint_Reverse = mayac.createNode( 'reverse', n="LeftForeArm_parent_Global_Constraint_Reverse")
        mayac.connectAttr("%s.ParentToGlobal" %(self.LeftForeArm.IK_CTRL), "%s.inputX" %(self.LeftForeArm.parent_Global_Constraint_Reverse))
        mayac.connectAttr("%s.ParentToGlobal" %(self.LeftForeArm.IK_CTRL), "%s.%sW1" %(self.LeftForeArm.parent_Global_Constraint, self.global_CTRL))
        mayac.connectAttr("%s.outputX" %(self.LeftForeArm.parent_Global_Constraint_Reverse), "%s.%sW0" %(self.LeftForeArm.parent_Global_Constraint, self.LeftForeArm.IK_CTRL_parent_POS_GRP))
        mayac.setAttr("%s.interpType" %(self.LeftForeArm.parent_Global_Constraint), 2)
        
        temp = mayac.parentConstraint(self.RightForeArm.IK_CTRL_parent_POS_GRP, self.RightForeArm.IK_CTRL_parent_Global_POS_GRP, maintainOffset = True)
        self.RightForeArm.parent_Global_Constraint = temp[0]
        mayac.parentConstraint(self.global_CTRL, self.RightForeArm.IK_CTRL_parent_Global_POS_GRP, maintainOffset = True)
        self.RightForeArm.parent_Global_Constraint_Reverse = mayac.createNode( 'reverse', n="RightForeArm_parent_Global_Constraint_Reverse")
        mayac.connectAttr("%s.ParentToGlobal" %(self.RightForeArm.IK_CTRL), "%s.inputX" %(self.RightForeArm.parent_Global_Constraint_Reverse))
        mayac.connectAttr("%s.ParentToGlobal" %(self.RightForeArm.IK_CTRL), "%s.%sW1" %(self.RightForeArm.parent_Global_Constraint, self.global_CTRL))
        mayac.connectAttr("%s.outputX" %(self.RightForeArm.parent_Global_Constraint_Reverse), "%s.%sW0" %(self.RightForeArm.parent_Global_Constraint, self.RightForeArm.IK_CTRL_parent_POS_GRP))
        mayac.setAttr("%s.interpType" %(self.RightForeArm.parent_Global_Constraint), 2)
        
        
        
        #IK Elbows and Knees to Hands and feet     
        temp = mayac.parentConstraint(self.LeftFoot.IK_CTRL, self.LeftLeg.Follow_Foot_GRP, maintainOffset = True)
        self.LeftLeg.Follow_Foot_Constraint = temp[0]
        temp = mayac.parentConstraint(self.LeftLeg.IK_CTRL_animData_CONST_GRP, self.LeftLeg.IK_CTRL_inRig_CONST_GRP, maintainOffset = False)
        self.LeftLeg.follow_extremity_Constraint = temp[0]
        mayac.parentConstraint(self.LeftLeg.Follow_Knee_GRP, self.LeftLeg.IK_CTRL_inRig_CONST_GRP, maintainOffset = False)
        self.LeftLeg.follow_extremity_Constraint_Reverse = mayac.createNode( 'reverse', n="LeftLeg_follow_extremity_Constraint_Reverse")
        mayac.connectAttr("%s.FollowFoot" %(self.LeftLeg.IK_CTRL), "%s.inputX" %(self.LeftLeg.follow_extremity_Constraint_Reverse))
        mayac.connectAttr("%s.FollowFoot" %(self.LeftLeg.IK_CTRL), "%s.%sW1" %(self.LeftLeg.follow_extremity_Constraint, self.LeftLeg.Follow_Knee_GRP))
        mayac.connectAttr("%s.outputX" %(self.LeftLeg.follow_extremity_Constraint_Reverse), "%s.%sW0" %(self.LeftLeg.follow_extremity_Constraint, self.LeftLeg.IK_CTRL_animData_CONST_GRP))
        mayac.setAttr("%s.interpType" %(self.LeftLeg.follow_extremity_Constraint), 2)
        
        temp = mayac.parentConstraint(self.RightFoot.IK_CTRL, self.RightLeg.Follow_Foot_GRP, maintainOffset = True)
        self.RightLeg.Follow_Foot_Constraint = temp[0]
        temp = mayac.parentConstraint(self.RightLeg.IK_CTRL_animData_CONST_GRP, self.RightLeg.IK_CTRL_inRig_CONST_GRP, maintainOffset = False)
        self.RightLeg.follow_extremity_Constraint = temp[0]
        mayac.parentConstraint(self.RightLeg.Follow_Knee_GRP, self.RightLeg.IK_CTRL_inRig_CONST_GRP, maintainOffset = False)
        self.RightLeg.follow_extremity_Constraint_Reverse = mayac.createNode( 'reverse', n="RightLeg_follow_extremity_Constraint_Reverse")
        mayac.connectAttr("%s.FollowFoot" %(self.RightLeg.IK_CTRL), "%s.inputX" %(self.RightLeg.follow_extremity_Constraint_Reverse))
        mayac.connectAttr("%s.FollowFoot" %(self.RightLeg.IK_CTRL), "%s.%sW1" %(self.RightLeg.follow_extremity_Constraint, self.RightLeg.Follow_Knee_GRP))
        mayac.connectAttr("%s.outputX" %(self.RightLeg.follow_extremity_Constraint_Reverse), "%s.%sW0" %(self.RightLeg.follow_extremity_Constraint, self.RightLeg.IK_CTRL_animData_CONST_GRP))
        mayac.setAttr("%s.interpType" %(self.RightLeg.follow_extremity_Constraint), 2)
        
        temp = mayac.parentConstraint(self.LeftForeArm.IK_CTRL_animData_CONST_GRP, self.LeftForeArm.IK_CTRL_inRig_CONST_GRP, maintainOffset = True)
        self.LeftForeArm.follow_extremity_Constraint = temp[0]
        mayac.parentConstraint(self.LeftHand.IK_CTRL, self.LeftForeArm.IK_CTRL_inRig_CONST_GRP, maintainOffset = True)
        self.LeftForeArm.follow_extremity_Constraint_Reverse = mayac.createNode( 'reverse', n="LeftForeArm_follow_extremity_Constraint_Reverse")
        mayac.connectAttr("%s.FollowHand" %(self.LeftForeArm.IK_CTRL), "%s.inputX" %(self.LeftForeArm.follow_extremity_Constraint_Reverse))
        mayac.connectAttr("%s.FollowHand" %(self.LeftForeArm.IK_CTRL), "%s.%sW1" %(self.LeftForeArm.follow_extremity_Constraint, self.LeftHand.IK_CTRL))
        mayac.connectAttr("%s.outputX" %(self.LeftForeArm.follow_extremity_Constraint_Reverse), "%s.%sW0" %(self.LeftForeArm.follow_extremity_Constraint, self.LeftForeArm.IK_CTRL_animData_CONST_GRP))
        mayac.setAttr("%s.interpType" %(self.LeftForeArm.follow_extremity_Constraint), 2)
        
        temp = mayac.parentConstraint(self.RightForeArm.IK_CTRL_animData_CONST_GRP, self.RightForeArm.IK_CTRL_inRig_CONST_GRP, maintainOffset = True)
        self.RightForeArm.follow_extremity_Constraint = temp[0]
        mayac.parentConstraint(self.RightHand.IK_CTRL, self.RightForeArm.IK_CTRL_inRig_CONST_GRP, maintainOffset = True)
        self.RightForeArm.follow_extremity_Constraint_Reverse = mayac.createNode( 'reverse', n="RightForeArm_follow_extremity_Constraint_Reverse")
        mayac.connectAttr("%s.FollowHand" %(self.RightForeArm.IK_CTRL), "%s.inputX" %(self.RightForeArm.follow_extremity_Constraint_Reverse))
        mayac.connectAttr("%s.FollowHand" %(self.RightForeArm.IK_CTRL), "%s.%sW1" %(self.RightForeArm.follow_extremity_Constraint, self.RightHand.IK_CTRL))
        mayac.connectAttr("%s.outputX" %(self.RightForeArm.follow_extremity_Constraint_Reverse), "%s.%sW0" %(self.RightForeArm.follow_extremity_Constraint, self.RightForeArm.IK_CTRL_animData_CONST_GRP))
        mayac.setAttr("%s.interpType" %(self.RightForeArm.follow_extremity_Constraint), 2)
        

        
        #IK feet
        self.Left_Ankle_IK_CTRL = DJB_createGroup(transform = None, suffix = None, fullName ="Left_Ankle_IK_CTRL", pivotFrom = self.LeftToeBase.Bind_Joint)
        self.Left_ToeBase_IK_CTRL = DJB_createGroup(transform = None, suffix = None, fullName ="Left_ToeBase_IK_CTRL", pivotFrom = self.LeftToeBase.Bind_Joint)
        self.Left_ToeBase_IK_AnimData_GRP = DJB_createGroup(transform = self.Left_ToeBase_IK_CTRL, suffix = None, fullName ="Left_ToeBase_IK_AnimData_GRP")
        self.Left_Ankle_IK_AnimData_GRP = DJB_createGroup(transform = self.Left_Ankle_IK_CTRL, suffix = None, fullName ="Left_Ankle_IK_AnimData_GRP")
        self.Left_Toe_IK_CTRL = DJB_createGroup(transform = None, suffix = None, fullName ="Left_Toe_End_IK_CTRL", pivotFrom = self.LeftToe_End.Bind_Joint)
        self.Left_Toe_IK_AnimData_GRP = DJB_createGroup(transform = self.Left_Toe_IK_CTRL, suffix = None, fullName ="Left_Toe_IK_AnimData_GRP")   
        #set rotation orders
        mayac.setAttr("%s.rotateOrder" % (self.Left_Ankle_IK_CTRL), self.LeftFoot.rotOrder)
        mayac.setAttr("%s.rotateOrder" % (self.Left_ToeBase_IK_CTRL), self.LeftToeBase.rotOrder)
        mayac.setAttr("%s.rotateOrder" % (self.Left_ToeBase_IK_AnimData_GRP), self.LeftToeBase.rotOrder)
        mayac.setAttr("%s.rotateOrder" % (self.Left_Ankle_IK_AnimData_GRP), self.LeftFoot.rotOrder)
        mayac.setAttr("%s.rotateOrder" % (self.Left_Toe_IK_CTRL), self.LeftToeBase.rotOrder)
        mayac.setAttr("%s.rotateOrder" % (self.Left_Toe_IK_AnimData_GRP), self.LeftToeBase.rotOrder)
        
        
        #handle     
        temp = mayac.ikHandle( n="Left_ToeBase_IkHandle", sj= self.LeftFoot.IK_Joint, ee= self.LeftToeBase.IK_Joint, solver = "ikSCsolver", weight = 1)
        self.Left_ToeBase_IkHandle = temp[0]
        mayac.setAttr("%s.visibility" % (self.Left_ToeBase_IkHandle), 0)

        mayac.parent(self.Left_Toe_IK_AnimData_GRP, self.LeftFoot.IK_CTRL)
        mayac.parent(self.Left_ToeBase_IK_AnimData_GRP, self.Left_Toe_IK_CTRL)
        mayac.parent(self.Left_Ankle_IK_AnimData_GRP, self.Left_Toe_IK_CTRL)
        mayac.parent(self.LeftFoot.IK_Handle, self.Left_Ankle_IK_CTRL)
        mayac.parent(self.Left_ToeBase_IkHandle, self.Left_Ankle_IK_CTRL)
        mayac.orientConstraint(self.Left_Toe_IK_CTRL, self.LeftToe_End.IK_Joint)
        mayac.orientConstraint(self.Left_ToeBase_IK_CTRL, self.LeftToeBase.IK_Joint)
        mayac.delete(self.LeftFoot.IK_Constraint)
        self.LeftFoot.IK_Constraint = None
        mayac.orientConstraint(self.Left_Ankle_IK_CTRL, self.LeftFoot.IK_Joint)
        
        self.Left_IK_ToeBase_animData_MultNode = mayac.createNode( 'multiplyDivide', n="Left_IK_ToeBase_animData_MultNode")
        mayac.connectAttr("%s.rotateX" %(self.LeftToeBase.AnimData_Joint), "%s.input1X" %(self.Left_IK_ToeBase_animData_MultNode), force = True)
        mayac.connectAttr("%s.AnimDataMult" %(self.LeftFoot.IK_CTRL), "%s.input2X" %(self.Left_IK_ToeBase_animData_MultNode), force = True)
        mayac.connectAttr("%s.rotateY" %(self.LeftToeBase.AnimData_Joint), "%s.input1Y" %(self.Left_IK_ToeBase_animData_MultNode), force = True)
        mayac.connectAttr("%s.AnimDataMult" %(self.LeftFoot.IK_CTRL), "%s.input2Y" %(self.Left_IK_ToeBase_animData_MultNode), force = True)
        mayac.connectAttr("%s.rotateZ" %(self.LeftToeBase.AnimData_Joint), "%s.input1Z" %(self.Left_IK_ToeBase_animData_MultNode), force = True)
        mayac.connectAttr("%s.AnimDataMult" %(self.LeftFoot.IK_CTRL), "%s.input2Z" %(self.Left_IK_ToeBase_animData_MultNode), force = True)
        mayac.connectAttr("%s.outputX" %(self.Left_IK_ToeBase_animData_MultNode), "%s.rotateX" %(self.Left_ToeBase_IK_AnimData_GRP), force = True)
        mayac.connectAttr("%s.outputY" %(self.Left_IK_ToeBase_animData_MultNode), "%s.rotateY" %(self.Left_ToeBase_IK_AnimData_GRP), force = True)
        mayac.connectAttr("%s.outputZ" %(self.Left_IK_ToeBase_animData_MultNode), "%s.rotateZ" %(self.Left_ToeBase_IK_AnimData_GRP), force = True)
    
        self.Right_Ankle_IK_CTRL = DJB_createGroup(transform = None, suffix = None, fullName ="Right_Ankle_IK_CTRL", pivotFrom = self.RightToeBase.Bind_Joint)
        self.Right_ToeBase_IK_CTRL = DJB_createGroup(transform = None, suffix = None, fullName ="Right_ToeBase_IK_CTRL", pivotFrom = self.RightToeBase.Bind_Joint)
        self.Right_ToeBase_IK_AnimData_GRP = DJB_createGroup(transform = self.Right_ToeBase_IK_CTRL, suffix = None, fullName ="Right_ToeBase_IK_AnimData_GRP")
        self.Right_Ankle_IK_AnimData_GRP = DJB_createGroup(transform = self.Right_Ankle_IK_CTRL, suffix = None, fullName ="Right_Ankle_IK_AnimData_GRP")
        self.Right_Toe_IK_CTRL = DJB_createGroup(transform = None, suffix = None, fullName ="Right_Toe_End_IK_CTRL", pivotFrom = self.RightToe_End.Bind_Joint)
        self.Right_Toe_IK_AnimData_GRP = DJB_createGroup(transform = self.Right_Toe_IK_CTRL, suffix = None, fullName ="Right_Toe_IK_AnimData_GRP")            
        #set rotation orders
        mayac.setAttr("%s.rotateOrder" % (self.Right_Ankle_IK_CTRL), self.LeftFoot.rotOrder)
        mayac.setAttr("%s.rotateOrder" % (self.Right_ToeBase_IK_CTRL), self.LeftToeBase.rotOrder)
        mayac.setAttr("%s.rotateOrder" % (self.Right_ToeBase_IK_AnimData_GRP), self.LeftToeBase.rotOrder)
        mayac.setAttr("%s.rotateOrder" % (self.Right_Ankle_IK_AnimData_GRP), self.LeftFoot.rotOrder)
        mayac.setAttr("%s.rotateOrder" % (self.Right_Toe_IK_CTRL), self.LeftToeBase.rotOrder)
        mayac.setAttr("%s.rotateOrder" % (self.Right_Toe_IK_AnimData_GRP), self.LeftToeBase.rotOrder)
        #IK Handle
        temp = mayac.ikHandle( n="Right_ToeBase_IkHandle", sj= self.RightFoot.IK_Joint, ee= self.RightToeBase.IK_Joint, solver = "ikSCsolver", weight = 1)
        self.Right_ToeBase_IkHandle = temp[0]
        mayac.setAttr("%s.visibility" % (self.Right_ToeBase_IkHandle), 0)

        
        mayac.parent(self.Right_Toe_IK_AnimData_GRP, self.RightFoot.IK_CTRL)
        mayac.parent(self.Right_ToeBase_IK_AnimData_GRP, self.Right_Toe_IK_CTRL)
        mayac.parent(self.Right_Ankle_IK_AnimData_GRP, self.Right_Toe_IK_CTRL)
        mayac.parent(self.RightFoot.IK_Handle, self.Right_Ankle_IK_CTRL)
        mayac.parent(self.Right_ToeBase_IkHandle, self.Right_Ankle_IK_CTRL)
        mayac.orientConstraint(self.Right_Toe_IK_CTRL, self.RightToe_End.IK_Joint)
        mayac.orientConstraint(self.Right_ToeBase_IK_CTRL, self.RightToeBase.IK_Joint)
        mayac.delete(self.RightFoot.IK_Constraint)
        self.RightFoot.IK_Constraint = None
        mayac.orientConstraint(self.Right_Ankle_IK_CTRL, self.RightFoot.IK_Joint)
        
        self.Right_IK_ToeBase_animData_MultNode = mayac.createNode( 'multiplyDivide', n="Right_IK_ToeBase_animData_MultNode")
        mayac.connectAttr("%s.rotateX" %(self.RightToeBase.AnimData_Joint), "%s.input1X" %(self.Right_IK_ToeBase_animData_MultNode), force = True)
        mayac.connectAttr("%s.AnimDataMult" %(self.RightFoot.IK_CTRL), "%s.input2X" %(self.Right_IK_ToeBase_animData_MultNode), force = True)
        mayac.connectAttr("%s.rotateY" %(self.RightToeBase.AnimData_Joint), "%s.input1Y" %(self.Right_IK_ToeBase_animData_MultNode), force = True)
        mayac.connectAttr("%s.AnimDataMult" %(self.RightFoot.IK_CTRL), "%s.input2Y" %(self.Right_IK_ToeBase_animData_MultNode), force = True)
        mayac.connectAttr("%s.rotateZ" %(self.RightToeBase.AnimData_Joint), "%s.input1Z" %(self.Right_IK_ToeBase_animData_MultNode), force = True)
        mayac.connectAttr("%s.AnimDataMult" %(self.RightFoot.IK_CTRL), "%s.input2Z" %(self.Right_IK_ToeBase_animData_MultNode), force = True)
        mayac.connectAttr("%s.outputX" %(self.Right_IK_ToeBase_animData_MultNode), "%s.rotateX" %(self.Right_ToeBase_IK_AnimData_GRP), force = True)
        mayac.connectAttr("%s.outputY" %(self.Right_IK_ToeBase_animData_MultNode), "%s.rotateY" %(self.Right_ToeBase_IK_AnimData_GRP), force = True)
        mayac.connectAttr("%s.outputZ" %(self.Right_IK_ToeBase_animData_MultNode), "%s.rotateZ" %(self.Right_ToeBase_IK_AnimData_GRP), force = True)

        #Zero offsets on Foot Constraints
        mayac.setAttr("%s.offsetX" % (self.LeftFoot.Constraint), 0)
        mayac.setAttr("%s.offsetY" % (self.LeftFoot.Constraint), 0)
        mayac.setAttr("%s.offsetZ" % (self.LeftFoot.Constraint), 0)
        mayac.setAttr("%s.offsetX" % (self.RightFoot.Constraint), 0)
        mayac.setAttr("%s.offsetY" % (self.RightFoot.Constraint), 0)
        mayac.setAttr("%s.offsetZ" % (self.RightFoot.Constraint), 0)

        #attr connections to foot controls
        if self.rigType == "AutoRig":
            self.LeftFoot_FootRoll_MultNode = mayac.createNode( 'multiplyDivide', n="LeftFoot_FootRoll_MultNode")
            mayac.setAttr("%s.input2X" %(self.LeftFoot_FootRoll_MultNode), -1)
            mayac.connectAttr("%s.FootRoll" %(self.LeftFoot.IK_CTRL), "%s.input1X" %(self.LeftFoot_FootRoll_MultNode), force = True)
            mayac.connectAttr("%s.outputX" %(self.LeftFoot_FootRoll_MultNode), "%s.rotateX" %(self.Left_Ankle_IK_CTRL), force = True)
    
            mayac.connectAttr("%s.ToeTap" %(self.LeftFoot.IK_CTRL), "%s.rotateX" %(self.Left_ToeBase_IK_CTRL), force = True)
            Left_ToeBase_ZAdd = mayac.shadingNode('plusMinusAverage', asUtility=True, n = "Left_ToeBase_ZAdd")
            mayac.connectAttr("%s.ToeSideToSide" %(self.LeftFoot.IK_CTRL), "%s.input1D[0]" %(Left_ToeBase_ZAdd), force = True)
            mayac.connectAttr("%s.output1D" %(Left_ToeBase_ZAdd), "%s.rotateZ" %(self.Left_ToeBase_IK_CTRL), force = True)
            mayac.connectAttr("%s.ToeRotate" %(self.LeftFoot.IK_CTRL), "%s.rotateY" %(self.Left_ToeBase_IK_CTRL), force = True)
            
            self.LeftFoot_ToeRoll_MultNode = mayac.createNode( 'multiplyDivide', n="LeftFoot_ToeRoll_MultNode")
            mayac.setAttr("%s.input2X" %(self.LeftFoot_ToeRoll_MultNode), -1)
            mayac.connectAttr("%s.ToeRoll" %(self.LeftFoot.IK_CTRL), "%s.input1X" %(self.LeftFoot_ToeRoll_MultNode), force = True)
            mayac.connectAttr("%s.outputX" %(self.LeftFoot_ToeRoll_MultNode), "%s.rotateX" %(self.Left_Toe_IK_CTRL), force = True)
            
            mayac.connectAttr("%s.HipPivot" %(self.LeftFoot.IK_CTRL), "%s.rotateY" %(self.LeftFoot.IK_CTRL_grandparent_inRig_CONST_GRP), force = True)
    
            mayac.connectAttr("%s.BallPivot" %(self.LeftFoot.IK_CTRL), "%s.input1D[1]" %(Left_ToeBase_ZAdd), force = True)
            mayac.connectAttr("%s.BallPivot" %(self.LeftFoot.IK_CTRL), "%s.rotateZ" %(self.Left_Ankle_IK_CTRL), force = True)
            
            mayac.connectAttr("%s.ToePivot" %(self.LeftFoot.IK_CTRL), "%s.rotateZ" %(self.Left_Toe_IK_CTRL), force = True)
            
            mayac.connectAttr("%s.HipSideToSide" %(self.LeftFoot.IK_CTRL), "%s.rotateZ" %(self.LeftFoot.IK_CTRL_grandparent_inRig_CONST_GRP), force = True)
    
            mayac.connectAttr("%s.HipBackToFront" %(self.LeftFoot.IK_CTRL), "%s.rotateX" %(self.LeftFoot.IK_CTRL_grandparent_inRig_CONST_GRP), force = True)
        
        
            self.RightFoot_FootRoll_MultNode = mayac.createNode( 'multiplyDivide', n="RightFoot_FootRoll_MultNode")
            mayac.setAttr("%s.input2X" %(self.RightFoot_FootRoll_MultNode), -1)
            mayac.connectAttr("%s.FootRoll" %(self.RightFoot.IK_CTRL), "%s.input1X" %(self.RightFoot_FootRoll_MultNode), force = True)
            mayac.connectAttr("%s.outputX" %(self.RightFoot_FootRoll_MultNode), "%s.rotateX" %(self.Right_Ankle_IK_CTRL), force = True)
    
            mayac.connectAttr("%s.ToeTap" %(self.RightFoot.IK_CTRL), "%s.rotateX" %(self.Right_ToeBase_IK_CTRL), force = True)
            Right_ToeBase_ZAdd = mayac.shadingNode('plusMinusAverage', asUtility=True, n = "Right_ToeBase_ZAdd")
            mayac.connectAttr("%s.ToeSideToSide" %(self.RightFoot.IK_CTRL), "%s.input1D[0]" %(Right_ToeBase_ZAdd), force = True)
            mayac.connectAttr("%s.output1D" %(Right_ToeBase_ZAdd), "%s.rotateZ" %(self.Right_ToeBase_IK_CTRL), force = True)
            mayac.connectAttr("%s.ToeRotate" %(self.RightFoot.IK_CTRL), "%s.rotateY" %(self.Right_ToeBase_IK_CTRL), force = True)
    
            self.RightFoot_ToeRoll_MultNode = mayac.createNode( 'multiplyDivide', n="RightFoot_ToeRoll_MultNode")
            mayac.setAttr("%s.input2X" %(self.RightFoot_ToeRoll_MultNode), -1)
            mayac.connectAttr("%s.ToeRoll" %(self.RightFoot.IK_CTRL), "%s.input1X" %(self.RightFoot_ToeRoll_MultNode), force = True)
            mayac.connectAttr("%s.outputX" %(self.RightFoot_ToeRoll_MultNode), "%s.rotateX" %(self.Right_Toe_IK_CTRL), force = True)
            
            self.RightFoot_HipPivot_MultNode = mayac.createNode( 'multiplyDivide', n="RightFoot_HipPivot_MultNode")
            mayac.setAttr("%s.input2X" %(self.RightFoot_HipPivot_MultNode), -1)
            mayac.connectAttr("%s.HipPivot" %(self.RightFoot.IK_CTRL), "%s.input1X" %(self.RightFoot_HipPivot_MultNode), force = True)
            mayac.connectAttr("%s.outputX" %(self.RightFoot_HipPivot_MultNode), "%s.rotateY" %(self.RightFoot.IK_CTRL_grandparent_inRig_CONST_GRP), force = True)
            
            self.RightFoot_BallPivot_MultNode = mayac.createNode( 'multiplyDivide', n="RightFoot_BallPivot_MultNode")
            mayac.setAttr("%s.input2X" %(self.RightFoot_BallPivot_MultNode), -1)
            mayac.connectAttr("%s.BallPivot" %(self.RightFoot.IK_CTRL), "%s.input1X" %(self.RightFoot_BallPivot_MultNode), force = True)
            mayac.connectAttr("%s.outputX" %(self.RightFoot_BallPivot_MultNode), "%s.input1D[1]" %(Right_ToeBase_ZAdd), force = True)
            mayac.connectAttr("%s.outputX" %(self.RightFoot_BallPivot_MultNode), "%s.rotateZ" %(self.Right_Ankle_IK_CTRL), force = True)
            
            self.RightFoot_ToePivot_MultNode = mayac.createNode( 'multiplyDivide', n="RightFoot_ToePivot_MultNode")
            mayac.setAttr("%s.input2X" %(self.RightFoot_ToePivot_MultNode), -1)
            mayac.connectAttr("%s.ToePivot" %(self.RightFoot.IK_CTRL), "%s.input1X" %(self.RightFoot_ToePivot_MultNode), force = True)
            mayac.connectAttr("%s.outputX" %(self.RightFoot_ToePivot_MultNode), "%s.rotateZ" %(self.Right_Toe_IK_CTRL), force = True)
            
            self.RightFoot_HipSideToSide_MultNode = mayac.createNode( 'multiplyDivide', n="RightFoot_HipSideToSide_MultNode")
            mayac.setAttr("%s.input2X" %(self.RightFoot_HipSideToSide_MultNode), -1)
            mayac.connectAttr("%s.HipSideToSide" %(self.RightFoot.IK_CTRL), "%s.input1X" %(self.RightFoot_HipSideToSide_MultNode), force = True)
            mayac.connectAttr("%s.outputX" %(self.RightFoot_HipSideToSide_MultNode), "%s.rotateZ" %(self.RightFoot.IK_CTRL_grandparent_inRig_CONST_GRP), force = True)
            
            mayac.connectAttr("%s.HipBackToFront" %(self.RightFoot.IK_CTRL), "%s.rotateX" %(self.RightFoot.IK_CTRL_grandparent_inRig_CONST_GRP), force = True)
        
        
        
        
        elif self.rigType == "World":
            self.LeftFoot_FootRoll_MultNode = mayac.createNode( 'multiplyDivide', n="LeftFoot_FootRoll_MultNode")
            mayac.setAttr("%s.input2X" %(self.LeftFoot_FootRoll_MultNode), 1)
            mayac.connectAttr("%s.FootRoll" %(self.LeftFoot.IK_CTRL), "%s.input1X" %(self.LeftFoot_FootRoll_MultNode), force = True)
            mayac.connectAttr("%s.outputX" %(self.LeftFoot_FootRoll_MultNode), "%s.rotateX" %(self.Left_Ankle_IK_CTRL), force = True)
    
            LeftFoot_ToeTap_MultNode = mayac.createNode( 'multiplyDivide', n="LeftFoot_ToeTap_MultNode")
            mayac.setAttr("%s.input2X" %(LeftFoot_ToeTap_MultNode), -1)
            mayac.connectAttr("%s.ToeTap" %(self.LeftFoot.IK_CTRL), "%s.input1X" %(LeftFoot_ToeTap_MultNode), force = True)
            mayac.connectAttr("%s.outputX" %(LeftFoot_ToeTap_MultNode), "%s.rotateX" %(self.Left_ToeBase_IK_CTRL), force = True)
            
            Left_ToeBase_ZAdd = mayac.shadingNode('plusMinusAverage', asUtility=True, n = "Left_ToeBase_ZAdd")
            mayac.connectAttr("%s.ToeSideToSide" %(self.LeftFoot.IK_CTRL), "%s.input1D[0]" %(Left_ToeBase_ZAdd), force = True)
            mayac.connectAttr("%s.output1D" %(Left_ToeBase_ZAdd), "%s.rotateY" %(self.Left_ToeBase_IK_CTRL), force = True)
            mayac.connectAttr("%s.ToeRotate" %(self.LeftFoot.IK_CTRL), "%s.rotateZ" %(self.Left_ToeBase_IK_CTRL), force = True)
            
            self.LeftFoot_ToeRoll_MultNode = mayac.createNode( 'multiplyDivide', n="LeftFoot_ToeRoll_MultNode")
            mayac.setAttr("%s.input2X" %(self.LeftFoot_ToeRoll_MultNode), 1)
            mayac.connectAttr("%s.ToeRoll" %(self.LeftFoot.IK_CTRL), "%s.input1X" %(self.LeftFoot_ToeRoll_MultNode), force = True)
            mayac.connectAttr("%s.outputX" %(self.LeftFoot_ToeRoll_MultNode), "%s.rotateX" %(self.Left_Toe_IK_CTRL), force = True)
            
            mayac.connectAttr("%s.HipPivot" %(self.LeftFoot.IK_CTRL), "%s.rotateY" %(self.LeftFoot.IK_CTRL_grandparent_inRig_CONST_GRP), force = True)
    
            mayac.connectAttr("%s.BallPivot" %(self.LeftFoot.IK_CTRL), "%s.input1D[1]" %(Left_ToeBase_ZAdd), force = True)
            mayac.connectAttr("%s.BallPivot" %(self.LeftFoot.IK_CTRL), "%s.rotateY" %(self.Left_Ankle_IK_CTRL), force = True)
            
            mayac.connectAttr("%s.ToePivot" %(self.LeftFoot.IK_CTRL), "%s.rotateY" %(self.Left_Toe_IK_CTRL), force = True)
            
            mayac.connectAttr("%s.HipSideToSide" %(self.LeftFoot.IK_CTRL), "%s.rotateZ" %(self.LeftFoot.IK_CTRL_grandparent_inRig_CONST_GRP), force = True)
    
            mayac.connectAttr("%s.HipBackToFront" %(self.LeftFoot.IK_CTRL), "%s.rotateX" %(self.LeftFoot.IK_CTRL_grandparent_inRig_CONST_GRP), force = True)
            
            
            self.RightFoot_FootRoll_MultNode = mayac.createNode( 'multiplyDivide', n="RightFoot_FootRoll_MultNode")
            mayac.setAttr("%s.input2X" %(self.RightFoot_FootRoll_MultNode), 1)
            mayac.connectAttr("%s.FootRoll" %(self.RightFoot.IK_CTRL), "%s.input1X" %(self.RightFoot_FootRoll_MultNode), force = True)
            mayac.connectAttr("%s.outputX" %(self.RightFoot_FootRoll_MultNode), "%s.rotateX" %(self.Right_Ankle_IK_CTRL), force = True)
    
            RightFoot_ToeTap_MultNode = mayac.createNode( 'multiplyDivide', n="RightFoot_ToeTap_MultNode")
            mayac.setAttr("%s.input2X" %(RightFoot_ToeTap_MultNode), -1)
            mayac.connectAttr("%s.ToeTap" %(self.RightFoot.IK_CTRL), "%s.input1X" %(RightFoot_ToeTap_MultNode), force = True)
            mayac.connectAttr("%s.outputX" %(RightFoot_ToeTap_MultNode), "%s.rotateX" %(self.Right_ToeBase_IK_CTRL), force = True)
            
            Right_ToeBase_ZAdd = mayac.shadingNode('plusMinusAverage', asUtility=True, n = "Right_ToeBase_ZAdd")
            mayac.connectAttr("%s.ToeSideToSide" %(self.RightFoot.IK_CTRL), "%s.input1D[0]" %(Right_ToeBase_ZAdd), force = True)
            mayac.connectAttr("%s.output1D" %(Right_ToeBase_ZAdd), "%s.rotateY" %(self.Right_ToeBase_IK_CTRL), force = True)
            mayac.connectAttr("%s.ToeRotate" %(self.RightFoot.IK_CTRL), "%s.rotateZ" %(self.Right_ToeBase_IK_CTRL), force = True)
    
            self.RightFoot_ToeRoll_MultNode = mayac.createNode( 'multiplyDivide', n="RightFoot_ToeRoll_MultNode")
            mayac.setAttr("%s.input2X" %(self.RightFoot_ToeRoll_MultNode), 1)
            mayac.connectAttr("%s.ToeRoll" %(self.RightFoot.IK_CTRL), "%s.input1X" %(self.RightFoot_ToeRoll_MultNode), force = True)
            mayac.connectAttr("%s.outputX" %(self.RightFoot_ToeRoll_MultNode), "%s.rotateX" %(self.Right_Toe_IK_CTRL), force = True)
            
            self.RightFoot_HipPivot_MultNode = mayac.createNode( 'multiplyDivide', n="RightFoot_HipPivot_MultNode")
            mayac.setAttr("%s.input2X" %(self.RightFoot_HipPivot_MultNode), -1)
            mayac.connectAttr("%s.HipPivot" %(self.RightFoot.IK_CTRL), "%s.input1X" %(self.RightFoot_HipPivot_MultNode), force = True)
            mayac.connectAttr("%s.outputX" %(self.RightFoot_HipPivot_MultNode), "%s.rotateY" %(self.RightFoot.IK_CTRL_grandparent_inRig_CONST_GRP), force = True)
            
            self.RightFoot_BallPivot_MultNode = mayac.createNode( 'multiplyDivide', n="RightFoot_BallPivot_MultNode")
            mayac.setAttr("%s.input2X" %(self.RightFoot_BallPivot_MultNode), -1)
            mayac.connectAttr("%s.BallPivot" %(self.RightFoot.IK_CTRL), "%s.input1X" %(self.RightFoot_BallPivot_MultNode), force = True)
            mayac.connectAttr("%s.outputX" %(self.RightFoot_BallPivot_MultNode), "%s.input1D[1]" %(Right_ToeBase_ZAdd), force = True)
            mayac.connectAttr("%s.outputX" %(self.RightFoot_BallPivot_MultNode), "%s.rotateY" %(self.Right_Ankle_IK_CTRL), force = True)
            
            self.RightFoot_ToePivot_MultNode = mayac.createNode( 'multiplyDivide', n="RightFoot_ToePivot_MultNode")
            mayac.setAttr("%s.input2X" %(self.RightFoot_ToePivot_MultNode), -1)
            mayac.connectAttr("%s.ToePivot" %(self.RightFoot.IK_CTRL), "%s.input1X" %(self.RightFoot_ToePivot_MultNode), force = True)
            mayac.connectAttr("%s.outputX" %(self.RightFoot_ToePivot_MultNode), "%s.rotateY" %(self.Right_Toe_IK_CTRL), force = True)
            
            self.RightFoot_HipSideToSide_MultNode = mayac.createNode( 'multiplyDivide', n="RightFoot_HipSideToSide_MultNode")
            mayac.setAttr("%s.input2X" %(self.RightFoot_HipSideToSide_MultNode), -1)
            mayac.connectAttr("%s.HipSideToSide" %(self.RightFoot.IK_CTRL), "%s.input1X" %(self.RightFoot_HipSideToSide_MultNode), force = True)
            mayac.connectAttr("%s.outputX" %(self.RightFoot_HipSideToSide_MultNode), "%s.rotateZ" %(self.RightFoot.IK_CTRL_grandparent_inRig_CONST_GRP), force = True)
            
            mayac.connectAttr("%s.HipBackToFront" %(self.RightFoot.IK_CTRL), "%s.rotateX" %(self.RightFoot.IK_CTRL_grandparent_inRig_CONST_GRP), force = True)


        
        
        #finger SDKs
        if self.rigType == "AutoRig":
            if self.LeftHandIndex1.Bind_Joint:
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.LeftHandIndex1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.IndexCurl"  % (self.LeftHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.LeftHandIndex1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.IndexCurl"  % (self.LeftHand.Options_CTRL), driverValue = 10.0, value = 90.0)
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.LeftHandIndex1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.IndexCurl"  % (self.LeftHand.Options_CTRL), driverValue = -10.0, value = -90.0)
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.LeftHandIndex2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.IndexCurl"  % (self.LeftHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.LeftHandIndex2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.IndexCurl"  % (self.LeftHand.Options_CTRL), driverValue = 10.0, value = 90.0)
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.LeftHandIndex2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.IndexCurl"  % (self.LeftHand.Options_CTRL), driverValue = -10.0, value = -90.0)
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.LeftHandIndex3.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.IndexCurl"  % (self.LeftHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.LeftHandIndex3.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.IndexCurl"  % (self.LeftHand.Options_CTRL), driverValue = 10.0, value = 90.0)
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.LeftHandIndex3.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.IndexCurl"  % (self.LeftHand.Options_CTRL), driverValue = -10.0, value = -90.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandIndex1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Sway"  % (self.LeftHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandIndex1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Sway"  % (self.LeftHand.Options_CTRL), driverValue = 10.0, value = 45.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandIndex1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Sway"  % (self.LeftHand.Options_CTRL), driverValue = -10.0, value = -45.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandIndex1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.LeftHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandIndex1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.LeftHand.Options_CTRL), driverValue = 10.0, value = -30.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandIndex1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.LeftHand.Options_CTRL), driverValue = -10.0, value = 12.0)
            else:
                mayac.deleteAttr("%s.IndexCurl"  % (self.LeftHand.Options_CTRL))
            if self.LeftHandMiddle1.Bind_Joint:
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.LeftHandMiddle1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.MiddleCurl"  % (self.LeftHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.LeftHandMiddle1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.MiddleCurl"  % (self.LeftHand.Options_CTRL), driverValue = 10.0, value = 90.0)
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.LeftHandMiddle1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.MiddleCurl"  % (self.LeftHand.Options_CTRL), driverValue = -10.0, value = -90.0)
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.LeftHandMiddle2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.MiddleCurl"  % (self.LeftHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.LeftHandMiddle2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.MiddleCurl"  % (self.LeftHand.Options_CTRL), driverValue = 10.0, value = 90.0)
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.LeftHandMiddle2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.MiddleCurl"  % (self.LeftHand.Options_CTRL), driverValue = -10.0, value = -90.0)
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.LeftHandMiddle3.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.MiddleCurl"  % (self.LeftHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.LeftHandMiddle3.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.MiddleCurl"  % (self.LeftHand.Options_CTRL), driverValue = 10.0, value = 90.0)
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.LeftHandMiddle3.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.MiddleCurl"  % (self.LeftHand.Options_CTRL), driverValue = -10.0, value = -90.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandMiddle1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Sway"  % (self.LeftHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandMiddle1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Sway"  % (self.LeftHand.Options_CTRL), driverValue = 10.0, value = 45.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandMiddle1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Sway"  % (self.LeftHand.Options_CTRL), driverValue = -10.0, value = -45.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandMiddle1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.LeftHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandMiddle1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.LeftHand.Options_CTRL), driverValue = 10.0, value = -10.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandMiddle1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.LeftHand.Options_CTRL), driverValue = -10.0, value = 3.0)
            else:
                mayac.deleteAttr("%s.MiddleCurl"  % (self.LeftHand.Options_CTRL))    
            if self.LeftHandRing1.Bind_Joint:
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.LeftHandRing1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.RingCurl"  % (self.LeftHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.LeftHandRing1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.RingCurl"  % (self.LeftHand.Options_CTRL), driverValue = 10.0, value = 90.0)
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.LeftHandRing1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.RingCurl"  % (self.LeftHand.Options_CTRL), driverValue = -10.0, value = -90.0)
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.LeftHandRing2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.RingCurl"  % (self.LeftHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.LeftHandRing2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.RingCurl"  % (self.LeftHand.Options_CTRL), driverValue = 10.0, value = 90.0)
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.LeftHandRing2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.RingCurl"  % (self.LeftHand.Options_CTRL), driverValue = -10.0, value = -90.0)
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.LeftHandRing3.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.RingCurl"  % (self.LeftHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.LeftHandRing3.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.RingCurl"  % (self.LeftHand.Options_CTRL), driverValue = 10.0, value = 90.0)
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.LeftHandRing3.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.RingCurl"  % (self.LeftHand.Options_CTRL), driverValue = -10.0, value = -90.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandRing1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Sway"  % (self.LeftHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandRing1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Sway"  % (self.LeftHand.Options_CTRL), driverValue = 10.0, value = 45.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandRing1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Sway"  % (self.LeftHand.Options_CTRL), driverValue = -10.0, value = -45.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandRing1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.LeftHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandRing1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.LeftHand.Options_CTRL), driverValue = 10.0, value = 15.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandRing1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.LeftHand.Options_CTRL), driverValue = -10.0, value = -5.0)
            else:
                mayac.deleteAttr("%s.RingCurl"  % (self.LeftHand.Options_CTRL))      
            if self.LeftHandPinky1.Bind_Joint:
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.LeftHandPinky1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.PinkyCurl"  % (self.LeftHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.LeftHandPinky1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.PinkyCurl"  % (self.LeftHand.Options_CTRL), driverValue = 10.0, value = 90.0)
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.LeftHandPinky1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.PinkyCurl"  % (self.LeftHand.Options_CTRL), driverValue = -10.0, value = -90.0)
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.LeftHandPinky2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.PinkyCurl"  % (self.LeftHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.LeftHandPinky2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.PinkyCurl"  % (self.LeftHand.Options_CTRL), driverValue = 10.0, value = 90.0)
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.LeftHandPinky2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.PinkyCurl"  % (self.LeftHand.Options_CTRL), driverValue = -10.0, value = -90.0)
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.LeftHandPinky3.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.PinkyCurl"  % (self.LeftHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.LeftHandPinky3.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.PinkyCurl"  % (self.LeftHand.Options_CTRL), driverValue = 10.0, value = 90.0)
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.LeftHandPinky3.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.PinkyCurl"  % (self.LeftHand.Options_CTRL), driverValue = -10.0, value = -90.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandPinky1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Sway"  % (self.LeftHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandPinky1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Sway"  % (self.LeftHand.Options_CTRL), driverValue = 10.0, value = 45.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandPinky1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Sway"  % (self.LeftHand.Options_CTRL), driverValue = -10.0, value = -45.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandPinky1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.LeftHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandPinky1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.LeftHand.Options_CTRL), driverValue = 10.0, value = 30.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandPinky1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.LeftHand.Options_CTRL), driverValue = -10.0, value = -13.0)
            else:
                mayac.deleteAttr("%s.PinkyCurl"  % (self.LeftHand.Options_CTRL))    
            if self.LeftHandThumb1.Bind_Joint:
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandThumb1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.ThumbCurl"  % (self.LeftHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandThumb1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.ThumbCurl"  % (self.LeftHand.Options_CTRL), driverValue = 10.0, value = 25.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandThumb1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.ThumbCurl"  % (self.LeftHand.Options_CTRL), driverValue = -10.0, value = -25.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandThumb2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.ThumbCurl"  % (self.LeftHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandThumb2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.ThumbCurl"  % (self.LeftHand.Options_CTRL), driverValue = 10.0, value = 60.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandThumb2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.ThumbCurl"  % (self.LeftHand.Options_CTRL), driverValue = -10.0, value = -60.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandThumb3.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.ThumbCurl"  % (self.LeftHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandThumb3.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.ThumbCurl"  % (self.LeftHand.Options_CTRL), driverValue = 10.0, value = 90.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandThumb3.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.ThumbCurl"  % (self.LeftHand.Options_CTRL), driverValue = -10.0, value = -90.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandThumb1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.LeftHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandThumb2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.LeftHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandThumb1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.LeftHand.Options_CTRL), driverValue = 10.0, value = -15.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandThumb1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.LeftHand.Options_CTRL), driverValue = -10.0, value = 15.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandThumb2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.LeftHand.Options_CTRL), driverValue = -10.0, value = 30.0)
            else:
                mayac.deleteAttr("%s.ThumbCurl"  % (self.LeftHand.Options_CTRL))
            if not self.LeftHandPinky1.Bind_Joint and not self.LeftHandRing1.Bind_Joint and not self.LeftHandMiddle1.Bind_Joint and not self.LeftHandIndex1.Bind_Joint:
                mayac.deleteAttr("%s.Sway"  % (self.LeftHand.Options_CTRL))
                if not self.LeftHandThumb1.Bind_Joint:
                    mayac.deleteAttr("%s.Spread"  % (self.LeftHand.Options_CTRL))
                    
                    
            if self.RightHandIndex1.Bind_Joint:
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.RightHandIndex1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.IndexCurl"  % (self.RightHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.RightHandIndex1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.IndexCurl"  % (self.RightHand.Options_CTRL), driverValue = 10.0, value = 90.0)
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.RightHandIndex1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.IndexCurl"  % (self.RightHand.Options_CTRL), driverValue = -10.0, value = -90.0)
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.RightHandIndex2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.IndexCurl"  % (self.RightHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.RightHandIndex2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.IndexCurl"  % (self.RightHand.Options_CTRL), driverValue = 10.0, value = 90.0)
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.RightHandIndex2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.IndexCurl"  % (self.RightHand.Options_CTRL), driverValue = -10.0, value = -90.0)
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.RightHandIndex3.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.IndexCurl"  % (self.RightHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.RightHandIndex3.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.IndexCurl"  % (self.RightHand.Options_CTRL), driverValue = 10.0, value = 90.0)
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.RightHandIndex3.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.IndexCurl"  % (self.RightHand.Options_CTRL), driverValue = -10.0, value = -90.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandIndex1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Sway"  % (self.RightHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandIndex1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Sway"  % (self.RightHand.Options_CTRL), driverValue = 10.0, value = -45.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandIndex1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Sway"  % (self.RightHand.Options_CTRL), driverValue = -10.0, value = 45.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandIndex1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.RightHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandIndex1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.RightHand.Options_CTRL), driverValue = 10.0, value = 30.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandIndex1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.RightHand.Options_CTRL), driverValue = -10.0, value = -12.0)
            else:
                mayac.deleteAttr("%s.IndexCurl"  % (self.RightHand.Options_CTRL))
            if self.RightHandMiddle1.Bind_Joint:
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.RightHandMiddle1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.MiddleCurl"  % (self.RightHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.RightHandMiddle1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.MiddleCurl"  % (self.RightHand.Options_CTRL), driverValue = 10.0, value = 90.0)
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.RightHandMiddle1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.MiddleCurl"  % (self.RightHand.Options_CTRL), driverValue = -10.0, value = -90.0)
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.RightHandMiddle2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.MiddleCurl"  % (self.RightHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.RightHandMiddle2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.MiddleCurl"  % (self.RightHand.Options_CTRL), driverValue = 10.0, value = 90.0)
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.RightHandMiddle2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.MiddleCurl"  % (self.RightHand.Options_CTRL), driverValue = -10.0, value = -90.0)
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.RightHandMiddle3.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.MiddleCurl"  % (self.RightHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.RightHandMiddle3.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.MiddleCurl"  % (self.RightHand.Options_CTRL), driverValue = 10.0, value = 90.0)
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.RightHandMiddle3.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.MiddleCurl"  % (self.RightHand.Options_CTRL), driverValue = -10.0, value = -90.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandMiddle1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Sway"  % (self.RightHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandMiddle1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Sway"  % (self.RightHand.Options_CTRL), driverValue = 10.0, value = -45.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandMiddle1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Sway"  % (self.RightHand.Options_CTRL), driverValue = -10.0, value = 45.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandMiddle1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.RightHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandMiddle1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.RightHand.Options_CTRL), driverValue = 10.0, value = 10.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandMiddle1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.RightHand.Options_CTRL), driverValue = -10.0, value = -3.0)
            else:
                mayac.deleteAttr("%s.MiddleCurl"  % (self.RightHand.Options_CTRL))    
            if self.RightHandRing1.Bind_Joint:
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.RightHandRing1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.RingCurl"  % (self.RightHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.RightHandRing1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.RingCurl"  % (self.RightHand.Options_CTRL), driverValue = 10.0, value = 90.0)
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.RightHandRing1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.RingCurl"  % (self.RightHand.Options_CTRL), driverValue = -10.0, value = -90.0)
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.RightHandRing2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.RingCurl"  % (self.RightHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.RightHandRing2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.RingCurl"  % (self.RightHand.Options_CTRL), driverValue = 10.0, value = 90.0)
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.RightHandRing2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.RingCurl"  % (self.RightHand.Options_CTRL), driverValue = -10.0, value = -90.0)
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.RightHandRing3.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.RingCurl"  % (self.RightHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.RightHandRing3.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.RingCurl"  % (self.RightHand.Options_CTRL), driverValue = 10.0, value = 90.0)
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.RightHandRing3.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.RingCurl"  % (self.RightHand.Options_CTRL), driverValue = -10.0, value = -90.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandRing1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Sway"  % (self.RightHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandRing1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Sway"  % (self.RightHand.Options_CTRL), driverValue = 10.0, value = -45.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandRing1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Sway"  % (self.RightHand.Options_CTRL), driverValue = -10.0, value = 45.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandRing1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.RightHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandRing1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.RightHand.Options_CTRL), driverValue = 10.0, value = -15.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandRing1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.RightHand.Options_CTRL), driverValue = -10.0, value = 5.0)
            else:
                mayac.deleteAttr("%s.RingCurl"  % (self.RightHand.Options_CTRL))      
            if self.RightHandPinky1.Bind_Joint:
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.RightHandPinky1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.PinkyCurl"  % (self.RightHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.RightHandPinky1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.PinkyCurl"  % (self.RightHand.Options_CTRL), driverValue = 10.0, value = 90.0)
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.RightHandPinky1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.PinkyCurl"  % (self.RightHand.Options_CTRL), driverValue = -10.0, value = -90.0)
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.RightHandPinky2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.PinkyCurl"  % (self.RightHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.RightHandPinky2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.PinkyCurl"  % (self.RightHand.Options_CTRL), driverValue = 10.0, value = 90.0)
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.RightHandPinky2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.PinkyCurl"  % (self.RightHand.Options_CTRL), driverValue = -10.0, value = -90.0)
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.RightHandPinky3.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.PinkyCurl"  % (self.RightHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.RightHandPinky3.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.PinkyCurl"  % (self.RightHand.Options_CTRL), driverValue = 10.0, value = 90.0)
                mayac.setDrivenKeyframe( "%s.rotateX" % (self.RightHandPinky3.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.PinkyCurl"  % (self.RightHand.Options_CTRL), driverValue = -10.0, value = -90.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandPinky1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Sway"  % (self.RightHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandPinky1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Sway"  % (self.RightHand.Options_CTRL), driverValue = 10.0, value = -45.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandPinky1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Sway"  % (self.RightHand.Options_CTRL), driverValue = -10.0, value = 45.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandPinky1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.RightHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandPinky1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.RightHand.Options_CTRL), driverValue = 10.0, value = -30.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandPinky1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.RightHand.Options_CTRL), driverValue = -10.0, value = 13.0)
            else:
                mayac.deleteAttr("%s.PinkyCurl"  % (self.RightHand.Options_CTRL))    
            if self.RightHandThumb1.Bind_Joint:
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandThumb1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.ThumbCurl"  % (self.RightHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandThumb1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.ThumbCurl"  % (self.RightHand.Options_CTRL), driverValue = 10.0, value = -25.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandThumb1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.ThumbCurl"  % (self.RightHand.Options_CTRL), driverValue = -10.0, value = 25.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandThumb2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.ThumbCurl"  % (self.RightHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandThumb2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.ThumbCurl"  % (self.RightHand.Options_CTRL), driverValue = 10.0, value = -60.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandThumb2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.ThumbCurl"  % (self.RightHand.Options_CTRL), driverValue = -10.0, value = 60.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandThumb3.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.ThumbCurl"  % (self.RightHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandThumb3.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.ThumbCurl"  % (self.RightHand.Options_CTRL), driverValue = 10.0, value = -90.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandThumb3.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.ThumbCurl"  % (self.RightHand.Options_CTRL), driverValue = -10.0, value = 90.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandThumb1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.RightHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandThumb2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.RightHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandThumb1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.RightHand.Options_CTRL), driverValue = 10.0, value = 15.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandThumb1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.RightHand.Options_CTRL), driverValue = -10.0, value = -15.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandThumb2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.RightHand.Options_CTRL), driverValue = -10.0, value = -30.0)
            else:
                mayac.deleteAttr("%s.ThumbCurl"  % (self.RightHand.Options_CTRL))
            if not self.RightHandPinky1.Bind_Joint and not self.RightHandRing1.Bind_Joint and not self.RightHandMiddle1.Bind_Joint and not self.RightHandIndex1.Bind_Joint:
                mayac.deleteAttr("%s.Sway"  % (self.RightHand.Options_CTRL))
                if not self.RightHandThumb1.Bind_Joint:
                    mayac.deleteAttr("%s.Spread"  % (self.RightHand.Options_CTRL))

        elif self.rigType == "World":
            if self.LeftHandIndex1.Bind_Joint:
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandIndex1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.IndexCurl"  % (self.LeftHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandIndex1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.IndexCurl"  % (self.LeftHand.Options_CTRL), driverValue = 10.0, value = -90.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandIndex1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.IndexCurl"  % (self.LeftHand.Options_CTRL), driverValue = -10.0, value = 90.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandIndex2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.IndexCurl"  % (self.LeftHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandIndex2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.IndexCurl"  % (self.LeftHand.Options_CTRL), driverValue = 10.0, value = -90.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandIndex2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.IndexCurl"  % (self.LeftHand.Options_CTRL), driverValue = -10.0, value = 90.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandIndex3.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.IndexCurl"  % (self.LeftHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandIndex3.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.IndexCurl"  % (self.LeftHand.Options_CTRL), driverValue = 10.0, value = -90.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandIndex3.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.IndexCurl"  % (self.LeftHand.Options_CTRL), driverValue = -10.0, value = 90.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.LeftHandIndex1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Sway"  % (self.LeftHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.LeftHandIndex1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Sway"  % (self.LeftHand.Options_CTRL), driverValue = 10.0, value = 45.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.LeftHandIndex1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Sway"  % (self.LeftHand.Options_CTRL), driverValue = -10.0, value = -45.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.LeftHandIndex1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.LeftHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.LeftHandIndex1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.LeftHand.Options_CTRL), driverValue = 10.0, value = -30.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.LeftHandIndex1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.LeftHand.Options_CTRL), driverValue = -10.0, value = 12.0)
            else:
                mayac.deleteAttr("%s.IndexCurl"  % (self.LeftHand.Options_CTRL))
            if self.LeftHandMiddle1.Bind_Joint:
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandMiddle1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.MiddleCurl"  % (self.LeftHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandMiddle1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.MiddleCurl"  % (self.LeftHand.Options_CTRL), driverValue = 10.0, value = -90.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandMiddle1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.MiddleCurl"  % (self.LeftHand.Options_CTRL), driverValue = -10.0, value = 90.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandMiddle2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.MiddleCurl"  % (self.LeftHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandMiddle2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.MiddleCurl"  % (self.LeftHand.Options_CTRL), driverValue = 10.0, value = -90.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandMiddle2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.MiddleCurl"  % (self.LeftHand.Options_CTRL), driverValue = -10.0, value = 90.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandMiddle3.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.MiddleCurl"  % (self.LeftHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandMiddle3.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.MiddleCurl"  % (self.LeftHand.Options_CTRL), driverValue = 10.0, value = -90.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandMiddle3.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.MiddleCurl"  % (self.LeftHand.Options_CTRL), driverValue = -10.0, value = 90.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.LeftHandMiddle1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Sway"  % (self.LeftHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.LeftHandMiddle1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Sway"  % (self.LeftHand.Options_CTRL), driverValue = 10.0, value = 45.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.LeftHandMiddle1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Sway"  % (self.LeftHand.Options_CTRL), driverValue = -10.0, value = -45.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.LeftHandMiddle1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.LeftHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.LeftHandMiddle1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.LeftHand.Options_CTRL), driverValue = 10.0, value = -10.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.LeftHandMiddle1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.LeftHand.Options_CTRL), driverValue = -10.0, value = 3.0)
            else:
                mayac.deleteAttr("%s.MiddleCurl"  % (self.LeftHand.Options_CTRL))    
            if self.LeftHandRing1.Bind_Joint:
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandRing1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.RingCurl"  % (self.LeftHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandRing1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.RingCurl"  % (self.LeftHand.Options_CTRL), driverValue = 10.0, value = -90.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandRing1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.RingCurl"  % (self.LeftHand.Options_CTRL), driverValue = -10.0, value = 90.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandRing2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.RingCurl"  % (self.LeftHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandRing2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.RingCurl"  % (self.LeftHand.Options_CTRL), driverValue = 10.0, value = -90.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandRing2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.RingCurl"  % (self.LeftHand.Options_CTRL), driverValue = -10.0, value = 90.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandRing3.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.RingCurl"  % (self.LeftHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandRing3.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.RingCurl"  % (self.LeftHand.Options_CTRL), driverValue = 10.0, value = -90.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandRing3.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.RingCurl"  % (self.LeftHand.Options_CTRL), driverValue = -10.0, value = 90.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.LeftHandRing1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Sway"  % (self.LeftHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.LeftHandRing1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Sway"  % (self.LeftHand.Options_CTRL), driverValue = 10.0, value = 45.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.LeftHandRing1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Sway"  % (self.LeftHand.Options_CTRL), driverValue = -10.0, value = -45.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.LeftHandRing1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.LeftHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.LeftHandRing1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.LeftHand.Options_CTRL), driverValue = 10.0, value = 15.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.LeftHandRing1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.LeftHand.Options_CTRL), driverValue = -10.0, value = -5.0)
            else:
                mayac.deleteAttr("%s.RingCurl"  % (self.LeftHand.Options_CTRL))      
            if self.LeftHandPinky1.Bind_Joint:
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandPinky1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.PinkyCurl"  % (self.LeftHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandPinky1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.PinkyCurl"  % (self.LeftHand.Options_CTRL), driverValue = 10.0, value = -90.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandPinky1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.PinkyCurl"  % (self.LeftHand.Options_CTRL), driverValue = -10.0, value = 90.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandPinky2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.PinkyCurl"  % (self.LeftHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandPinky2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.PinkyCurl"  % (self.LeftHand.Options_CTRL), driverValue = 10.0, value = -90.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandPinky2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.PinkyCurl"  % (self.LeftHand.Options_CTRL), driverValue = -10.0, value = 90.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandPinky3.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.PinkyCurl"  % (self.LeftHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandPinky3.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.PinkyCurl"  % (self.LeftHand.Options_CTRL), driverValue = 10.0, value = -90.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.LeftHandPinky3.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.PinkyCurl"  % (self.LeftHand.Options_CTRL), driverValue = -10.0, value = 90.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.LeftHandPinky1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Sway"  % (self.LeftHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.LeftHandPinky1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Sway"  % (self.LeftHand.Options_CTRL), driverValue = 10.0, value = 45.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.LeftHandPinky1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Sway"  % (self.LeftHand.Options_CTRL), driverValue = -10.0, value = -45.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.LeftHandPinky1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.LeftHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.LeftHandPinky1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.LeftHand.Options_CTRL), driverValue = 10.0, value = 30.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.LeftHandPinky1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.LeftHand.Options_CTRL), driverValue = -10.0, value = -13.0)
            else:
                mayac.deleteAttr("%s.PinkyCurl"  % (self.LeftHand.Options_CTRL))    
            if self.LeftHandThumb1.Bind_Joint:
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.LeftHandThumb1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.ThumbCurl"  % (self.LeftHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.LeftHandThumb1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.ThumbCurl"  % (self.LeftHand.Options_CTRL), driverValue = 10.0, value = 25.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.LeftHandThumb1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.ThumbCurl"  % (self.LeftHand.Options_CTRL), driverValue = -10.0, value = -25.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.LeftHandThumb2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.ThumbCurl"  % (self.LeftHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.LeftHandThumb2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.ThumbCurl"  % (self.LeftHand.Options_CTRL), driverValue = 10.0, value = 60.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.LeftHandThumb2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.ThumbCurl"  % (self.LeftHand.Options_CTRL), driverValue = -10.0, value = -60.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.LeftHandThumb3.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.ThumbCurl"  % (self.LeftHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.LeftHandThumb3.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.ThumbCurl"  % (self.LeftHand.Options_CTRL), driverValue = 10.0, value = 90.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.LeftHandThumb3.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.ThumbCurl"  % (self.LeftHand.Options_CTRL), driverValue = -10.0, value = -90.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.LeftHandThumb1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.LeftHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.LeftHandThumb2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.LeftHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.LeftHandThumb1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.LeftHand.Options_CTRL), driverValue = 10.0, value = -15.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.LeftHandThumb1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.LeftHand.Options_CTRL), driverValue = -10.0, value = 15.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.LeftHandThumb2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.LeftHand.Options_CTRL), driverValue = -10.0, value = 30.0)
            else:
                mayac.deleteAttr("%s.ThumbCurl"  % (self.LeftHand.Options_CTRL))
            if not self.LeftHandPinky1.Bind_Joint and not self.LeftHandRing1.Bind_Joint and not self.LeftHandMiddle1.Bind_Joint and not self.LeftHandIndex1.Bind_Joint:
                mayac.deleteAttr("%s.Sway"  % (self.LeftHand.Options_CTRL))
                if not self.LeftHandThumb1.Bind_Joint:
                    mayac.deleteAttr("%s.Spread"  % (self.LeftHand.Options_CTRL))
                    
                    
            if self.RightHandIndex1.Bind_Joint:
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandIndex1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.IndexCurl"  % (self.RightHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandIndex1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.IndexCurl"  % (self.RightHand.Options_CTRL), driverValue = 10.0, value = 90.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandIndex1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.IndexCurl"  % (self.RightHand.Options_CTRL), driverValue = -10.0, value = -90.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandIndex2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.IndexCurl"  % (self.RightHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandIndex2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.IndexCurl"  % (self.RightHand.Options_CTRL), driverValue = 10.0, value = 90.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandIndex2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.IndexCurl"  % (self.RightHand.Options_CTRL), driverValue = -10.0, value = -90.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandIndex3.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.IndexCurl"  % (self.RightHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandIndex3.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.IndexCurl"  % (self.RightHand.Options_CTRL), driverValue = 10.0, value = 90.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandIndex3.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.IndexCurl"  % (self.RightHand.Options_CTRL), driverValue = -10.0, value = -90.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.RightHandIndex1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Sway"  % (self.RightHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.RightHandIndex1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Sway"  % (self.RightHand.Options_CTRL), driverValue = 10.0, value = -45.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.RightHandIndex1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Sway"  % (self.RightHand.Options_CTRL), driverValue = -10.0, value = 45.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.RightHandIndex1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.RightHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.RightHandIndex1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.RightHand.Options_CTRL), driverValue = 10.0, value = 30.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.RightHandIndex1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.RightHand.Options_CTRL), driverValue = -10.0, value = -12.0)
            else:
                mayac.deleteAttr("%s.IndexCurl"  % (self.RightHand.Options_CTRL))
            if self.RightHandMiddle1.Bind_Joint:
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandMiddle1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.MiddleCurl"  % (self.RightHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandMiddle1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.MiddleCurl"  % (self.RightHand.Options_CTRL), driverValue = 10.0, value = 90.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandMiddle1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.MiddleCurl"  % (self.RightHand.Options_CTRL), driverValue = -10.0, value = -90.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandMiddle2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.MiddleCurl"  % (self.RightHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandMiddle2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.MiddleCurl"  % (self.RightHand.Options_CTRL), driverValue = 10.0, value = 90.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandMiddle2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.MiddleCurl"  % (self.RightHand.Options_CTRL), driverValue = -10.0, value = -90.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandMiddle3.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.MiddleCurl"  % (self.RightHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandMiddle3.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.MiddleCurl"  % (self.RightHand.Options_CTRL), driverValue = 10.0, value = 90.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandMiddle3.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.MiddleCurl"  % (self.RightHand.Options_CTRL), driverValue = -10.0, value = -90.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.RightHandMiddle1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Sway"  % (self.RightHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.RightHandMiddle1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Sway"  % (self.RightHand.Options_CTRL), driverValue = 10.0, value = -45.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.RightHandMiddle1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Sway"  % (self.RightHand.Options_CTRL), driverValue = -10.0, value = 45.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.RightHandMiddle1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.RightHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.RightHandMiddle1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.RightHand.Options_CTRL), driverValue = 10.0, value = 10.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.RightHandMiddle1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.RightHand.Options_CTRL), driverValue = -10.0, value = -3.0)
            else:
                mayac.deleteAttr("%s.MiddleCurl"  % (self.RightHand.Options_CTRL))    
            if self.RightHandRing1.Bind_Joint:
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandRing1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.RingCurl"  % (self.RightHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandRing1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.RingCurl"  % (self.RightHand.Options_CTRL), driverValue = 10.0, value = 90.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandRing1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.RingCurl"  % (self.RightHand.Options_CTRL), driverValue = -10.0, value = -90.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandRing2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.RingCurl"  % (self.RightHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandRing2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.RingCurl"  % (self.RightHand.Options_CTRL), driverValue = 10.0, value = 90.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandRing2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.RingCurl"  % (self.RightHand.Options_CTRL), driverValue = -10.0, value = -90.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandRing3.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.RingCurl"  % (self.RightHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandRing3.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.RingCurl"  % (self.RightHand.Options_CTRL), driverValue = 10.0, value = 90.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandRing3.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.RingCurl"  % (self.RightHand.Options_CTRL), driverValue = -10.0, value = -90.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.RightHandRing1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Sway"  % (self.RightHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.RightHandRing1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Sway"  % (self.RightHand.Options_CTRL), driverValue = 10.0, value = -45.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.RightHandRing1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Sway"  % (self.RightHand.Options_CTRL), driverValue = -10.0, value = 45.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.RightHandRing1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.RightHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.RightHandRing1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.RightHand.Options_CTRL), driverValue = 10.0, value = -15.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.RightHandRing1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.RightHand.Options_CTRL), driverValue = -10.0, value = 5.0)
            else:
                mayac.deleteAttr("%s.RingCurl"  % (self.RightHand.Options_CTRL))      
            if self.RightHandPinky1.Bind_Joint:
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandPinky1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.PinkyCurl"  % (self.RightHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandPinky1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.PinkyCurl"  % (self.RightHand.Options_CTRL), driverValue = 10.0, value = 90.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandPinky1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.PinkyCurl"  % (self.RightHand.Options_CTRL), driverValue = -10.0, value = -90.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandPinky2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.PinkyCurl"  % (self.RightHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandPinky2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.PinkyCurl"  % (self.RightHand.Options_CTRL), driverValue = 10.0, value = 90.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandPinky2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.PinkyCurl"  % (self.RightHand.Options_CTRL), driverValue = -10.0, value = -90.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandPinky3.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.PinkyCurl"  % (self.RightHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandPinky3.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.PinkyCurl"  % (self.RightHand.Options_CTRL), driverValue = 10.0, value = 90.0)
                mayac.setDrivenKeyframe( "%s.rotateZ" % (self.RightHandPinky3.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.PinkyCurl"  % (self.RightHand.Options_CTRL), driverValue = -10.0, value = -90.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.RightHandPinky1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Sway"  % (self.RightHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.RightHandPinky1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Sway"  % (self.RightHand.Options_CTRL), driverValue = 10.0, value = -45.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.RightHandPinky1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Sway"  % (self.RightHand.Options_CTRL), driverValue = -10.0, value = 45.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.RightHandPinky1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.RightHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.RightHandPinky1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.RightHand.Options_CTRL), driverValue = 10.0, value = -30.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.RightHandPinky1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.RightHand.Options_CTRL), driverValue = -10.0, value = 13.0)
            else:
                mayac.deleteAttr("%s.PinkyCurl"  % (self.RightHand.Options_CTRL))    
            if self.RightHandThumb1.Bind_Joint:
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.RightHandThumb1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.ThumbCurl"  % (self.RightHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.RightHandThumb1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.ThumbCurl"  % (self.RightHand.Options_CTRL), driverValue = 10.0, value = -25.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.RightHandThumb1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.ThumbCurl"  % (self.RightHand.Options_CTRL), driverValue = -10.0, value = 25.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.RightHandThumb2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.ThumbCurl"  % (self.RightHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.RightHandThumb2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.ThumbCurl"  % (self.RightHand.Options_CTRL), driverValue = 10.0, value = -60.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.RightHandThumb2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.ThumbCurl"  % (self.RightHand.Options_CTRL), driverValue = -10.0, value = 60.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.RightHandThumb3.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.ThumbCurl"  % (self.RightHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.RightHandThumb3.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.ThumbCurl"  % (self.RightHand.Options_CTRL), driverValue = 10.0, value = -90.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.RightHandThumb3.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.ThumbCurl"  % (self.RightHand.Options_CTRL), driverValue = -10.0, value = 90.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.RightHandThumb1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.RightHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.RightHandThumb2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.RightHand.Options_CTRL), driverValue = 0.0, value = 0.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.RightHandThumb1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.RightHand.Options_CTRL), driverValue = 10.0, value = 15.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.RightHandThumb1.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.RightHand.Options_CTRL), driverValue = -10.0, value = -15.0)
                mayac.setDrivenKeyframe( "%s.rotateY" % (self.RightHandThumb2.FK_CTRL_inRig_CONST_GRP), currentDriver="%s.Spread"  % (self.RightHand.Options_CTRL), driverValue = -10.0, value = -30.0)
            else:
                mayac.deleteAttr("%s.ThumbCurl"  % (self.RightHand.Options_CTRL))
            if not self.RightHandPinky1.Bind_Joint and not self.RightHandRing1.Bind_Joint and not self.RightHandMiddle1.Bind_Joint and not self.RightHandIndex1.Bind_Joint:
                mayac.deleteAttr("%s.Sway"  % (self.RightHand.Options_CTRL))
                if not self.RightHandThumb1.Bind_Joint:
                    mayac.deleteAttr("%s.Spread"  % (self.RightHand.Options_CTRL))
            
            

        
        #global scale
        mayac.scaleConstraint(self.global_CTRL, self.Joint_GRP, name = "Global_Scale_Constraint")
        
        #IKFK switches
        self.LeftArm_Switch_Reverse = mayac.createNode( 'reverse', n="LeftArm_Switch_Reverse")
        self.RightArm_Switch_Reverse = mayac.createNode( 'reverse', n="RightArm_Switch_Reverse")
        self.LeftLeg_Switch_Reverse = mayac.createNode( 'reverse', n="LeftLeg_Switch_Reverse")
        self.RightLeg_Switch_Reverse = mayac.createNode( 'reverse', n="RightLeg_Switch_Reverse")
        mayac.connectAttr("%s.FK_IK" %(self.LeftHand.Options_CTRL), "%s.inputX" %(self.LeftArm_Switch_Reverse))
        mayac.connectAttr("%s.FK_IK" %(self.RightHand.Options_CTRL), "%s.inputX" %(self.RightArm_Switch_Reverse))
        mayac.connectAttr("%s.FK_IK" %(self.LeftFoot.Options_CTRL), "%s.inputX" %(self.LeftLeg_Switch_Reverse))
        mayac.connectAttr("%s.FK_IK" %(self.RightFoot.Options_CTRL), "%s.inputX" %(self.RightLeg_Switch_Reverse))
        
        mayac.setAttr("%s.interpType" %(self.LeftArm.Constraint), 2)
        mayac.setAttr("%s.interpType" %(self.LeftForeArm.Constraint), 2)
        mayac.setAttr("%s.interpType" %(self.LeftHand.Constraint), 2)
        mayac.setAttr("%s.interpType" %(self.RightArm.Constraint), 2)
        mayac.setAttr("%s.interpType" %(self.RightForeArm.Constraint), 2)
        mayac.setAttr("%s.interpType" %(self.RightHand.Constraint), 2)
        mayac.setAttr("%s.interpType" %(self.LeftUpLeg.Constraint), 2)
        mayac.setAttr("%s.interpType" %(self.LeftLeg.Constraint), 2)
        mayac.setAttr("%s.interpType" %(self.LeftFoot.Constraint), 2)
        mayac.setAttr("%s.interpType" %(self.LeftToeBase.Constraint), 2)
        mayac.setAttr("%s.interpType" %(self.RightUpLeg.Constraint), 2)
        mayac.setAttr("%s.interpType" %(self.RightLeg.Constraint), 2)
        mayac.setAttr("%s.interpType" %(self.RightFoot.Constraint), 2)
        mayac.setAttr("%s.interpType" %(self.RightToeBase.Constraint), 2)
        
        mayac.connectAttr("%s.FK_IK" %(self.LeftHand.Options_CTRL), "%s.%sW1" %(self.LeftArm.Constraint, self.LeftArm.IK_Joint))
        mayac.connectAttr("%s.outputX" %(self.LeftArm_Switch_Reverse), "%s.%sW0" %(self.LeftArm.Constraint, self.LeftArm.FK_Joint))
        mayac.connectAttr("%s.FK_IK" %(self.LeftHand.Options_CTRL), "%s.%sW1" %(self.LeftForeArm.Constraint, self.LeftForeArm.IK_Joint))
        mayac.connectAttr("%s.outputX" %(self.LeftArm_Switch_Reverse), "%s.%sW0" %(self.LeftForeArm.Constraint, self.LeftForeArm.FK_Joint))
        mayac.connectAttr("%s.FK_IK" %(self.LeftHand.Options_CTRL), "%s.%sW1" %(self.LeftHand.Constraint, self.LeftHand.IK_Joint))
        mayac.connectAttr("%s.outputX" %(self.LeftArm_Switch_Reverse), "%s.%sW0" %(self.LeftHand.Constraint, self.LeftHand.FK_Joint))
        mayac.connectAttr("%s.FK_IK" %(self.RightHand.Options_CTRL), "%s.%sW1" %(self.RightArm.Constraint, self.RightArm.IK_Joint))
        mayac.connectAttr("%s.outputX" %(self.RightArm_Switch_Reverse), "%s.%sW0" %(self.RightArm.Constraint, self.RightArm.FK_Joint))
        mayac.connectAttr("%s.FK_IK" %(self.RightHand.Options_CTRL), "%s.%sW1" %(self.RightForeArm.Constraint, self.RightForeArm.IK_Joint))
        mayac.connectAttr("%s.outputX" %(self.RightArm_Switch_Reverse), "%s.%sW0" %(self.RightForeArm.Constraint, self.RightForeArm.FK_Joint))
        mayac.connectAttr("%s.FK_IK" %(self.RightHand.Options_CTRL), "%s.%sW1" %(self.RightHand.Constraint, self.RightHand.IK_Joint))
        mayac.connectAttr("%s.outputX" %(self.RightArm_Switch_Reverse), "%s.%sW0" %(self.RightHand.Constraint, self.RightHand.FK_Joint))
        
        mayac.connectAttr("%s.FK_IK" %(self.LeftFoot.Options_CTRL), "%s.%sW1" %(self.LeftUpLeg.Constraint, self.LeftUpLeg.IK_Joint))
        mayac.connectAttr("%s.outputX" %(self.LeftLeg_Switch_Reverse), "%s.%sW0" %(self.LeftUpLeg.Constraint, self.LeftUpLeg.FK_Joint))
        mayac.connectAttr("%s.FK_IK" %(self.LeftFoot.Options_CTRL), "%s.%sW1" %(self.LeftLeg.Constraint, self.LeftLeg.IK_Joint))
        mayac.connectAttr("%s.outputX" %(self.LeftLeg_Switch_Reverse), "%s.%sW0" %(self.LeftLeg.Constraint, self.LeftLeg.FK_Joint))
        mayac.connectAttr("%s.FK_IK" %(self.LeftFoot.Options_CTRL), "%s.%sW1" %(self.LeftFoot.Constraint, self.LeftFoot.IK_Joint))
        mayac.connectAttr("%s.outputX" %(self.LeftLeg_Switch_Reverse), "%s.%sW0" %(self.LeftFoot.Constraint, self.LeftFoot.FK_Joint))
        mayac.connectAttr("%s.FK_IK" %(self.LeftFoot.Options_CTRL), "%s.%sW1" %(self.LeftToeBase.Constraint, self.LeftToeBase.IK_Joint))
        mayac.connectAttr("%s.outputX" %(self.LeftLeg_Switch_Reverse), "%s.%sW0" %(self.LeftToeBase.Constraint, self.LeftToeBase.FK_Joint))
        mayac.connectAttr("%s.FK_IK" %(self.RightFoot.Options_CTRL), "%s.%sW1" %(self.RightUpLeg.Constraint, self.RightUpLeg.IK_Joint))
        mayac.connectAttr("%s.outputX" %(self.RightLeg_Switch_Reverse), "%s.%sW0" %(self.RightUpLeg.Constraint, self.RightUpLeg.FK_Joint))
        mayac.connectAttr("%s.FK_IK" %(self.RightFoot.Options_CTRL), "%s.%sW1" %(self.RightLeg.Constraint, self.RightLeg.IK_Joint))
        mayac.connectAttr("%s.outputX" %(self.RightLeg_Switch_Reverse), "%s.%sW0" %(self.RightLeg.Constraint, self.RightLeg.FK_Joint))
        mayac.connectAttr("%s.FK_IK" %(self.RightFoot.Options_CTRL), "%s.%sW1" %(self.RightFoot.Constraint, self.RightFoot.IK_Joint))
        mayac.connectAttr("%s.outputX" %(self.RightLeg_Switch_Reverse), "%s.%sW0" %(self.RightFoot.Constraint, self.RightFoot.FK_Joint))
        mayac.connectAttr("%s.FK_IK" %(self.RightFoot.Options_CTRL), "%s.%sW1" %(self.RightToeBase.Constraint, self.RightToeBase.IK_Joint))
        mayac.connectAttr("%s.outputX" %(self.RightLeg_Switch_Reverse), "%s.%sW0" %(self.RightToeBase.Constraint, self.RightToeBase.FK_Joint))
        
        #FKIK Visibilities
        DJB_Unlock_Connect_Lock("%s.FK_IK" %(self.LeftHand.Options_CTRL), "%s.visibility" %(self.LeftArm.IK_Joint))
        DJB_Unlock_Connect_Lock("%s.FK_IK" %(self.LeftHand.Options_CTRL), "%s.visibility" %(self.LeftForeArm.IK_CTRL_POS_GRP))
        DJB_Unlock_Connect_Lock("%s.FK_IK" %(self.LeftHand.Options_CTRL), "%s.visibility" %(self.LeftHand.IK_CTRL_POS_GRP))
        DJB_Unlock_Connect_Lock("%s.FK_IK" %(self.RightHand.Options_CTRL), "%s.visibility" %(self.RightArm.IK_Joint))
        DJB_Unlock_Connect_Lock("%s.FK_IK" %(self.RightHand.Options_CTRL), "%s.visibility" %(self.RightForeArm.IK_CTRL_POS_GRP))
        DJB_Unlock_Connect_Lock("%s.FK_IK" %(self.RightHand.Options_CTRL), "%s.visibility" %(self.RightHand.IK_CTRL_POS_GRP))

        DJB_Unlock_Connect_Lock("%s.FK_IK" %(self.LeftFoot.Options_CTRL), "%s.visibility" %(self.LeftUpLeg.IK_Joint))
        DJB_Unlock_Connect_Lock("%s.FK_IK" %(self.LeftFoot.Options_CTRL), "%s.visibility" %(self.LeftLeg.IK_CTRL_POS_GRP))
        DJB_Unlock_Connect_Lock("%s.FK_IK" %(self.LeftFoot.Options_CTRL), "%s.visibility" %(self.LeftFoot.IK_CTRL_POS_GRP))
        DJB_Unlock_Connect_Lock("%s.FK_IK" %(self.RightFoot.Options_CTRL), "%s.visibility" %(self.RightUpLeg.IK_Joint))
        DJB_Unlock_Connect_Lock("%s.FK_IK" %(self.RightFoot.Options_CTRL), "%s.visibility" %(self.RightLeg.IK_CTRL_POS_GRP))
        DJB_Unlock_Connect_Lock("%s.FK_IK" %(self.RightFoot.Options_CTRL), "%s.visibility" %(self.RightFoot.IK_CTRL_POS_GRP))
     
        DJB_Unlock_Connect_Lock("%s.outputX" %(self.LeftArm_Switch_Reverse), "%s.visibility" %(self.LeftArm.FK_Joint))
        DJB_Unlock_Connect_Lock("%s.outputX" %(self.LeftArm_Switch_Reverse), "%s.visibility" %(self.LeftArm.FK_CTRL_POS_GRP))
        DJB_Unlock_Connect_Lock("%s.outputX" %(self.RightArm_Switch_Reverse), "%s.visibility" %(self.RightArm.FK_Joint))
        DJB_Unlock_Connect_Lock("%s.outputX" %(self.RightArm_Switch_Reverse), "%s.visibility" %(self.RightArm.FK_CTRL_POS_GRP))
        
        DJB_Unlock_Connect_Lock("%s.outputX" %(self.LeftLeg_Switch_Reverse), "%s.visibility" %(self.LeftUpLeg.FK_Joint))
        DJB_Unlock_Connect_Lock("%s.outputX" %(self.LeftLeg_Switch_Reverse), "%s.visibility" %(self.LeftUpLeg.FK_CTRL_POS_GRP))
        DJB_Unlock_Connect_Lock("%s.outputX" %(self.RightLeg_Switch_Reverse), "%s.visibility" %(self.RightUpLeg.FK_Joint))
        DJB_Unlock_Connect_Lock("%s.outputX" %(self.RightLeg_Switch_Reverse), "%s.visibility" %(self.RightUpLeg.FK_CTRL_POS_GRP))
        
        mayac.select(clear = True)
        self.Misc_GRP = mayac.group(em = True, name = "Misc_GRP", world = True)
        DJB_movePivotToObject(self.Misc_GRP, self.global_CTRL)
        mayac.parent(self.Misc_GRP, self.Character_GRP)
        self.LeftForeArm.createGuideCurve(self.Misc_GRP, optionsCTRL = self.LeftHand.Options_CTRL)
        self.RightForeArm.createGuideCurve(self.Misc_GRP, optionsCTRL = self.RightHand.Options_CTRL)
        self.LeftLeg.createGuideCurve(self.Misc_GRP, optionsCTRL = self.LeftFoot.Options_CTRL)
        self.RightLeg.createGuideCurve(self.Misc_GRP, optionsCTRL = self.RightFoot.Options_CTRL)

        #Layers
        mayac.select(clear = True)
        self.Mesh_Layer = mayac.createDisplayLayer(name = "MeshLayer", number = 1)
        mayac.editDisplayLayerMembers(self.Mesh_Layer, self.Mesh_GRP)
        self.Bind_Joint_Layer = mayac.createDisplayLayer(name = "BindJointLayer", number = 2)
        mayac.editDisplayLayerMembers(self.Bind_Joint_Layer, self.Bind_Joint_GRP)
        #self.AnimData_Joint_Layer = mayac.createDisplayLayer(name = "AnimDataJointLayer", number = 3)
        #mayac.editDisplayLayerMembers(self.AnimData_Joint_Layer, self.AnimData_Joint_GRP)
        mayac.setAttr("%s.visibility" % (self.AnimData_Joint_GRP), 0)
        self.Control_Layer = mayac.createDisplayLayer(name = "ControlLayer", number = 4)
        mayac.editDisplayLayerMembers(self.Control_Layer, self.CTRL_GRP)
        mayac.editDisplayLayerMembers(self.Control_Layer, self.Misc_GRP)
        mayac.setAttr("%s.visibility" %(self.Mesh_Layer), 1)
        mayac.setAttr("%s.displayType" %(self.Mesh_Layer), 2)
        mayac.setAttr("%s.visibility" %(self.Bind_Joint_Layer), 1)
        mayac.setAttr("%s.displayType" %(self.Bind_Joint_Layer), 2)
        #mayac.setAttr("%s.visibility" %(self.AnimData_Joint_Layer), 0)
        #mayac.setAttr("%s.displayType" %(self.AnimData_Joint_Layer), 2)
        
        for bodyPart in self.bodyParts:
            bodyPart.fixAllLayerOverrides(self.Control_Layer)
        self.Hips.fixLayerOverrides(self.global_CTRL, "black", self.Control_Layer)
        self.Hips.fixLayerOverrides(self.LeftForeArm.Guide_Curve, "black", self.Control_Layer, referenceAlways = True)
        self.Hips.fixLayerOverrides(self.RightForeArm.Guide_Curve, "black", self.Control_Layer, referenceAlways = True)
        self.Hips.fixLayerOverrides(self.LeftLeg.Guide_Curve, "black", self.Control_Layer, referenceAlways = True)
        self.Hips.fixLayerOverrides(self.RightLeg.Guide_Curve, "black", self.Control_Layer, referenceAlways = True)
         
         
        #quick select sets
        mayac.select(clear = True)
        for bodyPart in self.bodyParts:
            if bodyPart.Bind_Joint:
                mayac.select(bodyPart.Bind_Joint, add = True)
        self.Bind_Joint_SelectSet = mayac.sets(text = "gCharacterSet", name = "Bind_Joint_SelectSet")
        #mayac.select(clear = True)
        #for bodyPart in self.bodyParts:
            #if bodyPart.AnimData_Joint:
                #mayac.select(bodyPart.AnimData_Joint, add = True)
        #self.AnimData_Joint_SelectSet = mayac.sets(text = "gCharacterSet", name = "AnimData_Joint_SelectSet")
        mayac.select(clear = True)
        for bodyPart in self.bodyParts:
            if bodyPart.FK_CTRL:
                mayac.select(bodyPart.FK_CTRL, add = True)
            if bodyPart.IK_CTRL:
                mayac.select(bodyPart.IK_CTRL, add = True)
            if bodyPart.Options_CTRL:
                mayac.select(bodyPart.Options_CTRL, add = True)
        mayac.select(self.global_CTRL, add = True)
        self.Controls_SelectSet = mayac.sets(text = "gCharacterSet", name = "Controls_SelectSet")
        mayac.select(clear = True)
        for geo in self.mesh:
            mayac.select(geo, add = True)
        self.Geo_SelectSet = mayac.sets(text = "gCharacterSet", name = "Geo_SelectSet")
        mayac.select(clear = True)
        
        #Cleanup
        mayac.delete(self.LeftFoot.footRotateLOC)
        mayac.delete(self.RightFoot.footRotateLOC)
        DJB_LockNHide(self.Character_GRP)
        DJB_LockNHide(self.CTRL_GRP)
        DJB_LockNHide(self.Joint_GRP)
        DJB_LockNHide(self.Bind_Joint_GRP)
        DJB_LockNHide(self.AnimData_Joint_GRP)
        DJB_LockNHide(self.Mesh_GRP)
        DJB_LockNHide(self.Misc_GRP)
        mayac.setAttr("%s.visibility" % (self.IK_Dummy_Joint_GRP), 0)
        DJB_LockNHide(self.IK_Dummy_Joint_GRP)
        
        DJB_LockNHide(self.Left_ToeBase_IkHandle)
        DJB_LockNHide(self.Right_ToeBase_IkHandle)
        DJB_LockNHide(self.Left_Ankle_IK_CTRL)
        DJB_LockNHide(self.Left_ToeBase_IK_CTRL)
        DJB_LockNHide(self.Left_ToeBase_IK_AnimData_GRP)
        DJB_LockNHide(self.Left_Ankle_IK_AnimData_GRP)
        DJB_LockNHide(self.Left_Toe_IK_CTRL)
        DJB_LockNHide(self.Left_Toe_IK_AnimData_GRP)
        DJB_LockNHide(self.Right_Ankle_IK_CTRL)
        DJB_LockNHide(self.Right_ToeBase_IK_CTRL)
        DJB_LockNHide(self.Right_ToeBase_IK_AnimData_GRP)
        DJB_LockNHide(self.Right_Ankle_IK_AnimData_GRP)
        DJB_LockNHide(self.Right_Toe_IK_CTRL)
        DJB_LockNHide(self.Right_Toe_IK_AnimData_GRP)

        
        
        
        #lock CTRLS
        for bodyPart in self.bodyParts:
            bodyPart.lockUpCTRLs()
        
        #defaultValues
        mayac.setAttr("%s.FK_IK" % (self.LeftFoot.Options_CTRL), 1)
        mayac.setAttr("%s.FK_IK" % (self.RightFoot.Options_CTRL), 1)
        mayac.setAttr("%s.FK_IK" % (self.LeftHand.Options_CTRL), 0)
        mayac.setAttr("%s.FK_IK" % (self.RightHand.Options_CTRL), 0)
        
        mayac.setAttr("%s.FollowBody" % (self.LeftHand.IK_CTRL), 0)
        mayac.setAttr("%s.FollowBody" % (self.RightHand.IK_CTRL), 0)
        mayac.setAttr("%s.FollowBody" % (self.LeftForeArm.IK_CTRL), 0)
        mayac.setAttr("%s.FollowBody" % (self.RightForeArm.IK_CTRL), 0)
        mayac.setAttr("%s.FollowBody" % (self.LeftFoot.IK_CTRL), 0)
        mayac.setAttr("%s.FollowBody" % (self.RightFoot.IK_CTRL), 0)
        mayac.setAttr("%s.FollowBody" % (self.LeftLeg.IK_CTRL), 0)
        mayac.setAttr("%s.FollowBody" % (self.RightLeg.IK_CTRL), 0)
        
        selfPOS = mayac.xform(self.LeftLeg.Bind_Joint, query = True, absolute = True, worldSpace = True, translation = True)
        parentPOS = mayac.xform(self.LeftLeg.parent.Bind_Joint, query = True, absolute = True, worldSpace = True, translation = True)
        tempDistance = math.sqrt((selfPOS[0]-parentPOS[0])*(selfPOS[0]-parentPOS[0]) + (selfPOS[1]-parentPOS[1])*(selfPOS[1]-parentPOS[1]) + (selfPOS[2]-parentPOS[2])*(selfPOS[2]-parentPOS[2]))
        mayac.setAttr("%s.translateZ" % (self.LeftLeg.IK_CTRL), tempDistance / 2)
        mayac.setAttr("%s.translateZ" % (self.RightLeg.IK_CTRL), tempDistance / 2)
        if self.rigType == "AutoRig":
            mayac.setAttr("%s.translateX" % (self.LeftForeArm.IK_CTRL), tempDistance / 2)
            mayac.setAttr("%s.translateX" % (self.RightForeArm.IK_CTRL), tempDistance / -2)
        elif self.rigType == "World":
            mayac.setAttr("%s.translateZ" % (self.LeftForeArm.IK_CTRL), tempDistance / -2)
            mayac.setAttr("%s.translateZ" % (self.RightForeArm.IK_CTRL), tempDistance / -2)
        DJB_LockNHide(self.global_CTRL, tx = False, ty = False, tz = False, rx = False, ry = False, rz = False, s = False, v = True)
        
        OpenMaya.MGlobal.displayInfo("Rig Complete")

        
    def checkSkeletonProportions(self, incomingDataRootJoint):
        return True
        global proportionCheckTolerance
        success = True
        New_joint_Namespace = DJB_findBeforeSeparator(incomingDataRootJoint, ':')
        if not self.hulaOption and "Root" in incomingDataRootJoint:
            print "failing because of hula"
            success = False
        for bodyPart in self.bodyParts:
            if bodyPart.children and bodyPart.nodeName != "Root" and bodyPart.Bind_Joint:
                selfPOS = mayac.xform(bodyPart.Bind_Joint, query = True, absolute = True, worldSpace = True, translation = True)
                if not mayac.objExists("%s%s" % (New_joint_Namespace, bodyPart.nodeName)):
                    print "failing becuase of %s%s not existing"%(New_joint_Namespace, bodyPart.nodeName)
                    success = False
                    break
                else:
                    DataSelfPOS = mayac.xform("%s%s" % (New_joint_Namespace, bodyPart.nodeName), query = True, absolute = True, worldSpace = True, translation = True)
                    for child in bodyPart.children:
                        if child in self.bodyParts:
                            if child.Bind_Joint and "End" not in child.nodeName:
                                childPOS = mayac.xform(child.Bind_Joint, query = True, absolute = True, worldSpace = True, translation = True)
                                if not mayac.objExists("%s%s" % (New_joint_Namespace, child.nodeName)):
                                    print "failing becuase of %s%s not existing"%(New_joint_Namespace, child.nodeName)
                                    success = False
                                    break
                                else:
                                    DataChildPOS = mayac.xform("%s%s" % (New_joint_Namespace, child.nodeName), query = True, absolute = True, worldSpace = True, translation = True)
                                    correctDistance = math.sqrt((selfPOS[0]-childPOS[0])*(selfPOS[0]-childPOS[0]) + (selfPOS[1]-childPOS[1])*(selfPOS[1]-childPOS[1]) + (selfPOS[2]-childPOS[2])*(selfPOS[2]-childPOS[2])) / mayac.getAttr("%s.scaleX" % (self.global_CTRL))
                                    distanceInQuestion = math.sqrt((DataSelfPOS[0]-DataChildPOS[0])*(DataSelfPOS[0]-DataChildPOS[0]) + (DataSelfPOS[1]-DataChildPOS[1])*(DataSelfPOS[1]-DataChildPOS[1]) + (DataSelfPOS[2]-DataChildPOS[2])*(DataSelfPOS[2]-DataChildPOS[2]))
                                    if not math.fabs(distanceInQuestion/correctDistance) > 1 - proportionCheckTolerance or not math.fabs(distanceInQuestion/correctDistance) < 1 + proportionCheckTolerance:
                                        print "Failing because proportions are incorrect for %s%s"%(New_joint_Namespace, bodyPart.nodeName)
                                        success = False
                                        break
                                if bodyPart.rotOrder != mayac.getAttr("%s.rotateOrder" % (New_joint_Namespace + bodyPart.nodeName)):
                                    print "Failing because rotation Orders are incorrect for %s%s"%(New_joint_Namespace, bodyPart.nodeName)
                                    success = False
                                    break
        return success
        
        
    def connectMotionToAnimDataJoints(self, incomingDataRootJoint): 
        mayac.currentTime(1)
        New_joint_Namespace = DJB_findBeforeSeparator(incomingDataRootJoint, ':')
        curJoint = 0.0
        objectsOfInterest = []
        for bodyPart in self.bodyParts:
            if bodyPart.nodeName == "Root" and self.hulaOption:
                if mayac.objExists("%sRoot" % (New_joint_Namespace)):
                    objectsOfInterest.append("%sRoot" % (New_joint_Namespace))
                    DJB_ConnectAll("%sRoot" % (New_joint_Namespace), bodyPart.AnimData_Joint)
                else:
                    objectsOfInterest.append("%sHips" % (New_joint_Namespace))
                    DJB_ConnectAll("%sHips" % (New_joint_Namespace), bodyPart.AnimData_Joint)
            elif bodyPart.nodeName == "Hips" and self.hulaOption and mayac.objExists("%sRoot" % (New_joint_Namespace)):
                objectsOfInterest.append("%sHips" % (New_joint_Namespace))
                DJB_ConnectAll("%sHips" % (New_joint_Namespace), bodyPart.AnimData_Joint)
            elif bodyPart.nodeName == "Hips" and not self.hulaOption:
                objectsOfInterest.append("%sHips" % (New_joint_Namespace))
                DJB_ConnectAll("%sHips" % (New_joint_Namespace), bodyPart.AnimData_Joint)
            elif bodyPart.nodeName not in ["Hips", "HeadTop_End", "LeftHandThumb4", "LeftHandIndex4", "LeftHandMiddle4", "LeftHandRing4", "LeftHandPinky4", "LeftToe_End", "RightHandThumb4", "RightHandIndex4", "RightHandMiddle4", "RightHandRing4", "RightHandPinky4", "RightToe_End"]:
                newAnimDataJoint = "%s%s" % (New_joint_Namespace, bodyPart.nodeName)
                if mayac.objExists(newAnimDataJoint):
                    objectsOfInterest.append(newAnimDataJoint)
                    DJB_ConnectAll(newAnimDataJoint, bodyPart.AnimData_Joint)
            curJoint += 1
        
        ##adjust timeline to fit animation
        #find first and last frames
        howManyKeys = []
        last = 0
        highestTime = -999999999
        lowestTime = 99999999
        for obj in objectsOfInterest:
            myKeys = mayac.keyframe(obj, query = True, name = True)
            if myKeys:
                howManyKeys = mayac.keyframe(myKeys[0], query = True, timeChange = True)
                last = len(howManyKeys)-1
                if howManyKeys[last] > highestTime:
                    highestTime = howManyKeys[last]
                if howManyKeys[0] < lowestTime:
                    lowestTime = howManyKeys[0]
        
        startTime = lowestTime
        endTime = highestTime
        mayac.playbackOptions(minTime = startTime, maxTime = highestTime)
        
        OpenMaya.MGlobal.displayInfo("Animation Data Connected")
        
        
        
        
    def transferMotionToAnimDataJoints(self, incomingDataRootJoint, newStartTime = 0, mixMethod = "insert", directConnect_ = False): #mixMethod - insert or merge
        mayac.currentTime(1)
        New_joint_Namespace = DJB_findBeforeSeparator(incomingDataRootJoint, ':')
        keyList = mayac.keyframe("%s.translateX"%(incomingDataRootJoint),query = True, timeChange = True)
        lastFrame = keyList[len(keyList)-1]
        curJoint = 0.0
        gMainProgressBar = mel.eval('$tmp = $gMainProgressBar');
        if not directConnect_:
            mayac.progressBar( gMainProgressBar,
                           edit=True,
                           beginProgress=True,
                           isInterruptable=True,
                           status='Copying Keyframes for joint %d/%d ...' % (curJoint, len(self.bodyParts)-1),
                           maxValue=lastFrame )
            for bodyPart in self.bodyParts:
                if mayac.progressBar(gMainProgressBar, query=True, isCancelled=True ) :
                    break
                if bodyPart.nodeName == "Root" and self.hulaOption:
                    if mayac.objExists("%sRoot" % (New_joint_Namespace)):
                        mayac.copyKey("%sRoot" % (New_joint_Namespace), time = (0,lastFrame), hierarchy = "none", controlPoints = 0, shape = 1)
                        mayac.pasteKey(bodyPart.AnimData_Joint, option = mixMethod, connect = 1, timeOffset = newStartTime, valueOffset = 0)
                    else:
                        mayac.copyKey("%sHips" % (New_joint_Namespace), time = (0,lastFrame), hierarchy = "none", controlPoints = 0, shape = 1)
                        mayac.pasteKey(bodyPart.AnimData_Joint, option = mixMethod, connect = 1, timeOffset = newStartTime, valueOffset = 0)
                elif bodyPart.nodeName == "Hips" and self.hulaOption and mayac.objExists("%sRoot" % (New_joint_Namespace)):
                    mayac.copyKey("%sHips" % (New_joint_Namespace), time = (0,lastFrame), hierarchy = "none", controlPoints = 0, shape = 1)
                    mayac.pasteKey(bodyPart.AnimData_Joint, option = mixMethod, connect = 1, timeOffset = newStartTime, valueOffset = 0)
                elif bodyPart.nodeName == "Hips" and not self.hulaOption:
                    mayac.copyKey("%sHips" % (New_joint_Namespace), time = (0,lastFrame), hierarchy = "none", controlPoints = 0, shape = 1)
                    mayac.pasteKey(bodyPart.AnimData_Joint, option = mixMethod, connect = 1, timeOffset = newStartTime, valueOffset = 0)
                elif bodyPart.nodeName not in ["Hips", "HeadTop_End", "LeftHandThumb4", "LeftHandIndex4", "LeftHandMiddle4", "LeftHandRing4", "LeftHandPinky4", "LeftToe_End", "RightHandThumb4", "RightHandIndex4", "RightHandMiddle4", "RightHandRing4", "RightHandPinky4", "RightToe_End"]:
                    newAnimDataJoint = "%s%s" % (New_joint_Namespace, bodyPart.nodeName)
                    if mayac.objExists(newAnimDataJoint):
                        numCurves = mayac.copyKey(newAnimDataJoint, time = (0,lastFrame), hierarchy = "none", controlPoints = 0, shape = 1)
                        if numCurves:
                            mayac.pasteKey(bodyPart.AnimData_Joint, option = mixMethod, connect = 1, timeOffset = newStartTime, valueOffset = 0)
                mayac.progressBar(gMainProgressBar, edit=True, step=1)    
                curJoint += 1
        mayac.progressBar(gMainProgressBar, edit=True, endProgress=True)
        sClusters = []
        sClusters = mayac.listConnections(incomingDataRootJoint, destination = True, type = "skinCluster")
        for joint in mayac.listRelatives(incomingDataRootJoint, allDescendents = True, type = 'joint'):
            checkClusterList = mayac.listConnections(joint, destination = True, type = "skinCluster")
            if checkClusterList:
                for checkCluster in checkClusterList:
                    if checkCluster not in sClusters:
                        sClusters.append(checkCluster)
        self.origAnim = mayac.group(incomingDataRootJoint, name = "Original_Animation_GRP")
        if sClusters:
            for sCluster in sClusters:
                shapes =  mayac.listConnections(sCluster, destination = True, type = "mesh")
                if shapes:
                    for shape in shapes:
                        parent = mayac.listRelatives(shape, parent = True)
                        if parent and self.origAnim not in parent:
                            DJB_Unlock(shape)
                            while "Original_Animation_" not in shape:
                                shape = mayac.rename(shape, "Original_Animation_%s" % (shape))
                            shape = mayac.parent(shape, self.origAnim)[0]
                        if not parent:
                            DJB_Unlock(shape)
                            while "Original_Animation_" not in shape:
                                shape = mayac.rename(shape, "Original_Animation_%s" % (shape))
                            shape = mayac.parent(shape, self.origAnim)[0]
                                
        if not directConnect_:                    
            #rename orig anim joints
            for bodyPart in self.bodyParts:
                if mayac.objExists("%s%s" % (New_joint_Namespace, bodyPart.nodeName)):
                    mayac.rename("%s%s" % (New_joint_Namespace, bodyPart.nodeName), "Original_Animation_%s" % (bodyPart.nodeName))
            if self.ExtraJoints:
                for extraJoint in self.ExtraJoints:
                    if mayac.objExists("%s%s" % (New_joint_Namespace, extraJoint.nodeName)):
                        mayac.rename("%s%s" % (New_joint_Namespace, extraJoint.nodeName), "Original_Animation_%s" % (extraJoint.nodeName))
            
            mayac.parent(self.origAnim, self.Character_GRP)
            self.origAnimation_Layer = mayac.createDisplayLayer(name = "OrigAnimationLayer", number = 1)
            mayac.editDisplayLayerMembers(self.origAnimation_Layer, self.origAnim)
            mayac.setAttr("%s.visibility" %(self.origAnimation_Layer), 0)
            mayac.setAttr("%s.displayType" %(self.origAnimation_Layer), 2)
            #update infoNode
            pyToAttr("%s.origAnim" % (self.infoNode), self.origAnim)
            pyToAttr("%s.origAnimation_Layer" % (self.infoNode), self.origAnimation_Layer)
        
        
        ##adjust timeline to fit animation
        #find first and last frames
        howManyKeys = []
        last = 0
        highestTime = -999999999
        lowestTime = 99999999
        objectsOfInterest = []
        for bodyPart in self.bodyParts:
            if "4" not in bodyPart.nodeName and "End" not in bodyPart.nodeName:
                if bodyPart.FK_CTRL:
                    objectsOfInterest.append(bodyPart.FK_CTRL)
                if bodyPart.IK_CTRL:
                    objectsOfInterest.append(bodyPart.IK_CTRL)
                if bodyPart.Options_CTRL:
                    objectsOfInterest.append(bodyPart.Options_CTRL)
                if bodyPart.AnimData_Joint:
                    objectsOfInterest.append(bodyPart.AnimData_Joint)
        objectsOfInterest.append(self.global_CTRL)
        for obj in objectsOfInterest:
            myKeys = mayac.keyframe(obj, query = True, name = True)
            if myKeys:
                howManyKeys = mayac.keyframe(myKeys[0], query = True, timeChange = True)
                last = len(howManyKeys)-1
                if howManyKeys[last] > highestTime:
                    highestTime = howManyKeys[last]
                if howManyKeys[0] < lowestTime:
                    lowestTime = howManyKeys[0]
        
        startTime = lowestTime
        endTime = highestTime
        mayac.playbackOptions(minTime = startTime, maxTime = highestTime)
        
        OpenMaya.MGlobal.displayInfo("Animation Data Attached")
        
        
    def deleteOriginalAnimation(self):
        mayac.delete(self.origAnim, self.origAnimation_Layer)
        self.origAnim = None
        self.origAnimation_Layer = None
        pyToAttr("%s.origAnim" % (self.infoNode), self.origAnim)
        pyToAttr("%s.origAnimation_Layer" % (self.infoNode), self.origAnimation_Layer)
        
        OpenMaya.MGlobal.displayInfo("Original Animation Deleted")
        
    
    
    def bakeAnimationToControls(self, bodyPart_ = "all"):
        #find first and last frames
        howManyKeys = []
        last = 0
        highestTime = -999999999
        lowestTime = 99999999
        objectsOfInterest = []
        for bodyPart in self.bodyParts:
            if "4" not in bodyPart.nodeName and "End" not in bodyPart.nodeName:
                if bodyPart.FK_CTRL:
                    objectsOfInterest.append(bodyPart.FK_CTRL)
                if bodyPart.IK_CTRL:
                    objectsOfInterest.append(bodyPart.IK_CTRL)
                if bodyPart.Options_CTRL:
                    objectsOfInterest.append(bodyPart.Options_CTRL)
                if bodyPart.AnimData_Joint:
                    objectsOfInterest.append(bodyPart.AnimData_Joint)
        objectsOfInterest.append(self.global_CTRL)
        for obj in objectsOfInterest:
            myKeys = mayac.keyframe(obj, query = True, name = True)
            if myKeys:
                howManyKeys = mayac.keyframe(myKeys[0], query = True, timeChange = True)
                last = len(howManyKeys)-1
                if howManyKeys[last] > highestTime:
                    highestTime = howManyKeys[last]
                if howManyKeys[0] < lowestTime:
                    lowestTime = howManyKeys[0]
        
        startTime = lowestTime
        endTime = highestTime
        
        if startTime == 99999999 and endTime == -999999999:
            OpenMaya.MGlobal.displayError("No Keyframes found on Character to bake!")
            return None
        
        #create locators
        locators = []
        for bodyPart in self.bodyParts:
            if "LeftLeg" in bodyPart.nodeName or "RightLeg" in bodyPart.nodeName or "ForeArm" in bodyPart.nodeName:
                temp = mayac.spaceLocator(n = "%s_locator1" % (bodyPart.nodeName))
                bodyPart.locator1 = temp[0]
                mayac.setAttr("%s.rotateOrder" % (bodyPart.locator1), bodyPart.rotOrder)
                mayac.setAttr("%s.visibility"%(bodyPart.locator1), 0)
                mayac.parent(bodyPart.locator1, self.global_CTRL)
                locators.append(bodyPart.locator1)
                temp = mayac.pointConstraint(bodyPart.IK_BakingLOC, bodyPart.locator1)
                bodyPart.locatorConstraint1 = temp[0]
            if "Foot" not in bodyPart.nodeName:
                temp = mayac.spaceLocator(n = "%s_locator" % (bodyPart.nodeName))
                bodyPart.locator = temp[0]
                mayac.setAttr("%s.rotateOrder" % (bodyPart.locator), bodyPart.rotOrder)
                mayac.setAttr("%s.visibility"%(bodyPart.locator), 0)
                mayac.parent(bodyPart.locator, self.global_CTRL)
                locators.append(bodyPart.locator)
                temp = mayac.parentConstraint(bodyPart.Bind_Joint, bodyPart.locator)
                bodyPart.locatorConstraint = temp[0]
            else:
                temp = mayac.spaceLocator(n = "%s_locator1" % (bodyPart.nodeName))
                bodyPart.locator1 = temp[0]
                mayac.setAttr("%s.rotateOrder" % (bodyPart.locator1), bodyPart.rotOrder)
                mayac.setAttr("%s.visibility"%(bodyPart.locator1), 0)
                mayac.parent(bodyPart.locator1, self.global_CTRL)
                mayac.delete(mayac.parentConstraint(bodyPart.Bind_Joint, bodyPart.locator1))
                temp = mayac.spaceLocator(n = "%s_locator" % (bodyPart.nodeName))
                bodyPart.locator = temp[0]
                mayac.setAttr("%s.rotateOrder" % (bodyPart.locator), bodyPart.rotOrder)
                mayac.setAttr("%s.visibility"%(bodyPart.locator), 0)
                mayac.parent(bodyPart.locator, self.global_CTRL)
                mayac.delete(mayac.parentConstraint(bodyPart.IK_BakingLOC, bodyPart.locator))
                temp = mayac.parentConstraint(bodyPart.locator1, bodyPart.locator, maintainOffset = True)
                bodyPart.locatorConstraint1 = temp[0]
                
                locators.append(bodyPart.locator)
                locators.append(bodyPart.locator1)
                temp = mayac.parentConstraint(bodyPart.Bind_Joint, bodyPart.locator1)
                bodyPart.locatorConstraint = temp[0]
                
        #bake onto locators
        mayac.select(clear = True)
        mayac.bakeResults(locators, simulation = True, time = (startTime, endTime))
        for bodyPart in self.bodyParts:
            mayac.delete(bodyPart.locatorConstraint)
            bodyPart.locatorConstraint = None
            if bodyPart.locatorConstraint1:
                mayac.delete(bodyPart.locatorConstraint1)
                bodyPart.locatorConstraint1 = None
        
        #zero out controls, animJoints
        for bodyPart in self.bodyParts:
            if bodyPart.AnimData_Joint:
                bodyPart.zeroToOrig(bodyPart.AnimData_Joint)
            if bodyPart.FK_CTRL:
                DJB_ZeroOut(bodyPart.FK_CTRL)
                DJB_ZeroOutAtt(bodyPart.FK_CTRL + ".AnimDataMult", value = 1)
                if "Root" in bodyPart.nodeName and self.hulaOption:
                    DJB_ZeroOutAtt(bodyPart.FK_CTRL + ".AnimDataMultTrans", value = 1)
                elif "Hips" in bodyPart.nodeName and not self.hulaOption:
                    DJB_ZeroOutAtt(bodyPart.FK_CTRL + ".AnimDataMultTrans", value = 1)
                if "Head" in bodyPart.nodeName:
                    DJB_ZeroOutAtt(bodyPart.FK_CTRL + ".InheritRotation", value = 1)
            if bodyPart.IK_CTRL:
                DJB_ZeroOut(bodyPart.IK_CTRL)
                DJB_ZeroOutAtt(bodyPart.IK_CTRL + ".AnimDataMult", value = 1)
                DJB_ZeroOutAtt(bodyPart.IK_CTRL + ".ParentToGlobal")
                DJB_ZeroOutAtt(bodyPart.IK_CTRL + ".FollowBody")
                if "Leg" in bodyPart.nodeName:
                    DJB_ZeroOutAtt(bodyPart.IK_CTRL + ".FollowFoot")
                if "ForeArm" in bodyPart.nodeName:
                    DJB_ZeroOutAtt(bodyPart.IK_CTRL + ".FollowHand")
                if "Foot" in bodyPart.nodeName:
                    DJB_ZeroOutAtt(bodyPart.IK_CTRL + ".FootRoll")
                    DJB_ZeroOutAtt(bodyPart.IK_CTRL + ".ToeTap")
                    DJB_ZeroOutAtt(bodyPart.IK_CTRL + ".ToeSideToSide")
                    DJB_ZeroOutAtt(bodyPart.IK_CTRL + ".ToeRotate")
                    DJB_ZeroOutAtt(bodyPart.IK_CTRL + ".ToeRoll")
                    DJB_ZeroOutAtt(bodyPart.IK_CTRL + ".HipPivot")
                    DJB_ZeroOutAtt(bodyPart.IK_CTRL + ".BallPivot")
                    DJB_ZeroOutAtt(bodyPart.IK_CTRL + ".ToePivot")
                    DJB_ZeroOutAtt(bodyPart.IK_CTRL + ".HipSideToSide")
                    DJB_ZeroOutAtt(bodyPart.IK_CTRL + ".HipBackToFront")
            if bodyPart.Options_CTRL:
                if "Hand" in bodyPart.nodeName:
                    DJB_ZeroOutAtt(bodyPart.Options_CTRL + ".FollowHand")
                    DJB_ZeroOutAtt(bodyPart.Options_CTRL + ".ThumbCurl")
                    DJB_ZeroOutAtt(bodyPart.Options_CTRL + ".IndexCurl")
                    DJB_ZeroOutAtt(bodyPart.Options_CTRL + ".MiddleCurl")
                    DJB_ZeroOutAtt(bodyPart.Options_CTRL + ".RingCurl")
                    DJB_ZeroOutAtt(bodyPart.Options_CTRL + ".PinkyCurl")
                    DJB_ZeroOutAtt(bodyPart.Options_CTRL + ".Sway")
                    DJB_ZeroOutAtt(bodyPart.Options_CTRL + ".Spread")
                   
            
    
        #constraints
        bakeConstraintList = []
        bakeCTRLList = []
        EulerList = []
        for bodyPart in self.bodyParts:
            if bodyPart.FK_CTRL:
                if "Root" in bodyPart.nodeName:
                    temp = mayac.parentConstraint(bodyPart.locator, bodyPart.FK_CTRL)
                    bakeConstraintList.append(temp[0])
                    bakeCTRLList.append(bodyPart.FK_CTRL + ".translateX")
                    bakeCTRLList.append(bodyPart.FK_CTRL + ".translateY")
                    bakeCTRLList.append(bodyPart.FK_CTRL + ".translateZ")
                    bakeCTRLList.append(bodyPart.FK_CTRL + ".rotateX")
                    bakeCTRLList.append(bodyPart.FK_CTRL + ".rotateY")
                    bakeCTRLList.append(bodyPart.FK_CTRL + ".rotateZ")
                    
                elif "Hips" in bodyPart.nodeName and not self.hulaOption:
                    temp = mayac.parentConstraint(bodyPart.locator, bodyPart.FK_CTRL)
                    bakeConstraintList.append(temp[0])
                    bakeCTRLList.append(bodyPart.FK_CTRL + ".translateX")
                    bakeCTRLList.append(bodyPart.FK_CTRL + ".translateY")
                    bakeCTRLList.append(bodyPart.FK_CTRL + ".translateZ")
                    bakeCTRLList.append(bodyPart.FK_CTRL + ".rotateX")
                    bakeCTRLList.append(bodyPart.FK_CTRL + ".rotateY")
                    bakeCTRLList.append(bodyPart.FK_CTRL + ".rotateZ")
                   
                elif "Foot" in bodyPart.nodeName:
                    temp = mayac.orientConstraint(bodyPart.locator1, bodyPart.FK_CTRL)
                    bakeConstraintList.append(temp[0])
                    bakeCTRLList.append(bodyPart.FK_CTRL + ".rotateX")
                    bakeCTRLList.append(bodyPart.FK_CTRL + ".rotateY")
                    bakeCTRLList.append(bodyPart.FK_CTRL + ".rotateZ")
                    
                else:
                    temp = mayac.orientConstraint(bodyPart.locator, bodyPart.FK_CTRL)
                    bakeConstraintList.append(temp[0])
                    bakeCTRLList.append(bodyPart.FK_CTRL + ".rotateX")
                    bakeCTRLList.append(bodyPart.FK_CTRL + ".rotateY")
                    bakeCTRLList.append(bodyPart.FK_CTRL + ".rotateZ")

            if bodyPart.IK_CTRL:
                
                if "ForeArm" in bodyPart.nodeName or "Leg" in bodyPart.nodeName:
                    temp = mayac.pointConstraint(bodyPart.locator1, bodyPart.IK_CTRL)
                    bakeConstraintList.append(temp[0])
                    bakeCTRLList.append(bodyPart.IK_CTRL + ".translateX")
                    bakeCTRLList.append(bodyPart.IK_CTRL + ".translateY")
                    bakeCTRLList.append(bodyPart.IK_CTRL + ".translateZ")
                else:
                    temp = mayac.parentConstraint(bodyPart.locator, bodyPart.IK_CTRL)
                    bakeConstraintList.append(temp[0])
                    bakeCTRLList.append(bodyPart.IK_CTRL + ".translateX")
                    bakeCTRLList.append(bodyPart.IK_CTRL + ".translateY")
                    bakeCTRLList.append(bodyPart.IK_CTRL + ".translateZ")
                    bakeCTRLList.append(bodyPart.IK_CTRL + ".rotateX")
                    bakeCTRLList.append(bodyPart.IK_CTRL + ".rotateY")
                    bakeCTRLList.append(bodyPart.IK_CTRL + ".rotateZ")

                
        #bake onto controls
        mayac.bakeResults(bakeCTRLList, simulation = True, time = (startTime, endTime))
        mayac.delete(bakeConstraintList)

        
        #Euler filter
        for bodyPart in self.bodyParts:
            if bodyPart.FK_CTRL:
                mayac.filterCurve( '%s_rotateX'%(bodyPart.FK_CTRL), '%s_rotateY'%(bodyPart.FK_CTRL), '%s_rotateZ'%(bodyPart.FK_CTRL))
            if bodyPart.nodeName  == "LeftHand" or bodyPart.nodeName  == "RightHand" or bodyPart.nodeName  == "LeftFoot" or bodyPart.nodeName  == "RightFoot":
                mayac.filterCurve( '%s_rotateX'%(bodyPart.IK_CTRL), '%s_rotateY'%(bodyPart.IK_CTRL), '%s_rotateZ'%(bodyPart.IK_CTRL))
            
        
        #delete garbage
        for bodyPart in self.bodyParts:
            mayac.delete(bodyPart.locator)
            bodyPart.locator = None
            if bodyPart.locator1:
                mayac.delete(bodyPart.locator1)
                bodyPart.locator1 = None
                
        #make sure animLayer1 is active
        baseLayer = mayac.animLayer(query = True, root = True)
        if baseLayer:
            layers = mayac.ls(type = 'animLayer')
            for layer in layers:
                mel.eval('animLayerEditorOnSelect "%s" 0;'%(layer))
            mel.eval('animLayerEditorOnSelect "%s" 1;'%(baseLayer))
             
        #IK Toe Tap
        if self.rigType == "AutoRig":
            mayac.copyKey(self.LeftToeBase.FK_CTRL, time = (startTime, endTime), hierarchy = "none", controlPoints = 0, shape = 1, attribute = "rotateX")
            mayac.pasteKey(self.LeftFoot.IK_CTRL, connect = 1, attribute = "ToeTap")
            mayac.copyKey(self.LeftToeBase.FK_CTRL, time = (startTime, endTime), hierarchy = "none", controlPoints = 0, shape = 1, attribute = "rotateY")
            mayac.pasteKey(self.LeftFoot.IK_CTRL, connect = 1, attribute = "ToeRotate")
            mayac.copyKey(self.LeftToeBase.FK_CTRL, time = (startTime, endTime), hierarchy = "none", controlPoints = 0, shape = 1, attribute = "rotateZ")
            mayac.pasteKey(self.LeftFoot.IK_CTRL, connect = 1, attribute = "ToeSideToSide")
            mayac.copyKey(self.RightToeBase.FK_CTRL, time = (startTime, endTime), hierarchy = "none", controlPoints = 0, shape = 1, attribute = "rotateX")
            mayac.pasteKey(self.RightFoot.IK_CTRL, connect = 1, attribute = "ToeTap")
            mayac.copyKey(self.RightToeBase.FK_CTRL, time = (startTime, endTime), hierarchy = "none", controlPoints = 0, shape = 1, attribute = "rotateY")
            mayac.pasteKey(self.RightFoot.IK_CTRL, connect = 1, attribute = "ToeRotate")
            mayac.copyKey(self.RightToeBase.FK_CTRL, time = (startTime, endTime), hierarchy = "none", controlPoints = 0, shape = 1, attribute = "rotateZ")
            mayac.pasteKey(self.RightFoot.IK_CTRL, connect = 1, attribute = "ToeSideToSide")
        elif self.rigType == "World":
            mayac.copyKey(self.LeftToeBase.FK_CTRL, time = (startTime, endTime), hierarchy = "none", controlPoints = 0, shape = 1, attribute = "rotateX")
            mayac.pasteKey(self.LeftFoot.IK_CTRL, connect = 1, attribute = "ToeTap")
            mayac.scaleKey(self.LeftFoot.IK_CTRL, at='ToeTap', time=(startTime, endTime), valueScale = -1, valuePivot=0 )
            
            mayac.copyKey(self.LeftToeBase.FK_CTRL, time = (startTime, endTime), hierarchy = "none", controlPoints = 0, shape = 1, attribute = "rotateY")
            mayac.pasteKey(self.LeftFoot.IK_CTRL, connect = 1, attribute = "ToeSideToSide")
            mayac.copyKey(self.LeftToeBase.FK_CTRL, time = (startTime, endTime), hierarchy = "none", controlPoints = 0, shape = 1, attribute = "rotateZ")
            mayac.pasteKey(self.LeftFoot.IK_CTRL, connect = 1, attribute = "ToeRotate")
            mayac.copyKey(self.RightToeBase.FK_CTRL, time = (startTime, endTime), hierarchy = "none", controlPoints = 0, shape = 1, attribute = "rotateX")
            mayac.pasteKey(self.RightFoot.IK_CTRL, connect = 1, attribute = "ToeTap")
            mayac.scaleKey(self.RightFoot.IK_CTRL, at='ToeTap', time=(startTime, endTime), valueScale = -1, valuePivot=0 )
            
            mayac.copyKey(self.RightToeBase.FK_CTRL, time = (startTime, endTime), hierarchy = "none", controlPoints = 0, shape = 1, attribute = "rotateY")
            mayac.pasteKey(self.RightFoot.IK_CTRL, connect = 1, attribute = "ToeSideToSide")
            mayac.copyKey(self.RightToeBase.FK_CTRL, time = (startTime, endTime), hierarchy = "none", controlPoints = 0, shape = 1, attribute = "rotateZ")
            mayac.pasteKey(self.RightFoot.IK_CTRL, connect = 1, attribute = "ToeRotate")
            
        OpenMaya.MGlobal.displayInfo("Bake Successful")


    def clearAnimationControls(self, bodyPart_ = "all"):
        #find first and last frames
        #find first and last frames
        howManyKeys = []
        last = 0
        highestTime = -999999999
        lowestTime = 99999999
        objectsOfInterest = []
        for bodyPart in self.bodyParts:
            if "4" not in bodyPart.nodeName and "End" not in bodyPart.nodeName:
                if bodyPart.FK_CTRL:
                    objectsOfInterest.append(bodyPart.FK_CTRL)
                if bodyPart.IK_CTRL:
                    objectsOfInterest.append(bodyPart.IK_CTRL)
                if bodyPart.Options_CTRL:
                    objectsOfInterest.append(bodyPart.Options_CTRL)
                if bodyPart.AnimData_Joint:
                    objectsOfInterest.append(bodyPart.AnimData_Joint)
        objectsOfInterest.append(self.global_CTRL)
        for object in objectsOfInterest:
            myKeys = mayac.keyframe(object, query = True, name = True)
            if myKeys:
                howManyKeys = mayac.keyframe(myKeys[0], query = True, timeChange = True)
                last = len(howManyKeys)-1
                if howManyKeys[last] > highestTime:
                    highestTime = howManyKeys[last]
                if howManyKeys[0] < lowestTime:
                    lowestTime = howManyKeys[0]
        
        startTime = lowestTime
        endTime = highestTime
        
        if startTime == 99999999 and endTime == -999999999:
            OpenMaya.MGlobal.displayError("No Keyframes found on Character to clear!")
            return None
        
            
            
            
            
        #create locators
        locators = []
        temp = mayac.duplicate(self.global_CTRL, parentOnly = True)
        fakeGlobal = temp[0]
        mayac.setAttr("%s.translateX"%(fakeGlobal), 0)
        mayac.setAttr("%s.translateY"%(fakeGlobal), 0)
        mayac.setAttr("%s.translateZ"%(fakeGlobal), 0)
        mayac.setAttr("%s.rotateX"%(fakeGlobal), 0)
        mayac.setAttr("%s.rotateY"%(fakeGlobal), 0)
        mayac.setAttr("%s.rotateZ"%(fakeGlobal), 0)
        mayac.connectAttr("%s.scaleX"%(self.global_CTRL), "%s.scaleX"%(fakeGlobal))
        mayac.connectAttr("%s.scaleY"%(self.global_CTRL), "%s.scaleY"%(fakeGlobal))
        mayac.connectAttr("%s.scaleZ"%(self.global_CTRL), "%s.scaleZ"%(fakeGlobal))
        mayac.setAttr("%s.visibility"%(fakeGlobal), lock = False, keyable = True)
        mayac.setAttr("%s.visibility"%(fakeGlobal), 0)
        for bodyPart in self.bodyParts:
            temp = mayac.spaceLocator(n = "%s_locator" % (bodyPart.nodeName))
            bodyPart.locator = temp[0]
            locators.append(bodyPart.locator)
            mayac.setAttr("%s.visibility"%(bodyPart.locator), 0)
            mayac.parent(bodyPart.locator, self.global_CTRL)
            temp = mayac.parentConstraint(bodyPart.Bind_Joint, bodyPart.locator)
            bodyPart.locatorConstraint = temp[0]
            if "LeftLeg" in bodyPart.nodeName or "RightLeg" in bodyPart.nodeName or "ForeArm" in bodyPart.nodeName:
                temp = mayac.spaceLocator(n = "%s_locator2" % (bodyPart.nodeName))
                bodyPart.locator2 = temp[0]
                locators.append(bodyPart.locator2)
                mayac.setAttr("%s.visibility"%(bodyPart.locator2), 0)
                mayac.parent(bodyPart.locator2, self.global_CTRL)
                temp = mayac.parentConstraint(bodyPart.IK_BakingLOC, bodyPart.locator2)
                bodyPart.locatorConstraint2 = temp[0]
                temp = mayac.spaceLocator(n = "%s_locator3" % (bodyPart.nodeName))
                bodyPart.locator3 = temp[0]
                mayac.parent(bodyPart.locator3, fakeGlobal)
                mayac.setAttr("%s.visibility"%(bodyPart.locator3), 0)
                locators.append(bodyPart.locator3)
                mayac.connectAttr("%s.translateX" % (bodyPart.locator2), "%s.translateX" % (bodyPart.locator3))
                mayac.connectAttr("%s.translateY" % (bodyPart.locator2), "%s.translateY" % (bodyPart.locator3))
                mayac.connectAttr("%s.translateZ" % (bodyPart.locator2), "%s.translateZ" % (bodyPart.locator3))
                mayac.connectAttr("%s.rotateX" % (bodyPart.locator2), "%s.rotateX" % (bodyPart.locator3))
                mayac.connectAttr("%s.rotateY" % (bodyPart.locator2), "%s.rotateY" % (bodyPart.locator3))
                mayac.connectAttr("%s.rotateZ" % (bodyPart.locator2), "%s.rotateZ" % (bodyPart.locator3))
           
            temp = mayac.spaceLocator(n = "%s_locator1" % (bodyPart.nodeName))
            bodyPart.locator1 = temp[0]
            mayac.setAttr("%s.visibility"%(bodyPart.locator1), 0)
            locators.append(bodyPart.locator1)
            mayac.parent(bodyPart.locator1, fakeGlobal)
            mayac.connectAttr("%s.translateX" % (bodyPart.locator), "%s.translateX" % (bodyPart.locator1))
            mayac.connectAttr("%s.translateY" % (bodyPart.locator), "%s.translateY" % (bodyPart.locator1))
            mayac.connectAttr("%s.translateZ" % (bodyPart.locator), "%s.translateZ" % (bodyPart.locator1))
            mayac.connectAttr("%s.rotateX" % (bodyPart.locator), "%s.rotateX" % (bodyPart.locator1))
            mayac.connectAttr("%s.rotateY" % (bodyPart.locator), "%s.rotateY" % (bodyPart.locator1))
            mayac.connectAttr("%s.rotateZ" % (bodyPart.locator), "%s.rotateZ" % (bodyPart.locator1))
        mayac.select(clear = True)
            
                
        
        #bake onto locators
        mayac.bakeResults(locators, simulation = True, time = (startTime, endTime))
        for bodyPart in self.bodyParts:
            mayac.delete(bodyPart.locatorConstraint)
            bodyPart.locatorConstraint = None
            if bodyPart.locatorConstraint1:
                mayac.delete(bodyPart.locatorConstraint1)
                bodyPart.locatorConstraint1 = None
            if bodyPart.locatorConstraint2:
                mayac.delete(bodyPart.locatorConstraint2)
                bodyPart.locatorConstraint2 = None
            if bodyPart.locatorConstraint3:
                mayac.delete(bodyPart.locatorConstraint3)
                bodyPart.locatorConstraint3 = None
                
        
        bakeConstraintList = []
        bakeJointList = []
        #zero out controls, animJoints
        for bodyPart in self.bodyParts:
            if bodyPart.AnimData_Joint:
                bodyPart.zeroToOrig(bodyPart.AnimData_Joint)
            if bodyPart.FK_CTRL:
                DJB_ZeroOut(bodyPart.FK_CTRL)
                DJB_ZeroOutAtt(bodyPart.FK_CTRL + ".AnimDataMult", value = 1)
                if "Root" in bodyPart.nodeName:
                    DJB_ZeroOutAtt(bodyPart.FK_CTRL + ".AnimDataMultTrans", value = 1)
                elif "Hips" in bodyPart.nodeName and not self.hulaOption:
                    DJB_ZeroOutAtt(bodyPart.FK_CTRL + ".AnimDataMultTrans", value = 1)
                if "Head" in bodyPart.nodeName:
                    DJB_ZeroOutAtt(bodyPart.FK_CTRL + ".InheritRotation", value = 1)
            if bodyPart.IK_CTRL:
                DJB_ZeroOut(bodyPart.IK_CTRL)
                DJB_ZeroOutAtt(bodyPart.IK_CTRL + ".AnimDataMult", value = 1)
                DJB_ZeroOutAtt(bodyPart.IK_CTRL + ".ParentToGlobal")
                DJB_ZeroOutAtt(bodyPart.IK_CTRL + ".FollowBody")
                if "LeftLeg" in bodyPart.nodeName or "RightLeg" in bodyPart.nodeName or "ForeArm" in bodyPart.nodeName:
                    temp = mayac.pointConstraint(bodyPart.IK_CTRL, bodyPart.locator1)
                    bodyPart.locatorConstraint1 = temp[0]
                if "Leg" in bodyPart.nodeName:
                    DJB_ZeroOutAtt(bodyPart.IK_CTRL + ".FollowFoot")
                if "ForeArm" in bodyPart.nodeName:
                    DJB_ZeroOutAtt(bodyPart.IK_CTRL + ".FollowHand")
                if "Foot" in bodyPart.nodeName:
                    DJB_ZeroOutAtt(bodyPart.IK_CTRL + ".FootRoll")
                    DJB_ZeroOutAtt(bodyPart.IK_CTRL + ".ToeTap")
                    DJB_ZeroOutAtt(bodyPart.IK_CTRL + ".ToeSideToSide")
                    DJB_ZeroOutAtt(bodyPart.IK_CTRL + ".ToeRotate")
                    DJB_ZeroOutAtt(bodyPart.IK_CTRL + ".ToeRoll")
                    DJB_ZeroOutAtt(bodyPart.IK_CTRL + ".HipPivot")
                    DJB_ZeroOutAtt(bodyPart.IK_CTRL + ".BallPivot")
                    DJB_ZeroOutAtt(bodyPart.IK_CTRL + ".ToePivot")
                    DJB_ZeroOutAtt(bodyPart.IK_CTRL + ".HipSideToSide")
                    DJB_ZeroOutAtt(bodyPart.IK_CTRL + ".HipBackToFront")
            if bodyPart.Options_CTRL:
                if "Hand" in bodyPart.nodeName:
                    DJB_ZeroOutAtt(bodyPart.Options_CTRL + ".FollowHand")
                    DJB_ZeroOutAtt(bodyPart.Options_CTRL + ".ThumbCurl")
                    DJB_ZeroOutAtt(bodyPart.Options_CTRL + ".IndexCurl")
                    DJB_ZeroOutAtt(bodyPart.Options_CTRL + ".MiddleCurl")
                    DJB_ZeroOutAtt(bodyPart.Options_CTRL + ".RingCurl")
                    DJB_ZeroOutAtt(bodyPart.Options_CTRL + ".PinkyCurl")
                    DJB_ZeroOutAtt(bodyPart.Options_CTRL + ".Sway")
                    DJB_ZeroOutAtt(bodyPart.Options_CTRL + ".Spread")
                    
            
        
        #constraints
        for bodyPart in self.bodyParts:
            if "Root" in bodyPart.nodeName and self.hulaOption:
                temp = mayac.parentConstraint(bodyPart.locator1, bodyPart.AnimData_Joint)
                bakeConstraintList.append(temp[0])
                bakeJointList.append(bodyPart.AnimData_Joint + ".translateX")
                bakeJointList.append(bodyPart.AnimData_Joint + ".translateY")
                bakeJointList.append(bodyPart.AnimData_Joint + ".translateZ")
                bakeJointList.append(bodyPart.AnimData_Joint + ".rotateX")
                bakeJointList.append(bodyPart.AnimData_Joint + ".rotateY")
                bakeJointList.append(bodyPart.AnimData_Joint + ".rotateZ")   
            elif "Hips" in  bodyPart.nodeName and not self.hulaOption:
                temp = mayac.parentConstraint(bodyPart.locator1, bodyPart.AnimData_Joint)
                bakeConstraintList.append(temp[0])
                bakeJointList.append(bodyPart.AnimData_Joint + ".translateX")
                bakeJointList.append(bodyPart.AnimData_Joint + ".translateY")
                bakeJointList.append(bodyPart.AnimData_Joint + ".translateZ")
                bakeJointList.append(bodyPart.AnimData_Joint + ".rotateX")
                bakeJointList.append(bodyPart.AnimData_Joint + ".rotateY")
                bakeJointList.append(bodyPart.AnimData_Joint + ".rotateZ")            
            else:
                temp = mayac.orientConstraint(bodyPart.locator1, bodyPart.AnimData_Joint)
                bakeConstraintList.append(temp[0])
                bakeJointList.append(bodyPart.AnimData_Joint + ".rotateX")
                bakeJointList.append(bodyPart.AnimData_Joint + ".rotateY")
                bakeJointList.append(bodyPart.AnimData_Joint + ".rotateZ")

                
        #bake onto joints
        mayac.bakeResults(bakeJointList, simulation = True, time = (startTime, endTime))
        mayac.delete(bakeConstraintList)
        
                
        #Euler filter
        for bodyPart in self.bodyParts:
            if bodyPart.AnimData_Joint:
                mayac.filterCurve( '%s_rotateX'%(bodyPart.AnimData_Joint), '%s_rotateY'%(bodyPart.AnimData_Joint), '%s_rotateZ'%(bodyPart.AnimData_Joint))

        
        #delete garbage
        for bodyPart in self.bodyParts:
            mayac.delete(bodyPart.locator)
            bodyPart.locator = None
            if bodyPart.locator1:
                mayac.delete(bodyPart.locator1)
                bodyPart.locator1 = None
            if bodyPart.locator2:
                mayac.delete(bodyPart.locator2)
                bodyPart.locator2 = None
            if bodyPart.locator3:
                mayac.delete(bodyPart.locator3)
                bodyPart.locator3 = None
        #mayac.delete(fakeGlobal)
            
        #move PVs out a bit
        DJB_ZeroOut(self.LeftForeArm.IK_BakingLOC)
        DJB_ZeroOut(self.RightForeArm.IK_BakingLOC)
        DJB_ZeroOut(self.LeftLeg.IK_BakingLOC)
        DJB_ZeroOut(self.RightLeg.IK_BakingLOC)
        DJB_ZeroOut(self.LeftForeArm.IK_CTRL)
        DJB_ZeroOut(self.RightForeArm.IK_CTRL)
        DJB_ZeroOut(self.LeftLeg.IK_CTRL)
        DJB_ZeroOut(self.RightLeg.IK_CTRL)

        selfPOS = mayac.xform(self.LeftLeg.Bind_Joint, query = True, absolute = True, worldSpace = True, translation = True)
        parentPOS = mayac.xform(self.LeftLeg.parent.Bind_Joint, query = True, absolute = True, worldSpace = True, translation = True)
        tempDistance = math.sqrt((selfPOS[0]-parentPOS[0])*(selfPOS[0]-parentPOS[0]) + (selfPOS[1]-parentPOS[1])*(selfPOS[1]-parentPOS[1]) + (selfPOS[2]-parentPOS[2])*(selfPOS[2]-parentPOS[2]))
        mayac.setAttr("%s.translateZ" % (self.LeftLeg.IK_CTRL), tempDistance / 2)
        mayac.setAttr("%s.translateZ" % (self.RightLeg.IK_CTRL), tempDistance / 2)
        mayac.setAttr("%s.translateZ" % (self.LeftLeg.IK_BakingLOC), tempDistance / 2)
        mayac.setAttr("%s.translateZ" % (self.RightLeg.IK_BakingLOC), tempDistance / 2)
        selfPOS = mayac.xform(self.LeftForeArm.Bind_Joint, query = True, absolute = True, worldSpace = True, translation = True)
        parentPOS = mayac.xform(self.LeftForeArm.parent.Bind_Joint, query = True, absolute = True, worldSpace = True, translation = True)
        tempDistance = math.sqrt((selfPOS[0]-parentPOS[0])*(selfPOS[0]-parentPOS[0]) + (selfPOS[1]-parentPOS[1])*(selfPOS[1]-parentPOS[1]) + (selfPOS[2]-parentPOS[2])*(selfPOS[2]-parentPOS[2]))
        if self.rigType == "AutoRig":
            mayac.setAttr("%s.translateX" % (self.LeftForeArm.IK_CTRL), tempDistance / 2)
            mayac.setAttr("%s.translateX" % (self.RightForeArm.IK_CTRL), tempDistance / -2)
            mayac.setAttr("%s.translateX" % (self.LeftForeArm.IK_BakingLOC), tempDistance / 2)
            mayac.setAttr("%s.translateX" % (self.RightForeArm.IK_BakingLOC), tempDistance / -2)
        elif self.rigType == "World":
            mayac.setAttr("%s.translateZ" % (self.LeftForeArm.IK_CTRL), tempDistance / -2)
            mayac.setAttr("%s.translateZ" % (self.RightForeArm.IK_CTRL), tempDistance / -2)
            mayac.setAttr("%s.translateZ" % (self.LeftForeArm.IK_BakingLOC), tempDistance / -2)
            mayac.setAttr("%s.translateZ" % (self.RightForeArm.IK_BakingLOC), tempDistance / -2)
        
        OpenMaya.MGlobal.displayInfo("Un-Bake Successful")
        


    def createExportSkeleton(self, keepMesh_ = False, dynamicsToFK = 0, reduceNonEssential = False, start=None, end=None, removeEndJoints=False):
        #copy joints and mesh
        if self.exportList:
            for obj in self.exportList:
                if mayac.objExists(obj):
                    mayac.delete(obj)
        self.exportList = []
        self.exportListDropFrames = []
        translateOpenList = []
        for bodyPart in self.bodyParts:
            if bodyPart.children:
                if "Root" in bodyPart.nodeName or "Hips" in bodyPart.nodeName or "Leg" in bodyPart.nodeName or "Foot" in bodyPart.nodeName or "Toe" in bodyPart.nodeName or "Spine" in bodyPart.nodeName or "Shoulder" in bodyPart.nodeName or "Arm" in bodyPart.nodeName or bodyPart.nodeName == "LeftHand" or bodyPart.nodeName == "RightHand":
                    bodyPart.duplicateJoint("ExportSkeleton", jointNamespace = self.jointNamespace)
                    self.exportList.append(bodyPart.Export_Joint)
                else:
                    bodyPart.duplicateJoint("ExportSkeleton", jointNamespace = self.jointNamespace)
                    self.exportListDropFrames.append(bodyPart.Export_Joint)
            elif not removeEndJoints:
                bodyPart.duplicateJoint("ExportSkeleton", jointNamespace = self.jointNamespace)
                self.exportListDropFrames.append(bodyPart.Export_Joint)
            if bodyPart.translateOpen:
                translateOpenList.append(bodyPart.Export_Joint)
        
        if self.ExtraJoints:
            for node in self.ExtraJoints:
                if node.children:
                    node.duplicateJoint("ExportSkeleton", jointNamespace = self.jointNamespace)
                    node.Export_Joint = mayac.rename(node.Export_Joint, node.nodeName)
                    node.Export_Joint = mayac.rename(node.Export_Joint, DJB_findAfterSeperator(node.Export_Joint,":"))
                    self.exportListDropFrames.append(node.Export_Joint)
                    if node.translateOpen:
                        translateOpenList.append(node.Export_Joint)
                elif node.translateOpen:
                    node.duplicateJoint("ExportSkeleton", jointNamespace = self.jointNamespace)
                    node.Export_Joint = mayac.rename(node.Export_Joint, node.nodeName)
                    node.Export_Joint = mayac.rename(node.Export_Joint, DJB_findAfterSeperator(node.Export_Joint,":"))
                    self.exportListDropFrames.append(node.Export_Joint)
                    translateOpenList.append(node.Export_Joint)
                elif node.twistJoint:
                    node.duplicateJoint("ExportSkeleton", jointNamespace = self.jointNamespace)
                    node.Export_Joint = mayac.rename(node.Export_Joint, node.nodeName)
                    node.Export_Joint = mayac.rename(node.Export_Joint, DJB_findAfterSeperator(node.Export_Joint,":"))
                    self.exportListDropFrames.append(node.Export_Joint)
        pyToAttr("%s.exportList" % (self.infoNode), self.exportList)
        
        #lock unneeded attributes:
        for joint in (self.exportList + self.exportListDropFrames):
            if "Root" not in joint and "FacialAnim" not in joint and "Hips" not in joint and joint not in translateOpenList:
                DJB_LockNHide(joint, tx = True, ty = True, tz = True, rx = False, ry = False, rz = False, s = True, v = True, other = ("jointOrientX", "jointOrientY", "jointOrientZ", "lockInfluenceWeights", "liw"))
            elif joint in translateOpenList:
                DJB_LockNHide(joint, tx = False, ty = False, tz = False, rx = False, ry = False, rz = False, s = True, v = True, other = ("jointOrientX", "jointOrientY", "jointOrientZ", "lockInfluenceWeights", "liw"))
            else:
                DJB_LockNHide(joint, tx = False, ty = False, tz = False, rx = False, ry = False, rz = False, s = True, v = True, other = ("lockInfluenceWeights", "liw"))
        
        #create Constraints
        constraintList = []
        for bodyPart in self.bodyParts:
            if bodyPart.Bind_Joint and bodyPart.children and "Root" not in bodyPart.nodeName and "Hips" not in bodyPart.nodeName:
                if not bodyPart.translateOpen:
                    constraintList.append(mayac.orientConstraint(bodyPart.Bind_Joint, bodyPart.Export_Joint))
                else:
                    constraintList.append(mayac.parentConstraint(bodyPart.Bind_Joint, bodyPart.Export_Joint))
            elif bodyPart.Bind_Joint and bodyPart.children:
                constraintList.append(mayac.parentConstraint(bodyPart.Bind_Joint, bodyPart.Export_Joint))
        if self.ExtraJoints:
            for node in self.ExtraJoints:
                if node.children and not node.translateOpen:
                    constraintList.append(mayac.orientConstraint(node.Bind_Joint, node.Export_Joint))
                elif node.translateOpen:
                    print node.nodeName
                    constraintList.append(mayac.parentConstraint(node.Bind_Joint, node.Export_Joint))
                elif node.twistJoint:
                    constraintList.append(mayac.orientConstraint(node.Bind_Joint, node.Export_Joint))
        
        
        #find first and last frames
        startTime = start
        endTime = end
        if startTime == None:
            howManyKeys = []
            last = 0
            highestTime = -999999999
            lowestTime = 99999999
            objectsOfInterest = []
            for bodyPart in self.bodyParts:
                if "4" not in bodyPart.nodeName and "End" not in bodyPart.nodeName:
                    if bodyPart.FK_CTRL:
                        objectsOfInterest.append(bodyPart.FK_CTRL)
                    if bodyPart.IK_CTRL:
                        objectsOfInterest.append(bodyPart.IK_CTRL)
                    if bodyPart.Options_CTRL:
                        objectsOfInterest.append(bodyPart.Options_CTRL)
                    if bodyPart.AnimData_Joint:
                        objectsOfInterest.append(bodyPart.AnimData_Joint)
            objectsOfInterest.append(self.global_CTRL)
            for obj in objectsOfInterest:
                myKeys = mayac.keyframe(obj, query = True, name = True)
                if myKeys:
                    howManyKeys = mayac.keyframe(myKeys[0], query = True, timeChange = True)
                    last = len(howManyKeys)-1
                    if howManyKeys[last] > highestTime:
                        highestTime = howManyKeys[last]
                    if howManyKeys[0] < lowestTime:
                        lowestTime = howManyKeys[0]
            
            startTime = lowestTime
            endTime = highestTime
        highestTime = endTime
        lowestTime = startTime
        
        anythingToBake = True
        
        if startTime == 99999999 and endTime == -999999999:
            anythingToBake = False
        else:
            mayac.currentTime( lowestTime, edit=True )
        
            #control layer must be visible
            controlLayer = DJB_addNameSpace(self.characterNameSpace, "SecondaryControlLayer")
            if mayac.objExists(controlLayer):
                mayac.setAttr("%s.visibility" %(controlLayer), 1)
            if dynamicsToFK:
                if self.ExtraJoints:
                    for node in self.ExtraJoints:
                        if node.Options_CTRL:
                            mayac.setKeyframe(node.Options_CTRL, attribute='FK_Dyn', t=[lowestTime + dynamicsToFK, highestTime - dynamicsToFK])
                            mayac.setKeyframe(node.Options_CTRL, attribute='FK_Dyn', v = 0, t=[lowestTime, highestTime])
            for i in range(int(lowestTime-.5),int(lowestTime-.5)+15):
                mayac.currentTime( i, edit=True )
        
        
        #bake animation to joints
        mayac.select(clear = True)
        if anythingToBake and self.exportList:
            mayac.bakeResults(self.exportList + self.exportListDropFrames, simulation = True, time = (startTime, endTime), sampleBy = 1.0)
        for constraint in constraintList:
            mayac.delete(constraint)
        
        if anythingToBake:
        
            if self.exportListDropFrames:
                if reduceNonEssential:
                    for jointNum in self.exportListDropFrames:
                        animCurves = []
                        temp = mayac.listConnections( '%s.tx' % (jointNum), d=False, s=True )
                        if temp:
                            animCurves.append(temp[0])
                        temp = mayac.listConnections( '%s.ty' % (jointNum), d=False, s=True )
                        if temp:
                            animCurves.append(temp[0])
                        temp = mayac.listConnections( '%s.tz' % (jointNum), d=False, s=True )
                        if temp:
                            animCurves.append(temp[0])
                        temp = mayac.listConnections( '%s.rx' % (jointNum), d=False, s=True )
                        if temp:
                            animCurves.append(temp[0])
                        temp = mayac.listConnections( '%s.ry' % (jointNum), d=False, s=True )
                        if temp:
                            animCurves.append(temp[0])
                        temp = mayac.listConnections( '%s.rz' % (jointNum), d=False, s=True )
                        if temp:
                            animCurves.append(temp[0])
                        if animCurves:
                            for curve in animCurves:
                                mayac.filterCurve(curve, f = "simplify", tol = .015, timeTolerance = .05)
            self.exportList += self.exportListDropFrames
        
        
        #unlock all attributes:
        for joint in (self.exportList+self.exportListDropFrames):
            for attr in ["filmboxTypeID"]:
                if mayac.objExists("%s.%s"%(joint,attr)):
                    mayac.setAttr("%s.%s"%(joint,attr), lock = False, keyable = True)
                    mayac.deleteAttr("%s.%s"%(joint,attr))
            for attr in ["lockInfluenceWeights","liw"]:
                if mayac.objExists("%s.%s"%(joint,attr)):
                    mayac.setAttr("%s.%s"%(joint,attr), lock = False, keyable = True)
            DJB_Unlock(joint)
            mayac.setAttr("%s.jointOrientX" % (joint), lock = False, keyable = True)
            mayac.setAttr("%s.jointOrientY" % (joint), lock = False, keyable = True)
            mayac.setAttr("%s.jointOrientZ" % (joint), lock = False, keyable = True)
            
        #add mesh
        if keepMesh_:
            print "KEEPING MESH!!!"
            #clean up attrs on joints that may cause issues
            
            self.blendShapeTrackers = [] 
            for i in range(len(self.mesh)):
                print self.mesh[i]
                oldSkin = mayac.listConnections(self.characterNameSpace + self.mesh[i], destination = True, type = "skinCluster")
                if oldSkin:
                    oldSkin = oldSkin[0]
                else:  #special case if there are deformers on top of rig and skinCluster is no longer directly connected
                    connections = mayac.listConnections((self.characterNameSpace + self.mesh[i]), destination = True)
                    for connection in connections:
                        if "skinCluster" in connection:
                            oldSkin = connection[:-3]
                
                blendshapeTrack = None
                isBlendShape = mayac.listConnections(self.mesh[i], d=True, type='blendShape')
                if not isBlendShape:
                    print "its a real boy!"    
                    #Keep track of blendshapes and zero out
                    meshConnections = mayac.listConnections(self.mesh[i], type = "objectSet")
                    if meshConnections:
                        meshConnections = set(meshConnections)
                        autoKeyframeState = mayac.autoKeyframe(q=True, state=True)
                        mayac.autoKeyframe(state=False)   
                        for con in meshConnections:
                            blendShapeCons = mayac.listConnections(con, type = "blendShape")
                            if blendShapeCons:
                                for blendShapeNode in blendShapeCons:
                                    blendshapeTrack = blendShapeTracker(blendShapeNode, self.mesh[i])
                                    self.blendShapeTrackers.append(blendshapeTrack)
                
                                     
                    duplicatedMesh = mayac.duplicate(self.characterNameSpace + self.mesh[i], renameChildren = True)[0]
                    shapeNode = mayac.listRelatives(duplicatedMesh, children = True, type = "shape", fullPath = True)[0]
                    oldTransform = mayac.listRelatives(self.characterNameSpace + self.mesh[i], parent = True)[0]
                    DJB_Unlock(duplicatedMesh)
                    DJB_Unlock(oldTransform)
                    isItLocked = mayac.getAttr("%s.visibility" % (oldTransform))
                    mayac.setAttr("%s.visibility" % (oldTransform), 1)
                    mayac.setAttr("%s.visibility" % (self.characterNameSpace + self.mesh[i]), 1)
                    mayac.setAttr("%s.visibility" % (duplicatedMesh), 1)
                    mayac.setAttr("%s.visibility" % (shapeNode), 1)
                    mayac.parent(duplicatedMesh, world = True)
                    duplicatedMesh = mayac.rename(duplicatedMesh, self.original_Mesh_Names[i])
                    self.exportList.append(duplicatedMesh)
                    mayac.disconnectAttr("%s.drawInfo" % (self.Mesh_Layer), "%s.drawOverride" % (duplicatedMesh))
                    shapeNode = mayac.listRelatives(duplicatedMesh, children = True, type = "shape", fullPath = True)[0]
                    mayac.disconnectAttr("%s.drawInfo" % (self.Mesh_Layer), "%s.drawOverride" % (shapeNode))
                    connections = mayac.listConnections("%s.instObjGroups[0]" % (shapeNode), destination=True, plugs=True)
                    if connections:
                        mayac.disconnectAttr("%s.instObjGroups[0]" % (shapeNode), connections[0])
                    if oldSkin:
                        newSkin = None
                        if self.hulaOption:
                            newSkin = mayac.skinCluster( self.Root.Export_Joint, duplicatedMesh)[0]
                        else:
                            newSkin = mayac.skinCluster( self.Hips.Export_Joint, duplicatedMesh)[0]
                        mayac.copySkinWeights( ss= oldSkin, ds= newSkin, noMirror=True )
                    mayac.setAttr("%s.visibility" % (oldTransform), isItLocked)
                    mayac.setAttr("%s.visibility" % (self.characterNameSpace + self.mesh[i]), isItLocked)
                    mayac.setAttr("%s.visibility" % (duplicatedMesh), isItLocked)
                    mayac.setAttr("%s.visibility" % (shapeNode), isItLocked)
                    
                    #Handle Blendshape creation and connections
                    if blendshapeTrack:
                        autoKeyframeState = mayac.autoKeyframe(q=True, state=True)
                        mayac.autoKeyframe(state=False)   
                        blendshapeTrack.duplicate(duplicatedMesh)                                
                        mayac.autoKeyframe(state=autoKeyframeState)  
            #Bake Blendshapes and add to exportList
            if self.blendShapeTrackers:
                bakeList = []
                for tracker in self.blendShapeTrackers:
                    bakeList += tracker.bakeAttrs
                    for attrTracker in tracker.blendShapeAttrTrackers:
                        self.exportList.append(attrTracker.newGeo)
                if anythingToBake:
                    mayac.bakeResults(bakeList, simulation = True, time = (startTime, endTime), sampleBy = 1.0)
        
        
        pyToAttr("%s.exportList" % (self.infoNode), self.exportList)
        return self.exportList
        
        
    def exportSkeleton(self, fileName = None):
        mayac.select(self.exportList+self.exportListDropFrames, replace = True)
        if not fileName:
            mayac.ExportSelection()
        else:
            melLine = 'FBXExport -f "%s.fbx" -s' % (fileName)
            mel.eval(melLine)
        mayac.delete(self.exportList)
        self.exportList = []
        if self.blendShapeTrackers:
            for tracker in self.blendShapeTrackers:
                tracker.restoreScene()
    
    def dynamicsStartEndPoseKeys(self, dynamicsToFK = 0):
        highestTime = -999999999
        lowestTime = 99999999
        objectsOfInterest = []
        for bodyPart in self.bodyParts:
            if "4" not in bodyPart.nodeName and "End" not in bodyPart.nodeName:
                if bodyPart.FK_CTRL:
                    objectsOfInterest.append(bodyPart.FK_CTRL)
                if bodyPart.IK_CTRL:
                    objectsOfInterest.append(bodyPart.IK_CTRL)
                if bodyPart.Options_CTRL:
                    objectsOfInterest.append(bodyPart.Options_CTRL)
                if bodyPart.AnimData_Joint:
                    objectsOfInterest.append(bodyPart.AnimData_Joint)
        objectsOfInterest.append(self.global_CTRL)
        for obj in objectsOfInterest:
            myKeys = mayac.keyframe(obj, query = True, name = True)
            if myKeys:
                howManyKeys = mayac.keyframe(myKeys[0], query = True, timeChange = True)
                last = len(howManyKeys)-1
                if howManyKeys[last] > highestTime:
                    highestTime = howManyKeys[last]
                if howManyKeys[0] < lowestTime:
                    lowestTime = howManyKeys[0]
        
        startTime = lowestTime
        endTime = highestTime
        
        if dynamicsToFK:
            if self.ExtraJoints:
                for node in self.ExtraJoints:
                    if node.Options_CTRL:
                        mayac.setKeyframe(node.Options_CTRL, attribute='FK_Dyn', t=[lowestTime + dynamicsToFK, highestTime - dynamicsToFK])
                        mayac.setKeyframe(node.Options_CTRL, attribute='FK_Dyn', v = 0, t=[lowestTime, highestTime])
    
    #for early version
    def deleteExportSkeleton(self):
        if self.exportList:
            mayac.select(self.exportList, replace = True)
            mayac.delete()
        self.exportList = None
        pyToAttr("%s.exportList" % (self.infoNode), self.exportList)



    def writeInfoNode(self):
        self.infoNode = mayac.createNode("transform", name = "MIXAMO_CHARACTER_infoNode")
        pyToAttr("%s.ExtraJoints" % (self.infoNode), self.ExtraJoints)
        pyToAttr("%s.numExtraJointChains" % (self.infoNode), self.numExtraJointChains)
        
        
        pyToAttr("%s.name" % (self.infoNode), self.name)
        pyToAttr("%s.mesh" % (self.infoNode), self.mesh)
        pyToAttr("%s.original_Mesh_Names" % (self.infoNode), self.original_Mesh_Names)
        pyToAttr("%s.jointNamespace" % (self.infoNode), self.jointNamespace)
        pyToAttr("%s.rigType" % (self.infoNode), self.rigType)
        pyToAttr("%s.BoundingBox" % (self.infoNode), self.BoundingBox)
        pyToAttr("%s.Root" % (self.infoNode), self.Root.writeInfoNode())
        pyToAttr("%s.Hips" % (self.infoNode), self.Hips.writeInfoNode())
        pyToAttr("%s.Spine" % (self.infoNode), self.Spine.writeInfoNode())
        pyToAttr("%s.Spine1" % (self.infoNode), self.Spine1.writeInfoNode())
        pyToAttr("%s.Spine2" % (self.infoNode), self.Spine2.writeInfoNode())
        if self.Spine3:
            pyToAttr("%s.Spine3" % (self.infoNode), self.Spine3.writeInfoNode())
        pyToAttr("%s.Neck" % (self.infoNode), self.Neck.writeInfoNode())
        pyToAttr("%s.Neck1" % (self.infoNode), self.Neck1.writeInfoNode())
        pyToAttr("%s.Head" % (self.infoNode), self.Head.writeInfoNode())
        pyToAttr("%s.HeadTop_End" % (self.infoNode), self.HeadTop_End.writeInfoNode())
        pyToAttr("%s.LeftShoulder" % (self.infoNode), self.LeftShoulder.writeInfoNode())
        pyToAttr("%s.LeftArm" % (self.infoNode), self.LeftArm.writeInfoNode())
        pyToAttr("%s.LeftForeArm" % (self.infoNode), self.LeftForeArm.writeInfoNode())
        pyToAttr("%s.LeftHand" % (self.infoNode), self.LeftHand.writeInfoNode())
        pyToAttr("%s.LeftHandThumb1" % (self.infoNode), self.LeftHandThumb1.writeInfoNode())
        pyToAttr("%s.LeftHandThumb2" % (self.infoNode), self.LeftHandThumb2.writeInfoNode())
        pyToAttr("%s.LeftHandThumb3" % (self.infoNode), self.LeftHandThumb3.writeInfoNode())
        pyToAttr("%s.LeftHandThumb4" % (self.infoNode), self.LeftHandThumb4.writeInfoNode())
        pyToAttr("%s.LeftHandIndex1" % (self.infoNode), self.LeftHandIndex1.writeInfoNode())
        pyToAttr("%s.LeftHandIndex2" % (self.infoNode), self.LeftHandIndex2.writeInfoNode())
        pyToAttr("%s.LeftHandIndex3" % (self.infoNode), self.LeftHandIndex3.writeInfoNode())
        pyToAttr("%s.LeftHandIndex4" % (self.infoNode), self.LeftHandIndex4.writeInfoNode())
        pyToAttr("%s.LeftHandMiddle1" % (self.infoNode), self.LeftHandMiddle1.writeInfoNode())
        pyToAttr("%s.LeftHandMiddle2" % (self.infoNode), self.LeftHandMiddle2.writeInfoNode())
        pyToAttr("%s.LeftHandMiddle3" % (self.infoNode), self.LeftHandMiddle3.writeInfoNode())
        pyToAttr("%s.LeftHandMiddle4" % (self.infoNode), self.LeftHandMiddle4.writeInfoNode())
        pyToAttr("%s.LeftHandRing1" % (self.infoNode), self.LeftHandRing1.writeInfoNode())
        pyToAttr("%s.LeftHandRing2" % (self.infoNode), self.LeftHandRing2.writeInfoNode())
        pyToAttr("%s.LeftHandRing3" % (self.infoNode), self.LeftHandRing3.writeInfoNode())
        pyToAttr("%s.LeftHandRing4" % (self.infoNode), self.LeftHandRing4.writeInfoNode())
        pyToAttr("%s.LeftHandPinky1" % (self.infoNode), self.LeftHandPinky1.writeInfoNode())
        pyToAttr("%s.LeftHandPinky2" % (self.infoNode), self.LeftHandPinky2.writeInfoNode())
        pyToAttr("%s.LeftHandPinky3" % (self.infoNode), self.LeftHandPinky3.writeInfoNode())
        pyToAttr("%s.LeftHandPinky4" % (self.infoNode), self.LeftHandPinky4.writeInfoNode())
        pyToAttr("%s.RightShoulder" % (self.infoNode), self.RightShoulder.writeInfoNode())
        pyToAttr("%s.RightArm" % (self.infoNode), self.RightArm.writeInfoNode())
        pyToAttr("%s.RightForeArm" % (self.infoNode), self.RightForeArm.writeInfoNode())
        pyToAttr("%s.RightHand" % (self.infoNode), self.RightHand.writeInfoNode())
        pyToAttr("%s.RightHandThumb1" % (self.infoNode), self.RightHandThumb1.writeInfoNode())
        pyToAttr("%s.RightHandThumb2" % (self.infoNode), self.RightHandThumb2.writeInfoNode())
        pyToAttr("%s.RightHandThumb3" % (self.infoNode), self.RightHandThumb3.writeInfoNode())
        pyToAttr("%s.RightHandThumb4" % (self.infoNode), self.RightHandThumb4.writeInfoNode())
        pyToAttr("%s.RightHandIndex1" % (self.infoNode), self.RightHandIndex1.writeInfoNode())
        pyToAttr("%s.RightHandIndex2" % (self.infoNode), self.RightHandIndex2.writeInfoNode())
        pyToAttr("%s.RightHandIndex3" % (self.infoNode), self.RightHandIndex3.writeInfoNode())
        pyToAttr("%s.RightHandIndex4" % (self.infoNode), self.RightHandIndex4.writeInfoNode())
        pyToAttr("%s.RightHandMiddle1" % (self.infoNode), self.RightHandMiddle1.writeInfoNode())
        pyToAttr("%s.RightHandMiddle2" % (self.infoNode), self.RightHandMiddle2.writeInfoNode())
        pyToAttr("%s.RightHandMiddle3" % (self.infoNode), self.RightHandMiddle3.writeInfoNode())
        pyToAttr("%s.RightHandMiddle4" % (self.infoNode), self.RightHandMiddle4.writeInfoNode())
        pyToAttr("%s.RightHandRing1" % (self.infoNode), self.RightHandRing1.writeInfoNode())
        pyToAttr("%s.RightHandRing2" % (self.infoNode), self.RightHandRing2.writeInfoNode())
        pyToAttr("%s.RightHandRing3" % (self.infoNode), self.RightHandRing3.writeInfoNode())
        pyToAttr("%s.RightHandRing4" % (self.infoNode), self.RightHandRing4.writeInfoNode())
        pyToAttr("%s.RightHandPinky1" % (self.infoNode), self.RightHandPinky1.writeInfoNode())
        pyToAttr("%s.RightHandPinky2" % (self.infoNode), self.RightHandPinky2.writeInfoNode())
        pyToAttr("%s.RightHandPinky3" % (self.infoNode), self.RightHandPinky3.writeInfoNode())
        pyToAttr("%s.RightHandPinky4" % (self.infoNode), self.RightHandPinky4.writeInfoNode())
        pyToAttr("%s.LeftUpLeg" % (self.infoNode), self.LeftUpLeg.writeInfoNode())
        pyToAttr("%s.LeftLeg" % (self.infoNode), self.LeftLeg.writeInfoNode())
        pyToAttr("%s.LeftFoot" % (self.infoNode), self.LeftFoot.writeInfoNode())
        pyToAttr("%s.LeftToeBase" % (self.infoNode), self.LeftToeBase.writeInfoNode())
        pyToAttr("%s.LeftToe_End" % (self.infoNode), self.LeftToe_End.writeInfoNode())
        pyToAttr("%s.RightUpLeg" % (self.infoNode), self.RightUpLeg.writeInfoNode())
        pyToAttr("%s.RightLeg" % (self.infoNode), self.RightLeg.writeInfoNode())
        pyToAttr("%s.RightFoot" % (self.infoNode), self.RightFoot.writeInfoNode())
        pyToAttr("%s.RightToeBase" % (self.infoNode), self.RightToeBase.writeInfoNode())
        pyToAttr("%s.RightToe_End" % (self.infoNode), self.RightToe_End.writeInfoNode())
        
        mayac.parent(self.infoNode, self.Misc_GRP)
        DJB_LockNHide(self.infoNode)
        for bodyPart in (self.Root, self.Hips, self.Spine, self.Spine1, self.Spine2, self.Spine3, self.Neck, self.Neck1, self.Head, self.HeadTop_End, self.LeftShoulder, 
                              self.LeftArm, self.LeftForeArm, self.LeftHand, self.LeftHandThumb1, self.LeftHandThumb2, self.LeftHandThumb3, 
                              self.LeftHandThumb4, self.LeftHandIndex1, self.LeftHandIndex2, self.LeftHandIndex3, self.LeftHandIndex4,
                              self.LeftHandMiddle1, self.LeftHandMiddle2, self.LeftHandMiddle3, self.LeftHandMiddle4, self.LeftHandRing1,
                              self.LeftHandRing2, self.LeftHandRing3, self.LeftHandRing4, self.LeftHandPinky1, self.LeftHandPinky2, 
                              self.LeftHandPinky3, self.LeftHandPinky4, self.RightShoulder, self.RightArm, self.RightForeArm, 
                              self.RightHand, self.RightHandThumb1, self.RightHandThumb2, self.RightHandThumb3, 
                              self.RightHandThumb4, self.RightHandIndex1, self.RightHandIndex2, self.RightHandIndex3, self.RightHandIndex4,
                              self.RightHandMiddle1, self.RightHandMiddle2, self.RightHandMiddle3, self.RightHandMiddle4, self.RightHandRing1,
                              self.RightHandRing2, self.RightHandRing3, self.RightHandRing4, self.RightHandPinky1, self.RightHandPinky2, 
                              self.RightHandPinky3, self.RightHandPinky4, self.LeftUpLeg, self.LeftLeg, self.LeftFoot, self.LeftToeBase,
                              self.LeftToe_End, self.RightUpLeg, self.RightLeg, self.RightFoot, self.RightToeBase, self.RightToe_End):
            mayac.parent(bodyPart.infoNode, self.Misc_GRP)
            DJB_LockNHide(bodyPart.infoNode)

        pyToAttr("%s.proportions" % (self.infoNode), self.proportions)
        pyToAttr("%s.defaultControlScale" % (self.infoNode), self.defaultControlScale)
        pyToAttr("%s.Character_GRP" % (self.infoNode), self.Character_GRP)
        pyToAttr("%s.global_CTRL" % (self.infoNode), self.global_CTRL)
        pyToAttr("%s.CTRL_GRP" % (self.infoNode), self.CTRL_GRP)
        pyToAttr("%s.Joint_GRP" % (self.infoNode), self.Joint_GRP)
        pyToAttr("%s.AnimData_Joint_GRP" % (self.infoNode), self.AnimData_Joint_GRP)
        pyToAttr("%s.Bind_Joint_GRP" % (self.infoNode), self.Bind_Joint_GRP)
        pyToAttr("%s.Mesh_GRP" % (self.infoNode), self.Mesh_GRP)
        pyToAttr("%s.Misc_GRP" % (self.infoNode), self.Misc_GRP)
        pyToAttr("%s.LeftArm_Switch_Reverse" % (self.infoNode), self.LeftArm_Switch_Reverse)
        pyToAttr("%s.RightArm_Switch_Reverse" % (self.infoNode), self.RightArm_Switch_Reverse)
        pyToAttr("%s.LeftLeg_Switch_Reverse" % (self.infoNode), self.LeftLeg_Switch_Reverse)
        pyToAttr("%s.RightLeg_Switch_Reverse" % (self.infoNode), self.RightLeg_Switch_Reverse)
        pyToAttr("%s.Bind_Joint_SelectSet" % (self.infoNode), self.Bind_Joint_SelectSet)
        pyToAttr("%s.AnimData_Joint_SelectSet" % (self.infoNode), self.AnimData_Joint_SelectSet)
        pyToAttr("%s.Controls_SelectSet" % (self.infoNode), self.Controls_SelectSet)
        pyToAttr("%s.Geo_SelectSet" % (self.infoNode), self.Geo_SelectSet)
        pyToAttr("%s.Left_Toe_IK_AnimData_GRP" % (self.infoNode), self.Left_Toe_IK_AnimData_GRP)
        pyToAttr("%s.Left_Toe_IK_CTRL" % (self.infoNode), self.Left_Toe_IK_CTRL)
        pyToAttr("%s.Left_ToeBase_IK_AnimData_GRP" % (self.infoNode), self.Left_ToeBase_IK_AnimData_GRP)
        pyToAttr("%s.Left_IK_ToeBase_animData_MultNode" % (self.infoNode), self.Left_IK_ToeBase_animData_MultNode)
        pyToAttr("%s.Left_ToeBase_IK_CTRL" % (self.infoNode), self.Left_ToeBase_IK_CTRL)
        pyToAttr("%s.Left_Ankle_IK_AnimData_GRP" % (self.infoNode), self.Left_Ankle_IK_AnimData_GRP)
        pyToAttr("%s.Left_Ankle_IK_CTRL" % (self.infoNode), self.Left_Ankle_IK_CTRL)
        pyToAttr("%s.Left_ToeBase_IkHandle" % (self.infoNode), self.Left_ToeBase_IkHandle)
        pyToAttr("%s.Left_ToeEnd_IkHandle" % (self.infoNode), self.Left_ToeEnd_IkHandle)
        pyToAttr("%s.Right_Toe_IK_AnimData_GRP" % (self.infoNode), self.Right_Toe_IK_AnimData_GRP)
        pyToAttr("%s.Right_Toe_IK_CTRL" % (self.infoNode), self.Right_Toe_IK_CTRL)
        pyToAttr("%s.Right_ToeBase_IK_AnimData_GRP" % (self.infoNode), self.Right_ToeBase_IK_AnimData_GRP)
        pyToAttr("%s.Right_IK_ToeBase_animData_MultNode" % (self.infoNode), self.Right_IK_ToeBase_animData_MultNode)
        pyToAttr("%s.Right_ToeBase_IK_CTRL" % (self.infoNode), self.Right_ToeBase_IK_CTRL)
        pyToAttr("%s.Right_Ankle_IK_AnimData_GRP" % (self.infoNode), self.Right_Ankle_IK_AnimData_GRP)
        pyToAttr("%s.Right_Ankle_IK_CTRL" % (self.infoNode), self.Right_Ankle_IK_CTRL)
        pyToAttr("%s.Right_ToeBase_IkHandle" % (self.infoNode), self.Right_ToeBase_IkHandle)
        pyToAttr("%s.Right_ToeEnd_IkHandle" % (self.infoNode), self.Right_ToeEnd_IkHandle)
        pyToAttr("%s.LeftHand_CTRLs_GRP" % (self.infoNode), self.LeftHand_CTRLs_GRP)
        pyToAttr("%s.RightHand_CTRLs_GRP" % (self.infoNode), self.RightHand_CTRLs_GRP)
        pyToAttr("%s.LeftFoot_FootRoll_MultNode" % (self.infoNode), self.LeftFoot_FootRoll_MultNode)
        pyToAttr("%s.LeftFoot_ToeRoll_MultNode" % (self.infoNode), self.LeftFoot_ToeRoll_MultNode)
        pyToAttr("%s.RightFoot_FootRoll_MultNode" % (self.infoNode), self.RightFoot_FootRoll_MultNode)
        pyToAttr("%s.RightFoot_ToeRoll_MultNode" % (self.infoNode), self.RightFoot_ToeRoll_MultNode)
        pyToAttr("%s.RightFoot_HipPivot_MultNode" % (self.infoNode), self.RightFoot_HipPivot_MultNode)
        pyToAttr("%s.RightFoot_BallPivot_MultNode" % (self.infoNode), self.RightFoot_BallPivot_MultNode)
        pyToAttr("%s.RightFoot_ToePivot_MultNode" % (self.infoNode), self.RightFoot_ToePivot_MultNode)
        pyToAttr("%s.RightFoot_HipSideToSide_MultNode" % (self.infoNode), self.RightFoot_HipSideToSide_MultNode)
        pyToAttr("%s.RightFoot_ToeRotate_MultNode" % (self.infoNode), self.RightFoot_ToeRotate_MultNode)
        pyToAttr("%s.IK_Dummy_Joint_GRP" % (self.infoNode), self.IK_Dummy_Joint_GRP)
        pyToAttr("%s.LeftHand_grandparent_Constraint" % (self.infoNode), self.LeftHand_grandparent_Constraint)
        pyToAttr("%s.LeftHand_grandparent_Constraint_Reverse" % (self.infoNode), self.LeftHand_grandparent_Constraint_Reverse)
        pyToAttr("%s.RightHand_grandparent_Constraint" % (self.infoNode), self.RightHand_grandparent_Constraint)
        pyToAttr("%s.RightHand_grandparent_Constraint_Reverse" % (self.infoNode), self.RightHand_grandparent_Constraint_Reverse)
        pyToAttr("%s.LeftForeArm_grandparent_Constraint" % (self.infoNode), self.LeftForeArm_grandparent_Constraint)
        pyToAttr("%s.LeftForeArm_grandparent_Constraint_Reverse" % (self.infoNode), self.LeftForeArm_grandparent_Constraint_Reverse)
        pyToAttr("%s.RightForeArm_grandparent_Constraint" % (self.infoNode), self.RightForeArm_grandparent_Constraint)
        pyToAttr("%s.RightForeArm_grandparent_Constraint_Reverse" % (self.infoNode), self.RightForeArm_grandparent_Constraint_Reverse)
        pyToAttr("%s.origAnim" % (self.infoNode), self.origAnim)
        pyToAttr("%s.origAnimation_Layer" % (self.infoNode), self.origAnimation_Layer)
        pyToAttr("%s.Mesh_Layer" % (self.infoNode), self.Mesh_Layer)
        pyToAttr("%s.Bind_Joint_Layer" % (self.infoNode), self.Bind_Joint_Layer)
        pyToAttr("%s.hulaOption" % (self.infoNode), self.hulaOption)
        pyToAttr("%s.exportList" % (self.infoNode), self.exportList)
        pyToAttr("%s.fingerFlip" % (self.infoNode), self.fingerFlip)
        
    
    def remakeMeshInfoNode(self):
        joints = []
        for bodyPart in self.bodyParts:
            if bodyPart.Bind_Joint:
                if mayac.objExists(bodyPart.Bind_Joint):
                    joints.append(bodyPart.Bind_Joint)
        meshes = []
        for skin in mayac.listConnections(joints,type='skinCluster'):  
            if skin:  
                geos = mayac.skinCluster(skin,query=True,geometry=True)
                for geo in geos:
                    if geo not in meshes:
                        meshes.append(geo)
        transformNames = []
        for geo in meshes:
            if "ShapeOrig" not in geo and "Bounding_Box_Override_Cube" not in geo:
                transform = mayac.listRelatives(geo, parent = True)[0]
                while transform.find("Mesh_"[0]) != -1:
                    transform = transform[5:len(transform)] #...hopefully they shouldn't start with Mesh_
                transformNames.append(transform)
        self.mesh = meshes
        self.original_Mesh_Names = transformNames
        pyToAttr("%s.mesh" % (self.infoNode), self.mesh)
        pyToAttr("%s.original_Mesh_Names" % (self.infoNode), self.original_Mesh_Names)
        OpenMaya.MGlobal.displayInfo("Process Complete")
        
        
        
    def makeExtraJointsInfoNode(self, joints):
        newExtraJoints = []
        #new characterNode for each joint
        if self.numExtraJointChains:
            self.numExtraJointChains += 1
        else:
            self.numExtraJointChains = 1
        for i in range(len(joints)):
            parentJoint = mayac.listRelatives(joints[i], parent = True)[0]
            if i == 0:
                ParentBodyPart = None
                for bodyPart in self.bodyParts:
                    if parentJoint == bodyPart.Bind_Joint:
                        ParentBodyPart = bodyPart
                if not ParentBodyPart:
                    for extraJoint in self.ExtraJoints:
                        if parentJoint == extraJoint.Bind_Joint:
                            ParentBodyPart = extraJoint
                newExtraJoints.append(DJB_CharacterNode(joints[i], parent = ParentBodyPart, twistJoint_ = True, translateOpen_ = True))
                jointIndex = len(newExtraJoints)-1
            else:
                newExtraJoints.append(DJB_CharacterNode(joints[i], parent = newExtraJoints[jointIndex], twistJoint_ = True, translateOpen_ = True))
                jointIndex = len(newExtraJoints)-1

        #infoNode stuff
        for i in range(len(joints)):
            newExtraJoints[i].writeInfoNode()
            mayac.parent(newExtraJoints[i].infoNode, self.Misc_GRP)
        infoNodes = []
        if not self.ExtraJoints:
            self.ExtraJoints = []
        else:
            infoNodes = attrToPy("%s.ExtraJoints" % (self.infoNode))
        if not infoNodes:
            infoNodes = []
        for joint in newExtraJoints:
            self.ExtraJoints.append(joint)
            infoNodes.append(joint.infoNode)
        pyToAttr("%s.ExtraJoints" % (self.infoNode), infoNodes)
        OpenMaya.MGlobal.displayInfo("Process Complete")
        
    def makeDynamicChainRig(self, joints, dynamic_ = "ZV", control_ = "FK"):
        newExtraJoints = []
        #new characterNode for each joint
        if self.numExtraJointChains:
            self.numExtraJointChains += 1
        else:
            self.numExtraJointChains = 1
        for i in range(len(joints)):
            parentJoint = mayac.listRelatives(joints[i], parent = True)[0]
            if i == 0:
                ParentBodyPart = None
                for bodyPart in self.bodyParts:
                    if parentJoint == bodyPart.Bind_Joint:
                        ParentBodyPart = bodyPart
                if not ParentBodyPart:
                    for extraJoint in self.ExtraJoints:
                        if parentJoint == extraJoint.Bind_Joint:
                            ParentBodyPart = extraJoint
                newExtraJoints.append(DJB_CharacterNode(joints[i], parent = ParentBodyPart, dynamic_ = dynamic_))
                jointIndex = len(newExtraJoints)-1
                newExtraJoints[jointIndex].duplicateJoint(control_, parent_ = "Bind_Joint")
                newExtraJoints[jointIndex].duplicateJoint(dynamic_, parent_ = "Bind_Joint")
                newExtraJoints[jointIndex].duplicateJoint("AnimData")
            else:
                newExtraJoints.append(DJB_CharacterNode(joints[i], parent = newExtraJoints[jointIndex], dynamic_ = dynamic_))
                jointIndex = len(newExtraJoints)-1
                newExtraJoints[jointIndex].duplicateJoint(control_)
                newExtraJoints[jointIndex].duplicateJoint(dynamic_)
                newExtraJoints[jointIndex].duplicateJoint("AnimData")
            
            #FK controls
            if i < len(joints)-1 and len(joints) > 1:
                newExtraJoints[jointIndex].createControl(type = "FK", rigType = "Dyn",
                                    style = "circle", 
                                    scale = (self.proportions["depth"]*0.10, self.proportions["depth"]*0.10, self.proportions["depth"]*0.10),
                                    offset = (self.proportions["depth"]*0.05, 0, 0),
                                    rotate = (0, 0, 90),
                                    color_ = "white")
            elif len(joints) == 1:
                newExtraJoints[jointIndex].createControl(type = "FK", rigType = "Dyn",
                                    style = "circle", 
                                    scale = (self.proportions["depth"]*0.10, self.proportions["depth"]*0.10, self.proportions["depth"]*0.10),
                                    offset = (self.proportions["depth"]*0.05, 0, 0),
                                    rotate = (0, 0, 90),
                                    color_ = "white")
                
                
            #Options CTRL
            if i == len(joints)-1:
                newExtraJoints[jointIndex].createControl(type = "options", 
                                    style = "options",
                                    scale = (self.proportions["depth"]*0.06, self.proportions["depth"]*0.06, self.proportions["depth"]*-0.06),
                                    rotate = (-90, 0, 90),
                                    offset = (0, self.proportions["depth"]*.15, 0),  
                                    partialConstraint = 0,
                                    color_ = "white",
                                    name_ = "%s_Options"%(newExtraJoints[0].nodeName))
                
        #ZV controls
        #one joint
        if len(joints) == 1:
            newExtraJoints[0].translateOpen = True
            FullName = newExtraJoints[0].nodeName
            newExtraJoints[0].IK_Handle = DJB_createGroup(pivotFrom = newExtraJoints[0].Bind_Joint, fullName = "%s_Dyn_NULL"%(FullName))
            newExtraJoints[0].IK_CTRL_POS_GRP = DJB_createGroup(newExtraJoints[0].IK_Handle)
            mayac.parent(newExtraJoints[i].IK_CTRL_POS_GRP, self.global_CTRL)
            mayac.setAttr("%s.visibility"%(newExtraJoints[i].IK_Handle), 0)
            mayac.parentConstraint(newExtraJoints[0].parent.Bind_Joint, newExtraJoints[0].IK_CTRL_POS_GRP, maintainOffset = True)
            newExtraJoints[0].Dyn_Node = nParticleMethod(newExtraJoints[0].IK_Handle, weight=0.7, conserve=1.0, transfShapes=False)
            newExtraJoints[0].createControl(type = "Dyn",
                                    style = "box1",
                                    scale = (self.proportions["depth"]*0.1, self.proportions["depth"]*0.1, self.proportions["depth"]*0.1),
                                    offset = (0, 0, 0),
                                    color_ = "white",
                                    name_ = "%s_Dyn_CTRL"%(newExtraJoints[0].nodeName))
            mayac.parent(newExtraJoints[0].Dyn_CTRL, self.global_CTRL)
            mayac.parentConstraint(newExtraJoints[0].Bind_Joint, newExtraJoints[0].Dyn_CTRL)
            mayac.parentConstraint(newExtraJoints[0].IK_Handle, newExtraJoints[0].Dyn_Joint)
            
            
            
        endJointIndex = len(newExtraJoints)-1
        if dynamic_ == "ZV" and jointIndex > 0: #more than one dynamic joint  
            for i in range(1, endJointIndex+1): 
                temp = mayac.ikHandle( sj=newExtraJoints[i].parent.Dyn_Joint, ee=newExtraJoints[i].Dyn_Joint, n = "%s_DYN_IKHandle"%(newExtraJoints[i-1].nodeName))
                newExtraJoints[i].IK_Handle = temp[0]
                mayac.rename(temp[1], "%s_DYN_IKEffector"%(newExtraJoints[i].nodeName))
                mayac.setAttr("%s.visibility"%(newExtraJoints[i].IK_Handle), 0)
                newExtraJoints[i].IK_CTRL_POS_GRP = DJB_createGroup(newExtraJoints[i].IK_Handle)
                if i==1:
                    mayac.parent(newExtraJoints[i].IK_CTRL_POS_GRP, self.global_CTRL)
                    mayac.parentConstraint(newExtraJoints[0].parent.Bind_Joint, newExtraJoints[i].IK_CTRL_POS_GRP, maintainOffset = True)
                else:
                    mayac.parent(newExtraJoints[i].IK_CTRL_POS_GRP, newExtraJoints[i-1].IK_Handle)
                newExtraJoints[i].Dyn_Node = nParticleMethod(newExtraJoints[i].IK_Handle, weight=0.7, conserve=1.0, transfShapes=False)
            newExtraJoints[endJointIndex].createControl(type = "Dyn",
                                    style = "box1",
                                    scale = (self.proportions["depth"]*0.1, self.proportions["depth"]*0.1, self.proportions["depth"]*0.1),
                                    offset = (0, 0, 0),
                                    color_ = "white",
                                    name_ = "%s_Dyn_CTRL"%(newExtraJoints[0].nodeName))
            mayac.parent(newExtraJoints[endJointIndex].Dyn_CTRL, self.global_CTRL)
            mayac.parentConstraint(newExtraJoints[endJointIndex].Bind_Joint, newExtraJoints[endJointIndex].Dyn_CTRL)
                

        for i in range(len(joints)):
            #Hook up controls
            newExtraJoints[i].finalizeCTRLs()
            newExtraJoints[i].lockUpCTRLs()
        mayac.parent(newExtraJoints[len(newExtraJoints)-1].Options_CTRL, self.global_CTRL)
        #Hook up Attrs
        for i in range(len(joints)):
            if newExtraJoints[i].Dyn_Node:
                mayac.connectAttr("%s.weight" %(newExtraJoints[len(newExtraJoints)-1].Dyn_CTRL), "%s.weight" %(newExtraJoints[i].Dyn_Node))
                mayac.connectAttr("%s.conserve" %(newExtraJoints[len(newExtraJoints)-1].Dyn_CTRL), "%s.conserve" %(newExtraJoints[i].Dyn_Node))
            if newExtraJoints[i].Dyn_Joint:
                mayac.connectAttr("%s.multiplier" %(newExtraJoints[len(newExtraJoints)-1].Dyn_CTRL), "%s.input2X" %(newExtraJoints[i].Dyn_Mult))
                mayac.connectAttr("%s.multiplier" %(newExtraJoints[len(newExtraJoints)-1].Dyn_CTRL), "%s.input2Y" %(newExtraJoints[i].Dyn_Mult))
                mayac.connectAttr("%s.multiplier" %(newExtraJoints[len(newExtraJoints)-1].Dyn_CTRL), "%s.input2Z" %(newExtraJoints[i].Dyn_Mult))
                if newExtraJoints[i].translateOpen:
                    jointPosHolder = mayac.shadingNode ('multiplyDivide', asUtility = True, name = "%s_JointPos"%(newExtraJoints[i].Dyn_Mult1))
                    jointPosHolder1 = mayac.shadingNode ('multiplyDivide', asUtility = True, name = "%s_JointPos"%(newExtraJoints[i].Dyn_Mult1))
                    trans = mayac.getAttr("%s.translate"%(newExtraJoints[i].Bind_Joint))[0]
                    mayac.setAttr("%s.input1X"%(jointPosHolder), trans[0])
                    mayac.setAttr("%s.input1Y"%(jointPosHolder), trans[1])
                    mayac.setAttr("%s.input1Z"%(jointPosHolder), trans[2])
                    mayac.setAttr("%s.input1X"%(jointPosHolder1), trans[0])
                    mayac.setAttr("%s.input1Y"%(jointPosHolder1), trans[1])
                    mayac.setAttr("%s.input1Z"%(jointPosHolder1), trans[2])
                    subtract1 = mayac.shadingNode ('plusMinusAverage', asUtility = True, name = "%s_Subtract"%(newExtraJoints[i].Dyn_Mult1))
                    mel.eval('AEnewNonNumericMultiAddNewItem("%s", "input3D");'%(subtract1))
                    mel.eval('AEnewNonNumericMultiAddNewItem("%s", "input3D");'%(subtract1))
                    mayac.setAttr("%s.operation"%(subtract1), 2)
                    mayac.connectAttr("%s.output"%(jointPosHolder), "%s.input3D[0]"%(subtract1), force = True)
                    mayac.connectAttr("%s.translate"%(newExtraJoints[i].Dyn_Joint), "%s.input3D[1]"%(subtract1), force = True)
                    mayac.connectAttr("%s.output3D"%(subtract1), "%s.input1"%(newExtraJoints[i].Dyn_Mult1), force = True)
                    add1 = mayac.shadingNode ('plusMinusAverage', asUtility = True, name = "%s_Add"%(newExtraJoints[i].Dyn_Mult1))
                    mel.eval('AEnewNonNumericMultiAddNewItem("%s", "input3D");'%(add1))
                    mel.eval('AEnewNonNumericMultiAddNewItem("%s", "input3D");'%(add1))
                    mayac.connectAttr("%s.output"%(newExtraJoints[i].Dyn_Mult1), "%s.input3D[0]"%(add1), force = True)
                    mayac.connectAttr("%s.output"%(jointPosHolder1), "%s.input3D[1]"%(add1), force = True)
                    mayac.connectAttr("%s.output3D"%(add1), "%s.translate"%(newExtraJoints[i].DynMult_Joint), force = True)
                    mayac.connectAttr("%s.multiplier" %(newExtraJoints[len(newExtraJoints)-1].Dyn_CTRL), "%s.input2Y" %(newExtraJoints[i].Dyn_Mult1))
                    mayac.connectAttr("%s.multiplier" %(newExtraJoints[len(newExtraJoints)-1].Dyn_CTRL), "%s.input2Z" %(newExtraJoints[i].Dyn_Mult1))
        #Contraint Reverses
        reverseNode = mayac.createNode( 'reverse', n="%s_Switch_Reverse" %(newExtraJoints[0].nodeName))
        typeName = ""
        if dynamic_ == "ZV" and control_ == "FK":
            typeName = "FK_Dyn"
        mayac.setAttr("%s.weight" %(newExtraJoints[len(joints)-1].Dyn_CTRL), 0.8)
        mayac.setAttr("%s.conserve" %(newExtraJoints[len(joints)-1].Dyn_CTRL), 1.0)
        mayac.setAttr("%s.%s" %(newExtraJoints[len(newExtraJoints)-1].Options_CTRL, typeName), 1.0)
        mayac.connectAttr("%s.%s" %(newExtraJoints[len(joints)-1].Options_CTRL, typeName), "%s.inputX" %(reverseNode))
        for i in range(len(joints)):
            if newExtraJoints[i].Constraint:
                mayac.setAttr("%s.interpType" %(newExtraJoints[i].Constraint), 2)
                mayac.connectAttr("%s.%s" %(newExtraJoints[len(joints)-1].Options_CTRL, typeName), "%s.%sW1" %(newExtraJoints[i].Constraint, newExtraJoints[i].DynMult_Joint))
                mayac.connectAttr("%s.outputX" %(reverseNode), "%s.%sW0" %(newExtraJoints[i].Constraint, newExtraJoints[i].FK_Joint))
            DJB_Unlock_Connect_Lock("%s.%s" %(newExtraJoints[len(joints)-1].Options_CTRL, typeName), "%s.visibility" %(newExtraJoints[i].DynMult_Joint))
            DJB_Unlock_Connect_Lock("%s.outputX" %(reverseNode), "%s.visibility" %(newExtraJoints[i].FK_Joint))
            if newExtraJoints[i].FK_CTRL:
                DJB_Unlock_Connect_Lock("%s.outputX" %(reverseNode), "%s.visibility" %(newExtraJoints[i].FK_CTRL))
            if newExtraJoints[i].Dyn_CTRL:
                DJB_Unlock_Connect_Lock("%s.%s" %(newExtraJoints[len(joints)-1].Options_CTRL, typeName), "%s.visibility" %(newExtraJoints[i].Dyn_CTRL))
        #infoNode stuff
        for i in range(len(joints)):
            newExtraJoints[i].writeInfoNode()
            mayac.parent(newExtraJoints[i].infoNode, self.Misc_GRP)
        infoNodes = []
        if not self.ExtraJoints:
            self.ExtraJoints = []
        else:
            infoNodes = attrToPy("%s.ExtraJoints" % (self.infoNode))
        if not infoNodes:
            infoNodes = []
        for joint in newExtraJoints:
            self.ExtraJoints.append(joint)
            infoNodes.append(joint.infoNode)
        pyToAttr("%s.ExtraJoints" % (self.infoNode), infoNodes)
        
 
 
def DJB_populatePythonSpaceWithCharacter():
    global DJB_CharacterInstance
    DJB_CharacterInstance = []
    mayac.select(all = True, hi = True)
    unknownNodes = mayac.ls(selection = True, type = "transform")
    infoNodes = []
    for check in unknownNodes:
        if "MIXAMO_CHARACTER_infoNode" in check:
            infoNodes.append(check)
    for infoNode in infoNodes:
        DJB_CharacterInstance.append(DJB_Character(infoNode_ = infoNode))
    mayac.select(clear = True)

            
            
            

            
class MIXAMO_AutoControlRig_UI:
    def __init__(self):
        global Mixamo_AutoControlRig_Version
        self.file1Dir = None
        self.name = "MIXAMO_AutoControlRig_UI"
        self.title = "MIXAMO Auto-Control-Rig v. %s" % (Mixamo_AutoControlRig_Version)

        # Begin creating the UI
        if (mayac.window(self.name, q=1, exists=1)): mayac.deleteUI(self.name)
        self.window = mayac.window(self.name, title=self.title, menuBar=True)
        
        #menu
        mayac.menu( label='Help', helpMenu=True )
        mayac.menuItem(l='Tutorials Site', command = lambda *args: goToWebpage("tutorials")) 
        mayac.menuItem( label='Bugs, Feature Requests, Confusions, Praise, Support', command = lambda *args: goToWebpage("community"))
        mayac.menuItem( label='About', command = self.showAboutWindow)
        
        
        #forms
        self.form = mayac.formLayout(w=650)
        mayac.columnLayout(adjustableColumn = True, w=650)
        mayac.text( label=' Thank you for trying the Mixamo Maya Auto-Control-Rig!', align='center' )
        mayac.text( label=' Please send Bugs, Feature Requests, Confusions, and/or Praise', align='center' )
        supportText = mayac.text( label=' to our community site.(Link in Help menu)', align='center' )
        mayac.popupMenu(parent=supportText, ctl=False, button=1) 
        
        mayac.menuItem(l='Go to community site', command = lambda *args: goToWebpage("community")) 
        mayac.text( label='', align='left' )
        happyAnimatingText = mayac.text( label='  Happy Animating! www.mixamo.com', align='center' )
        mayac.popupMenu(parent=happyAnimatingText, ctl=False, button=1) 
        mayac.menuItem(l='Go to Mixamo.com', command = lambda *args: goToWebpage("mixamo")) 
        mayac.text( label='', align='left' )
        
        
        mayac.setParent( '..' )
        
        self.tabs = mayac.tabLayout(innerMarginWidth=5, innerMarginHeight=5)
        self.layout = mayac.formLayout( self.form, edit=True, attachForm=((self.tabs, 'top', 90), (self.tabs, 'left', 0), (self.tabs, 'bottom', 0), (self.tabs, 'right', 0)) )
        
        #Rig Tab
        self.child1 = mayac.columnLayout(adjustableColumn = True)
        mayac.text( label='', align='left' )
        mayac.text( label='Control Sizing Helper', align='center')
        mayac.text( label='  If the character has unusual proportions or large appendages, the button below will create a cube that you may scale to', align='center' )
        mayac.text( label='compensate for the unusual proportions.', align='center' )
        self.fakeBB_button = mayac.button(label='Create override Bounding Box', w=100, c=self.createOverrideBB_function)
        mayac.text( label='', align='left' )
        
        mayac.separator( height=15, style='in' )
        mayac.text( label='Advanced Options', align='center' )
        mayac.text( label='WARNING!!!!: The following changes the rig.  Skeleton will no longer match original fbx.', align='center')
        mayac.text( label='For best results with animation, export from the Export tab once rigging is complete and', align='center')
        mayac.text( label='upload the new rig to mixamo.com to apply animations to.')
        self.hulaOptionCheckBox = mayac.checkBox(label = 'Add Pelvis ("hula") Control', align='left' )
        mayac.separator( height=15, style='in' )
        autoSkinnerText = mayac.text( label='  Import your downloaded MIXAMO character and then press the button below.', align='left' )
        mayac.popupMenu(parent=autoSkinnerText, ctl=False, button=1) 
        mayac.menuItem(l='Go to Mixamo Auto-Rigger webpage', command = lambda *args: goToWebpage("autoRigger"))
        self.setupControls_button = mayac.button(label='Rig Character', w=100, c=self.setupControls_function)
        mayac.text( label='', align='left' )
        mayac.setParent( '..' )
        
        
        #Animate Tab
        self.child2 = mayac.columnLayout(adjustableColumn = True)
        mayac.text( label='', align='left' )
        mayac.text( label="**Please note that the animation data functionality is only designed to work with animations retargeted to your character's skeleton**", align='left' )
        mayac.text( label='', align='left' )
        mayac.text( label='', align='left' )
        animationText = mayac.text( label='  Import your downloaded MIXAMO animation.', align='left' )
        mayac.popupMenu(parent=animationText, ctl=False, button=1) 
        mayac.menuItem(l='Go to Mixamo Motions webpage', command = lambda *args: goToWebpage("motions")) 
        self.browseMotions_button = mayac.button(label='Import Animation', w=100, c=self.browseMotions_function)
        mayac.text( label='', align='left' )
        mayac.text( label='  Select the "Hips" joint of the imported motion and then press the button below.', align='left' )
        mayac.button(label='Copy Animation to Rig (for imported animation)', w=100, c=self.copyAnimationToRig_function)
        mayac.text( label='', align='left' )
        mayac.button(label='Direct Connect Animation to Rig (for referenced animation)', w=100, c=self.connectAnimationToRig_function)
        mayac.text( label='', align='left' )
        mayac.text( label='', align='left' )
        mayac.text( label='Here you can bake the animation to the controls and/or revert to clean controls at any time.', align='center' )
        controlRigText = mayac.text( label="For more details see the documentation or www.mixamo.com/c/auto-control-rig-for-maya", align='center' )
        mayac.popupMenu(parent=controlRigText, ctl=False, button=1) 
        mayac.menuItem(l='Go to Auto-Control-Rig webpage', command = lambda *args: goToWebpage("autoControlRig")) 
        mayac.text( label='', align='left' )
        self.bakeAnimation_button = mayac.button(label='Bake Animation to Controls (imported anim only)', w=100, c=self.bakeAnimation_function)
        mayac.text( label='', align='left' )
        self.bakeAnimation_button = mayac.button(label='Clear Animation Controls (imported anim only)', w=100, c=self.clearAnimation_function)
        mayac.text( label='', align='left' )
        mayac.text( label='', align='left' )
        mayac.text( label='  Note: The original animation resides in the scene on its own layer until deleted.', align='left' )
        mayac.text( label='', align='left' )
        self.deleteOrigAnimation_button = mayac.button(label='Delete Original Animation (imported anim only)', w=100, c=self.deleteOrigAnimation_function)
        mayac.text( label='', align='left' )
        mayac.setParent( '..' )
        
        
        #Export Tab
        self.child3 = mayac.columnLayout(adjustableColumn = True)
        mayac.text( label='', align='left' )
        mayac.text( label='General Options', align='center')
        self.removeEndJointsCheckBox = mayac.checkBox(label = 'Remove End Joints', align='left')
        self.reduceNonEssentialJointsCheckBox = mayac.checkBox(label = 'Reduce Keyframes on Non-Essential Joints', align='left' )
        self.exportWithMeshOptionCheckBox = mayac.checkBox(label = 'Export Mesh with Skeleton', align='left' )
        
        mayac.separator( height=15, style='in' )
        mayac.text( label='Dynamics Options', align='center')
        self.dynamicsFadeFramesSlider = mayac.intSliderGrp( field=True, label='Dynamics Pose-Match Frame', minValue=0, maxValue=50, value=0, columnAttach3=("both","both","both"))
        mayac.separator( height=15, style='in' )
        self.exportBakedSkeleton_button = mayac.button(label='Export Baked Skeleton', w=100, c=self.exportBakedSkeleton_function)
        mayac.text( label='', align='left' )
        mayac.setParent( '..' )
        
        
        #Batch Tab
        self.child4 = mayac.columnLayout(adjustableColumn = True)
        mayac.text( label='', align='left' )
        self.batch_fileOptionRadio = mayac.radioButtonGrp(label = "Animated File:", labelArray3 = ["Open", "Import","Reference"], numberOfRadioButtons=3, sl = 1)
        self.batch_File1_browse = mayac.button(label = "Browse", w=15, c=self.batch_File1_browse_function)
        self.batch_File1_selectAll = mayac.button(label = "Select All", w=30, c=self.batch_File1_selectAll_function)
        self.batch_File1_ScrollField = mayac.textScrollList( numberOfRows=10, allowMultiSelection=True, height = 100)
        mayac.separator( height=15, style='in')
        self.batch_replaceRigReference_checkbox = mayac.checkBox(label="Replace Rig Reference", v = True)
        self.batch_replaceRigReference_textFieldButtonGrp = mayac.textFieldButtonGrp( label='New Rig Reference', text='', buttonLabel='Browse', buttonCommand = self.batch_replaceRigReferencePath_function)
        mayac.separator( height=15, style='in' )
        self.batch_playblast_checkbox = mayac.checkBox(label="Playblast", v = True)
        self.batch_playblastPath_textFieldButtonGrp = mayac.textFieldButtonGrp( label='Playblast Save Path', text='', buttonLabel='Browse', buttonCommand = self.batch_playblastPath_function)
        mayac.separator( height=15, style='in' )
        self.batch_saveFileOptionRadio = mayac.radioButtonGrp(label = "Finished File:",
                                            labelArray3 = ["Export", "Save", "Don't Save or Export"], 
                                            numberOfRadioButtons=3, 
                                            sl = 1, 
                                            columnAlign3 = ['left','center','right'],
                                            columnWidth3 = [10,500,20])
        self.batch_savePath_textFieldButtonGrp = mayac.textFieldButtonGrp( label='File Save Path', text='', buttonLabel='Browse', buttonCommand = self.batch_savePath_function)
        mayac.text( label='', align='left' )
        self.batchButton = mayac.button(label = "Batch", w=15, c=self.batch_function)
        mayac.text( label='', align='left' )
        mayac.setParent( '..' )
        

        #Utilities Tab
        self.child5 = mayac.columnLayout(adjustableColumn = True)
        mayac.text( label='', align='left' )
        mayac.text( label="If you've added a skinned mesh to your rig, ", align='center')
        mayac.text( label="the button below will let the system know about it for exports.", align='center' )
        self.batch_startFileOption = mayac.button(label='Remake Mesh Infonode', w=100, c=self.remakeMeshInfoNode_function)
        mayac.text( label='', align='left' )
        mayac.text( label="If you've added joints to your rig, ", align='center')
        mayac.text( label="select them and click the button below.", align='center' )
        self.makeExtraJointsInfoNode_button = mayac.button(label='Make Extra Joints Infonode from selection', w=100, c=self.makeExtraJointsInfoNode_function)
        mayac.text( label='', align='left' )
        mayac.text( label="If you've added joints that you wish to have dynamic, ", align='center')
        mayac.text( label="select them and click the button below for automatic followthrough.", align='center' )
        mayac.text( label="(powered by ZV Dynamics by Paolo Dominici)", align='center')
        self.makeDynamicChainRigFromSelection_button = mayac.button(label='Make Dynamic Chain Rig from selection', w=100, c=self.makeDynamicChainRigFromSelection_function)
        
        
        mayac.setParent( '..' )
        
        
        mayac.tabLayout( self.tabs, edit=True, tabLabel=((self.child1, 'Rig'), (self.child2, 'Animate'), (self.child3, 'Export'), (self.child4, 'Batching'), (self.child5, 'Utilities')) )
        mayac.window(self.window, e=1, w=650, h=575, sizeable = 0) #580,560
        mayac.showWindow(self.window)
            

    def showAboutWindow(self, arg = None):
        if (mayac.window("DJB_MACR_About", q=1, exists=1)): mayac.deleteUI("DJB_MACR_About")
        about_window = mayac.window("DJB_MACR_About", title="About %s" % (self.title))
        about_form = mayac.formLayout()
        about_tabs = mayac.tabLayout(innerMarginWidth=5, innerMarginHeight=5)
        about_layout = mayac.formLayout( about_form, edit=True, attachForm=((about_tabs, 'top', 0), (about_tabs, 'left', 0), (about_tabs, 'bottom', 0), (about_tabs, 'right', 0)) )
        #About Tab
        child1 = mayac.columnLayout(adjustableColumn = True)
        mayac.scrollField( editable=False, wordWrap=False, text= DJB_ABOUT_TEXT, h=450, w=750)
        mayac.setParent( '..' )
        #Changelog Tab
        child2 = mayac.columnLayout(adjustableColumn = True)
        mayac.scrollField( editable=False, wordWrap=False, text= DJB_CHANGELOG_TEXT, h=450, w=750)
        mayac.setParent( '..' )
        mayac.tabLayout( about_tabs, edit=True, tabLabel=((child1, 'General'), (child2, 'Changelog')) )
         
        mayac.window(about_window, e=1, w=650, h=450, sizeable = 0) #580,560
        mayac.showWindow(about_window)


    def createOverrideBB_function(self, arg = None):
        global DJB_CharacterInstance
        DJB_CharacterInstance = None
        DJB_populatePythonSpaceWithCharacter()
        if not DJB_CharacterInstance:
            global DJB_Character_ProportionOverrideCube
            if mayac.objExists(DJB_Character_ProportionOverrideCube):
                mayac.delete(DJB_Character_ProportionOverrideCube)
                DJB_Character_ProportionOverrideCube = ""
            DJB_Character_ProportionOverrideCube = mayac.polyCube(n = "Bounding_Box_Override_Cube", ch = False)[0]
            
            #get default proportions
            mesh = []
            temp = mayac.ls(geometry = True)
            shapes = []
            for geo in temp:
                if "ShapeOrig" not in geo:
                    shapes.append(geo)
                    transform = mayac.listRelatives(geo, parent = True)[0]
            for geo in shapes:
                parent = mayac.listRelatives(geo, parent = True, path=True)[0]
                mesh.append(mayac.listRelatives(parent, children = True, type = "shape", path=True)[0])
            #place and lock up cube
            BoundingBox = mayac.exactWorldBoundingBox(mesh)
            mayac.move(BoundingBox[0], BoundingBox[1], BoundingBox[5], "%s.vtx[0]" % (DJB_Character_ProportionOverrideCube), absolute = True)
            mayac.move(BoundingBox[3], BoundingBox[1], BoundingBox[5], "%s.vtx[1]" % (DJB_Character_ProportionOverrideCube), absolute = True)
            mayac.move(BoundingBox[0], BoundingBox[4], BoundingBox[5], "%s.vtx[2]" % (DJB_Character_ProportionOverrideCube), absolute = True)
            mayac.move(BoundingBox[3], BoundingBox[4], BoundingBox[5], "%s.vtx[3]" % (DJB_Character_ProportionOverrideCube), absolute = True)
            mayac.move(BoundingBox[0], BoundingBox[4], BoundingBox[2], "%s.vtx[4]" % (DJB_Character_ProportionOverrideCube), absolute = True)
            mayac.move(BoundingBox[3], BoundingBox[4], BoundingBox[2], "%s.vtx[5]" % (DJB_Character_ProportionOverrideCube), absolute = True)
            mayac.move(BoundingBox[0], BoundingBox[1], BoundingBox[2], "%s.vtx[6]" % (DJB_Character_ProportionOverrideCube), absolute = True)
            mayac.move(BoundingBox[3], BoundingBox[1], BoundingBox[2], "%s.vtx[7]" % (DJB_Character_ProportionOverrideCube), absolute = True)
            pivotPointX = ((BoundingBox[3] - BoundingBox[0]) / 2) + BoundingBox[0]
            pivotPointY = BoundingBox[1]
            pivotPointZ = ((BoundingBox[5] - BoundingBox[2]) / 2) + BoundingBox[2]
            mayac.move(pivotPointX, pivotPointY, pivotPointZ, "%s.scalePivot" % (DJB_Character_ProportionOverrideCube), "%s.rotatePivot" % (DJB_Character_ProportionOverrideCube), absolute = True)
            mayac.setAttr("%s.tx" % (DJB_Character_ProportionOverrideCube),lock = True)
            mayac.setAttr("%s.ty" % (DJB_Character_ProportionOverrideCube),lock = True)
            mayac.setAttr("%s.tz" % (DJB_Character_ProportionOverrideCube),lock = True)
            mayac.setAttr("%s.rx" % (DJB_Character_ProportionOverrideCube),lock = True)
            mayac.setAttr("%s.ry" % (DJB_Character_ProportionOverrideCube),lock = True)
            mayac.setAttr("%s.rz" % (DJB_Character_ProportionOverrideCube),lock = True)
            
        else:
            OpenMaya.MGlobal.displayError("You must create and scale the override cube before rigging the character.")
        mayac.select(clear = True)
        
            
    def setupControls_function(self, arg = None):
        global DJB_CharacterInstance
        DJB_CharacterInstance = None
        DJB_populatePythonSpaceWithCharacter()
        if not DJB_CharacterInstance:
            joints = mayac.ls(type = "joint")
            if not joints:
                OpenMaya.MGlobal.displayError("There must be a Mixamo Autorigged character in the scene.")
            else:
                hulaValue = mayac.checkBox(self.hulaOptionCheckBox, query = True, value = True)
                DJB_CharacterInstance.append(DJB_Character(hulaOption_ = hulaValue))
                DJB_CharacterInstance[len(DJB_CharacterInstance)-1].fixArmsAndLegs()
                
                DJB_CharacterInstance[len(DJB_CharacterInstance)-1].makeAnimDataJoints()
                DJB_CharacterInstance[len(DJB_CharacterInstance)-1].makeControls()
                DJB_CharacterInstance[len(DJB_CharacterInstance)-1].hookUpControls()
                DJB_CharacterInstance[len(DJB_CharacterInstance)-1].writeInfoNode()
        else:
            OpenMaya.MGlobal.displayError("There is already a rig in the scene")
        mayac.select(clear = True)
        
        
    def browseMotions_function(self, arg = None):
        mayac.Import()
    
    def connectAnimationToRig_function(self, arg = None):
        global DJB_CharacterInstance
        selection = mayac.ls(selection = True)
        DJB_CharacterInstance = None
        DJB_populatePythonSpaceWithCharacter()
        if not DJB_CharacterInstance:
            OpenMaya.MGlobal.displayError("You must rig a character first")
        elif len(selection) == 0 or mayac.nodeType(selection[0]) != "joint":
            OpenMaya.MGlobal.displayError("You must select the 'Hips' Joint of the imported animation")
        elif len(DJB_CharacterInstance) == 1:
            if DJB_CharacterInstance[0].Hips.Bind_Joint:
                isCorrectRig = DJB_CharacterInstance[0].checkSkeletonProportions(selection[0])
                if isCorrectRig:
                    DJB_CharacterInstance[0].connectMotionToAnimDataJoints(selection[0])
                else:
                    OpenMaya.MGlobal.displayError("Imported Skeleton does not match character!")
        else: #more than one character, spawn a choice window
            mayac.select(selection, r=True)
            ACR_connectAnimationToRigWindow()
        
        
                
    def copyAnimationToRig_function(self, arg = None):
        global DJB_CharacterInstance
        selection = mayac.ls(selection = True)
        DJB_CharacterInstance = None
        DJB_populatePythonSpaceWithCharacter()
        if not DJB_CharacterInstance:
            OpenMaya.MGlobal.displayError("You must rig a character first")
        elif len(selection) == 0 or mayac.nodeType(selection[0]) != "joint":
            OpenMaya.MGlobal.displayError("You must select the 'Hips' Joint of the imported animation")
        elif len(DJB_CharacterInstance) == 1:
            if DJB_CharacterInstance[0].Hips.Bind_Joint:
                isCorrectRig = DJB_CharacterInstance[0].checkSkeletonProportions(selection[0])
                if isCorrectRig:
                    DJB_CharacterInstance[0].transferMotionToAnimDataJoints(selection[0], newStartTime = 0, mixMethod = "insert")
                else:
                    OpenMaya.MGlobal.displayError("Imported Skeleton does not match character!")
        else: #more than one character, spawn a choice window
            mayac.select(selection, r=True)
            ACR_copyAnimationToRigWindow()
            
    def deleteOrigAnimation_function(self, arg = None):
        global DJB_CharacterInstance
        DJB_CharacterInstance = None
        DJB_populatePythonSpaceWithCharacter()
        if not DJB_CharacterInstance:
            OpenMaya.MGlobal.displayError("No Character Found!")
        else:
            if DJB_CharacterInstance[0].origAnim:
                DJB_CharacterInstance[0].deleteOriginalAnimation()
            else:
                OpenMaya.MGlobal.displayError("No Original Animation Found!")
            
    def bakeAnimation_function(self, arg = None):
        global DJB_CharacterInstance
        DJB_CharacterInstance = None
        DJB_populatePythonSpaceWithCharacter()
        if DJB_CharacterInstance:
            DJB_CharacterInstance[0].bakeAnimationToControls()
        else:
            OpenMaya.MGlobal.displayError("No Character Found!")
        
    def clearAnimation_function(self, arg = None):
        global DJB_CharacterInstance
        DJB_CharacterInstance = None
        DJB_populatePythonSpaceWithCharacter()
        if DJB_CharacterInstance:
            DJB_CharacterInstance[0].clearAnimationControls()
        else:
            OpenMaya.MGlobal.displayError("No Character Found!")
                     
    def exportBakedSkeleton_function(self, arg = None):
        global DJB_CharacterInstance
        DJB_CharacterInstance = None
        DJB_populatePythonSpaceWithCharacter()
        if DJB_CharacterInstance:
            keepMesh = mayac.checkBox(self.exportWithMeshOptionCheckBox, query = True, value = True)
            reduce = mayac.checkBox(self.reduceNonEssentialJointsCheckBox, query = True, value = True)
            removeEndJoints = mayac.checkBox(self.removeEndJointsCheckBox, query = True, value = True)
            dynamicsFadeFrames = mayac.intSliderGrp(self.dynamicsFadeFramesSlider, query = True, value = True)
            DJB_CharacterInstance[0].createExportSkeleton(keepMesh_ = keepMesh, dynamicsToFK = dynamicsFadeFrames, reduceNonEssential = reduce, removeEndJoints = removeEndJoints)
            if arg:
                DJB_CharacterInstance[0].exportSkeleton(arg)
            else:
                DJB_CharacterInstance[0].exportSkeleton()
            version = mel.eval("float $ver = `getApplicationVersionAsFloat`;")
            if version != 2010.0:
                DJB_CharacterInstance[0].deleteExportSkeleton()
            if version == 2010.0:
                OpenMaya.MGlobal.displayInfo("You may delete the newly created geometry and joints after exporting is complete")
        else:
            OpenMaya.MGlobal.displayError("No Character Found!")
     
     
    def remakeMeshInfoNode_function(self, arg = None):
        global DJB_CharacterInstance
        DJB_CharacterInstance = None
        DJB_populatePythonSpaceWithCharacter()
        if DJB_CharacterInstance:
            DJB_CharacterInstance[0].remakeMeshInfoNode()
        else:
            OpenMaya.MGlobal.displayError("No Character Found!")   
    
    
    def makeExtraJointsInfoNode_function(self, arg = None):
        global DJB_CharacterInstance
        DJB_CharacterInstance = None
        sel = mayac.ls(sl=True)
        DJB_populatePythonSpaceWithCharacter()
        if DJB_CharacterInstance:
            if sel:
                DJB_CharacterInstance[0].makeExtraJointsInfoNode(sel)
            else:
                OpenMaya.MGlobal.displayError("Extra Joints Must Be Selected!")  
        else:
            OpenMaya.MGlobal.displayError("No Character Found!")  
            
    def makeDynamicChainRigFromSelection_function(self, arg = None):
        global DJB_CharacterInstance
        sel = mayac.ls(sl=True)
        DJB_CharacterInstance = None
        DJB_populatePythonSpaceWithCharacter()
        if DJB_CharacterInstance:
            if sel:
                for cur in sel:
                    mayac.select(cur, replace = True)
                    mayac.select(hierarchy = True)
                    chain = mayac.ls(sl=True)
                    DJB_CharacterInstance[0].makeDynamicChainRig(chain, dynamic_ = "ZV", control_ = "FK") #need to add checks for eligible joint chain
            else:
                OpenMaya.MGlobal.displayError("Eligible Joints Must Be Selected!")
        else:
            OpenMaya.MGlobal.displayError("No Character Found!")
            
    def batch_function(self, arg = None):
        #get all options
        keepMesh = mayac.checkBox(self.exportWithMeshOptionCheckBox, query = True, value = True)
        
        filesShort = mayac.textScrollList(self.batch_File1_ScrollField, query = True, selectItem = True)
        #iterate through top level files
        for file in filesShort:
            
            fileType = file[len(file)-3:]
            fileName = file[0:len(file)-3]
            file = self.file1Dir + "/" + file
            #open top level
            openOption = mayac.radioButtonGrp(self.batch_fileOptionRadio, query = True, sl = True)
            if openOption == 1:#open
                mayac.file( file, o=True, force = True )
            elif openOption == 2:#import
                mayac.file( file, i=True, force = True )
            elif openOption == 3:#reference
                mayac.file( file, r=True, force = True )
            #if rig replace
            rigReplace = mayac.checkBox(self.batch_replaceRigReference_checkbox, query = True, value = True)
            references = None
            if rigReplace:
                references=mayac.file(q=True, reference = True)[0]
            if references:
                ref = mayac.referenceQuery(references, rfn = True)
                newRef = mayac.textFieldButtonGrp(self.batch_replaceRigReference_textFieldButtonGrp, query = True, text = True)
                if ".ma" in newRef:
                    mayac.file(newRef, loadReference = ref, type = "mayaAscii", options = ("v=0"))
                else:
                    mayac.file(newRef, loadReference = ref, type = "mayaBinary", options = ("v=0"))
            
            #save or bake and export
            global DJB_CharacterInstance
            DJB_CharacterInstance = None
            DJB_populatePythonSpaceWithCharacter()
            saveOption = mayac.radioButtonGrp(self.batch_saveFileOptionRadio, query = True, sl = True)
            saveFolder = mayac.textFieldButtonGrp(self.batch_savePath_textFieldButtonGrp, query = True, text = True)
            saveFile = saveFolder + "/" + fileName
            if saveOption == 2:#save
                #Pre-setup dynamics
                dynamicsFadeFrames = mayac.intSliderGrp(self.dynamicsFadeFramesSlider, query = True, value = True)
                if dynamicsFadeFrames:
                    DJB_CharacterInstance.dynamicsStartEndPoseKeys(dynamicsToFK = dynamicsFadeFrames)
                if ".ma" in fileType:
                    mayac.file( rename= saveFile + ".ma" )
                    mayac.file( save=True, type='mayaAscii', force=True )
                else:
                    mayac.file( rename= saveFile + ".mb" )
                    mayac.file( save=True, type='mayaBinary', force=True )
                #mayac.file(saveFile, save = True, type = "mayaAscii", force = True)
            elif saveOption == 1:#bake and export
                for i in range(0,10):
                    mayac.currentTime( i, edit=True )
                mayac.currentTime( 0, edit=True )
                self.exportBakedSkeleton_function(arg = saveFile)
            #if playblast
            playblast = mayac.checkBox(self.batch_playblast_checkbox, query = True, value = True)
            if playblast:
                controlLayer = DJB_addNameSpace(DJB_CharacterInstance[0].characterNameSpace, "ControlLayer")
                mayac.setAttr("%s.visibility" %(controlLayer), 1)
                for i in range(0,10):
                    mayac.currentTime( i, edit=True )
                mayac.currentTime( 0, edit=True )
                blastPath = mayac.textFieldButtonGrp(self.batch_playblastPath_textFieldButtonGrp, query = True, text = True)
                blastFile = blastPath + "/" + fileName
                mayac.setAttr("persp.tx",-0.358)
                mayac.setAttr("persp.ty",86.261)
                mayac.setAttr("persp.tz",503.388)
                mayac.setAttr("persp.rx",-.338)
                mayac.setAttr("persp.ry",-2.4)
                mayac.setAttr("persp.rz",0)
                mayac.setAttr("perspShape.farClipPlane", 100000)
                mayac.setAttr("perspShape.nearClipPlane", 100)
                #base_OpenGL_Renderer
                #hwRender_OpenGL_Renderer
                mayac.modelEditor( "modelPanel4", edit=True, camera="persp", rnm = "base_OpenGL_Renderer", nurbsCurves=False, joints=False, cameras = False, grid = False, ikh = False, deformers = False, dynamics = False, nParticles = False, follicles = False, locators = False, activeView=True )
                mel.eval('playblast  -format avi -filename "%s" -sequenceTime 0 -clearCache 1 -viewer 1 -showOrnaments 0 -offScreen  -fp 4 -percent 100 -compression "XVID" -quality 70 -widthHeight 1280 720;'%(blastFile))
                #mayac.playblast(f=blastFile, format = "avi", showOrnaments = 0, percent = 100, compression = "XVID", quality = 70, widthHeight = [1280,720])


        
    def batch_File1_browse_function(self, arg = None):
        self.file1Dir = DJB_BrowserWindow(filter_ = "Maya", caption_ = "Browse for character files directory", fileMode_ = "directory")
        filesRaw = os.listdir(self.file1Dir)
        filesRaw.sort()
        mayac.textScrollList(self.batch_File1_ScrollField, edit = True, removeAll = True)
        for file in filesRaw:
            if ".ma" in file or ".mb" in file:
                mayac.textScrollList(self.batch_File1_ScrollField, edit = True, append = file)
    def batch_File1_selectAll_function(self, arg = None):
        allItems = mayac.textScrollList(self.batch_File1_ScrollField, query = True, allItems = True)
        if not allItems:
            OpenMaya.MGlobal.displayError("Nothing to select")
        else:
            for item in allItems:
                mayac.textScrollList(self.batch_File1_ScrollField, edit = True, selectItem = item)
    def batch_replaceRigReferencePath_function(self, arg = None):
        replaceRigReferencePath = DJB_BrowserWindow(filter_ = "Maya", caption_ = "Browse for rig reference replacement", fileMode_ = "Maya")
        if replaceRigReferencePath:
            mayac.textFieldButtonGrp(self.batch_replaceRigReference_textFieldButtonGrp, edit = True, text = replaceRigReferencePath)
        else:
            mayac.textFieldButtonGrp(self.batch_replaceRigReference_textFieldButtonGrp, edit = True, text = "")
    def batch_playblastPath_function(self, arg = None):
        playblastPath = DJB_BrowserWindow(filter_ = None, caption_ = "Browse for playblast folder", fileMode_ = "directory")
        if playblastPath:
            mayac.textFieldButtonGrp(self.batch_playblastPath_textFieldButtonGrp, edit = True, text = playblastPath)
        else:
            mayac.textFieldButtonGrp(self.batch_playblastPath_textFieldButtonGrp, edit = True, text = "")
    def batch_savePath_function(self, arg = None):
        savePath = DJB_BrowserWindow(filter_ = None, caption_ = "Browse for save folder", fileMode_ = "directory")
        if savePath:
            mayac.textFieldButtonGrp(self.batch_savePath_textFieldButtonGrp, edit = True, text = savePath)
        else:
            mayac.textFieldButtonGrp(self.batch_savePath_textFieldButtonGrp, edit = True, text = "")
          

class ACR_connectAnimationToRigWindow:
    def __init__(self):
        self.file1Dir = None
        self.name = "Connect Animation to Rig"
        self.title = "Connect Animation to Rig"

        # Begin creating the UI
        if (mayac.window(self.name, q=1, exists=1)): 
            mayac.deleteUI(self.name)
        self.window = mayac.window(self.name, title=self.title, menuBar=True)
        #forms
        self.form = mayac.formLayout(w=650)
        mayac.columnLayout(adjustableColumn = True, w=650)
        mayac.text( label='', align='left' )
        self.characters_ScrollList = mayac.textScrollList( numberOfRows=5, allowMultiSelection=False)
        mayac.separator( height=40, style='in' )
        mayac.text( label='', align='left' )
        self.batchButton = mayac.button(label = "Connect Animation to selected Character", w=15, c=self.connectFunction)
        mayac.text( label='', align='left' )
        
        self.populateScrollField()
        mayac.window(self.window, e=1, w=650, h=515, sizeable = 1) #580,560
        mayac.showWindow(self.window)
        
    def populateScrollField(self, arg = None):
        global DJB_CharacterInstance
        for char in DJB_CharacterInstance:
            mayac.textScrollList(self.characters_ScrollList, edit = True, append = char.name)
        mayac.textScrollList(self.characters_ScrollList, edit=True, selectIndexedItem = 1)
        
    def connectFunction(self, arg = None):
        global DJB_CharacterInstance
        selection = mayac.ls(sl=True)
        selectedIndex = mayac.textScrollList(self.characters_ScrollList, query=True, selectIndexedItem = True)
        #print selectedIndex
        
        DJB_CharacterInstance[selectedIndex[0]-1].connectMotionToAnimDataJoints(selection[0])
        
class ACR_copyAnimationToRigWindow():
    def __init__(self):
        self.file1Dir = None
        self.name = "Copy Animation to Rig"
        self.title = "Copy Animation to Rig"

        # Begin creating the UI
        if (mayac.window(self.name, q=1, exists=1)): 
            mayac.deleteUI(self.name)
        self.window = mayac.window(self.name, title=self.title, menuBar=True)
        #forms
        self.form = mayac.formLayout(w=650)
        mayac.columnLayout(adjustableColumn = True, w=650)
        mayac.text( label='', align='left' )
        self.characters_ScrollList = mayac.textScrollList( numberOfRows=5, allowMultiSelection=False)
        mayac.separator( height=40, style='in' )
        mayac.text( label='', align='left' )
        self.batchButton = mayac.button(label = "Copy Animation to selected Character", w=15, c=self.copyFunction)
        mayac.text( label='', align='left' )
        
        self.populateScrollField()
        mayac.window(self.window, e=1, w=650, h=515, sizeable = 1) #580,560
        mayac.showWindow(self.window)
    def populateScrollField(self, arg = None):
        global DJB_CharacterInstance
        for char in DJB_CharacterInstance:
            mayac.textScrollList(self.characters_ScrollList, edit = True, append = char.name)
        mayac.textScrollList(self.characters_ScrollList, edit=True, selectIndexedItem = 1)
        
    def copyFunction(self, arg = None):
        global DJB_CharacterInstance
        selection = mayac.ls(sl=True)
        selectedIndex = mayac.textScrollList(self.characters_ScrollList, query=True, selectIndexedItem = True)
        DJB_CharacterInstance[selectedIndex[0]-1].transferMotionToAnimDataJoints(selection[0], newStartTime = 0, mixMethod = "insert")
        
            