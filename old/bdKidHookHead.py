import pymel.core as pm

def bdHookGeo():
	refHeadGeoGrp = pm.ls('Head:GEO',type='transform')[0]
	refHeadGeoGrpRelatives = pm.listRelatives(refHeadGeoGrp,ad=True,type='transform')
	refHeadGeo = []
	
	for relative in refHeadGeoGrpRelatives:
		if relative.getShape():
			if relative.getShape().type() == 'mesh':
				refHeadGeo.append(relative)
				print relative.name()
	
	pm.select(refHeadGeo)

	for obj in refHeadGeo:
		sourceStr = obj.name().split(':')[2]
		target = pm.ls(sourceStr,type='transform')[0]
		pm.select([obj,target])
		blendshape = pm.blendShape(n=sourceStr + '_BS')
		#print obj.name()

def bdHookCons():
	headConsGrp = pm.ls('Head_Cons_GRP',type='transform')[0]
	headRelatives = pm.listRelatives(headConsGrp,ad=True,type='shape')
	headCons = []
	for relative in headRelatives:
		headCons.append(relative.getParent())
		print relative.name()
	
	pm.select(headCons)
	
	for con in headCons:
		refCon = pm.ls('Head:' + con.name(),type='transform')[0]
		con.translate.connect(refCon.translate)
		con.rotate.connect(refCon.rotate)
		

