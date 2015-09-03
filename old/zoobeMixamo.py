# Imports an fbx file containing a skeleton + skin generated through Mixamo's auto rigging tool and it does the following:
# - characterizes the char ( needed for transfering the animation )
# - converts the materials in scene to cgfx shader
# - adds a shadow plane
# - scales the char to 15 units
# - saves the character as  a mata file
# - exports the mesh for the Ogre Engine
# - imports animations from Mixamo and / or from Zoobe characters and saves them
# - exports the animations for the Ogre Engine

import pymel.core as pm
import os, shutil,platform
import maya.OpenMaya as OpenMaya
import logging



# ############
hkIkDict = {"Reference":0,"Hips":1,"LeftUpLeg":2,"LeftLeg":3,"LeftFoot":4,"RightUpLeg":5,"RightLeg":6,"RightFoot":7,"Spine":8,"LeftArm":9,"LeftForeArm":10,"LeftHand":11,"RightArm":12,"RightForeArm":13,"RightHand":14,"Head":15,"LeftToeBase":16,"RightToeBase":17,"LeftShoulder":18,"RightShoulder":19,"Neck":20,"LeftFingerBase":21,"RightFingerBase":22,"Spine1":23,"Spine2":24,"Spine3":25,"Spine4":26,"Spine5":27,"Spine6":28,"Spine7":29,"Spine8":30,"Spine9":31,"Neck1":32,"Neck2":33,"Neck3":34,"Neck4":35,"Neck5":36,"Neck6":37,"Neck7":38,"Neck8":39,"Neck9":40,"LeftUpLegRoll":41,"LeftLegRoll":42,"RightUpLegRoll":43,"RightLegRoll":44,"LeftArmRoll":45,"LeftForeArmRoll":46,"RightArmRoll":47,"RightForeArmRoll":48,"HipsTranslation":49,"LeftHandThumb1":50,"LeftHandThumb2":51,"LeftHandThumb3":52,"LeftHandThumb4":53,"LeftHandIndex1":54,"LeftHandIndex2":55,"LeftHandIndex3":56,"LeftHandIndex4":57,"LeftHandMiddle1":58,"LeftHandMiddle2":59,"LeftHandMiddle3":60,"LeftHandMiddle4":61,"LeftHandRing1":62,"LeftHandRing2":63,"LeftHandRing3":64,"LeftHandRing4":65,"LeftHandPinky1":66,"LeftHandPinky2":67,"LeftHandPinky3":68,"LeftHandPinky4":69,"LeftHandExtraFinger1":70,"LeftHandExtraFinger2":71,"LeftHandExtraFinger3":72,"LeftHandExtraFinger4":73,"RightHandThumb1":74,"RightHandThumb2":75,"RightHandThumb3":76,"RightHandThumb4":77,"RightHandIndex1":78,"RightHandIndex2":79,"RightHandIndex3":80,"RightHandIndex4":81,"RightHandMiddle1":82,"RightHandMiddle2":83,"RightHandMiddle3":84,"RightHandMiddle4":85,"RightHandRing1":86,"RightHandRing2":87,"RightHandRing3":88,"RightHandRing4":89,"RightHandPinky1":90,"RightHandPinky2":91,"RightHandPinky3":92,"RightHandPinky4":93,"RightHandExtraFinger1":94,"RightHandExtraFinger2":95,"RightHandExtraFinger3":96,"RightHandExtraFinger4":97,"LeftFootThumb1":98,"LeftFootThumb2":99,"LeftFootThumb3":100,"LeftFootThumb4":101,"LeftFootIndex1":102,"LeftFootIndex2":103,"LeftFootIndex3":104,"LeftFootIndex4":105,"LeftFootMiddle1":106,"LeftFootMiddle2":107,"LeftFootMiddle3":108,"LeftFootMiddle4":109,"LeftFootRing1":110,"LeftFootRing2":111,"LeftFootRing3":112,"LeftFootRing4":113,"LeftFootPinky1":114,"LeftFootPinky2":115,"LeftFootPinky3":116,"LeftFootPinky4":117,"LeftFootExtraFinger1":118,"LeftFootExtraFinger2":119,"LeftFootExtraFinger3":120,"LeftFootExtraFinger4":121,"RightFootThumb1":122,"RightFootThumb2":123,"RightFootThumb3":124,"RightFootThumb4":125,"RightFootIndex1":126,"RightFootIndex2":127,"RightFootIndex3":128,"RightFootIndex4":129,"RightFootMiddle1":130,"RightFootMiddle2":131,"RightFootMiddle3":132,"RightFootMiddle4":133,"RightFootRing1":134,"RightFootRing2":135,"RightFootRing3":136,"RightFootRing4":137,"RightFootPinky1":138,"RightFootPinky2":139,"RightFootPinky3":140,"RightFootPinky4":141,"RightFootExtraFinger1":142,"RightFootExtraFinger2":143,"RightFootExtraFinger3":144,"RightFootExtraFinger4":145,"LeftInHandThumb":146,"LeftInHandIndex":147,"LeftInHandMiddle":148,"LeftInHandRing":149,"LeftInHandPinky":150,"LeftInHandExtraFinger":151,"RightInHandThumb":152,"RightInHandIndex":153,"RightInHandMiddle":154,"RightInHandRing":155,"RightInHandPinky":156,"RightInHandExtraFinger":157,"LeftInFootThumb":158,"LeftInFootIndex":159,"LeftInFootMiddle":160,"LeftInFootRing":161,"LeftInFootPinky":162,"LeftInFootExtraFinger":163,"RightInFootThumb":164,"RightInFootIndex":165,"RightInFootMiddle":166,"RightInFootRing":167,"RightInFootPinky":168,"RightInFootExtraFinger":169,"LeftShoulderExtra":170,"RightShoulderExtra":171}
speakAnims = ['speak_jaw_down','speak_jaw_up','speak_mouth_narrow','speak_mouth_wide','speak_mouth_open','speak_mouth_shut','speak_tongue_in','speak_tongue_out']
morphs = ['jaw_down','jaw_up','mouth_narrow','mouth_wide','mouth_open','mouth_shut']

OS = platform.system()

#  Global paths need to be set
if OS == "Windows":
    CHARACTERS_PATH = 'p:/mixamo_character/working_project/scenes/characters/'
    ASSETS_PATH = 'p:/mixamo_character/assets/'
    PROJECT_PATH = 'p:/mixamo_character/working_project/'
    ANIM_LIB_PATH = 'p:/mixamo_character/working_project/data/animLib/'
elif OS == 'Linux':
    CHARACTERS_PATH = '/home/zoobe/mixamo/testproject/scenes/characters/'
    ASSETS_PATH = '/home/zoobe/mixamo/assets/'
    PROJECT_PATH = '/home/zoobe/mixamo/testproject/'
    ANIM_LIB_PATH = '/home/zoobe/mixamo/testproject/incoming/animLib/'

MIN_HEIGHT = 15
MAX_HEIGHT = 15
# ############

def removeNamespace():
    sceneNS = pm.namespaceInfo(lon=True,r=True)
    importNS = []
    mayaNS = set([u'UI', u'shared'])
    for ns in sceneNS:
        if ns not in mayaNS:
            importNS.append(ns)
    importNS.reverse()

    for ns in importNS:
        pm.namespace( rm = ns,mergeNamespaceWithRoot=True)

class MixamoCharacter(object):
    def __init__(self,*args,**kargs):
        # These plugins are needed by the script, loading them just in case they are not
        pm.loadPlugin('mayaHIK.mll')
        pm.loadPlugin('mayaCharacterization.mll')
        pm.loadPlugin('fbxmaya.mll')
        pm.loadPlugin('zoobe_maya_exporter.mll')

        # The object needs only two arguments : the path to the fbx file and the character name 
        self.name = kargs.setdefault('name','MixamoChar')
        self.fbxFile = kargs.setdefault('path')
        
        self.hasMorphs = 0
        self.characterPath = ''
        self.morphFiles = []
        self.backgroundFile = ''
        pm.mel.eval(' setProject "' + PROJECT_PATH + '"' )

        # A folder structer is needed for the maya part ( rig and animations) and for the export part ( mesh and animation assets)
        self.createCharDirectories()

    # Process character takes the fbx and creates the maya rig file for the character
    def processCharacter(self):
        if(self.importMixamoFbx()):
            self.cleanUpAnim()
            self.characterizeChar()
            self.createCgfxShader()
            self.addMorphs('obj')
            self.addShadowPlane()
            self.scaleChar()
            self.combineBindPoses()
            self.saveChar(self.name)
        else:
            pm.warning('Could not import the FBX file')

    def createCharDirectories(self):
        if os.path.isdir(CHARACTERS_PATH):
            currentCharacters = set(os.listdir(CHARACTERS_PATH))
            if self.name not in currentCharacters:
                mayaCharacterFolder = os.path.join(CHARACTERS_PATH,self.name)
                if not os.path.isdir(mayaCharacterFolder):
                    os.mkdir(mayaCharacterFolder )

                mayaRigFolder = os.path.join(CHARACTERS_PATH,self.name,'rigging')
                if not os.path.isdir(mayaRigFolder):
                    os.mkdir(mayaRigFolder)

                mayaAnimationsFolder = os.path.join(CHARACTERS_PATH,self.name,'animation')
                if not os.path.isdir(mayaAnimationsFolder):
                    os.mkdir(mayaAnimationsFolder)

        self.characterPath = ASSETS_PATH + 'characters/' + self.name + '_std/'
        matPath = self.characterPath + 'materials/'
        if not os.path.isdir(self.characterPath):
            os.mkdir(self.characterPath)
        if not os.path.isdir(matPath):
            os.mkdir(matPath)
        exportAnimationsFolder = ASSETS_PATH + 'characters/' + self.name + '_std/animations/'
        if not os.path.isdir(exportAnimationsFolder):
            os.mkdir(exportAnimationsFolder)        

    def combineBindPoses(self):
        #find all skinCluster in the scene
        skinCluster = pm.ls(type="skinCluster")
        #find all connected bindPoses
        influences = set()
        for sc in skinCluster:
            for i in pm.skinCluster( sc, q=1, influence=1):
                if pm.nodeType(i)=="joint": influences.add(i)

        #delete all dagPoses, create a new one and link to skin clusters
        dagPoses = pm.ls(type="dagPose")
        if dagPoses:
            print( "Converted:")
            print (dagPoses)
            pm.delete( dagPoses)

        pose = pm.dagPose( list(influences), s=1, sl=1, bp=1)
        for sc in skinCluster:
            pm.connectAttr( '%s.message'%pose, '%s.bindPose'%sc)


        print("to: %s\n" % pose)

    def replaceGeometry(self):

        fbxPath = os.path.split(self.fbxFile)[0]
        defaultMeshPath = os.path.join(fbxPath,'blendshapes/')

        meshes = pm.ls(type='mesh')
        meshesShaders = {}

        for m in meshes:
            if 'Orig' not in m.name():
                shader = pm.listConnections(m.name(),s=1,d=1,type = 'shadingEngine')
                if shader:
                    meshesShaders[str(m.name())] = str(shader[0].name())

        print meshesShaders

        morphFiles = [f for f in os.listdir(defaultMeshPath) if f.endswith('.obj')]
        print morphFiles 
        if 'default.obj' in morphFiles:
            print 'Found default'

            pm.importFile(defaultMeshPath + 'default.obj',namespace= 'tpose')
            importMeshes = pm.ls('tpose:*',type='mesh')

            for m in importMeshes:
                if 'Orig' not in m.name():
                    sourceMesh = m.name().split(':')[1]
                    pm.select(m)
                    pm.mel.eval('sets -e -forceElement ' + meshesShaders[sourceMesh])
                    pm.substituteGeometry(sourceMesh,m)


            removeNamespace()

        meshes = pm.ls(type='mesh')

        for m in meshes:
            if 'Orig' not in m.name():
                skinCls = pm.listConnections('%s.inMesh'%m)
                if len(skinCls)==0:
                    print m
                    pm.rename(m.getParent(),'rg_' + m.getParent().name())




    def importMixamoFbx(self) :
        print 'importMixamoFbx'
        pm.newFile(f=1)
        if self.fbxFile:
            if os.path.isfile(self.fbxFile):

                #import the FBX file
                pm.mel.eval( 'FBXImport -f "' + (self.fbxFile) + '"')
                #check for a default mesh in T-Pose. If found, replace geometry
                self.replaceGeometry()

                #clean its namespace
                removeNamespace()
                hips = pm.ls("Hips",type='joint')

                #add root joint for scale
                rootJnt = pm.joint(n='Root')
                pm.parent(hips[0],rootJnt)

                #clean up textures
                self.cleanUpTextures()
                pm.currentUnit(t='ntsc')

                return 1
            else:
                pm.error('Fbx file %s doesn\'t exist'%self.fbxFile)
                return 0
        else:
            pm.error('No file was given')
            return 0


    def addShadowPlane(self):
        print 'Creating the shadow plane'
        shadowPlane = pm.polyPlane( n='shadowPlane', w=10 , h=10, sx=1, sy= 1, ax=( 0, 1, 0),cuv = 2, ch = 0)
        shadowJoint = pm.joint(n='shadowJoint')
        pm.skinCluster(shadowJoint,shadowPlane)

        root = pm.ls("Root",type='joint')[0]
        pm.parent(shadowJoint,root)


        #rig the plane
        hips = pm.ls("Hips",type='joint')[0]
        leftFoot = pm.ls("LeftFoot",type='joint')[0]
        rightFoot = pm.ls("RightFoot",type='joint')[0]

        pm.pointConstraint(hips,shadowJoint,mo=0,skip='y')
        pm.pointConstraint(leftFoot,shadowJoint,mo=0,skip='y')
        pm.pointConstraint(rightFoot,shadowJoint,mo=0,skip='y')

        #default T pose Y value for the hips will be stored as reference
        #pm.addAttr(hips, ln = 'startY',t = 'double')
        hipsY = hips.getTranslation(space='world').y
        #pm.setAttr(hips.name() + '.startY',hipsY)

        shadowPlaneRV = pm.createNode('remapValue', n ='shadowPlane_RV')
        shadowPlaneRV.imx.set(hipsY * 2.0)
        shadowPlaneRV.outputMin.set(2.0)
        shadowPlaneRV.outputMax.set(0)

        hips.translateY.connect(shadowPlaneRV.inputValue)
        shadowPlaneRV.outValue.connect(shadowJoint.scaleX)
        shadowPlaneRV.outValue.connect(shadowJoint.scaleY)
        shadowPlaneRV.outValue.connect(shadowJoint.scaleZ)

        shadowPlaneCgfx = self.importCgfxShader()
        shadowPlaneCgfx.rename('shadowPlane_cgfx')
        shadowPlaneSg = pm.listConnections('%s.outColor'%shadowPlaneCgfx)[0]
        shadowPlaneSg.rename('shadowPlane_cgfxSG')        

        shadowPlaneTxt = pm.shadingNode('file',asTexture=1,name='shadowPlane_file')

        shadowPlaneTxt.fileTextureName.set('sourceimages\\groundshadow_diffusecolor.tga')
        shadowPlaneTxt.outColor.connect(shadowPlaneCgfx.diffuseMapSampler)

        pm.select(shadowPlane)
        pm.mel.eval('sets -e -forceElement ' + shadowPlaneSg)

        print 'Shadow plane created!!'


    # We need an animation clean skeleton. 
    def cleanUpAnim(self):
        animCurves = pm.ls(type='animCurve')
        pm.delete(animCurves)


    # HIK chracterization for the skeleton , needed to transfer animations from other skeletons ( like zoobe's)
    def characterizeChar (self):
        print 'characterizeChar '
        try:
            pm.mel.eval("hikCreateDefinition()")
        except:
            pass
        try:
            char = pm.mel.eval("hikGetCurrentCharacter()")
        except:
            pm.warning('Can\'t get current character')

        pm.rename(char,self.name)

        hips = pm.ls("Hips",type='joint')

        fullSkeleton = hips[0].listRelatives(ad=1)
        fullSkeleton  += hips

        for joint in fullSkeleton:
            if hkIkDict.has_key(joint.name()):
                cmd = 'setCharacterObject("' + joint + '",' + '"' + self.name + '",' + str(hkIkDict[joint.name()]) + ',' + '0);'
                pm.mel.eval(cmd)



    def saveChar(self,charName):
        print 'saveChar'
        if os.path.isdir(CHARACTERS_PATH):
            mayaFile = os.path.join(CHARACTERS_PATH,charName,'rigging',charName + '.ma')
            if os.path.isfile(mayaFile):
                pm.warning('File exists!!!')
            else:
                pm.saveAs(mayaFile,type='mayaAscii')


    def exportOgreMesh(self):
        print 'export mesh'
        rigFile = os.path.join(CHARACTERS_PATH,self.name,'rigging',self.name+ '.ma')
        pm.openFile(rigFile,f=1)
        options = ""


        options += " -outDir \"" + self.characterPath + "\""
        options += " -all -lu pref -scale 1.00"
        options += " -mesh \"" + self.characterPath + self.name + "_basic.mesh" + "\""

        # Various mesh options

        options += " -n -bn -v -t -tangents TANGENT -preventZeroTangent 100.0"


        # Material tab options
        # Material file path
        matPath = self.characterPath + 'materials/'

        options += " -mat \"" + matPath + self.name + "_std.material" + "\""

        # Various material options
        texturePath = ASSETS_PATH + 'textures/characters\\\\'
        options += " -copyTex \"" + texturePath + "\""

        if self.hasMorphs:
            options += " -blendShapes"
            
        pm.mel.eval( "ogreExport" + options)
        print ( "ogreExport" + options)

    def cleanUpTextures(self):
        # get a list of files in sourceimages folder, if they exist already, will not be copied
        existingTextureFiles = set()
        charSourceimages = os.path.join(pm.workspace.name,'sourceimages')
        if os.path.isdir(charSourceimages):
            existingTextureFiles = set(os.listdir(charSourceimages))

        #get the texture file nodes
        fList = pm.ls(type='file')

        for f in fList:
            tName = f.fileTextureName.get()
            #get the texture file path and name
            path,fileName = os.path.split (tName)
            #check if its already in sourceimages, if not it will make a copy there and assign the relative path to fileTextureName attr
            if fileName in existingTextureFiles:
                print ('Image %s exists, skiping'%fileName)
            else:
                shutil.copy2(tName, charSourceimages)

            f.fileTextureName.set('sourceimages\\' + fileName.lower())


    def importCgfxShader(self):
        shaderFile = os.path.join(pm.workspace.name,'scenes/cgfxShader.ma')
        pm.importFile(shaderFile,ra=1,mergeNamespacesOnClash=0,namespace="cgfx")
        removeNamespace()
        cgfxShader = pm.ls('cgfx_*')[0]
        return cgfxShader 

    def createCgfxShader(self):
        print 'Create cgfx shaders'
        diffuseFile = specFile = normFile = ''
        #get the materials starting from the shaders and looking for connections
        shadersList = [sh.name() for sh in pm.ls(type='shadingEngine')]
        #maya's default shaders, we remove them
        mayaShaders = ['initialParticleSE', 'initialShadingGroup']

        shadersList = set(shadersList) - set(mayaShaders)
        materialList = []

        for sh in shadersList:

            mat = pm.listConnections ('%s.surfaceShader'%sh)[0];
            if pm.listConnections(sh,type='mesh'):
                materialList.append(mat)
            else:
                pm.delete(sh)

        diffuseFile = specFile = normFile = ''
        for mat in materialList:
            try:
                diffuseFile = pm.listConnections('%s.color'%mat)[0]
            except:
                pm.warning('No diffuse file found')
            try:
                specFile = pm.listConnections('%s.specularColor'%mat)[0]
            except:
                pm.warning('No spec file found')
            try:
                bumpFile = pm.listConnections('%s.normalCamera'%mat)[0]
                normFile = pm.listConnections('%s.bumpValue'%bumpFile)[0]

            except:
                pm.warning('No norm file found')

            #create a cgfx material
            '''
            cgfxShader = pm.shadingNode('cgfxShader',asShader=1)
            cgfxShader.rename(mat + '_cgfx')
            cmd = 'cgfxShader -e -fx "'

            cmd += CHARACTERS_PATH.replace('scenes/characters','renderData/shaders') + 'zoobeCharacterShader2.cgfx"'
            cmd += cgfxShader.name()
            #assign the zoobe cgfx shader file
            pm.mel.eval(cmd)
            '''
            cgfxShader = self.importCgfxShader()
            cgfxShader.rename(mat + '_cgfx')

            if diffuseFile:
                diffuseFile.outColor.connect(cgfxShader.diffuseMapSampler)
            if specFile:
                specFile.outColor.connect(cgfxShader.specularMapSampler)
            if normFile:
                normFile.outColor.connect(cgfxShader.normalMapSampler)
                pm.setAttr('%s.Bump'%cgfxShader,5)

            #get the shaders for the materials 
            shader = pm.listConnections("%s.outColor"%mat)[0]
            print shader 

            #connect the cgfx material to the mesh shader
            shader.surfaceShader.disconnect()
            cgfxShader.outColor.connect(shader.surfaceShader)
            print ('Converted -> %s   to -> %s '%(mat,cgfxShader))
            pm.delete(mat)

            #connect the file outColor to the cgfx diffuseMapSampler input


    def scaleChar(self):
        headTop = pm.ls('HeadTop_End',type='joint')[0]
        posY = headTop.getTranslation(space='world').y
        scaleFactor = 1
        if posY < MIN_HEIGHT:
            scaleFactor = MIN_HEIGHT / posY
        elif posY > MAX_HEIGHT:
            scaleFactor = MAX_HEIGHT / posY

        root = pm.ls('Root',type='joint')[0]
        root.setScale([scaleFactor,scaleFactor,scaleFactor])


    def importAnimation(self, speak=0,lib=1):
        print 'Importing Animation'
        rigFile = os.path.join(CHARACTERS_PATH,self.name,'rigging',self.name + '.ma')
        pm.openFile(rigFile,f=1)
        if lib:
            importAnimPath = ANIM_LIB_PATH
        else:
            fbxPath = os.path.split(self.fbxFile)[0]
            importAnimPath = fbxPath + '/' + 'animations/'

        animFiles = [f for f in os.listdir(importAnimPath) if f.endswith('.fbx')]
        #self.logger.info('########### Importing animations from library ############')
        for anim in animFiles:
            pm.mel.eval('FBXImportFillTimeline -v 1;')
            cmd = 'FBXImport -f "' + importAnimPath + anim+ '" -caller \"FBXMayaTranslator\" -importFormat \"fbx;v=0\"'
            pm.mel.eval(cmd)
            #self.logger.info('Imported %s ', (importAnimPath + anim))
            #pm.importFile(importAnimPath + anim, type='FBX',mergeNamespacesOnClash=0,rpr=anim.split('.')[0],options = 'v=0;',loadReferenceDepth = 'all')
            start = pm.playbackOptions(q=1,ast=1)
            end = pm.playbackOptions(q=1,aet=1)
            pm.bakeResults( 'shadowJoint',t=(start,end), simulation=True )

            self.saveAnimation(anim.split('.')[0])

            pm.openFile(rigFile,f=1)

        if speak:
            #self.logger.info('Creating speak anims ')
            for anim in speakAnims:
                pm.openFile(rigFile,f=1)
                animationFile = os.path.join(CHARACTERS_PATH,self.name,'animation',anim + '.ma')
                #self.logger.info('%s created',animationFile)
                pm.saveAs(animationFile,f=1)



    def saveAnimation(self,animFile):
        print 'Saving file'
        start = pm.playbackOptions(q=1,ast=1)
        end = pm.playbackOptions(q=1,aet=1)
        length = int(end - start)
        saveName = animFile.replace('lib',self.name) + '_' + str(length) + '.ma'
        pm.playbackOptions(aet = end-1)
        animationFile = os.path.join(CHARACTERS_PATH,self.name,'animation',saveName)
        pm.saveAs(animationFile,f=1)
        #self.logger.info('Saved animation as %s ', animationFile)



    def exportAnimation(self):
        exportFolder = ASSETS_PATH + 'characters/' + self.name + '_std/animations/'
        exportAnimationsPath = os.path.join(CHARACTERS_PATH ,self.name,'animation')
        animFiles = []
        if os.path.isdir(exportAnimationsPath):
            animFiles = [f for f in sorted(os.listdir(exportAnimationsPath)) if f.endswith('.ma') or f.endswith('.ma') ]
        else:
            pm.warning('No animation files found, aborting!')
            return
        #self.logger.info('########### Exporting animations for OGRE ###########')
        for anim in animFiles:
            animFile = os.path.join(exportAnimationsPath,anim)
            pm.openFile(animFile,f=1)
            start = int(pm.playbackOptions(q=1,ast=1))
            end = int(pm.playbackOptions(q=1,aet=1))
            #ogreExport -all -outDir "P:/mixamo_character/assets/characters/EveBavaria_std/animations/" -skeletonClip "EveBavaria_action_unjured_walk_35" startEnd 0 34 frames sampleByFrames 1 -lu pref -scale 1.00 -skeletonAnims -skelBB -np bindPose

            cmd = 'ogreExport -all -outDir "'+ exportFolder + '"'
            cmd += ' -skeletonClip "' + anim.split('.')[0] + '"'
            if 'speak' in anim:
                cmd += ' startEnd 0 1' 
            else:
                cmd += ' startEnd ' + str(start) + ' ' + str(end)
            cmd += ' frames sampleByFrames 1 -lu pref -scale 1.00 -skeletonAnims -skelBB -np bindPose'

            pm.mel.eval(cmd)

            #self.logger.info('Exported %s', (exportFolder + anim.split('.')[0]))

        #self.logger.removeHandler(self.logHdlr)



    def addMorphs(self,type):
        print 'Adding Morphs'
        if type == 'fbx':
            self.addFbxMorphs()
        elif type == 'obj':
            self.addObjMorphs()


    def addFbxMorphs(self):
        morphPath = os.path.join(os.path.split(self.fbxFile)[0], 'blendshapes')
        morphFiles = [f for f in os.listdir(fbxPath) if f.endswith('.fbx')]

        if morphFiles:
            self.morphFiles = morphFiles
        else:
            pm.warning('No morph file found')
            return 0


        if len(self.morphFiles) > 0:
            rigMesh = [pm.ls(type='mesh')[0].getParent()]
            skinCls = pm.listConnections('%s.inMesh'%rigMesh[0].getShape())[0]      
            bsNode = pm.blendShape(rigMesh,name=self.name + '_BS')[0]

            print bsNode

            pm.reorderDeformers(skinCls.name(),bsNode,rigMesh[0].name())


            for morph in self.morphFiles:
                print morph
                if 'open' in morph:
                    pm.mel.eval( 'FBXImport -f "' + morphPath + '/' + morph + '"')
                    meshes = set(mesh.getParent() for mesh in pm.ls(type='mesh'))

                    newMesh = list(meshes - set(rigMesh))
                    newMesh[0].rename('Open')

                    pm.blendShape(bsNode,e=1,t=(rigMesh[0].name(), 0 , newMesh[0].name(), 1))
                    pm.delete(newMesh)

                elif 'blink' in morph:
                    pm.mel.eval( 'FBXImport -f "' + morphPath + '/' + morph + '"')
                    meshes = set(mesh.getParent() for mesh in pm.ls(type='mesh'))

                    newMesh = list(meshes - set(rigMesh))
                    newMesh[0].rename('Blink')

                    pm.blendShape(bsNode,e=1,t=(rigMesh[0].name(), 1 , newMesh[0].name(), 1))
                    pm.delete(newMesh)

    def addObjMorphs(self):
        morphPath = os.path.join(os.path.split(self.fbxFile)[0], 'blendshapes/')
        morphFiles = [f for f in os.listdir(morphPath) if f.endswith('.obj') and 'default' not in f ]
        meshesVtxCount = {}
        meshes = pm.ls(type='mesh')
        for m in meshes:
            if 'Orig' not in m.name() and 'rg' not in m.name():
                meshesVtxCount[m.name()] = pm.polyEvaluate(m,v=1)
        print meshesVtxCount
        
        if morphFiles:
            self.hasMorphs = 1
            bsNode = ''
            bsCreated = 0
            bsEntry =0
            
            for obj in morphFiles:
                speakName = obj.split('.')[0]
                speakName = 'speak_' + speakName
                pm.importFile(morphPath + obj,namespace= 'morph')
                morph = pm.ls('morph:*',type='mesh')[0]
                morph.rename(speakName)
                morphVtxCount = pm.polyEvaluate(morph,v=1)
                
                
                for mesh, count in meshesVtxCount.iteritems():
                    print mesh, count
                    if count == morphVtxCount:
                        rigMesh = [pm.ls(mesh,type='mesh')[0].getParent()]
                        skinCls = pm.listConnections('%s.inMesh'%rigMesh[0].getShape())[0]
    
                        
                        if not bsCreated:
                            print 'creating blendshape'
                            bsNode = pm.blendShape(rigMesh,name='speak_BS')[0].name()
                            pm.reorderDeformers(skinCls.name(),bsNode,rigMesh[0].name())
                            pm.blendShape(bsNode,e=1,t=(rigMesh[0].name(), bsEntry , morph.name(), 1))
                            bsCreated = 1
                        else:
                            print 'adding blendshape'
                            pm.blendShape(bsNode,e=1,t=(rigMesh[0].name(), bsEntry , morph.name(), 1))
                pm.delete(morph)
                bsEntry += 1
    
    
    
                removeNamespace()


    def copyZoobeAnimations(self,zoobeChar):
        print 'Importing Zoobe Animations'


        if zoobeChar:
            sourceChar = 'source:' + zoobeChar
            fuseChar = self.name

            rigFile = os.path.join(CHARACTERS_PATH,self.name,'rigging',self.name + '.ma')

            zoobeCharFolder = os.path.join(ANIM_LIB_PATH,zoobeChar)
            if os.path.isdir(zoobeCharFolder):
                animFiles = [f for f in os.listdir(zoobeCharFolder) if (f.endswith('.ma') or f.endswith('.mb'))]
                animFile = '/home/zoobe/mixamo/testproject/incoming/animLib/violet/violet_angry_action_01.ma'
                #self.copyAnimation(animFile,sourceChar,fuseChar,0,300)

                for anim in animFiles:
                    print animFile
                    animPath = os.path.join(zoobeCharFolder,anim)
                    print animPath 
                    pm.openFile(animPath,f=1)
                    start = pm.playbackOptions(q=1,ast=1)
                    end = pm.playbackOptions(q=1,aet=1)
                    print start, end
                    self.copyAnimation(animPath,sourceChar,fuseChar,start,end)
                    print 'saving animation %s'%anim.split('.')[0]

                    self.saveAnimation(anim.split('.')[0])
            else:
                pm.warning('Did not find %s char folder'%zoobeChar)






    def copyAnimation(self,sourceAnim,sourceChar,fuseChar,start,end):
        rigFile = os.path.join(CHARACTERS_PATH,self.name,'rigging',self.name + '.ma')
        pm.openFile(rigFile,f=1)

        referenceAnim = pm.createReference(sourceAnim,namespace='source')
        pm.playbackOptions(e=1,ast=start,aet=end,min=start,max=end)
        pm.mel.eval('hikSetCurrentCharacter("' + fuseChar + '")')
        #pm.mel.eval('mayaHIKsetStanceInput( "' + fuseChar + '" )')
        #pm.mel.eval('HIKCharacterControlsTool()')
        pm.mel.eval('hikToggleLockDefinition')
        #self.logger.info('Characterized the skeleton')        
        pm.mel.eval('mayaHIKsetCharacterInput( "' + fuseChar + '","' + sourceChar +  '")')
        #pm.mel.eval('HIKCharacterControlsTool()')
        pm.mel.eval('hikBakeCharacter 0')
        referenceAnim.remove()

