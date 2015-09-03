import sip,os, math
import maya.OpenMayaUI as mui
import maya.OpenMaya as om
import pymel.core as pm
import logging
from functools import *
import pymel.core.datatypes as dt
from xml.dom.minidom import Document,parse



class bdAnimCon(object):
    def __init__(self):
        self.conName = 'name'
        self.xmlPath = 'c:\\Users\\bogdan_d\\Documents\\bdPyScripts\\controllers\\'
        self.xmlFile = ''


    def bdExportCtrl(self):
        selection = pm.ls(sl=1, type = 'transform')


        if selection:
            if len(selection) ==1:
                cvPos = {}
                toExport = selection[0]
                shape = toExport.getShapes()
                self.xmlFile = toExport.name().replace(toExport.namespace(),'') + '.xml'
                xmlDoc = Document()
                root = xmlDoc.createElement('controller')
                root.setAttribute('name',toExport.name().replace(toExport.namespace(),''))
                xmlDoc.appendChild(root)
                for s in shape:
                    if 'Orig' not in s.name():
                        if s.type() == 'nurbsCurve':
                            node = xmlDoc.createElement('shape')

                            periodic = '0'
                            if s.form() == 'periodic':
                                periodic='1'
                            node.setAttribute('periodic',periodic)
                            degree = s.degree()
                            node.setAttribute('degree',str(degree))

                            cvPos = [ (x.x , x.y, x.z) for x in s.getCVs(space='world')]
                            node.setAttribute('cvs',str(cvPos))
                            knots =  [ k for k in s.getKnots()]
                            node.setAttribute('knots',str(knots))
                            node.setAttribute('name',s.name().replace(toExport.namespace(),''))

                            root.appendChild(node)
                        else:
                            pm.warning('You can only export NURBS curves')
                            break

                attrListNode = xmlDoc.createElement('attributesList')
                udAttr = toExport.listAttr(ud=True)
                for attr in udAttr:
                    attrNode = xmlDoc.createElement('attribute')
                    attrName = attr.name(includeNode=0).replace(toExport.namespace(),'')
                    attrType = attr.type()
                    if attrType == 'enum':
                        dictEnum = attr.getEnums()
                        val = [str(k) for k in dictEnum.keys() ]
                        enumValues = str(val).strip('[]').replace('\'','')
                        attrNode.setAttribute('enumValues',enumValues)
                    attrLocked = attr.get(l=True)
                    attrCB = attr.get(cb=True)
                    attrValue = attr.get()
                    attrMinMax = str(attr.getRange())


                    attrNode.setAttribute('name',attrName)
                    attrNode.setAttribute('type',attrType)
                    attrNode.setAttribute('locked',str(attrLocked))
                    attrNode.setAttribute('channelBox',str(attrCB))
                    attrNode.setAttribute('value',str(attrValue))
                    attrNode.setAttribute('minMax',attrMinMax)

                    attrListNode.appendChild(attrNode)

                root.appendChild(attrListNode)
                f= open(self.xmlPath + self.xmlFile, 'w')
                f.write(xmlDoc.toprettyxml())
                f.close()


            else:
                pm.warning( 'Select only one controller !!!' )
        else:
            pm.warning( 'Select a Nurbs Curve' )


    def bdImportCon(self,con):
        dom = parse(self.xmlPath + con + '.xml')
        controllerNode = dom.getElementsByTagName('controller')
        for node in controllerNode :
            conName =  node.getAttribute('name')
            shapeNodes = node.getElementsByTagName('shape')
            curvesToParent = []
            for s in shapeNodes:
                shapeName = s.getAttribute('name')
                print shapeName 
                shapeCvs = s.getAttribute('cvs')
                pos = [float(pos.strip('[](),')) for pos in shapeCvs.split(" ")]
                reconstructedPos = [(pos[i],pos[i+1],pos[i+2]) for i in range(0,len(pos),3)]

                shapeKnots = s.getAttribute('knots')
                knots = [float(k.strip('[](),')) for k in shapeKnots.split(" ")]
                reconstructedKnots = [k for k in knots]

                shapeDegree = int(s.getAttribute('degree'))
                shapePeriodic = int(s.getAttribute('periodic'))

                curve = pm.curve( p= reconstructedPos , k = reconstructedKnots , d = shapeDegree, per = shapePeriodic)
                curve.rename(shapeName.replace('Shape',''))
                curvesToParent.append(curve)

            parentCurve = curvesToParent[0]
            for curve in curvesToParent[1:]:
                pm.parent(curve.getShape(),parentCurve,r=1,shape=1)
                pm.delete(curve)

            pm.select(cl=1)
            parentCurve.centerPivots()

            atributesList = node.getElementsByTagName('attribute')
            if atributesList:
                for attr in atributesList:
                    attrType = attr.getAttribute('type')
                    attrName = attr.getAttribute('name')
                    attrLocked = attr.getAttribute('locked')
                    attrCB = attr.getAttribute('channelBox')
                    attrVal = attr.getAttribute('value')
                    attrMinMax = attr.getAttribute('minMax')
    
                    if attrType == 'string':
                        pm.addAttr(parentCurve, ln = attrName,dt = attrType )
                        parentCurve.attr(attrName).setLocked(attrLocked)
    
                    else:
                        pm.addAttr(parentCurve, ln = attrName,at = attrType)
                        parentCurve.attr(attrName).setLocked(attrLocked)