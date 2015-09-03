import pymel.core as pm


def bdAttrMoveUp(attr):
	print 'Moving %s attr up'%attr
	attrList = bdGetAttrList()
	attrIndex = 0
	for a in attrList:
		if attr in a.name():
			attrIndex = attrList.index(a)

	attrReconstruct = attrList[(attrIndex-1):]
	attrReconstructConnections = []
	attrReconstructValues = []
	attrReconstructType = []
	attrReconstructRange = []


	for attr in attrReconstruct:
		attrConnections = pm.listConnections('%s'%attr,plugs=1)
		attrReconstructConnections.append(attrConnections)
		
		attrValue = bdGetValue(attr)
		attrReconstructValues.append(attrValue)
		
		attrType = attr.type()
		attrReconstructType.append(attrType)
		
		attrRange = attr.getRange()
		attrReconstructRange.append(attrRange)
	

	shiftItem = attrReconstruct.pop(1)
	attrReconstruct.insert(0,shiftItem)

	shiftItem = attrReconstructConnections.pop(1)
	attrReconstructConnections.insert(0,shiftItem)

	shiftItem = attrReconstructValues.pop(1)
	attrReconstructValues.insert(0,shiftItem)

	shiftItem = attrReconstructType.pop(1)
	attrReconstructType.insert(0,shiftItem)

	shiftItem = attrReconstructRange.pop(1)
	attrReconstructRange.insert(0,shiftItem)
	'''
	i = 0
	for attr in attrReconstruct:
		print attr.name()
		print attrReconstructConnections[i]
		print attrReconstructValues[i]
		print attrReconstructType[i]
		print attrReconstructRange[i]
		i += 1

	'''
	for attr in attrReconstruct:
		try:
			pm.deleteAttr(attr)
		except:
			pm.warning('Fail to delete %s'%attr.name())
			


def bdGetAttrList():
	selection = pm.ls(sl=1,type='transform')
	attrList = selection[0].listAttr(ud=1)
	
	#look after compound attribytes and remove the children from the list 
	compoundAttrs = []
	for a in attrList:
		if a.isCompound():
			compoundAttrs.append(a)
			print a.children()
	for a in compoundAttrs:
		for child in a.children():
			attrList.remove(child)
	
	#remove 'anim_ctrl' 
	attrList.remove(selection[0].attr('anim_ctrl'))

	return attrList

def bdGetValue(attr):
	attrType = attr.type()
	if attrType == 'enum':
		dictEnum = a.getEnums()
		val = [str(k) for k in dictEnum.keys() ]
		values = str(val).strip('[]').replace('\'','')
		return values 
	else:
		val = attr.get()
		return val

