from pyfbsdk import *
import os


capcomJoints = ['Waist','LLeg1','LLeg2','LFoot','RLeg1','RLeg2','RFoot','Stomach','LArm1','LArm2','LhandRot','RArm1','RArm2','RhandRot','LToe','RToe','LShoulder','RShoulder','Neck','Head']
mobuNames  = ['Hips','LeftUpLeg','LeftLeg','LeftFoot','RightUpLeg','RightLeg','RightFoot','Spine','LeftArm','LeftForeArm','LeftHand','RightArm','RightForeArm','RightHand','LeftToeBase','RightToeBase','LeftShoulder','RightShoulder','Neck','Head']

character = FBCharacter('Blanka')

i=0
for jnt in capcomJoints:
    obj = FBFindModelByLabelName(jnt)
    print obj.Name
    linkName = mobuNames[i] + 'Link'
    linkProperty = character.PropertyList.Find(linkName)
    linkProperty.append(obj)
    print linkProperty.Name
    i+=1
    
if not character.SetCharacterizeOn(1):
    errorMessage = character.GetCharacterizeError()
    FBMessageBox('Characterization Error!', errorMessage, 'OK')
