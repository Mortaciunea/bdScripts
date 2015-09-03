import os, shutil, time
import subprocess
from xml.dom.minidom import Document,parse
from StringIO import StringIO
from random import shuffle
import distutils.core


ASSETS_PATH = 'p:/'
TEST_ASSETS_PATH = 'd:/Zoobe_SVN/zoobe_engine_2/test_assets/'
PREVIEW_PATH = 'c:/zoobe_engine_2/media_io/ojob4/'
ENGINE_PATH = 'd:/Zoobe_SVN/zoobe_engine_2/bin/Release_Win/'
ENGINE_START_BAT = 'start_test.bat'
TEST_PATH = 'd:/Zoobe_SVN/zoobe_testing_server/bin/Release_Win/'
GENERIC_XML = 'genericJob.xml'
#GENERIC_BAT = 'genericJob.bat'

class JobPreview():
    def __init__(self,*args,**kargs):
        self.jobId = kargs.setdefault('jobId','')
        self.charPath = kargs.setdefault('path','')
        self.charSkin = kargs.setdefault('skin','')
        self.stageName = kargs.setdefault('stage','')
        self.camera = kargs.setdefault('camera','')
        self.lightset = kargs.setdefault('lightset','')
        self.video = kargs.setdefault('video','')
        self.charJob = kargs.setdefault('jobName','')
        self.animationStyle = kargs.setdefault('animation','')
        self.width = kargs.setdefault('width','640')
        self.height = kargs.setdefault('height','360')
        self.allAnimations = kargs.setdefault('allAnimations','0')
        self.charXml = ''
        self.videoLength = kargs.setdefault('videoLength ','500')

    def createCharXML(self):
        genericXml = os.path.join(TEST_PATH , GENERIC_XML)
        print genericXml 
        if not genericXml:
            print 'Didn\'t find the generic mixamo xml file'
            exit(0)

        charXml = os.path.join(TEST_PATH ,self.charJob + '.xml')
        #print charXml
        #shutil.copy(genericXml, charXml)

        dom = parse(genericXml)

        charNode = dom.getElementsByTagName('char')
        for node in charNode :
            node.setAttribute('assetPath',self.charPath)

        skinNode  = dom.getElementsByTagName('skin')
        for node in skinNode :
            node.setAttribute('assetPath',self.charSkin)
        
        jobIdNode  = dom.getElementsByTagName('job')
        for node in jobIdNode :
            node.setAttribute('id',self.jobId)

        stageNode  = dom.getElementsByTagName('stage')
        for node in stageNode :
            node.setAttribute('assetPath',self.stageName)
            node.setAttribute('camera',self.camera)
            node.setAttribute('lightset',self.lightset)
            node.setAttribute('videoName',self.video)

        charNode = dom.getElementsByTagName('datadestination')
        for node in charNode :
            node.setAttribute('width',self.width)
            node.setAttribute('height',self.height)
            
        animNode  = dom.getElementsByTagName('animation')
        for node in animNode :
            parent = node.parentNode
            parent.removeChild(node)

        animationList = []
        animFolder = os.path.join(TEST_ASSETS_PATH,'characters',self.charPath ,'animations')

        if os.path.isdir(animFolder):
            animationList = [f.split('.')[0] for f in os.listdir(animFolder) if f.endswith('.skeleton') and 'speak' not in f and self.animationStyle in f]
        else:
            print 'No skeleton file'
            exit(0)
        
        renderAnims  = []
        startTime = 0
        print self.allAnimations
        if self.allAnimations == '0':
            entryAnimation = ''
            for anim in animationList:
                if 'entry' in anim:
                    entryAnimation = anim
                    break
            exitAnimation = ''
            for anim in animationList:
                if 'exit' in anim:
                    exitAnimation = anim
                    break
            

            entryDuration = exitDuration  = 0
            if entryAnimation!='':
                entryDuration = int(entryAnimation.split('_')[-1])
            if exitAnimation!='':
                exitDuration = int(exitAnimation.split('_')[-1])
            
            tempList = []
            for anim in animationList:
                if 'entry' not in anim and 'exit' not in anim:
                    tempList.append(anim)
    
            shuffle(tempList)
    
            totalLength = entryDuration + exitDuration
            for anim in tempList:
                animDuration = int(anim.split('_')[-1])
                renderAnims.append(anim)
                if totalLength < (int(self.videoLength) - entryDuration - exitDuration):
                    totalLength += animDuration
                else:
                    break
            
            if entryAnimation != '' and exitAnimation != '':
                renderAnims = [entryAnimation] + renderAnims + [exitAnimation]
    
        else:
            print 'All Animations'
            renderAnims = animationList
            
        animationsNode = dom.getElementsByTagName('animations')
            
        for anim in renderAnims:
            animNode = dom.createElement('animation')
            animNode.setAttribute('assetPath',anim)
            
            duration = anim.split('_')[-1]
            animNode.setAttribute('duration',duration)
            
            animNode.setAttribute('startTime',str(startTime))
            startTime += int(duration)
            
            animNode.setAttribute('timescale','1.0')
            animNode.setAttribute('weight','1.0')
            animationsNode[0].appendChild(animNode)

        outXml = open(charXml,'w')
        dom.writexml(outXml)
        outXml.close()
        print 'Character XML job file created: %s'%charXml

    def copyAssets(self, asset_path):
        if os.path.isdir(os.path.join(asset_path)):
            distutils.dir_util.copy_tree(asset_path, os.path.join(TEST_ASSETS_PATH))
        '''
        #grab character files 
        if os.path.isdir(os.path.join(asset_path,'characters')):
            charDir = os.listdir(os.path.join(asset_path,'characters'))
            if charDir:
                for folder in charDir:
                    if self.charPath in folder:
                        try:
                            shutil.copytree(os.path.join(asset_path,'characters',folder), os.path.join(TEST_ASSETS_PATH,'characters',folder))
                            print 'Character folder copied'
                        except:
                            print('Target files exist!!!')
        #grab texures
        sourceTextureFolder = os.path.join(asset_path,'textures','characters')
        if os.path.isdir(sourceTextureFolder ):
            textureFiles = os.listdir(os.path.join(asset_path,'textures','characters'))
            destinationFolder = os.path.join(TEST_ASSETS_PATH,'textures','characters')
            if os.path.isdir(destinationFolder):
                for tex in textureFiles:
                    shutil.copy(os.path.join(sourceTextureFolder,tex), os.path.join(destinationFolder,tex)) 
                print 'Textures folder copied'
        '''

    def startJob(self):
        batFile = os.path.join(ENGINE_PATH,ENGINE_START_BAT)
        if os.path.isfile(batFile):
            
            os.chdir(ENGINE_PATH)
            subprocess.Popen(batFile)
            
            time.sleep(5)
            genericJobFile = os.path.join(TEST_PATH,'mixamo.bat')
            
            self.editgenericJobFile()
            os.chdir(TEST_PATH)
            time.sleep(2)
            subprocess.call(genericJobFile)
            

    
    def createBatFile(self):
        # command looks like:  java -cp zbLauncher.jar com.zoobe.Launcher 127.0.0.1 mixamo.xml 2011
        # we replace 'mixamo.xml' ( or whichever string is on that position) with our character name
        command = 'java -cp zbLauncher.jar com.zoobe.Launcher 127.0.0.1 ' + self.charJob + '.xml 2011'

        charJobFile = os.path.join(TEST_PATH,self.charJob + '.bat')
        batFile = open(charJobFile,'w')
        batFile.write(command)
        batFile.close()
            
            
            