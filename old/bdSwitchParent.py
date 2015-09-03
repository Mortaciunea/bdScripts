import pymel.core as pm



def bdSwitchParent():
	selection = pm.ls(sl=1,type='transform')
	if selection:
		ctrl = selection[0]
		try:
			currentParent = ctrl.attr('Parent').get()
		except:
			pm.warning('Current selection has no Parent attribute, aborting!')
			return
		print currentParent 
		switchFrame = pm.currentTime(q=1)
		
	
		pm.currentTime(switchFrame-1,e=1)
		pm.setKeyframe(ctrl)
		pm.currentTime(switchFrame,e=1)

		#World Parent
		if currentParent == 1:
			print 'Frow World to hand'
			tempLoc = pm.spaceLocator(n='temp')
			tempCnstr = pm.parentConstraint(ctrl,tempLoc)
			pm.delete(tempCnstr)

			ctrl.attr('Parent').set(0)

			worldPos = tempLoc.getTranslation(space='world')
			worldRot = tempLoc.getRotation(space='world')


			ctrl.setTranslation(worldPos,space='world')
			ctrl.setRotation(worldRot,space='world')
			
			pm.delete(tempLoc)
			pm.setKeyframe(ctrl )

		else :
			print 'From hand to world'
			tempLoc = pm.spaceLocator(n='temp')
			tempCnstr = pm.parentConstraint(ctrl,tempLoc)
			pm.delete(tempCnstr)

			ctrl.attr('Parent').set(1)

			worldPos = tempLoc.getTranslation(space='world')
			worldRot = tempLoc.getRotation(space='world')


			ctrl.setTranslation(worldPos,space='world')
			ctrl.setRotation(worldRot,space='world')
			
			pm.delete(tempLoc)
			pm.setKeyframe(ctrl )


	else:
		pm.warning('Select a ticket ctrl or the pound bill ctrl')
			
bdSwitchParent()