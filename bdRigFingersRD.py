import bdRigUtils
import pymel.core as pm
reload(bdRigUtils)



def bdAddAllFingerAttr(side):
	fingerAnim = pm.ls(side + '_Fingers_CON',type='transform')[0]
	fingerList = ['Index','Middle','Ring','Pinky','Thumb']
	attrList = ['SpreadMeta','Spread','Curl','Scrunch','Twist','BendMeta','Bend']
	for finger in fingerList:
		bdRigUtils.bdAddSeparatorAttr(fingerAnim.name(),'_' + finger + '_')
		if finger == 'Thumb':
			attrList = ['Spread','Curl','Scrunch','Twist','Bend']
		for attr in attrList:
			pm.addAttr(fingerAnim,ln=finger + '_' + attr,at = 'float',dv=0,min=-10,max=10)
			pm.setAttr((fingerAnim + "." + finger + '_' + attr),e=True, keyable=True)



def bdAddSDK(side):

	fingerList =  ['Index','Middle','Ring','Pinky','Thumb']
	attrList = ['SpreadMeta','Spread','Curl','Scrunch','Twist','BendMeta','Bend']
	for finger in fingerList:
		for attr in attrList:
			if attr == 'Spread':
				print 'Spread'
				bdAddSpread(side,finger,finger + '_' + attr)
			elif attr == 'SpreadMeta':
				print 'Spread'
				bdAddSpreadMeta(side,finger,finger + '_' + attr)				
			elif attr =='Curl':
				print 'Curl'
				bdAddCurl(side,finger,finger + '_' + attr)
			elif attr == 'Scrunch':
				print 'Scrunch'
				bdAddScrunch(side,finger,finger + '_' + attr)
			elif attr == 'Twist':
				print 'Twist'
				bdAddTwist(side,finger,finger + '_' + attr)
			elif attr == 'BendMeta':
				print 'BendMeta'
				bdAddBendMeta(side,finger,finger + '_' + attr)
			elif attr == 'Bend':
				print 'Bend'
				bdAddBend(side,finger,finger + '_' + attr)				
			
			
def bdAddSpreadMeta(side,finger,attr):
	fingerAnim = pm.ls(side + 'Fingers_CON',type='transform')[0]
	if finger != 'Thumb':
		startFingerJnt = pm.ls(side + finger + '_00_JNT')[0]
		pm.setDrivenKeyframe(startFingerJnt, at='rotateY', cd = fingerAnim.name() + '.' + attr , dv= 0 , v = 0)
		pm.setDrivenKeyframe(startFingerJnt, at='rotateY', cd = fingerAnim.name() + '.' + attr , dv= 10 , v = -10)
		pm.setDrivenKeyframe(startFingerJnt, at='rotateY', cd = fingerAnim.name() + '.' + attr , dv= -10 , v = 10)
	

def bdAddSpread(side,finger,attr):
	fingerAnim = pm.ls(side + 'Fingers_CON',type='transform')[0]
	if finger != 'Thumb':
		startFingerJnt = pm.ls(side + finger + '_01_SDK')[0]
		pm.setDrivenKeyframe(startFingerJnt, at='rotateY', cd = fingerAnim.name() + '.' + attr , dv= 0 , v = 0)
		pm.setDrivenKeyframe(startFingerJnt, at='rotateY', cd = fingerAnim.name() + '.' + attr , dv= 10 , v = -10)
		pm.setDrivenKeyframe(startFingerJnt, at='rotateY', cd = fingerAnim.name() + '.' + attr , dv= -10 , v = 10)
	else:
		startFingerJnt = pm.ls(side + finger + '_01_SDK')[0]
		pm.setDrivenKeyframe(startFingerJnt, at='rotateY', cd = fingerAnim.name() + '.' + attr , dv= 0 , v = 0)
		pm.setDrivenKeyframe(startFingerJnt, at='rotateY', cd = fingerAnim.name() + '.' + attr , dv= 10 , v = -90)
		pm.setDrivenKeyframe(startFingerJnt, at='rotateY', cd = fingerAnim.name() + '.' + attr , dv= -10 , v = 90)		

				
def bdAddCurl(side,finger,attr):
	fingerAnim = pm.ls(side + 'Fingers_CON',type='transform')[0]
	targetValuesDown = [-100,-90,-125]
	sdkFingers = pm.ls(side + finger + '_*_SDK')
	for finger in sdkFingers:
		pm.setDrivenKeyframe(finger, at='rotateZ', cd = fingerAnim.name() + '.' + attr , dv= 0 , v = 0)
		pm.setDrivenKeyframe(finger, at='rotateZ', cd = fingerAnim.name() + '.' + attr , dv= 10 , v = targetValuesDown[sdkFingers.index(finger)])
		pm.setDrivenKeyframe(finger, at='rotateZ', cd = fingerAnim.name() + '.' + attr , dv= -10 , v = 25)

def bdAddScrunch(side,finger,attr):
	fingerAnim = pm.ls(side + 'Fingers_CON',type='transform')[0]
	targetValuesUp = [70,-85,-60]
	targetValuesDown = [-45,45,45]
	sdkFingers = pm.ls(side + finger + '_*_SDK')
	for finger in sdkFingers:
		print finger.name(), targetValuesUp[sdkFingers.index(finger)], targetValuesDown[sdkFingers.index(finger)]
		pm.setDrivenKeyframe(finger, at='rotateZ', cd = fingerAnim.name() + '.' + attr , dv= 0 , v = 0)
		pm.setDrivenKeyframe(finger, at='rotateZ', cd = fingerAnim.name() + '.' + attr , dv= 10 , v = targetValuesUp[sdkFingers.index(finger)])
		pm.setDrivenKeyframe(finger, at='rotateZ', cd = fingerAnim.name() + '.' + attr , dv= -10 , v = targetValuesDown[sdkFingers.index(finger)])

def bdAddTwist(side,finger,attr):
	fingerAnim = pm.ls(side + 'Fingers_CON',type='transform')[0]
	startFingerSdk = pm.ls(side + finger + '_01_SDK')[0]
	pm.setDrivenKeyframe(startFingerSdk, at='rotateX', cd = fingerAnim.name() + '.' + attr , dv= 0 , v = 0)
	pm.setDrivenKeyframe(startFingerSdk, at='rotateX', cd = fingerAnim.name() + '.' + attr , dv= 10 , v = -90)
	pm.setDrivenKeyframe(startFingerSdk, at='rotateX', cd = fingerAnim.name() + '.' + attr , dv= -10 , v = 90)

		

def bdAddBendMeta(side,finger,attr):
	fingerAnim = pm.ls(side + 'Fingers_CON',type='transform')[0]
	if finger != 'Thumb':
		startFingerJnt = pm.ls(side + finger + '_00_JNT')[0]
		startFingerSdk = pm.ls(side + finger + '_01_SDK')[0]
		pm.setDrivenKeyframe(startFingerJnt, at='rotateZ', cd = fingerAnim.name() + '.' + attr , dv= 0 , v = 0)
		pm.setDrivenKeyframe(startFingerJnt, at='rotateZ', cd = fingerAnim.name() + '.' + attr , dv= 10 , v = -45)
		pm.setDrivenKeyframe(startFingerJnt, at='rotateZ', cd = fingerAnim.name() + '.' + attr , dv= -10 , v = 45)
		
		pm.setDrivenKeyframe(startFingerSdk, at='rotateZ', cd = fingerAnim.name() + '.' + attr , dv= 0 , v = 0)
		pm.setDrivenKeyframe(startFingerSdk, at='rotateZ', cd = fingerAnim.name() + '.' + attr , dv= 10 , v = 45)
		pm.setDrivenKeyframe(startFingerSdk, at='rotateZ', cd = fingerAnim.name() + '.' + attr , dv= -10 , v = -45)
		


def bdAddBend(side,finger,attr):
	fingerAnim = pm.ls(side + 'Fingers_CON',type='transform')[0]
	if finger != 'Thumb':
		startFingerSdk = pm.ls(side + finger + '_01_SDK')[0]

		pm.setDrivenKeyframe(startFingerSdk, at='rotateZ', cd = fingerAnim.name() + '.' + attr , dv= 0 , v = 0)
		pm.setDrivenKeyframe(startFingerSdk, at='rotateZ', cd = fingerAnim.name() + '.' + attr , dv= 10 , v = 90)
		pm.setDrivenKeyframe(startFingerSdk, at='rotateZ', cd = fingerAnim.name() + '.' + attr , dv= -10 , v = -90)
		
	else:
		startFingerJnt = pm.ls(side + finger + '_01_SDK')[0]
		pm.setDrivenKeyframe(startFingerJnt, at='rotateZ', cd = fingerAnim.name() + '.' + attr , dv= 0 , v = 0)
		pm.setDrivenKeyframe(startFingerJnt, at='rotateZ', cd = fingerAnim.name() + '.' + attr , dv= 10 , v = -90)
		pm.setDrivenKeyframe(startFingerJnt, at='rotateZ', cd = fingerAnim.name() + '.' + attr , dv= -10 , v = 90)


#bdAddAllFingerAttr("L")		
#bdAddSDK("L_")
bdAddAllFingerAttr("R")		
bdAddSDK("R_")