import os, shutil, time
import subprocess
from xml.dom.minidom import Document,parse
from StringIO import StringIO


ASSETS_PATH = 'p:/mixamo_character/assets/'
TEST_ASSETS_PATH = 'd:/Zoobe_SVN/zoobe_engine_2/mixamo/'
PREVIEW_PATH = 'c:/zoobe_engine_2/media_io/mixamo/'
ENGINE_PATH = 'd:/Zoobe_SVN/zoobe_engine_2/bin/Release_Win/'
ENGINE_START_BAT = 'start_test_mixamo.bat'
TEST_PATH = 'd:/Zoobe_SVN/zoobe_testing_server/bin/Release_Win/'
GENERIC_XML = 'mixamo.xml'

class MixamoPreview():
    def __init__(self,*args,**kargs):
        self.name = kargs.setdefault('name','MixamoChar')
        self.charXml = ''
        self.copyAssets()

    def createCharXML(self):
        genericXml = os.path.join(TEST_PATH , GENERIC_XML)
        print genericXml 
        if not genericXml:
            print 'Didn\'t find the generic mixamo xmlm file'
            exit(0)

        charXml = os.path.join(TEST_PATH ,self.name + '.xml')
        #print charXml
        #shutil.copy(genericXml, charXml)

        dom = parse(genericXml)

        charNode = dom.getElementsByTagName('char')
        for node in charNode :
            node.setAttribute('assetPath',self.name + '_std')


        skinNode  = dom.getElementsByTagName('skin')
        for node in skinNode :
            node.setAttribute('assetPath',self.name + '_basic')

        animNode  = dom.getElementsByTagName('animation')
        for node in animNode :
            parent = node.parentNode
            parent.removeChild(node)

        animationList = []
        animFolder = os.path.join(TEST_ASSETS_PATH,'characters',self.name + '_std','animations')
        print animFolder
        if os.path.isdir(animFolder):
            animationList = [f.split('.')[0] for f in os.listdir(animFolder) if f.endswith('.skeleton') and 'speak' not in f]
        else:
            print 'No skeleton file'
            exit(0)

        startTime = 0

        animationsNode = dom.getElementsByTagName('animations')
        for anim in animationList:
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

    def copyAssets(self):
        #grab character files 
        if os.path.isdir(os.path.join(ASSETS_PATH,'characters')):
            charDir = os.listdir(os.path.join(ASSETS_PATH,'characters'))
            if charDir:
                for folder in charDir:
                    if self.name in folder:
                        try:
                            shutil.copytree(os.path.join(ASSETS_PATH,'characters',folder), os.path.join(TEST_ASSETS_PATH,'characters',folder))
                        except:
                            print('Target files exist!!!')
        #grab texures
        sourceTextureFolder = os.path.join(ASSETS_PATH,'textures','characters')
        if os.path.isdir(sourceTextureFolder ):
            textureFiles = os.listdir(os.path.join(ASSETS_PATH,'textures','characters'))
            destinationFolder = os.path.join(TEST_ASSETS_PATH,'textures','characters')
            if os.path.isdir(destinationFolder):
                for tex in textureFiles:
                    shutil.copy(os.path.join(sourceTextureFolder,tex), os.path.join(destinationFolder,tex)) 
            

    def startJob(self):
        batFile = os.path.join(ENGINE_PATH,ENGINE_START_BAT)
        if os.path.isfile(batFile):
            
            os.chdir(ENGINE_PATH)
            subprocess.Popen(batFile)
            
            time.sleep(5)
            mixamoJobFile = os.path.join(TEST_PATH,'mixamo.bat')
            
            self.editMixamoJobFile()
            os.chdir(TEST_PATH)
            time.sleep(2)
            subprocess.call(mixamoJobFile)
            

    
    def editMixamoJobFile(self):
        mixamoJobFile = os.path.join(TEST_PATH,'mixamo.bat')
        if os.path.isfile(mixamoJobFile):
            batFile = open(mixamoJobFile,'r')
            javaCommand = batFile.readline()
            batFile.close()
            # command looks like:  java -cp zbLauncher.jar com.zoobe.Launcher 127.0.0.1 mixamo.xml 2011
            # we replace 'mixamo.xml' ( or whichever string is on that position) with our character name
            tokens = javaCommand.split(' ')
            tokens[-2] = self.name + '.xml'
            newCommand = ''
            for t in tokens:
                newCommand += ( t + ' ')
            batFile = open(mixamoJobFile,'w')
            batFile.write(newCommand)
            batFile.close()
            
            
            