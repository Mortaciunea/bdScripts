# Author: Bogdan Diaconu
# Description: This script can be used to mirror the IK Feet controller for the KID rig
# Install: Copy the sript in your scripts folder
# Create two shelf buttons:
# first:
# import bdMirrorFeet
# bdMirrorFeet.copyAnim()
# second:
# import bdMirrorFeet
# bdMirrorFeet.mirrorAnim()
# Usage: Select both feet controllers, press 1st button. Move to the desired frame, press the second button. 
#
import pymel.core as pm

def copyAnim():
	selection = pm.ls(sl=True)
	if len(selection) != 2:
		pm.warning('Need exactly two objects to copy')
		return
	try:
		namespace = selection[0].namespace()
	except:
		namespace = ''
		
	print namespace
	holders = pm.ls('*_HOLDE*')
	if namespace != '':
		holders = pm.ls('*:*_HOLDE*')
	
	if holders:
		pm.delete(holders)

	source = selection[0]
	target = selection[1]
	
	pm.setKeyframe(source)
	pm.setKeyframe(target)
	
	sourceName = source.name()
	targetName = target.name()
	if namespace != '':
		sourceName =  source.stripNamespace()
		targetName =  target.stripNamespace()
		
	pm.select(cl=True)

	sourceAttr = pm.listAttr(source,k=True)
	sourceHolder = pm.group(n=namespace + sourceName + '_SOURCE_HOLDER')
	for attr in sourceAttr:
		attrType = source.attr(attr).type()
		pm.addAttr(sourceHolder,ln='__' + attr,nn=attr,at = attrType)
		sourceHolder.attr('__' + attr).set(source.attr(attr).get())
	
	pm.select(cl=True)
	targetAttr = pm.listAttr(target,k=True)
	targetHolder = pm.group(n=namespace + targetName + '_TARGET_HOLDER')
	for attr in targetAttr:
		attrType = target.attr(attr).type()
		pm.addAttr(targetHolder,ln='__' + attr,nn=attr,at = attrType)
		targetHolder.attr('__' + attr).set(target.attr(attr).get())
	
	pm.select([target,source])

def mirrorAnim():
	selection = pm.ls(sl=True)
	if len(selection) != 2:
		pm.warning('Need exactly two objects to mirror')
		return

	try:
		namespace = selection[0].namespace()
	except:
		namespace = ''
		

	try:
		sourceHolder = pm.ls(namespace + '*_SOURCE_HOLDER')[0]
		targetHolder = pm.ls(namespace + '*_TARGET_HOLDER')[0]
	except:
		pm.warning('No holders found to mirror animations')
		return
	source = pm.ls(sourceHolder.name().replace('_SOURCE_HOLDER',''),type='transform')[0]
	target= pm.ls(targetHolder.name().replace('_TARGET_HOLDER',''),type='transform')[0]
	
	sourceHolderAttr = pm.listAttr(sourceHolder,ud=True)
	targetHolderAttr = pm.listAttr(targetHolder,ud=True)
	
	for attr in sourceHolderAttr:
		print attr
		reverse = 1
		if (attr.find('translateX') > 0) or (attr.find('rotateY') > 0) or (attr.find('KneeTwist') > 0) or (attr.find('rotateZ') > 0):
			reverse = -1
		target.attr(attr.replace('__','')).set(sourceHolder.attr(attr).get() * reverse)
		
	for attr in targetHolderAttr:
		reverse = 1
		if (attr.find('translateX') > 0) or (attr.find('rotateY') > 0) or (attr.find('KneeTwist') > 0) or (attr.find('rotateZ') > 0):
			reverse = -1		
		source.attr(attr.replace('__','')).set(targetHolder.attr(attr).get() * reverse)
		
	pm.delete([sourceHolder,targetHolder])

	pm.setKeyframe(source)
	pm.setKeyframe(target)

