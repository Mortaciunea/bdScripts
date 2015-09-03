def bdCreateJoints(start,first):
	cmds.select(cl = True)
	if first:
		pos = cmds.xform(start,q=True, ws=True,rp=True)
		cmds.joint(name=start+'_jnt',p=(pos[0],pos[1],pos[2]))
		#cmds.parent(world=True)

	children=cmds.listRelatives(start, children=True,type='transform')
	
	
	if children:
		for child in children:
			pos = cmds.xform(child,q=True, ws=True,rp=True)
			cmds.joint(name=child + '_jnt',p=(pos[0],pos[1],pos[2]))
			cmds.parent(child + '_jnt',start+'_jnt')
			print child
			bdCreateJoints(child,False)
	
		
bdCreateJoints('Hip_Guide',True)
cmds.select('Hip_Guide' + '_jnt')
cmds.joint(e=True, oj='xzy',secondaryAxisOrient='zdown',ch= True,zso=True)

	
