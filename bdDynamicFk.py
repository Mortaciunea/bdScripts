import pymel.core as pm
import pymel.core.datatypes as dt

class bdDynamicChain():
    def __init__(self, *args, **kargs):
        
        self.segments = kargs.setdefault('segments')
        self.start = kargs.setdefault('start')
        self.end = kargs.setdefault('end')
        
        self.fkControllers = []
        self.buildChains(self.start,self.end,self.segments)
    
    @property
    def _segments(self):
        return self.segments
    
    @_segments.setter
    def _segments(self,value):
        self.segments = value
    
    def buildChains(self, start, end, segments):
        startPos = start.getTranslation(space = 'world')
        startPosVector = dt.Vector(startPos) 
        endPos = end.getTranslation(space = 'world')
        endPosVector = dt.Vector(endPos)
        
        totalLength = (endPosVector - startPosVector).length()
        print totalLength
        
        pm.select(clear=True)
        startJoint = pm.joint(p=startPos)
        endJoint = pm.joint(p=endPos)
        pm.joint(startJoint,e=True,zso = True, oj = 'xyz',sao='yup')
        
        
    
selection = pm.ls(sl = True)    
dynFk = bdDynamicChain(segments=3,start=selection[0],end=selection[1])

print dynFk._segments
dynFk._segments = 5
print dynFk._segments        