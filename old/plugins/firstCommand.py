#test plugin 1

import sys

import maya.OpenMayaMPx as omMpx
import maya.OpenMaya as om


cmdName = 'bdCmd1'

#data
class FirstCommand(omMpx.MPxCommand):
    def __init__(self):
        omMpx.MPxCommand.__init__(self)

    def doIt(self, args):
        om.MGlobal.displayInfo('first plugin')


#creators
def cmdCreator():
    return omMpx.asMPxPtr(FirstCommand())

def initializePlugin(mobject):
    mplugin = omMpx.MFnPlugin(mobject,'bd','1.0','Any')
    try:
        mplugin.registerCommand(cmdName, cmdCreator)
    except:
        sys.stderr.write("Failed to register command : %s \n" % cmdName)
        raise

def uninitializePlugin(mobject):
    mplugin = omMpx.MFnPlugin(mobject)
    try:
        mplugin.deregisterCommand(cmdName)
    except:
        sys.stderr.write("Failed to unregister command: %s\n" % cmdName)
        raise