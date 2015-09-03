import pymel.core as pm


class bdAttributer():
	def __init__(self, *args, **kargs):
		self.attrHolder = self.bdGetHolder()
		self.attrList = []
		self.attrReconstruct = []
		self.attrReconstructConnections = []
		self.attrReconstructValues = []
		self.attrReconstructType = []
		self.attrReconstructRange = []
		self.compoundAttrs = []
		self.attrIndex = 0

	
	def bdGetHolder(self):
		selection = pm.ls(sl=1,type='transform')
		if selection:
			return selection[0]
		else:
			pm.warning('Nothing selected')
		
		
	def bdAttrMoveUp(self,attr):
		if self.attrHolder:
			print 'Moving %s attr up'%attr
			self.bdGetAttrList()
			for a in self.attrList:
				if attr in a.name():
					self.attrIndex = self.attrList.index(a)
		
			self.attrReconstruct = self.attrList[(self.attrIndex-1):]
	
			for attr in self.attrReconstruct:
				attrConnections = pm.listConnections('%s'%attr,plugs=1)
				self.attrReconstructConnections.append(attrConnections)
				
				attrValue = self.bdGetValue(attr)
				self.attrReconstructValues.append(attrValue)
				
				attrType = attr.type()
				self.attrReconstructType.append(attrType)
				
				attrRange = attr.getRange()
				self.attrReconstructRange.append(attrRange)
			
		
			shiftItem = self.attrReconstruct.pop(1)
			self.attrReconstruct.insert(0,shiftItem)
		
			shiftItem = self.attrReconstructConnections.pop(1)
			self.attrReconstructConnections.insert(0,shiftItem)
		
			shiftItem = self.attrReconstructValues.pop(1)
			self.attrReconstructValues.insert(0,shiftItem)
		
			shiftItem = self.attrReconstructType.pop(1)
			self.attrReconstructType.insert(0,shiftItem)
		
			shiftItem = self.attrReconstructRange.pop(1)
			self.attrReconstructRange.insert(0,shiftItem)
			
			print self.attrReconstruct
			
			self.bdRebuildAttributes()
			'''
			for attr in self.attrReconstruct:
				try:
					pm.deleteAttr(attr)
				except:
					pm.warning('Fail to delete %s'%attr.name())
			'''
	
	
	def bdGetAttrList(self):
		if self.attrHolder:
			self.attrList = self.attrHolder.listAttr(ud=1)
			
			#look after compound attribytes and remove the children from the list 
	
			for a in self.attrList:
				if a.isCompound():
					self.compoundAttrs.append(a)
	
			for a in self.compoundAttrs:
				for child in a.children():
					self.attrList.remove(child)
			
			#remove 'anim_ctrl' , this one is always kept
			try:
				self.attrList.remove(selection[0].attr('anim_ctrl'))
			except:
				print 'anim_ctrl attr missing in action'



	def bdGetValue(self,attr):
		attrType = attr.type()
		if attrType == 'enum':
			dictEnum = a.getEnums()
			val = [str(k) for k in dictEnum.keys() ]
			values = str(val).strip('[]').replace('\'','')
			return values 
		else:
			val = attr.get()
			return val

	def bdRebuildAttributes(self):
		i=0

