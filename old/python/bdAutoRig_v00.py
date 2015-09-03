import maya.cmds as mc
import functools
import maya.mel as mm

#GENERIC FUNCTIONS
def removeNamespace(object, toBeReplaced,replaceWith):
	csRenameList = mc.ls(object, dag=True, ap=True, type='transform')
	#print(object)
	for node in csRenameList:
		#print(node)
		newName = str(node).replace(toBeReplaced,replaceWith)
		mc.rename(node,newName)
		#print(newName)
#END FUNCTIONS


def csSetFingersNumber(args):
	csFingerNumbersVal = mc.intSliderGrp("csFingersNumber",q=True,v=True)
	#print(csFingerNumbersVal)

def csSetToesNumber(args):
	csToesNumberVal = mc.intSliderGrp("csToesNumber",q=True,v=True)
	#print(csToesNumberVal)
	
def csScaleGuides(args):
	csScaleVal = mc.floatSliderGrp("csScaleSlider",q=True,v=True)
	mc.setAttr("Sphere_Guides.sx",csScaleVal)
	mc.setAttr("Sphere_Guides.sy",csScaleVal)
	mc.setAttr("Sphere_Guides.sz",csScaleVal)
	#print(csScaleVal)


def csCreateGuides(args):
	charName = mc.textFieldGrp("csChName",q=True,tx=True)
	if charName!= "":
		print(charName)
		mm.eval('source template_Skeleton.mel')
		mm.eval('template_skeleton("'+ charName+ '")')
		'''
		#create fingers
		csFingerNumbersVal = mc.intSliderGrp("csFingersNumber",q=True,v=True)
		for i in range(1,(csFingerNumbersVal+1),1):
			csGenericRFingerName = 'RFinger'
			csNSFinger = 'finger_'+str(i)
			mc.file('skeleton_assets/generic_finger.ma',i=True,type="mayaAscii",ra=True,rpr=csNSFinger,pr=True,options="v=0,p=17")
			removeNamespace((csNSFinger + '_' + csGenericRFingerName), csNSFinger + '_' , 'RightFinger' + str(i) + '_')
		mc.floatSliderGrp("csScaleSlider",e=True,en=1)
		'''

def csMirrorGuide(side="none",bla="none"):
	print(side)


def csCreateJoints(args):
	print("Creating Joints")

def csMainWindow():
    bdWin1 = mc.loadUI(f='bdAutoRigUI.ui')    
    mc.showWindow(bdWin1)
    

csMainWindow()
