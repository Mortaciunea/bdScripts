import pymel.core as pm
import glob,shutil,os

variation = ['normal', 'fire','ice','poison','lightning','andermight']
size = ['m']
tier = ['tier1','tier2','tier3']



def duplicateAssets():
    path = pm.workspace.name + '/gfxlib/effects/'
    name = 'status_enhancement_'
    
    tempList = glob.glob(path + '*_t*_m.mb')
    
    for fl in tempList:
        path,filename = os.path.split(fl)
        #destFile = filename.replace('_m','_s')
        destFile = filename.replace('_m','_l')
        if(os.path.isfile(os.path.join(path,destFile))):
            pm.warning('File exists!')
            pm.openFile(os.path.join(path,destFile),f=1)
        else:
            shutil.copyfile(fl,os.path.join(path,destFile))
    
            pm.openFile(os.path.join(path,destFile),f=1)
            modelGrp = pm.ls('model')[0]
            #modelGrp.scaleBy((0.5,0.5,0.5))
            modelGrp.scaleBy((3.2,3.2,3.2))
            pm.makeIdentity(modelGrp,apply=True,t=0,r=0,s=1)
            pm.saveAs(os.path.join(path,destFile),f=1)
    
        pm.mel.eval('rlExportGraphicsObjectNoBrowserN3')

def duplicateSequence():
    path = 'd:/drasa_online/work/sequences/statuseffect/'
    #name = 'status_enhancement_'
    
    tempList = glob.glob(path + '*t*_m.xml')
    
    for seq in tempList:
        filepath,filename = os.path.split(seq)
        destFile = filename.replace('_m','_s')
        
        seq = os.path.abspath(seq)
        with open(os.path.join(path,destFile), "wt") as fout:
            with open(seq, "rt") as fin:
                for line in fin:
                    fout.write(line.replace('_m', '_s'))

'''    
for var in variation:
    varName = name + var + '_'
    for t in tier:
        tierName = varName + t + '_'
        for s in size:
            sizeName = tierName + s
            print sizeName
'''