import maya.cmds as mc
import functools
import maya.mel as mm

#GENERIC FUNCTIONS
def bdRemoveNamespace(object, toBeReplaced,replaceWith):
	bdRenameList = mc.ls(object, dag=True, ap=True, type='transform')
	#print(object)
	for node in bdRenameList:
		#print(node)
		newName = str(node).replace(toBeReplaced,replaceWith)
		mc.rename(node,newName)
		#print(newName)
#END FUNCTIONS


def bdSetFingersNumber(args):
	bdFingerNumbersVal = mc.intSliderGrp("bdFingersNumber",q=True,v=True)
	#print(bdFingerNumbersVal)

def bdSetToesNumber(args):
	bdToesNumberVal = mc.intSliderGrp("bdToesNumber",q=True,v=True)
	#print(bdToesNumberVal)
	
def bdScaleGuides(args):
	bdScaleVal = mc.floatSliderGrp("bdScaleSlider",q=True,v=True)
	mc.setAttr("Sphere_Guides.sx",bdScaleVal)
	mc.setAttr("Sphere_Guides.sy",bdScaleVal)
	mc.setAttr("Sphere_Guides.sz",bdScaleVal)
	#print(bdScaleVal)


def bdCreateGuides(args):
	charName = mc.textFieldGrp("bdChName",q=True,tx=True)
	if charName!= "":
		print(charName)
		mm.eval('source template_Skeleton.mel')
		mm.eval('template_skeleton("'+ charName+ '")')
		'''
		#create fingers
		bdFingerNumbersVal = mc.intSliderGrp("bdFingersNumber",q=True,v=True)
		for i in range(1,(bdFingerNumbersVal+1),1):
			bdGenericRFingerName = 'RFinger'
			bdNSFinger = 'finger_'+str(i)
			mc.file('skeleton_assets/generic_finger.ma',i=True,type="mayaAscii",ra=True,rpr=bdNSFinger,pr=True,options="v=0,p=17")
			removeNamespace((bdNSFinger + '_' + bdGenericRFingerName), bdNSFinger + '_' , 'RightFinger' + str(i) + '_')
		mc.floatSliderGrp("bdScaleSlider",e=True,en=1)
		'''

def bdMirrorGuide(side="none",bla="none"):
	print(side)


def bdCreateJoints(args):
	print("Creating Joints")

#rig leg additionals
def bdAddAttribute(object, attrList,attrType='' ):
	attrNames = []
	for a in attrList:
		print a
		cmds.addAttr(object,ln=a,at='double')
		cmds.setAttr((object + "." + a),e=True, keyable=True)
		attrNames.append(object + "." + a)
			

def bdCreateGroup(objects,grpName,pivot,parent=''):
	grp = cmds.group(objects,n=grpName)
	footJntPos = cmds.xform(pivot,q=True,ws=True,t=True)
	cmds.move(footJntPos[0],footJntPos[1],footJntPos[2],grp + '.rp',grp + '.sp')
	return grp
	
def bdRigLegCtrl(side):
	print "Rigging %s side leg controller"%side
	
#create a group based rig for a leg
def bdRigLegBones(side):
        legBones = ['thigh','knee','foot','toe','toe_end']
        for i in range(len(legBones)):
                legBones[i] = side + '_' + legBones[i] + '_jnt'
	#START setup foot roll 
	legIk = cmds.ikHandle(sol= 'ikRPsolver',sticky='sticky', startJoint=legBones[0],endEffector = legBones[2],name = side + '_leg_ikHandle')
	footIk = cmds.ikHandle(sol= 'ikSCsolver',sticky='sticky', startJoint=legBones[2],endEffector = legBones[3],name = side + '_foot_ikHandle')
	toeIk = cmds.ikHandle(sol= 'ikSCsolver',sticky='sticky', startJoint=legBones[3],endEffector = legBones[4],name = side + '_toe_ikHandle')
	#create the groups that will controll the foot animations ( roll, bend, etc etc)
	footGrp = bdCreateGroup([legIk[0],footIk[0],toeIk[0]],side + '_foot_grp',legBones[2]) 
	ballGrp = bdCreateGroup([legIk[0]],side + '_ball_grp',legBones[3])
	toeGrp = bdCreateGroup([ballGrp,footIk[0],toeIk[0]],side + '_toe_grp',legBones[4])
	heelGrp = bdCreateGroup([toeGrp],side + '_heel_grp',legBones[2])
	#add atributes on the footGrp - will be conected later to an anim controler
	attrList = ['Heel_R','Ball_R','Toe_R','kneeTwist']
	bdAddAttribute(footGrp,attrList)
	#connect the attributes
	cmds.connectAttr(footGrp + '.' + attrList[0],heelGrp + '.rx')
	cmds.connectAttr(footGrp + '.' + attrList[1],ballGrp + '.rx')
	cmds.connectAttr(footGrp + '.' + attrList[2],toeGrp + '.rx')
	#setup the controller 
	bdRigLegCtrl(side)
	#END setup foot roll 
	
	#START no flip knee knee 
	poleVectorLoc = cmds.spaceLocator()
	poleVectorLoc = cmds.rename(poleVectorLoc,side + 'poleVector')
	poleVectorLocGrp = cmds.group(poleVectorLoc,n=poleVectorLoc + '_GRP')
	
	thighPos = cmds.xform(legBones[0],q=True,ws=True,t=True)
	cmds.move(thighPos[0] + 5,thighPos[1],thighPos[2],poleVectorLocGrp)
	
	cmds.poleVectorConstraint(poleVectorLoc,legIk[0])
	
	shadingNodeADL = cmds.shadingNode('addDoubleLinear', asUtility=True,name = side + 'adl_twist')
	cmds.setAttr(shadingNodeADL + '.input2',90)
	
	cmds.connectAttr(footGrp + '.' + attrList[3],shadingNodeADL + '.input1')
	cmds.connectAttr(shadingNodeADL + '.output',legIk[0] + '.twist')
	#END knee 

def bdMainWindow():
	bdWin = "CreateSkeleton"
	if mc.window(bdWin,q=True,ex=True):
		mc.deleteUI(bdWin)

	mc.window(bdWin,title = "Create Skeleton")
	mc.scrollLayout(horizontalScrollBarThickness=16)
	bdMainCL = mc.columnLayout(columnAttach=("both",5),rowSpacing=10,columnWidth=320)
	#GUIDES CREATION
	bdFL1 = mc.frameLayout(label="Create Guides",bs="etchedOut",w=300,mw=5,cll=1,p=bdMainCL)
	bdCL1= mc.columnLayout(rs=5,adj=1,p=bdFL1)
		#Character Name
	mc.textFieldGrp("bdChName",l="Character Name",tx="")
		#Number of Fingers/Toes
	#mc.intSliderGrp("bdFingersNumber",label="Number of Fingers",field=True,minValue=1,maxValue=5,fieldMinValue=1,fieldMaxValue=5,value=4,cw3=(100,30,10),dc=bdSetFingersNumber)
	#mc.checkBoxGrp("bdHasThumb",numberOfCheckBoxes=1, label='Thumb?')
	#mc.intSliderGrp("bdToesNumber",label="Number of Toes",field=True,minValue=1,maxValue=5,fieldMinValue=1,fieldMaxValue=5,value=4,cw3=(100,30,10),dc=bdSetToesNumber)
	mc.button(l="Create Guides",c=bdCreateGuides)
		#Character Scale Slider
	mc.floatSliderGrp("bdScaleSlider",en=0,label="Guide scale",field=True,minValue=1,maxValue=100,fieldMinValue=1,fieldMaxValue=100,value=1,cw3=(70,30,10),dc=bdScaleGuides)
		#Character Mirror
	mc.rowColumnLayout(nc=2,cw=[(1,138),(2,138)],p=bdCL1);
	mc.button(l="Mirror left << ",al="right",c = functools.partial(bdMirrorGuide,"left"))
	mc.button(l=">> Mirror right",al="left",c = functools.partial(bdMirrorGuide,"right"));
	#END GUIDES CREATION
	
	#JOINTS CREATION
	bdFL2 = mc.frameLayout(label="Create Joints",bs="etchedOut",w=300,mw=5,cll=1,p=bdMainCL)
	bdCL2 = mc.columnLayout(rs=5,adj=1,p=bdFL2)
	mc.button(l="Create Joints",c =bdCreateJoints)
	#floatSliderGrp -en 0 -label "THUMB Orient" -field true	-minValue 0 -maxValue 180 -fieldMinValue 1 -fieldMaxValue 100	-value 0 -cw3 80 40 10 -dc bdJointOrientX bdJointXSlider;
	#END JOINTS CREATION
	
	mc.showWindow(bdWin)

	

	
bdMainWindow()




'''
global proc createSkeleton1()
{
	string $bdWin = "CreateSkeleton";
	if ((`window -exists $bdWin`) == true)
                deleteUI $bdWin;

	global int $bdJobNum;
	window -title "Create Skeleton -----  by Ender" $bdWin;
	scrollLayout -horizontalScrollBarThickness 16;
	    columnLayout -columnAttach "both" 5 -rowSpacing 10 -columnWidth 300 bdMainCL;
				frameLayout -label "Create Guides" -bs "etchedOut" -w 450 -mw 5 -cll 1 -p bdMainCL bdFL1;
					columnLayout -rs 5 -adj 1 -p bdFL1 bdCL1;
							textFieldGrp -l "Character Name" -tx "" bdChName;
		       		button -l "Create Guides" -c createGuides;
 							floatSliderGrp -en 0 -label "Guide scale" -field true	-minValue 1 -maxValue 100 -fieldMinValue 1 -fieldMaxValue 100	-value 1 -cw3 70 30 10 -dc bdScaleGuides bdScaleSlider;
//		       		checkBoxGrp -numberOfCheckBoxes 1	-label "Mirror Guides" -l1 "On/Off" -cc bdSelectSJ bdCkBoxGrp;
							rowColumnLayout -nc 2 -cw 1 138 -cw 2 138 -p bdCL1;
								button -l "Mirror left << " -al "right" -c "bdMirrorGuide L";
								button -l ">> Mirror right" -al "left"  -c "bdMirrorGuide R";
				
				frameLayout -label "Create Joints" -bs "etchedOut" -w 450 -mw 5 -cll 1 -p bdMainCL bdFL2;
					columnLayout -rs 5 -adj 1 -p bdFL2 bdCL2;
		       		button -l "Create Joints" -c createJoints;
 							floatSliderGrp -en 0 -label "THUMB Orient" -field true	-minValue 0 -maxValue 180 -fieldMinValue 1 -fieldMaxValue 100	-value 0 -cw3 80 40 10 -dc bdJointOrientX bdJointXSlider;
		       		
				frameLayout -label "Create Puppets" -bs "etchedOut" -w 450 -mw 5 -cll 1 -p bdMainCL bdFL3;
					columnLayout -rs 5 -adj 1 -p bdFL3 bdCL3;
		       		button -l "Create Puppets" -c createPuppets;	

				frameLayout -label "Create links" -bs "etchedOut" -w 450 -mw 5 -cll 1 -p bdMainCL bdFL4;
					columnLayout -rs 5 -adj 1 -p bdFL4 bdCL4;
		       		button -l "Link joints to puppets" -c createRigg;					
	showWindow $bdWin;
}
'''