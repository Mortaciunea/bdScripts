def bdcleanForExport():
  
    cmds.select('b_*')
    bones = cmds.ls(sl=True, type='joint')
    minTime = cmds.playbackOptions(q=True,minTime=True)
    maxTime = cmds.playbackOptions(q=True,maxTime=True)
    cmds.bakeResults(bones,simulation=True, t=(minTime,maxTime) )

    constraints = cmds.ls(type='constraint')
    cmds.delete (constraints)


    cmds.delete('*IKHandles')
    cmds.delete('*Controllers')   

bdcleanForExport()