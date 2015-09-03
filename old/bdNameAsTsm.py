import pymel.core as pm


def bdApplyTsmFormat():
    exportHeadJnt  = pm.ls('export_Head_jnt')[0]
    facialJoints = exportHeadJnt.listRelatives(ad=True,type='joint')
    for facialJnt in facialJoints:
        if ('left' in facialJnt.name()):
            #export_eyelid_outcorner_fleshy_left
            newName = ''
            nameParts = facialJnt.name().replace('_left','').split('_')
            nameParts[1] = 'Left' + nameParts[1].title()
            print nameParts
            for part in nameParts:
                newName = newName + part + '_'

            facialJnt.rename(newName[:-1])
        elif ('right' in facialJnt.name()):
            #export_eyelid_outcorner_fleshy_left
            newName = ''
            nameParts = facialJnt.name().replace('_right','').split('_')
            nameParts[1] = 'Right' + nameParts[1].title()
            print nameParts
            for part in nameParts:
                newName = newName + part + '_'

            facialJnt.rename(newName[:-1])

            
    
bdApplyTsmFormat()