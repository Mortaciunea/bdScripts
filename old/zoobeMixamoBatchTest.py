#import maya.standalone
# Start Maya in batch mode
#maya.standalone.initialize()
from sys import argv

import pymel.core as pm
import os, shutil
import maya.OpenMaya as OpenMaya
import logging

#import otherTools


# ############
hkIkDict = {"Reference":0,"Hips":1,"LeftUpLeg":2,"LeftLeg":3,"LeftFoot":4,"RightUpLeg":5,"RightLeg":6,"RightFoot":7,"Spine":8,"LeftArm":9,"LeftForeArm":10,"LeftHand":11,"RightArm":12,"RightForeArm":13,"RightHand":14,"Head":15,"LeftToeBase":16,"RightToeBase":17,"LeftShoulder":18,"RightShoulder":19,"Neck":20,"LeftFingerBase":21,"RightFingerBase":22,"Spine1":23,"Spine2":24,"Spine3":25,"Spine4":26,"Spine5":27,"Spine6":28,"Spine7":29,"Spine8":30,"Spine9":31,"Neck1":32,"Neck2":33,"Neck3":34,"Neck4":35,"Neck5":36,"Neck6":37,"Neck7":38,"Neck8":39,"Neck9":40,"LeftUpLegRoll":41,"LeftLegRoll":42,"RightUpLegRoll":43,"RightLegRoll":44,"LeftArmRoll":45,"LeftForeArmRoll":46,"RightArmRoll":47,"RightForeArmRoll":48,"HipsTranslation":49,"LeftHandThumb1":50,"LeftHandThumb2":51,"LeftHandThumb3":52,"LeftHandThumb4":53,"LeftHandIndex1":54,"LeftHandIndex2":55,"LeftHandIndex3":56,"LeftHandIndex4":57,"LeftHandMiddle1":58,"LeftHandMiddle2":59,"LeftHandMiddle3":60,"LeftHandMiddle4":61,"LeftHandRing1":62,"LeftHandRing2":63,"LeftHandRing3":64,"LeftHandRing4":65,"LeftHandPinky1":66,"LeftHandPinky2":67,"LeftHandPinky3":68,"LeftHandPinky4":69,"LeftHandExtraFinger1":70,"LeftHandExtraFinger2":71,"LeftHandExtraFinger3":72,"LeftHandExtraFinger4":73,"RightHandThumb1":74,"RightHandThumb2":75,"RightHandThumb3":76,"RightHandThumb4":77,"RightHandIndex1":78,"RightHandIndex2":79,"RightHandIndex3":80,"RightHandIndex4":81,"RightHandMiddle1":82,"RightHandMiddle2":83,"RightHandMiddle3":84,"RightHandMiddle4":85,"RightHandRing1":86,"RightHandRing2":87,"RightHandRing3":88,"RightHandRing4":89,"RightHandPinky1":90,"RightHandPinky2":91,"RightHandPinky3":92,"RightHandPinky4":93,"RightHandExtraFinger1":94,"RightHandExtraFinger2":95,"RightHandExtraFinger3":96,"RightHandExtraFinger4":97,"LeftFootThumb1":98,"LeftFootThumb2":99,"LeftFootThumb3":100,"LeftFootThumb4":101,"LeftFootIndex1":102,"LeftFootIndex2":103,"LeftFootIndex3":104,"LeftFootIndex4":105,"LeftFootMiddle1":106,"LeftFootMiddle2":107,"LeftFootMiddle3":108,"LeftFootMiddle4":109,"LeftFootRing1":110,"LeftFootRing2":111,"LeftFootRing3":112,"LeftFootRing4":113,"LeftFootPinky1":114,"LeftFootPinky2":115,"LeftFootPinky3":116,"LeftFootPinky4":117,"LeftFootExtraFinger1":118,"LeftFootExtraFinger2":119,"LeftFootExtraFinger3":120,"LeftFootExtraFinger4":121,"RightFootThumb1":122,"RightFootThumb2":123,"RightFootThumb3":124,"RightFootThumb4":125,"RightFootIndex1":126,"RightFootIndex2":127,"RightFootIndex3":128,"RightFootIndex4":129,"RightFootMiddle1":130,"RightFootMiddle2":131,"RightFootMiddle3":132,"RightFootMiddle4":133,"RightFootRing1":134,"RightFootRing2":135,"RightFootRing3":136,"RightFootRing4":137,"RightFootPinky1":138,"RightFootPinky2":139,"RightFootPinky3":140,"RightFootPinky4":141,"RightFootExtraFinger1":142,"RightFootExtraFinger2":143,"RightFootExtraFinger3":144,"RightFootExtraFinger4":145,"LeftInHandThumb":146,"LeftInHandIndex":147,"LeftInHandMiddle":148,"LeftInHandRing":149,"LeftInHandPinky":150,"LeftInHandExtraFinger":151,"RightInHandThumb":152,"RightInHandIndex":153,"RightInHandMiddle":154,"RightInHandRing":155,"RightInHandPinky":156,"RightInHandExtraFinger":157,"LeftInFootThumb":158,"LeftInFootIndex":159,"LeftInFootMiddle":160,"LeftInFootRing":161,"LeftInFootPinky":162,"LeftInFootExtraFinger":163,"RightInFootThumb":164,"RightInFootIndex":165,"RightInFootMiddle":166,"RightInFootRing":167,"RightInFootPinky":168,"RightInFootExtraFinger":169,"LeftShoulderExtra":170,"RightShoulderExtra":171}
speakAnims = ['speak_jaw_down','speak_jaw_up','speak_mouth_narrow','speak_mouth_wide','speak_mouth_open','speak_mouth_shut','speak_tongue_in','speak_tongue_out']

CHARACTERS_PATH = '/home/zoobe/mixamo/testproject/scenes/characters/'
ASSETS_PATH = '/home/zoobe/mixamo/assets/'
ANIM_LIB_PATH = 'p:/mixamo_character/working_project/data/animLib/'
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
        print 'init'
        pm.loadPlugin('cgfxShader.mll')
        #pm.loadPlugin('zoobe_maya_exporter.mll')
        pm.loadPlugin('fbxmaya.mll')

        self.name = kargs.setdefault('name','MixamoChar')
        self.fbxFile = kargs.setdefault('path')

        self.characterPath = ''
        self.morphFiles = []
        self.backgroundFile = ''
        
        print self.fbxFile, self.name
        pm.mel.eval(' setProject "/home/zoobe/mixamo/testproject/"')
        self.createCharDirectories()
        #self.logger, self.logHdlr = self.createLogger()
        self.processCharacter()


    def createCharDirectories(self):
        print 'Creating directories'
        if os.path.isdir(CHARACTERS_PATH):
            currentCharacters = set(os.listdir(CHARACTERS_PATH))
            if self.name not in currentCharacters:
                if os.path.isdir(os.path.join(CHARACTERS_PATH , '01_default')):
                    
                    shutil.copytree(os.path.join(CHARACTERS_PATH , '01_default'), os.path.join(CHARACTERS_PATH,self.name))
                else:
                    pm.warning('Couldnt find a default character directory to duplicate the structure!!!')

        self.characterPath = ASSETS_PATH + 'characters/' + self.name + '_std/'
        matPath = self.characterPath + 'materials/'
        if not os.path.isdir(self.characterPath):
            os.mkdir(self.characterPath)
        if not os.path.isdir(matPath):
            os.mkdir(matPath)
        
        print 'Directories Created'
            
    def processCharacter(self):
        self.importMixamoFbx()
        
        self.cleanUpAnim()
        self.createCgfxShader()
        self.saveChar(self.name)
        '''
        if(self.importMixamoFbx()):
            
            #self.characterizeChar()
            #self.createCgfxShader()
            #self.addMorphs()
            #self.addShadowPlane()
            #self.scaleChar()
            #merge bind poses
            #reload(otherTools)
            #otherTools.combineBindPoses()

            self.saveChar(self.name)

        else:
            pm.warning('Could not import the FBX file')
        '''
    def importMixamoFbx(self) :
        print 'importMixamoFbx'
        pm.newFile(f=1)
        if self.fbxFile:
            if os.path.isfile(self.fbxFile):

                #import the FBX file
                pm.mel.eval( 'FBXImport -f "' + (self.fbxFile) + '"')
                #clean its namespace
                removeNamespace()
                #self.logger.info('Imported file %s',self.fbxFile)
                hips = pm.ls("Hips",type='joint')

                #add root joint for scale
                rootJnt = pm.joint(n='Root')
                pm.parent(hips[0],rootJnt)
                #self.logger.info('Added root joint %s',rootJnt)

                #clean up textures
                self.cleanUpTextures()
                pm.currentUnit(t='ntsc')
                # add shadow plane

                return 1
            else:
                pm.error('Fbx file %s doesn\'t exist'%self.fbxFile)
                return 0
        else:
            pm.error('No file was given')
            return 0

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
                os.rename(os.path.join(charSourceimages,fileName),os.path.join(charSourceimages,fileName.lower()))

            f.fileTextureName.set('sourceimages\\' + fileName.lower())        

    def cleanUpAnim(self):
        animCurves = pm.ls(type='animCurve')
        pm.delete(animCurves)

    def createCgfxShader(self):
        #get the materials starting from the shaders and looking for connections
        shadersList = [sh.name() for sh in pm.ls(type='shadingEngine')]
        #maya's default shaders, we remove them
        mayaShaders = ['initialParticleSE', 'initialShadingGroup']

        shadersList = set(shadersList) - set(mayaShaders)
        materialList = []

        for sh in shadersList:

            mat = pm.listConnections ('%s.surfaceShader'%sh)[0];
            materialList.append(mat)

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
                normFile = pm.listConnections('%s.normalCamera'%mat)[0]
            except:
                pm.warning('No norm file found')

            #create a cgfx material
            cgfxShader = pm.shadingNode('cgfxShader',asShader=1)
            cgfxShader.rename(mat + '_cgfx')
            cmd = 'cgfxShader -e -fx "'
            
            cmd += CHARACTERS_PATH.replace('scenes/characters','renderData/shaders') + 'zoobeCharacterShader2.cgfx"'
            cmd += cgfxShader.name()
            #assign the zoobe cgfx shader file
            pm.mel.eval(cmd)
            
            self.saveChar(self.name)
            '''
            if diffuseFile:
                #diffuseFile.outColor.connect(cgfxShader.diffuseMapSampler)
                pm.connectAttr('%s.outColor'%diffuseFile.name(),'%s.diffuseMapSampler'%cgfxShader.name())
            
            if specFile:
                specFile.outColor.connect(cgfxShader.specularMapSampler)
            if normFile:
                normFile.outNormal.connect(cgfxShader.normalMapSampler)
            '''
            #get the shaders for the materials 
            shader = pm.listConnections("%s.outColor"%mat)[0]
            print shader 

            #connect the cgfx material to the mesh shader
            shader.surfaceShader.disconnect()
            cgfxShader.outColor.connect(shader.surfaceShader)
            #connect the file outColor to the cgfx diffuseMapSampler input

    def saveChar(self,charName):
        print 'saveChar'
        if os.path.isdir(CHARACTERS_PATH):
            currentCharacters = set(os.listdir(CHARACTERS_PATH))
            if charName not in currentCharacters:
                if os.path.isdir(os.path.join(CHARACTERS_PATH , '01_default')):
                    shutil.copytree(os.path.join(CHARACTERS_PATH , '01_default'), os.path.join(CHARACTERS_PATH,charName))
                    mayaFile = os.path.join(CHARACTERS_PATH,charName,'03_rigging','05_approved',charName + '.ma')
                    pm.saveAs(mayaFile)
                else:
                    pm.warning('File not saved, couldnt find a default character directory!!!')
            else:
                mayaFile = os.path.join(CHARACTERS_PATH,charName,'03_rigging','05_approved',charName + '.ma')
                if os.path.isfile(mayaFile):
                    pm.warning('File exists!!!')
                else:
                    pm.saveAs(mayaFile)
'''


    def addShadowPlane(self):
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

        shadowPlaneCgfx = pm.shadingNode('cgfxShader',asShader=1,n='shadowPlane_cgfx')
        cmd = 'cgfxShader -e -fx "'
        cmd += CHARACTERS_PATH.replace('scenes/characters','renderData/shaders') + 'zoobeCharacterShader2.cgfx"'
        cmd += shadowPlaneCgfx.name()
        pm.mel.eval(cmd)    

        shadowPlaneTxt = pm.shadingNode('file',asTexture=1,name='shadowPlane_file')

        shadowPlaneTxt.fileTextureName.set('sourceimages\\groundshadow_diffusecolor.tga')
        shadowPlaneTxt.outColor.connect(shadowPlaneCgfx.diffuseMapSampler)

        pm.select(shadowPlane)
        pm.hyperShade(a=shadowPlaneCgfx)

        #self.logger.info('Added the shadow plane')



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

        #self.logger.info('Characterized the skeleton')





    def exportOgreMesh(self):
        print 'export mesh'
        rigFile = os.path.join(CHARACTERS_PATH,self.name,'03_rigging','05_approved',self.name+ '.ma')
        pm.openFile(rigFile,f=1)
        options = ""


        options += " -outDir \"" + self.characterPath + "\""
        options += " -all"
        options += " -lu pref -scale 1.00"
        options += " -mesh \"" + self.characterPath + self.name + "_std.mesh" + "\""
        # Various mesh options
        #exportVertexNormals
        options += " -n 1"
        #exportVertexBinormals
        options += " -bn 1"
        #exportVertexBoneAssignments
        options += " -v 1"
        #exportTextureCoords
        options += " -t 1"
        #buildTangents
        options += " -tangents TANGENT"
        options += " -preventZeroTangent 100.0"
        #buildEdgesList
        options += " -edges 0" 

        # Material tab options
        # Material file path
        matPath = self.characterPath + 'materials/'

        options += " -mat \"" + matPath + self.name + "_std.material" + "\""

        # Various material options
        options += " -lightOff 0"
        texturePath = ASSETS_PATH + 'textures/characters\\\\'
        options += " -copyTex \"" + texturePath + "\""
        options += " -applyGamma 0"
        options += " -applyScaling 0"

        pm.mel.eval( "ogreExport" + options)
        print ( "ogreExport" + options)





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
        rigFile = os.path.join(CHARACTERS_PATH,self.name,'03_rigging','05_approved',self.name + '.ma')
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
                animationFile = os.path.join(CHARACTERS_PATH,self.name,'07_animation','05_approved',anim + '.ma')
                #self.logger.info('%s created',animationFile)
                pm.saveAs(animationFile,f=1)



    def saveAnimation(self,animFile):
        print 'Saving file'
        start = pm.playbackOptions(q=1,ast=1)
        end = pm.playbackOptions(q=1,aet=1)
        length = int(end - start)
        saveName = animFile.replace('lib',self.name) + '_' + str(length) + '.ma'
        pm.playbackOptions(aet = end-1)
        animationFile = os.path.join(CHARACTERS_PATH,self.name,'07_animation','05_approved',saveName)
        pm.saveAs(animationFile,f=1)
        #self.logger.info('Saved animation as %s ', animationFile)



    def exportAnimation(self):
        exportFolder = ASSETS_PATH + 'characters/' + self.name + '_std/animations/'
        if not os.path.isdir(exportFolder):
            os.mkdir(exportFolder)

        exportAnimationsPath = os.path.join(CHARACTERS_PATH ,self.name,'07_animation','05_approved')
        animFiles = []
        if os.path.isdir(exportAnimationsPath):
            animFiles = [f for f in sorted(os.listdir(exportAnimationsPath)) if f.endswith('.ma') or f.endswith('.mb') ]
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



    def addMorphs(self):
        print 'Adding Morphs'
        fbxPath = os.path.split(self.fbxFile)[0]
        charFiles = [f for f in os.listdir(fbxPath) if f.endswith('.fbx')]

        for f in charFiles:
            if 'morph' in f:
                self.morphFiles.append(f)


        if len(self.morphFiles) > 0:
            rigMesh = [pm.ls(type='mesh')[0].getParent()]
            skinCls = pm.listConnections('%s.inMesh'%rigMesh[0].getShape())[0]      
            self.bsNode = pm.blendShape(rigMesh,name=self.name + '_BS')[0]

            print self.bsNode

            pm.reorderDeformers(skinCls.name(),self.bsNode,rigMesh[0].name())


            for morph in self.morphFiles:
                print morph
                if 'open' in morph:
                    pm.mel.eval( 'FBXImport -f "' + fbxPath + '/' + morph + '"')
                    meshes = set(mesh.getParent() for mesh in pm.ls(type='mesh'))

                    newMesh = list(meshes - set(rigMesh))
                    newMesh[0].rename('Open')

                    pm.blendShape(self.bsNode,e=1,t=(rigMesh[0].name(), 0 , newMesh[0].name(), 1))
                    pm.delete(newMesh)

                elif 'blink' in morph:
                    pm.mel.eval( 'FBXImport -f "' + fbxPath + '/' + morph + '"')
                    meshes = set(mesh.getParent() for mesh in pm.ls(type='mesh'))

                    newMesh = list(meshes - set(rigMesh))
                    newMesh[0].rename('Blink')

                    pm.blendShape(self.bsNode,e=1,t=(rigMesh[0].name(), 1 , newMesh[0].name(), 1))
                    pm.delete(newMesh)

            #self.logger.info('Added blendshapes')
'''

def main():
    fbxFile = argv[1]
    charName = argv[2]

    
    mixamoChar = MixamoCharacter(name = charName,path = fbxFile)
    

