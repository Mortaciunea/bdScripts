import pymel.core as pm

def bdRenameForMobu():
    exportSpineJoints = ['export_Spine_influence1','export_Spine_influence2','export_Spine_influence3','export_Spine_influence4','export_Spine_influence5','export_Spine_influence6','export_Spine_influence7','export_Head_influence1','export_Head_influence2','export_Head_influence3']
    mobuSpineJoints = ['Hips','Spine','Spine1','Spine2','Spine3','Spine4','Spine5','Neck','Neck1','Head']
    exportArmJoints = ['export_LeftArm_influence1','export_LeftArm_influence2','export_LeftArm_influence3_intermediate','export_LeftArm_influence5','export_LeftArm_influence7_intermediate_constrain','export_LeftArm_influence9','export_LeftArm_influence11_intermediate_constrain']
    mobuArmJoints = ['LeftShoulder','LeftShoulderExtra','LeftArm','LeftArmRoll','LeftForeArm','LeftForeArmRoll','LeftHand']
    exportLegJoints = ['export_LeftLeg_influence1_intermediate','export_LeftLeg_influence3','export_LeftLeg_influence5_intermediate_constrain','export_LeftLeg_influence7','export_LeftLeg_influence9_intermediate','export_LeftLeg_influence12_intermediate']
    mobuLegJoints = ['LeftUpLeg','LeftUpLegRoll','LeftLeg','LeftLegRoll','LeftFoot','LeftToeBase']
    
    bdRenameChain(exportSpineJoints,mobuSpineJoints)
    bdRenameChain(exportArmJoints,mobuArmJoints)
    bdRenameChain(exportArmJoints,mobuArmJoints,'Right')
    bdRenameChain(exportLegJoints,mobuLegJoints)
    bdRenameChain(exportLegJoints,mobuLegJoints,'Right')

def bdRenameChain(chain1, chain2,side=''):
    if side == '':
        for i in range(len(chain1)):
            pm.rename(chain1[i],chain2[i])
    elif side == 'Right':
        for i in range(len(chain1)):
            pm.rename(chain1[i].replace('Left','Right'),chain2[i].replace('Left','Right'))



bdRenameForMobu()