import random 
import pymel.core as pm

def animateHeartJnt(heartJnt,timeOffset=0):
    offsetMin = 0.005
    offsetMax = 0.015
    animLength=30
    pos = heartJnt.getTranslation(space='world')
    pos1 = [pos.x + random.uniform(offsetMin,offsetMax) , pos.y,pos.z]
    pos2 = [pos.x  , pos.y - random.uniform(offsetMin,offsetMax) ,pos.z]
    #pos3 = [pos.x - random.uniform(offsetMin,offsetMax) , pos.y - random.uniform(offsetMin,offsetMax) ,pos.z]
    '''
    pm.setKeyframe(heartJnt,attribute='translateX',t=0,value=pos[0])
    pm.setKeyframe(heartJnt,attribute='translateX',t=animLength/4,value=pos1[0])
    pm.setKeyframe(heartJnt,attribute='translateX',t=2*animLength/4,value=pos1[0])
    pm.setKeyframe(heartJnt,attribute='translateX',t=3*animLength/4,value=pos[0])
    pm.setKeyframe(heartJnt,attribute='translateX',t=animLength,value=pos[0])
    '''
    pm.setKeyframe(heartJnt,attribute='translateY',t=timeOffset,value=pos[1])
    pm.setKeyframe(heartJnt,attribute='translateY',t=timeOffset + animLength/2,value=pos2[1])
    #pm.setKeyframe(heartJnt,attribute='translateY',t=2*animLength/4,value=pos2[1])
    #pm.setKeyframe(heartJnt,attribute='translateY',t=3*animLength/4,value=pos2[1])
    pm.setKeyframe(heartJnt,attribute='translateY',t=timeOffset + animLength,value=pos[1])
    
def animateHearts():
    heartJoints = pm.ls('rig:heart*jnt')
    for heart in heartJoints:
        jntNum = random.randint(0,int(heart.name().split('_')[2]))
        animateHeartJnt(heart,jntNum)

animateHearts()

    