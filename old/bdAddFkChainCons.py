import pymel.core as pm


def bdSetUpCtrl(ctrl,jnt):
	ctrl.rename(jnt.name().replace('fk','ctrl'))
	ctrlGrp = pm.group([ctrl])
	ctrl.setTranslation([0,0,0],space='object')
	ctrl.setRotation([0,0,0],space='object')
	ctrlGrp.rename(ctrl.name() + '_GRP')
	ctrlGrp.centerPivots()
	
	tempConstraint = pm.parentConstraint(jnt,ctrlGrp)
	pm.delete(tempConstraint)
	
	pm.parentConstraint(ctrl,jnt,mo =True)
	
	return ctrlGrp

def bdAddFkCtrls():
	ctrl, fkRootObj = pm.ls(sl=1,type='transform')


	ctrlGrpAll = []
	
	tempCtrl = ctrl.duplicate()[0]
	ctrlGrp = bdSetUpCtrl(ctrl,fkRootObj)
	ctrlGrpAll.append(ctrlGrp)
	ctrl.overrideEnabled.set(1)
	ctrl.overrideColor.set(6)

	fkChainDesc = fkRootObj.listRelatives(type='joint', ad=True, f=True)
	fkChainDesc.reverse()

	for jnt in fkChainDesc:
		newCtrl = tempCtrl.duplicate()[0]
		newCtrl.overrideEnabled.set(1)
		newCtrl.overrideColor.set(6)
		ctrlGrp = bdSetUpCtrl(newCtrl, jnt)
		ctrlGrpAll.append(ctrlGrp)
	
	print range(len(ctrlGrpAll))
	
	for i in range(len(ctrlGrpAll)-1,0,-1):
		pm.parent(ctrlGrpAll[i],ctrlGrpAll[i-1].getChildren()[0])
		
	pm.delete([tempCtrl])
