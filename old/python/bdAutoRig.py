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
	csWin = "CreateSkeleton"
	if mc.window(csWin,q=True,ex=True):
		mc.deleteUI(csWin)

	mc.window(csWin,title = "Create Skeleton")
	mc.scrollLayout(horizontalScrollBarThickness=16)
	csMainCL = mc.columnLayout(columnAttach=("both",5),rowSpacing=10,columnWidth=320)
	#GUIDES CREATION
	csFL1 = mc.frameLayout(label="Create Guides",bs="etchedOut",w=300,mw=5,cll=1,p=csMainCL)
	csCL1= mc.columnLayout(rs=5,adj=1,p=csFL1)
		#Character Name
	mc.textFieldGrp("csChName",l="Character Name",tx="")
		#Number of Fingers/Toes
	#mc.intSliderGrp("csFingersNumber",label="Number of Fingers",field=True,minValue=1,maxValue=5,fieldMinValue=1,fieldMaxValue=5,value=4,cw3=(100,30,10),dc=csSetFingersNumber)
	#mc.checkBoxGrp("csHasThumb",numberOfCheckBoxes=1, label='Thumb?')
	#mc.intSliderGrp("csToesNumber",label="Number of Toes",field=True,minValue=1,maxValue=5,fieldMinValue=1,fieldMaxValue=5,value=4,cw3=(100,30,10),dc=csSetToesNumber)
	mc.button(l="Create Guides",c=csCreateGuides)
		#Character Scale Slider
	mc.floatSliderGrp("csScaleSlider",en=0,label="Guide scale",field=True,minValue=1,maxValue=100,fieldMinValue=1,fieldMaxValue=100,value=1,cw3=(70,30,10),dc=csScaleGuides)
		#Character Mirror
	mc.rowColumnLayout(nc=2,cw=[(1,138),(2,138)],p=csCL1);
	mc.button(l="Mirror left << ",al="right",c = functools.partial(csMirrorGuide,"left"))
	mc.button(l=">> Mirror right",al="left",c = functools.partial(csMirrorGuide,"right"));
	#END GUIDES CREATION
	
	#JOINTS CREATION
	csFL2 = mc.frameLayout(label="Create Joints",bs="etchedOut",w=300,mw=5,cll=1,p=csMainCL)
	csCL2 = mc.columnLayout(rs=5,adj=1,p=csFL2)
	mc.button(l="Create Joints",c =csCreateJoints)
	#floatSliderGrp -en 0 -label "THUMB Orient" -field true	-minValue 0 -maxValue 180 -fieldMinValue 1 -fieldMaxValue 100	-value 0 -cw3 80 40 10 -dc csJointOrientX csJointXSlider;
	#END JOINTS CREATION
	
	mc.showWindow(csWin)

	

	
csMainWindow()




'''
global proc createSkeleton1()
{
	string $csWin = "CreateSkeleton";
	if ((`window -exists $csWin`) == true)
                deleteUI $csWin;

	global int $csJobNum;
	window -title "Create Skeleton -----  by Ender" $csWin;
	scrollLayout -horizontalScrollBarThickness 16;
	    columnLayout -columnAttach "both" 5 -rowSpacing 10 -columnWidth 300 csMainCL;
				frameLayout -label "Create Guides" -bs "etchedOut" -w 450 -mw 5 -cll 1 -p csMainCL csFL1;
					columnLayout -rs 5 -adj 1 -p csFL1 csCL1;
							textFieldGrp -l "Character Name" -tx "" csChName;
		       		button -l "Create Guides" -c createGuides;
 							floatSliderGrp -en 0 -label "Guide scale" -field true	-minValue 1 -maxValue 100 -fieldMinValue 1 -fieldMaxValue 100	-value 1 -cw3 70 30 10 -dc csScaleGuides csScaleSlider;
//		       		checkBoxGrp -numberOfCheckBoxes 1	-label "Mirror Guides" -l1 "On/Off" -cc csSelectSJ csCkBoxGrp;
							rowColumnLayout -nc 2 -cw 1 138 -cw 2 138 -p csCL1;
								button -l "Mirror left << " -al "right" -c "csMirrorGuide L";
								button -l ">> Mirror right" -al "left"  -c "csMirrorGuide R";
				
				frameLayout -label "Create Joints" -bs "etchedOut" -w 450 -mw 5 -cll 1 -p csMainCL csFL2;
					columnLayout -rs 5 -adj 1 -p csFL2 csCL2;
		       		button -l "Create Joints" -c createJoints;
 							floatSliderGrp -en 0 -label "THUMB Orient" -field true	-minValue 0 -maxValue 180 -fieldMinValue 1 -fieldMaxValue 100	-value 0 -cw3 80 40 10 -dc csJointOrientX csJointXSlider;
		       		
				frameLayout -label "Create Puppets" -bs "etchedOut" -w 450 -mw 5 -cll 1 -p csMainCL csFL3;
					columnLayout -rs 5 -adj 1 -p csFL3 csCL3;
		       		button -l "Create Puppets" -c createPuppets;	

				frameLayout -label "Create links" -bs "etchedOut" -w 450 -mw 5 -cll 1 -p csMainCL csFL4;
					columnLayout -rs 5 -adj 1 -p csFL4 csCL4;
		       		button -l "Link joints to puppets" -c createRigg;					
	showWindow $csWin;
}
'''