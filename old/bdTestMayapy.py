import sys

import maya.standalone as std
std.initialize(name='pymel')

import pymel.core as pm
import zoobeMixamo as zm
reload(zm)

filename = sys.argv[1]

pm.loadPlugin('mayaHIK.mll')
pm.loadPlugin('zoobe_maya_exporter.mll')
pm.loadPlugin('fbxmaya.mll')
pm.loadPlugin('cgfxShader.mll')

def procesFbx(filename):
  fbxPath = filename #'p:/mixamo_character/working_project/data/_incoming_data/mixamo/eve_bavaria_geo.fbx'
  eve = zm.MixamoCharacter(name = 'eve_bavaria',path = fbxPath)
  eve.processCharacter()
  eve.exportOgreMesh()
  eve.importAnimation()
  eve.exportAnimation()

#procesFbx(filename)

print filename