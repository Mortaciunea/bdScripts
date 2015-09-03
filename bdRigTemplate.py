import bdRigUtils
import maya.cmds as cmds
reload(bdRigUtils)


import math
import json
import collections
import pymel.core as pm
import pymel.core.datatypes as dt


class bdRigTemplate():
	def __init__(self, *args, **kargs):
		self.templatePath = 'd:\\bogdan\\_EyeRD\\templates\\'
		self.templateType = kargs.setdefault('type')
		self.templateFile = kargs.setdefault('file')
		self.templateJson = ''
		self.templateSide = kargs.setdefault('side')
		
		self.templateNamesFile = ''


	def bdImportTemplate(self):
		'''
		with open(self.templatePath + self.templateFile , 'r') as f:
			self.eyeJson = json.load(f)
		self.bdBuildGuidesFromTemplate()
		'''
		selection = pm.ls(sl=True)
		if self.templateSide == 'both':
			pm.importFile(self.templatePath + self.templateFile,ns =  'left' )
			pm.importFile(self.templatePath + self.templateFile,ns =  'right' )
			self.bdInitialPlacement(selection)
			self.bdMirrorRight()
		else:
			pm.importFile(self.templatePath + self.templateFile,ns =  self.templateSide )
			self.bdInitialPlacement(selection)

	def bdMirrorRight(self):

		print 'Mirroring left to right'
		leftGroup = pm.ls('left:'+ self.templateType + '*grp')[0]
		rightGroup = pm.ls('right:'+ self.templateType + '*grp')[0]
		leftGroupPos = leftGroup.getRotatePivot(space='world')
		leftGroupPos[0] = -1.0 * leftGroupPos[0]
		rightGroup.setTranslation(leftGroupPos,space='world')

		leftGrpChildren = leftGroup.listRelatives(f=True, ad=True,type='transform')
		rightGrpChildren = rightGroup.listRelatives(f=True, ad=True,type='transform')

		i=0
		for target in leftGrpChildren:
			targetPos = target.getRotatePivot(space='object')
			targetPos = [-2.0 * targetPos[0],0,0]
			rightGrpChildren[i].translateBy(targetPos,space='object')
			pm.makeIdentity(rightGrpChildren[i], apply=True, translate=True, rotate=True, scale=True )
			i+=1
		i=0
		for target in leftGrpChildren:
			mdNode = pm.createNode('multiplyDivide',name = target + '_X_MD')
			mdNode.input2X.set(-1)
			target.translateX.connect(mdNode.input1X)
			mdNode.outputX.connect(rightGrpChildren[i].translateX)
			target.translateY.connect(rightGrpChildren[i].translateY)
			target.translateZ.connect(rightGrpChildren[i].translateZ)
			target.scaleX.connect(rightGrpChildren[i].scaleX)
			target.scaleY.connect(rightGrpChildren[i].scaleY)
			target.scaleZ.connect(rightGrpChildren[i].scaleZ)
			i+=1
		
		
	def bdInitialPlacement(self,startPoint):
		if startPoint:
			pos = startPoint[0].getRotatePivot(space='world')
			if self.templateSide == "both":
				leftEyeCenterGuide = pm.ls('left:*grp')[0]
				leftEyeCenterGuide.setTranslation(pos)
			else:
				eyeCenterGuide = pm.ls(self.templateSide + ':*grp')[0]
				eyeCenterGuide.setTranslation(pos)
				
	'''
	def bdBuildGuidesFromTemplate(self):
		for token in self.eyeJson['Eye_Template']:
			tokenDict = token[1]
			markSphere = pm.sphere(name=tokenDict['name'],radius=0.3)
			markSphere[0].setTranslation(tokenDict['position'],space='world')
			parent = tokenDict['parent']
			#pm.addAttr(markSphere[0],ln='chain',dt='string')
			#markSphere[0].attr('chain').set(tokenDict['chain'])
	@staticmethod
	def bdExportTemplate():
		eyeMarkersDict = {}
		eyeMarkers = pm.ls('eye*', type='transform')
		i=0
		for mark in eyeMarkers:
			markerDict = {}
			markerDict['name'] = mark.name()
			markPos = mark.getRotatePivot(space='world')
			markerDict['position'] = [markPos.x,markPos.y,markPos.z]
			parent = mark.getParent()
			if parent:
				markerDict['parent'] =  parent.name()
			else:
				markerDict['parent'] =  'world'
			eyeMarkersDict['Marker' + str(i)] = markerDict

			i+=1

		eyeTemplate = {}
		eyeTemplate['Eye_Template'] = sorted(eyeMarkersDict.items())

		with open('d:\\eye_template.json', mode='w') as f:
			json.dump(eyeTemplate, f,  indent = 2)

	@staticmethod
	def bdTemplateSetParent():
		selected = pm.ls(sl=True,type='transform')
		parent = selected[-1]
		children = selected[:-1]
		i=0
		for child in children:
			print parent, child.name()
			try:
				pm.addAttr(parent,ln = child.name(), at = "message")
				child.message.connect(parent.attr(child.name()))
			except:
				print 'Attr exists'
			i+=1
	'''


