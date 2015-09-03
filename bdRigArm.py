import bdRigUtils
import maya.cmds as cmds


armBones = ['shoulder','elbow','wrist','palm']

def bdBuildDrvChain(side,drvType):
    shoulderJnt = cmds.ls(side + '*' + armBones[0] + '*', type='joint')
    ikChainStart = cmds.duplicate(shoulderJnt[0])[0]
    ikChainStart = cmds.rename(ikChainStart,shoulderJnt[0].replace('bnd',drvType))
    ikRelatives = cmds.listRelatives(ikChainStart, ad=True,type='joint',pa=True)
    ikRelatives.reverse()
    toDelete = ikRelatives[3:]
    cmds.delete(toDelete)
    ikRelatives = ikRelatives[:3]
    ikRelatives.reverse()
    for jnt in ikRelatives:
        cmds.rename(jnt,jnt.split('|')[-1].replace('bnd',drvType))
    return [ikChainStart]

def bdRigIkArm(side):
    ikChainStart = bdBuildDrvChain(side,'ik')
    ikChainJoints = cmds.listRelatives(ikChainStart, ad=True,type='joint')
    ikChainJoints.reverse()
    ikBones = ikChainStart + ikChainJoints
    print ikBones
    armIk = cmds.ikHandle(sol= 'ikRPsolver',sticky='sticky', startJoint=ikBones[0],endEffector = ikBones[2],name = side + '_arm_ikHandle')
    handIk = cmds.ikHandle(sol= 'ikSCsolver',sticky='sticky', startJoint=ikBones[2],endEffector = ikBones[3],name = side + '_hand_ikHandle')
    ikHandlesGrp = cmds.group([armIk[0],handIk[0]],n=side + '_arm_ikHandles_grp')
    wristPos = cmds.xform(ikBones[2],q=True,ws=True,t=True)
    cmds.move(wristPos[0], wristPos[1], wristPos[2], [ikHandlesGrp + '.scalePivot',ikHandlesGrp + '.rotatePivot'])
    pvAnim = cmds.ls(side + '_elbow_ik_anim', type='transform')[0]
    if pvAnim:
        cmds.poleVectorConstraint(pvAnim,armIk[0])
    
    ikAnimCtrl = cmds.ls(side + '_hand_ik_anim',type='transform')[0] 
    cmds.parentConstraint(ikAnimCtrl, ikHandlesGrp)
    
            

def bdRigArm(side,ik=1,fk=0):
    bdRigIkArm(side)
    
    
