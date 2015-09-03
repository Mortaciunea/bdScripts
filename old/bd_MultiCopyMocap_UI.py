import maya.cmds as cmds


def bdSnapToBips():
    print 'bla'
    targets = cmds.textScrollList('bipList',q=True,ai = True)
    destinations = cmds.textScrollList('genericList',q=True,ai = True)

    for i in range(len(targets)):
        target = targets[i]
        dest = destinations[i] + '|Controllers|World_Anim_grp|Global_Scale_Anim'
        const = cmds.parentConstraint(target,dest)
        cmds.delete(const)
        cmds.setAttr(dest + ".translateZ", 0)
        cmds.setAttr(dest + ".rotateX", 0)
        cmds.setAttr(dest + ".rotateY", 0)


def bdAproximateScaling(destination,target):
    destinationRootTy = cmds.getAttr(destination + "|Skeleton|b_Root.translateY")
    targetRootTy = cmds.getAttr(target+ ".translateY")

    scaleFactor = targetRootTy/destinationRootTy
    cmds.setAttr(destination + '|Controllers|World_Anim_grp|Global_Scale_Anim.Global_Scale',scaleFactor)

def bd_createPairs():
    targets = cmds.ls('Bip??',type='joint')

    if targets:
        for t in range(len(targets)-1):
            cmds.duplicate('Generic',rr=True,un=True)
        destinations = cmds.ls('Generic*',type='transform')

        cmds.textScrollList('bipList',e=True,removeAll=True)
        for i in range(len(targets)):

            cmds.textScrollList('bipList',e=True,append = targets[i])
            cmds.textScrollList('genericList',e=True,append = destinations[i])
            bdAproximateScaling(destinations[i],targets[i])


    else:
        print 'No Bip found in file'

def bd_renameBips(args):
    bipRoots = cmds.ls('Bip??',type='joint',ap=True)
    for root in bipRoots:
        print "Renaming %s chain"%root
        allChildren = cmds.listRelatives(root,c=True, ad=True, type='joint',fullPath=True)

        mocapBones = []
        for bone in allChildren:
            mocapBones.append(bone)


        if root in mocapBones[0].split('|')[-1]:
            for bone in mocapBones:
                if 'FBXASC032' in bone:
                    boneName = bone.split('|')[-1]
                    newName = boneName.replace('FBXASC032','_')
                    cmds.rename(bone,newName)

        else:
            for bone in mocapBones:
                if 'FBXASC032' in bone:
                    temp = (bone.split('|')[-1]).split('FBXASC032')
                    newName = root
                    for i in temp[1:]:
                        newName += ('_' + i)
                    if 'Finger' in newName:
                        cmds.rename(bone, newName[:-1])
                    else:
                        cmds.rename(bone, newName[:-2])                  
            pelvisBone = cmds.ls(root + "|*Pelvis",type='joint',ap=True)
            spineStart = cmds.listRelatives(pelvisBone,c=True, type='joint',fullPath=True)
            spineMiddle = cmds.listRelatives(spineStart,c=True, type='joint',fullPath=True)
            newName = spineMiddle[0].split('|')[-1] + '1'
            spineMiddle = cmds.rename(spineMiddle[0],newName)
            spineEnd = cmds.listRelatives(spineMiddle,c=True, type='joint',fullPath=True)
            newName = spineEnd[0].split('|')[-1] + '2'
            spineMiddle = cmds.rename(spineEnd[0],newName)

            print spineEnd[0]


def bd_mocapToCotrollers(args):
    balls = cmds.ls('Bip*_ball')
    for b in balls:
	cmds.xform(b,cp=True)
	
    targets = cmds.textScrollList('bipList',q=True,ai = True)
    destinations = cmds.textScrollList('genericList',q=True,ai = True)
    animPairs = []
    for i in range(len(targets)):
        animPairs.append([targets[i],destinations[i]])    
        print animPairs

    for srcDest in animPairs:
        print srcDest

        worldBones = [('','World_Anim'),('_Footsteps','Footsteps_Anim'),('_Pelvis','Pelvis_Anim')]
        spineBones = [('_Spine','Spine_Anim'),('_Spine1','Spine1_Anim'),('_Spine2','Spine2_Anim'),('_Neck','Neck_DoNot_Anim'),('_Head','Head_Anim')]
        armBones = [('_L_Clavicle','L_Clav_Anim'),('_L_UpperArm','L_Upperarm_Anim'),('_L_Forearm','L_Forearm_Anim'),('_L_Hand','L_Hand_Anim'),('_L_Finger0','L_Fingers_Anim'),('_R_Clavicle','R_Clav_Anim'),('_R_UpperArm','R_Upperarm_Anim'),('_R_Forearm','R_Forearm_Anim'),('_R_Hand','R_Hand_Anim'),('_R_Finger0','R_Fingers_Anim')]
        legBones = [('_L_Foot','L_Foot_Anim'),('_R_Foot','R_Foot_Anim'),('_L_Calf','L_Knee_Anim'),('_R_Calf','R_Knee_Anim'),('_ball','Ball_Anim')]

        for pair in worldBones:
            animCtrl = ''
            ctrls = cmds.ls(pair[1])

            if len(ctrls) > 1:
                for obj in ctrls:
                    if srcDest[1] in obj:
                        animCtrl = obj
            else:
                animCtrl = pair[1]                       

            print animCtrl            
            mocapBone = srcDest[0] + pair[0]

            cmds.parentConstraint(mocapBone,animCtrl)

        for pair in spineBones:
            animCtrl = ''
            ctrls = cmds.ls(pair[1])
            if len(ctrls) > 1:
                for obj in ctrls:
                    if srcDest[1] in obj:
                        animCtrl = obj
            else:
                animCtrl = pair[1]   

            mocapBone = srcDest[0] + pair[0]

            cmds.orientConstraint(mocapBone,animCtrl)

        for pair in armBones:
            animCtrl = ''
            ctrls = cmds.ls(pair[1])
            if len(ctrls) > 1:
                for obj in ctrls:
                    if srcDest[1] in obj:
                        animCtrl = obj
            else:
                animCtrl = pair[1]   

            mocapBone = srcDest[0] + pair[0]

            cmds.orientConstraint(mocapBone,animCtrl)


        for pair in legBones:
            animCtrl = ''
            ctrls = cmds.ls(pair[1])
            if len(ctrls) > 1:
                for obj in ctrls:
                    if srcDest[1] in obj:
                        animCtrl = obj
            else:
                animCtrl = pair[1]   

            mocapBone = srcDest[0] + pair[0]

            cnstr = cmds.orientConstraint(mocapBone,animCtrl)
            if 'Foot_Anim' in animCtrl:
                cmds.setAttr(cnstr[0] + '.offsetY',-90)
                cmds.setAttr(cnstr[0] + '.offsetZ',90)
            cnstr = cmds.pointConstraint(mocapBone,animCtrl)
            if 'Knee_Anim' in animCtrl:
                cmds.setAttr(cnstr[0] + '.offsetX',20)




def bd_bakeControllers(args):
    cmds.select('*_Anim')
    animCtrls = cmds.ls(sl=True, type='transform')
    minTime = cmds.playbackOptions(q=True,minTime=True)
    maxTime = cmds.playbackOptions(q=True,maxTime=True)
    cmds.bakeResults(animCtrls,simulation=True, t=(minTime,maxTime) )

    cmds.select('*_Anim')
    animCtrls = cmds.ls(sl=True, type='transform')
    cmds.select(clear=True)
    for anim in animCtrls:
        constr = cmds.listRelatives(anim, children=True,type = 'constraint')
        if constr:
            cmds.delete(constr)

def bdPopulateBipList():
    bipRoots = cmds.ls('Bip??', type='joint')
    cmds.textScrollList('bipList',e=True,append = bipRoots)


def bdRemoveNamespace(object, toBeReplaced,replaceWith):
    csRenameList = cmds.listRelatives(object, dag=True, ap=True, type='transform')
    print(object)
    for node in csRenameList:
        print(node)
        newName = str(node).replace(toBeReplaced,replaceWith)
        cmds.rename(node,newName)


def bdImportGeneric(args):
    basicFilter = "Maya Files (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb)"
    genericFile = cmds.fileDialog2(fileFilter=basicFilter, dialogStyle=0,cap='Import Generic',fm=1)    
    if genericFile:
        print genericFile
        #cmds.file( genericFile[0],  namespace="generic", import = True)
        cmds.file( genericFile[0], i=True,namespace = 'genericchar' )
	#remove namespaces
	sceneNS = cmds.namespaceInfo(lon=True,r=True)
	importNS = []
	for ns in sceneNS:
		if 'genericchar' in ns:
			importNS.append(ns)
	importNS.reverse()
	
	for ns in importNS:
		cmds.namespace(setNamespace=ns)
		parentNS = cmds.namespaceInfo( parent = True)
		nemName = ":" + ns
		cmds.namespace( force = True, moveNamespace = [ nemName, ':' ] )
		cmds.namespace( rm = nemName)        
        

    else:
        print 'No file was selected'
    bipsInScene = cmds.ls('Bip??')
    if len(bipsInScene) == 1:
        target = bipsInScene[0]
        dest = 'Generic|Controllers|World_Anim_grp|Global_Scale_Anim'
        const = cmds.parentConstraint(target,dest)
        cmds.delete(const)
        cmds.setAttr(dest + ".translateZ", 0)
        cmds.setAttr(dest + ".rotateX", 0)
        cmds.setAttr(dest + ".rotateY", 0)	

def bdDuplicateGeneric(args):
    genericInFile = cmds.ls('Generic',type='transform')
    if genericInFile:
        if len(genericInFile) > 1:
            print 'more then one Generic character in file, need only one'
        else:
            animPairs = bd_createPairs()
    else:
        print 'No Generic character in file, import one'
    bdSnapToBips()

def bdSelectBip():
    bipSelected = cmds.textScrollList('bipList',q=True,si=True)
    cmds.select(bipSelected[0])

def bdSelectGeneric():
    genSelected = cmds.textScrollList('genericList',q=True,si=True)
    worldAnim = cmds.ls(genSelected[0]+"|Controllers|World_Anim_grp|Global_Scale_Anim")
    cmds.select(worldAnim[0])


def bdRemoveMocapData(args):
    bipsInScene = cmds.ls('Bip??')
    cmds.delete(bipsInScene)
    
    bipMeshes = []
    meshes = cmds.ls(type='mesh')
    
    
    for m in meshes:
	    transformNode = cmds.listRelatives(m,p=True,f=True)
	    bipMeshes.append(transformNode[0])
    
    for t in bipMeshes:
	    if t.find('Generic') < 0:
		    cmds.select(t,add=True)
    
    cmds.delete()

def UI():
    bdWin = "FootballUtils"
    if cmds.window(bdWin,q=True,ex=True):
        cmds.deleteUI(bdWin)

    cmds.window(bdWin,title = "Football Utils")
    cmds.scrollLayout(horizontalScrollBarThickness=16)
    bdMainCL = cmds.columnLayout(columnAttach=("both",5),rowSpacing=10,columnWidth=320)
    #Bip List
    bdFL1 = cmds.frameLayout(label="Bips",bs="etchedOut",w=300,mw=5,cll=1,p=bdMainCL)
    bdRL= cmds.rowLayout(numberOfColumns=2, columnWidth2=(150, 150), p=bdFL1 )

    bdBipList = cmds.textScrollList('bipList',numberOfRows = 10, allowMultiSelection=True,height = 100,sc=bdSelectBip,p=bdRL)
    bdGenericList = cmds.textScrollList('genericList',numberOfRows = 10, allowMultiSelection=True,height = 100,sc=bdSelectGeneric,p=bdRL)


    bdPopulateBipList()
    cmds.button(l="Rename Bips",c=bd_renameBips,p=bdFL1 )    

    bdFL2 = cmds.frameLayout(label="Generic",bs="etchedOut",w=300,mw=5,cll=1,p=bdMainCL)
    cmds.button(l="Import Generic Character",al="right",c = bdImportGeneric)
    cmds.button(l="Duplicate Generic Character",al="right",c = bdDuplicateGeneric)
    cmds.text(l='Note: Even if there is only one Generic, click Duplicate Generic\n Use the Global_Scale_Anim to scale the Generic chars')
    cmds.button(l="Copy Anim ",al="right",c = bd_mocapToCotrollers)
    cmds.button(l="Bake Anim",al="left",c = bd_bakeControllers);
    cmds.button(l="Remove Mocap data",c =bdRemoveMocapData)
    #END JOINTS CREATION

    cmds.showWindow(bdWin)    

