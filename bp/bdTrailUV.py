# Author: Bogdan Diaconu

import pymel.core as pm
import functools,os,sys
from maya.OpenMaya import MVector

def createTrail():
    if pm.window('trailUI',ex=1):
        pm.deleteUI('trailUI')
    
    pm.window('trailUI')
    pm.columnLayout(adj=1)
    fsSample = pm.floatSliderGrp('sampleSlider', label='Sample by', cw=(1,70), adj=1, en=1,minValue=0.01, maxValue=100, fieldMinValue=0.01, fieldMaxValue=100,pre=2, field=1, v=1)
    pm.separator (height=4,style="in")
    startFrame = pm.playbackOptions(q=1,min=1)
    currentFrame = pm.currentTime(q=1)
    if currentFrame > startFrame:
        startFrame = currentFrame
    pm.intSliderGrp('startFrameSlider', label='Start frame', cw=(1,70), adj=1, en=1,minValue=0, maxValue=100, fieldMinValue=0, fieldMaxValue=10000, field=1, v=startFrame)
    pm.popupMenu(button=3,pmc = functools.partial(setTime,'start'))
    pm.intSliderGrp('endFrameSlider', label='End frame', cw=(1,70), adj=1, en=1,minValue=0, maxValue=100, fieldMinValue=0, fieldMaxValue=10000, field=1, v=startFrame+30)
    pm.popupMenu(button=3,pmc = functools.partial(setTime,'end'))
    pm.intSliderGrp('trailDivisions', label='Trail divisions', cw=(1,70), adj=1, en=1,minValue=1, maxValue=100, fieldMinValue=1, fieldMaxValue=10000, field=1, v=40)
    pm.separator (height=4,style="in")
    cbUvDistorted = pm.checkBox('cbUV',l='UV distorted',v=1)
    pm.separator (height=4,style="in")
    
    rowBtn = pm.rowColumnLayout(numberOfRows=1)
    pm.button(l='Create Trail',command=functools.partial(createTrailMesh))
    pm.button(l='Rebuil uvs',c=functools.partial(createTrailUv,''))
    pm.button(l='ELP !!!',c=openHelpPage)
    pm.showWindow('trailUI')
    

def setTime(time,*args):
    pm.intSliderGrp(time + 'FrameSlider',e=1,v=pm.currentTime(q=1))
    
def openHelpPage(*args):
    confluenceUrl = 'https://confluence.bigpoint.net/display/drasa/createTrail'
    #scriptName = os.path.basename(__file__).split('.')[0]
    #confluenceUrl += scriptName
    os.startfile(confluenceUrl)
    print "CWD: ",os.getcwd()
    print "Script: ",sys.argv[0]
    print ".EXE: ",os.path.dirname(sys.executable)
    print "Script dir: ", os.path.realpath(os.path.dirname(sys.argv[0]))
    pathname, scriptname = os.path.split(sys.argv[0])
    print "Relative script dir: ",pathname
    print "Script dir: ", os.path.abspath(pathname)    
    
def createTrailMesh(*args):
    startVertices = pm.ls(sl=1,fl=1)
    if len(startVertices) != 2:
        pm.warning('Select 2 vertices to have the width of the trail')
        return
    
    vert1 = startVertices[0]
    vert2 = startVertices[1]

    pathCrv = createCurveFromPoints(vert1,vert2 )
    dirVec = getPlaneDirection(pathCrv)
    tempPoly = createStartPoly(vert1,vert2,dirVec)
    extrudeTrail(tempPoly,pathCrv)
    createTrailUv(tempPoly)
    
def createTrailUv(poly,*args):
    sel = pm.ls(sl=1,type='transform')
    if sel:
        poly=sel[0]
    if poly == '':
        pm.warning('No trail selected / found')
        return
    
    startEdge  = pm.ls(poly+ '.e[0]',fl=1)[0]
    
    edges = pm.polySelectSp(startEdge,ring=1)
    pm.select(cl=1)
    ringEdges = pm.ls(edges,fl=1)
    
    leftSideVtx = []
    rightSideVtx = []

    '''
    for edge in ringEdges[1:-1]:
        sew = pm.polyMapSewMove(edge,nf=10,lps=0, ch=1)
        #pm.delete(sew)
    pm.select(poly)
    norm  = pm.polyNormalizeUV (normalizeType=1 ,preserveAspectRatio=0)
    #pm.delete(norm)
    '''
    for edge in ringEdges:
        vtxs = edge.connectedVertices()
        leftSideVtx.append(vtxs[0])
        rightSideVtx.append(vtxs[1])

    leftLength = getTotalEdgesLength(leftSideVtx)
    #print leftLength
    rightLength = getTotalEdgesLength(rightSideVtx)
    #print rightLength
    
    uvDistorted = pm.checkBox('cbUV',q=1,v=1)

    setPosUv(leftSideVtx,leftLength,'left',uvDistorted)
    setPosUv(rightSideVtx,rightLength,'right',uvDistorted)

    pm.select(poly)
    
def setPosUv(vtxs,length,side,uvDistorted):
    startUv = pm.ls(pm.polyListComponentConversion(vtxs[0],fv=1,tuv=1),fl=1)

    if side == 'left':
        pm.polyEditUV(startUv,r=0,u=0,v=0)
    else:
        pm.polyEditUV(startUv,r=0,u=1,v=0)
    

    for i in range(1,len(vtxs)):
        vtx1Pos = pm.xform(vtxs[i-1],q=1,t=1,ws=1)
        vtx2Pos = pm.xform(vtxs[i],q=1,t=1,ws=1)
        vtx1PosVec = MVector(vtx1Pos[0],vtx1Pos[1],vtx1Pos[2])
        vtx2PosVec = MVector(vtx2Pos[0],vtx2Pos[1],vtx2Pos[2])
        dist = (vtx2PosVec  - vtx1PosVec).length()
        
        factor=0.0
        if uvDistorted:
            factor = dist / length
        else:
            factor = 1.0 / (len(vtxs) - 1)
            
                             
        uv1 = pm.ls(pm.polyListComponentConversion(vtxs[i-1],fv=1,tuv=1),fl=1)
        uv2 = pm.ls(pm.polyListComponentConversion(vtxs[i],fv=1,tuv=1),fl=1)
        uv1Pos = pm.polyEditUV(uv1,q=1)
        uv2Pos = uv1Pos[1] + factor
        if side == 'left':
            pm.polyEditUV(uv2,r=0,u=0,v=uv2Pos)
        else:
            pm.polyEditUV(uv2,r=0,u=1,v=uv2Pos)
        

    
def getTotalEdgesLength(vtxs):
    length = 0
    for i in range(0,len(vtxs)-1):
        vtx1Pos = pm.xform(vtxs[i],q=1,t=1,ws=1)
        vtx2Pos = pm.xform(vtxs[i+1],q=1,t=1,ws=1)
        vtx1PosVec = MVector(vtx1Pos[0],vtx1Pos[1],vtx1Pos[2])
        vtx2PosVec = MVector(vtx2Pos[0],vtx2Pos[1],vtx2Pos[2])
        dist = (vtx2PosVec  - vtx1PosVec).length()
        length += dist
    return length

def getMidPointPos(vert1,vert2):
    vert1Pos = vert1.getPosition(space='world')
    vert2Pos = vert2.getPosition(space='world')
    midPoint = (MVector(vert1Pos) + MVector(vert2Pos))*0.5
    vert3Pos = [midPoint.x,midPoint.y,midPoint.z]
    return vert3Pos

def createCurveFromPoints(vert1,vert2):
    startFrame = pm.intSliderGrp('startFrameSlider',q=1,v=1)
    endFrame  = pm.intSliderGrp('endFrameSlider',q=1,v=1)
    
    points = []
    tempPos = [0,0,0]
    sample = pm.floatSliderGrp('sampleSlider',q=1,v=1)
    for f in drange(startFrame,endFrame+1,sample):
        pm.currentTime(f)
        pos = getMidPointPos(vert1, vert2)
        if pos != tempPos:
            points.append(pos)
        tempPos = pos
    
    crvName = vert1.name().split('.')[0] + '_trail_crv'
    crv = pm.curve(name = crvName, ep=points)
    pm.currentTime(startFrame)
    return crv


def createStartPoly(vert1,vert2,dirVec):
    vert1Pos = vert1.getPosition(space='world')
    vert2Pos = vert2.getPosition(space='world')
    midPos = getMidPointPos(vert1, vert2)
    
    vert1PosVec = MVector(vert1Pos[0],vert1Pos[1],vert1Pos[2])
    vert2PosVec = MVector(vert2Pos[0],vert2Pos[1],vert2Pos[2])
    midPosVec = MVector(midPos[0],midPos[1]+3,midPos[2])

    lengthPlane = (vert1PosVec - vert2PosVec).length()/2
    lengthDir = dirVec.length()
    
    scaleFactor = lengthPlane/lengthDir
    print scaleFactor
    
    dirVec *= scaleFactor
    newVert1Vec = midPosVec + dirVec
    newVert2Vec =  midPosVec + dirVec * (-1)
    
    vert1Pos = [newVert1Vec.x,newVert1Vec.y,newVert1Vec.z]
    vert2Pos = [newVert2Vec.x,newVert2Vec.y,newVert2Vec.z]
    tempPoly = pm.polyCreateFacet(p=[vert1Pos,vert2Pos,midPos])[0]
    return tempPoly

def getPlaneDirection(crv):
    curvePosition = pm.pointOnCurve(crv, pr=0, p=True)
    curveTangent = pm.pointOnCurve(crv, pr=0, tangent=True)
    curvePosVec = MVector(curvePosition[0],curvePosition[1],curvePosition[2])
    curveTangentVec = MVector(curveTangent[0],curveTangent[1],curveTangent[2]).normal()

    yVec = MVector(0,1,0)
    dirVec = yVec ^ curveTangentVec
    return dirVec

def extrudeTrail(poly,crv):
    edge = pm.ls(poly+'.e[0]')
    pm.xform(poly,cp=1)
    polyPos = pm.xform(poly,q=1,rp=1,ws=1)
    
    divisions = pm.intSliderGrp('trailDivisions', q=1,v=1)
    pm.polyExtrudeEdge(edge,ch=1,kft=1,pvx=polyPos[0],pvy=polyPos[1],pvz=polyPos[2],divisions=divisions,inputCurve = crv)
    deleteFace = pm.ls(poly+'.f[0]')
    pm.delete(deleteFace)
    trailName = crv.replace('trail_crv','trail')
    pm.rename(poly,trailName)
    pm.intSliderGrp('trailDivisions',e=1,cc=changeTrailDivisions)

def changeTrailDivisions(*args):
    selection = pm.ls(sl=1)
    trail = ''
    if selection:
        trail = selection[0]
    else:
        pm.warning('Select a trail to change divisions')
        return
    
    try:
        extrudeNode = pm.listHistory(trail,exactType = 'polyExtrudeEdge')[0]
        divisions = pm.intSliderGrp('trailDivisions', q=1,v=1)
        pm.setAttr(extrudeNode + '.divisions',divisions)
        createTrailUv(trail)
        
    except:
        pm.warning('Couild not find an extrude in the history')


        
        
def drange(start, stop, step):
    r = start
    while r < stop:
        yield r
        r += step