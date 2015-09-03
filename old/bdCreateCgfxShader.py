import pymel.core as pm
import os,shutil,subprocess

'''
Creates cgfx shaders based on the current lambert materials from Mixamo fbx files.


The CGFX shaders are imported from 'p:\happywow\working_project\renderData\' and we have different types: skin, eyes, eyelashes, hair and cloth. They can have versions, with the default being 01. 
The name format for a shader is:
- shader_PPP_VV.ma
where PPP is the part type (skin, eyes, eyelashes, hair , cloth) and VV is the version ( can be 01, 02, 03 ... 10, 12, ... 99)


DEFAULT_SHADERS dictionary keeps the default setting, version 01 for each cgfx shader and it contains pairs (PPP:VV) where PPP and VV are as described above. 

The script also copies the texture files to the current project sourceimages folder and converts the to Jpeg ( if ImageMagic utility is found). If the utility is not found, it keeps the files as PNGs.

Usage:

Open the mixamo fbx file
Run:

import mixamo.bdCreateCgfxShaders as ccs
ccs.createCgfxShader()

or if a different list of shaders needs to be used run:

myShaders = {'skin':'02','cloth':'02','hair':'02','eyes':'01','eyelashes':'02'}

import mixamo.bdCreateCgfxShaders as ccs
ccs.createCgfxShader(shaders)


'''
#holds the default version for each shader type
DEFAULT_SHADERS  = {'skin':'01','cloth':'01','hair':'01','eyes':'01','eyelashes':'01'}

#path to the image converter
convertExe = "c:\\ZoobeTools\\3rd_party_tools\\ImageMagick\\convert.exe"


def createCgfxShader(shaders='',overwrite=1):
    '''
    'Converts' the materials that come with the Mixamo rig to cgfx shader. 
    Parameters:
    - shaders : If no shaders dictionary is defined,  it will use the DEFAULT_SHADERS
    - overwrite : default 1, it will overwrite the files in sourceimages . 
    
    In order not to manually create and assign shaders (which wil not work in maya batch mode), the cgfx materials are imported and assigned via connectiong them to the existing mesh shaders.
    '''
    
    global DEFAULT_SHADERS
    materialList = []
    
    if shaders:
        DEFAULT_SHADERS = shaders

    print 'Create cgfx shaders'
    diffuseFile = specFile = normFile = ''
    #get the materials starting from the shaders and looking for connections
    shadersList = [sh.name() for sh in pm.ls(type='shadingEngine')]
    #maya's default shaders, we will remove them from the list
    mayaShaders = ['initialParticleSE', 'initialShadingGroup']

    shadersList = set(shadersList) - set(mayaShaders)


    
    for sh in shadersList:

        mat = pm.listConnections ('%s.surfaceShader'%sh)[0];
        #cleanup shaders, remove those that are not assigned to a mesh
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
            pm.delete(bumpFile)
        except:
            pm.warning('No norm file found')
        try:
            setRangeNode = pm.listConnections('%s.cosinePower'%mat)[0]
            glossFile = pm.listConnections('%s.valueX'%setRangeNode)[0]
            pm.delete([glossFile,setRangeNode])
        except:
            pm.warning('No spec file found')
        
        cgfxShader = importCgfxShader(mat)

        #connects the file nodes to the cgfx material 
        if diffuseFile:
            diffuseFile.outColor.connect(cgfxShader.diffuseMapSampler)
        if specFile:
            specFile.outColor.connect(cgfxShader.specularMapSampler)
        if normFile:
            normFile.outColor.connect(cgfxShader.normalMapSampler)
            pm.setAttr('%s.Bump'%cgfxShader,5)

        #get the shaders for the materials 
        shader = pm.listConnections("%s.outColor"%mat)[0]


        #connect the cgfx material to the mesh shader
        shader.surfaceShader.disconnect()
        cgfxShader.outColor.connect(shader.surfaceShader)
        print ('Converted -> %s   to -> %s '%(mat,cgfxShader))
        pm.delete(mat)
    
    cleanUpTextures(overwrite)
    createEyelashesShader()


        
def importCgfxShader(material):
    '''
    Based on the material name , the proper cgfx material is imported with the desired version ( default version is 01)
    
    Add more entries for if elif in case more parts are added
    '''
    print material
    shaderFile = ''
    if 'body' in material.name().lower():
        shaderFile = 'shader_skin_' + DEFAULT_SHADERS['skin'] + '.ma'
    elif 'hair' in material.name().lower():
        shaderFile = 'shader_hair_' + DEFAULT_SHADERS['hair'] + '.ma'
    elif 'bottom' in material.name().lower():
        shaderFile = 'shader_cloth_' + DEFAULT_SHADERS['cloth'] + '.ma'
    elif 'glove' in material.name().lower():
        shaderFile = 'shader_cloth_' + DEFAULT_SHADERS['cloth'] + '.ma'
    elif 'hat' in material.name().lower():
        shaderFile = 'shader_cloth_' + DEFAULT_SHADERS['cloth'] + '.ma'
    elif 'shoes' in material.name().lower():
        shaderFile = 'shader_cloth_' + DEFAULT_SHADERS['cloth'] + '.ma'
    elif 'top' in material.name().lower():
        shaderFile = 'shader_cloth_' + DEFAULT_SHADERS['cloth'] + '.ma'
    elif 'eyes' in material.name().lower():
        shaderFile = 'shader_eyes_' + DEFAULT_SHADERS['eyes'] + '.ma'
    elif 'eyewear' in material.name().lower():
        shaderFile = 'shader_cloth_' + DEFAULT_SHADERS['cloth'] + '.ma'

    shaderFile = os.path.join(pm.workspace.name,'renderData',shaderFile)
    print shaderFile
    try:
        pm.importFile(shaderFile,ra=1,mergeNamespacesOnClash=0,namespace="cgfx")
    except:
        pm.error("Didn't find the shader file, aborting")
        return
    

    cgfxShader = pm.ls('cgfx:*',type = 'cgfxShader')[0]

    cgfxSG = pm.ls('cgfx:*',type = 'shadingEngine')[0]
    pm.delete (cgfxSG )
    #cgfxSG.rename(material.name().lower().replace('mat', '_cgfx_SG'))
    
    cgfxShader.rename(material.name().lower().replace('mat', '_shd'))

    removeNamespace()
    return cgfxShader 

def cleanUpTextures(overwrite):
    '''
    Copy the texture files to the sourceimages and converts the names to lower case. If the file exists in sourceimages, it will not be overwriten, delete them manually if needed.
    
    Converts the pngs to jpegs in case ImageMagick utility is found, it not they are kept as PNGs
    '''
    existingTextureFiles = []
    charSourceimages = os.path.join(pm.workspace.name,'sourceimages')
    if os.path.isdir(charSourceimages):
        existingTextureFiles = os.listdir(charSourceimages)
    #print existingTextureFiles 

    #get the texture file nodes
    fList = pm.ls(type='file')

    for f in fList:
        tName = f.fileTextureName.get()
        #get the texture file path and name
        path,fileName = os.path.split (tName)
        #check if its already in sourceimages, if not it will make a copy there and assign the relative path to fileTextureName attr
        if not overwrite:
            print ('Image %s exists and overwrite not enabled, skipping copying'%fileName)
        else:
            try:
                shutil.copy2(tName, charSourceimages)
            except:
                pm.warning("Couldn't copy %s file to source images"%tName)
            
            
            if os.path.isfile(convertExe):
                convertToJpeg(fileName)
                f.fileTextureName.set('sourceimages\\' + fileName.lower().replace('png','jpg'))
                if os.path.isfile(os.path.join(pm.workspace.name,'sourceimages',fileName)):
                    #remove the png file
                    os.remove(os.path.join(pm.workspace.name,'sourceimages',fileName))
            else:
                pm.warning("Didn't find ImageMagick, texture files are kept as png and were not converted to jpeg ")
                f.fileTextureName.set('sourceimages\\' + fileName.lower())


def convertToJpeg(fileName):
    jpegFile = os.path.join(pm.workspace.name,'sourceimages',fileName.lower().replace('png','jpg'))
    if not os.path.isfile(jpegFile):
        print ('%s "%s" "%s"'%(convertExe,os.path.abspath(tName),os.path.abspath(jpegFile)))
        subprocess.call('%s "%s" "%s"'%(convertExe,os.path.abspath(tName),os.path.abspath(jpegFile)))
        #print f.fileTextureName.set('sourceimages\\' + jpegFile.lower())
    else:
        print('Jpeg file %s exists already, conversion skipped'%jpegFile)
            
def copyTexturesToAssets(destination='assets',overwrite=1):
    '''
    Utility function, it will copy the texture files (found through the file nodes) from where they are ( default should be in sourceimages) to the assets texture folder.
    Normally the path is in the format: 
    p:\__char__\assets\textures\characters\
    where __char__ is the name of the character
    Parameters:
    - destination ( default 'assets')
    - overwrite   (default 1)
    
    In order to keep it simple, the destination can be specified just with one name and if none is provided it will default to 'assets'. 
    
    Default usage:
    import mixamo.bdCreateCgfxShaders as bdccs
    bdccs.copyTexturesToAssets()
    
    This will copy the texute files to p:\__char__\assets\textures\characters\ and overwrite them 
    
    For a different destination folder:
    import mixamo.bdCreateCgfxShaders as bdccs
    bdccs.copyTexturesToAssets('assets_sandbox')
    
    
    
    '''
    workspace = pm.workspace.path
    assetsFolder = workspace.replace('working_project','assets')

    #build the texture path
    charactersFolder = os.path.abspath(os.path.join(assetsFolder,'textures/characters'))
    print charactersFolder
    if os.path.isdir(charactersFolder):
        fList = pm.ls(type='file')
        for f in fList:
            tName = os.path.abspath(f.fileTextureName.get())
            path,fileName = os.path.split (tName)
            destFile = os.path.join(charactersFolder,fileName)
            if os.path.isfile(destFile):
                pm.warning('File %s exists already at the destination'%destFile)
                if overwrite:
                    try:
                        shutil.copy2(tName, destFile)
                        print('File %s was overwritten'%destFile)
                    except:
                        pm.warning("Couldn't copy %s file to character assets textures folder"%tName)
                else:
                    pm.warning('File %s was not overwritten'%destFile)
            else:
                try:
                    shutil.copy2(tName, destFile)
                    print('File %s Copied '%destFile)
                except:
                    pm.warning("Couldn't copy %s file to character assets textures folder"%tName)
                





def createEyelashesShader():
    '''
    Creates the eyelashes shader, will be the only shader with a png file assigned to it 
    '''
    shaderFile = 'shader_eyelashes_' + DEFAULT_SHADERS['eyelashes'] + '.ma'
    shaderFile = os.path.join(pm.workspace.name,'renderData',shaderFile)
    try:
        pm.importFile(shaderFile,ra=1,mergeNamespacesOnClash=0,namespace="cgfx")
    except:
        pm.error("Didnt find eyelashes file")
        return

    cgfxShader = pm.ls('cgfx:*',type = 'cgfxShader')[0]
    cgfxSG = pm.ls('cgfx:*',type = 'shadingEngine')[0]

    
    eyelashes = pm.ls('*Eyelashes')[0]
    pm.select(eyelashes)
    command = "sets -e -forceElement " + cgfxSG;
    pm.mel.eval(command)

    #pm.sets( e=True, forceElement= cgfxSG )
    
    removeNamespace()
     
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