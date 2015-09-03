import pymel.core as pm
import os


def bdCreateTSM2ShadowRig():
    selection = pm.ls(sl=1)
    TSM2 = []
    for obj in selection:
        if pm.attributeQuery('TSM2Control',node= obj,exists=1):
            TSM2.append(obj)
    
    upperBody = pm.ls('*:Upper_Body',type='transform')[0]
    TSM2.append(upperBody)
    
    bdCreateLocators(TSM2)
    
def bdCreateLocators(controllers):
    conLocators= []
    for con in controllers:
        loc = pm.spaceLocator(n=con.stripNamespace() + '_loc')
        
        pm.parentConstraint(con,loc)
        conLocators.append(loc)
    
    pm.group(conLocators, n='shadowRig')


def bdHookTSMG2toShadow():
    shadowLoc = pm.ls('shadow:*',type='transform') 
    mapping = bdGetMapping()
    for i in range(0,len(mapping),2):
        print mapping[i], mapping[i+1]
    print len(set(mapping))
    for loc in shadowLoc:
        tsm2Name = loc.stripNamespace().replace('_loc','')
        if tsm2Name in set(mapping):
            index = mapping.index(tsm2Name)
            tsmgName = mapping[index+1]
            con = pm.ls('*:' + tsmgName,type='transform')
            try:
                pm.pointConstraint(loc,con,mo=0)
            except:
                print 'No translations, skiping '
            try:
                pm.orientConstraint(loc,con,mo=0)
            except:
                print 'No rotations, skiping '

    
    
def bdGetMapping():
    animScene = pm.sceneName()
    fileName = animScene.split('/')[-1]
    shadowAnimFile = animScene.replace(fileName,'') + 'shadowAnim/tsm2_to_rsmg.map'
    if os.path.isfile(shadowAnimFile):
        f = open(shadowAnimFile,'r')
        mapping = f.read().split(' ')
        f.close()
        return mapping
    
def bdBakeAndClean():
    
    shadowRig = pm.ls('shadowRig',type='transform') [0]
    shadowLocs = shadowRig.getChildren()
    
    pm.select(shadowLocs )
    pm.bakeResults()
    '''
    animCurves = con.listConnections(type='animCurve')
    keyFrames = []
    for ac in animCurves:
        keytimes = pm.keyframe(con,q=1,t=(0,1000))
        keyFrames.append(keytimes)
    
    keytimes = set(keyFrames[0])
    for i in range(1,len(keyFrames)):
        keytimes = keytimes | set(keyFrames[i])
    
    print keytimes
    '''