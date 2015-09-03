import os
import pymel.core as pm
import csv
import rig_v2.ogreExporter as ex 


def bdReadCSV(csvFile,char):
    with open(csvFile,'rb') as file:
        contents = csv.reader(file)
        matrix = list()
        for row in contents:
            matrix.append(row)
        
    for r in matrix:
        if char.lower() in r[1].lower():
            index = matrix.index(r)
            rigPath = matrix[index][3]
            rigFile = matrix[index][2]
            if os.path.isfile(rigPath + '/' + rigFile):
                pm.openFile(rigPath + '/' + rigFile,f=1)
                meshPath = matrix[index][7]
                meshFile = matrix[index][6]
                meshFilePath = meshPath + '/' + meshFile
                if os.path.isfile(meshFilePath + '.mesh'):
                    os.rename(meshFilePath + '.mesh', meshFilePath + '_old.mesh')
                osMeshExport(meshPath,meshFile)
            else:
                pm.error('Didnt find the rig file %s'%rigFile)

#from Oleg 
def osMeshExport(outDir,fileName):
    me = ex.OgreMeshExporter()
    

    me.setOutDir(outDir)
    me.setFileName(fileName)

    me.setExportAll(1)
    
    me.setVtxNormals(1)
    me.setVtxBinormals(1)
    me.setVtxBone(1)
    me.setTangents(1)
    me.setTexCoord(1)
    me.setBuildEdges(0)

    me.setLightOff(0)
    me.setGammaCorr(0)
    me.setCopyTex(0)
    me.setScaleTex(0)

    me.doExport()

"""
def bdGetMeshFile():
    sceneName =  pm.sceneName()
    buff = sceneName.split('/')
    mayaFile = buff[-1]
    assetsPath = buff[0] + '/'+ buff[1] + '/assets/characters/'
    if os.path.isdir(assetsPath):
        for dirpath, dirnames, filenames in os.walk(assetsPath):
            if 'animations' in dirpath or 'materials' in dirpath:
                continue
            elif filenames:
                bdFindMesh(dirpath,mayaFile)


def bdFindMesh(dirpath,mayaFile):
    print dirpath
    print mayaFile
"""    