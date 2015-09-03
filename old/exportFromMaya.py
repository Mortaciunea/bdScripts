import maya.cmds as cmdsimport maya.mel as mmdef getPSAPath():	filePath = cmds.file(q=True,loc=True)	buff = filePath.split('/')	filePath = filePath.replace('Animation/Scenes/' + buff[len(buff)-1],'unreal_export/psa/')	return filePath def getJointsToBeBaked(root):	children = cmds.listRelatives(root, c=True, typ = 'joint')	listAttr = cmds.attributeQuery( 'list', node='listSkinJoints', listEnum=True )	newListAttr = listAttr[0] + ':' + root.replace('_:','')	cmds.addAttr('listSkinJoints.list',edit=True,enumName=newListAttr  )	if children:		for child in children:			print child.find('ik')			if (child.find('ik')<0) and (child.find('sim')<0):				getJointsToBeBaked(child)				def bakeSkinJoints():	startTime = cmds.playbackOptions(q=True, min = True)	endTime = cmds.playbackOptions(q=True, max = True)	listJoints = cmds.attributeQuery( 'list', node='listSkinJoints', listEnum=True )	bakeJoints = listJoints[0].rsplit(':')	del bakeJoints[0:1]	print bakeJoints 	cmds.bakeResults( bakeJoints , t=(startTime ,endTime), simulation=True )	def getMeshes(root):	children = cmds.listRelatives(root , c=True ,f=True)	if children:		for child in children:			shapeNode = cmds.listRelatives(child,c=True, typ = 'shape')			if shapeNode:				if cmds.objectType(shapeNode[0],isType = 'mesh'):					#cmds.parent(child,w=True)					mesh = cmds.ls(child,shortNames=True)					print mesh 					listAttr = cmds.attributeQuery( 'list', node='listMeshes', listEnum=True )					newListAttr = listAttr[0] + ':' + str(mesh[0])					cmds.addAttr('listMeshes.list',edit=True,enumName=newListAttr  )			getMeshes(child)	def extractMeshes():	listMeshes = cmds.attributeQuery( 'list', node='listMeshes', listEnum=True )	print listMeshes	worldMeshes = listMeshes[0].rsplit(':')	del worldMeshes [0:1]	for item in worldMeshes:		cmds.parent(item,w=True)		item 	return worldMeshesdef removeString(root,pattern):	tempName = str(root).replace(pattern,"")	fp = cmds.ls(root, l=True)	newName = cmds.rename(fp[0],tempName )	fp = cmds.ls(newName , l=True)	children = cmds.listRelatives(fp[0], c=True,type='transform')	if children:		for child in children:			removeString(child,pattern)def getReferencedFiles():	topNode = cmds.textScrollList('ceRefList',q=True,selectItem=True)	refFileName  = cmds.referenceQuery( topNode[0], filename=True )	remString = str(cmds.file(refFileName,q=True,namespace=True))	remString = remString + ':'	cmds.file(refFileName,ir=True)	cmds.textScrollList('ceRefList',e=True,removeItem=topNode[0])	return topNode[0],remString	def populateReferenceList():	references = cmds.ls(et='reference')	#del references[len(references)-1]	#print references	for ref in references:		refFileName  = cmds.referenceQuery(ref ,filename = True)		print refFileName  		if not(cmds.file(rfn=ref,q=True,dr=True)):			bla = cmds.referenceQuery(ref ,n = True)			cmds.textScrollList('ceRefList',e=True,append=[bla[0]])#	nsNode = cmds.file(refFileName,q=True,namespace=True)#	bla = cmds.referenceQuery(references[0],n = True)#	nsNode = cmds.file(refFileName,q=True,namespace=True)def cleanAndExportAnim(*arg):	cmds.spaceLocator (n='listMeshes')	cmds.spaceLocator (n='listSkinJoints')	cmds.addAttr('listMeshes',ln='list',at='enum',en='start:') 	cmds.addAttr('listSkinJoints',ln='list',at='enum',en='start:') 	topNode = getReferencedFiles()	removeString(topNode[0]  ,topNode[1] )	getJointsToBeBaked('b_root')	getMeshes(topNode[0].replace(topNode[1],''))	meshes = extractMeshes()	bakeSkinJoints()		cmds.delete('b_tail_sim_root')	cmds.delete('b_tail_ik_01')	select = cmds.ls(type='constraint')	cmds.delete(select)	cmds.parent('b_root',w=True)	cmds.delete(topNode[0].replace(topNode[1],'') )	cmds.delete('listMeshes')	cmds.delete('listSkinJoints')	cmds.select(meshes[0])		psaPath = getPSAPath()	fileName = cmds.textFieldGrp('animFileName',q=True,text=True)	seqName = cmds.textFieldGrp('animSeqName',q=True,text=True)	command = 'axexecute -path \"' + psaPath + '\" -sequence \"' + seqName + '\" -saveanim -animfile \"' + fileName + '\" '	print command	mm.eval(command)def cleanAndExportMesh(*arg):	topNode = cmds.ls(sl=True)	print topNodeo	cmds.spaceLocator (n='listMeshes')	cmds.addAttr('listMeshes',ln='list',at='enum',en='start:') 	getMeshes(topNode[0])	extractMeshes()		cmds.parent('b_root',w=True)		cmds.delete('b_tail_sim_root')	cmds.delete('b_tail_ik_01')	cmds.delete(topNode [0])	cmds.delete('listMeshes')	mm.eval("axmain")def cleanAndExportUI():	if cmds.objExists('sharedReferenceNode'):		cmds.delete('sharedReferenceNode')	ceWin = 'cleanExportUI2'	if cmds.window(ceWin,exists=True):		cmds.deleteUI(ceWin)	cmds.window(ceWin,title='clean for export')	cmds.columnLayout(adj=True,co=('both',10))	cmds.text(align="left",l="List Of Reference Nodes")	cmds.textScrollList('ceRefList', numberOfRows=8, allowMultiSelection=True )	populateReferenceList()	cmds.textFieldGrp('animFileName',label='File Name', text='Text',ct2=('left','right'),cw2=[1,290])	cmds.textFieldGrp('animSeqName',label='Anim Seq Name', text='Text',ct2=('left','right'),cw2=[1,310])	cmds.button(label = 'AnimExport!',c=cleanAndExportAnim)	cmds.button(label = 'MeshExport!',c=cleanAndExportMesh)	cmds.showWindow(ceWin)	cleanAndExportUI()