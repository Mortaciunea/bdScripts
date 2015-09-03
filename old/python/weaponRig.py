import maya.cmds as cmds
import maya.OpenMaya as OpenMaya

def listOfSelectedEdgesIds():
	"""
	Select edges of polygonal object
	RETURN: list of selected edges ids
	"""
	m_list = OpenMaya.MSelectionList()     # create selectionList
	OpenMaya.MGlobal.getActiveSelectionList( m_list )
	m_listIt = OpenMaya.MItSelectionList( m_list ) 
	m_edgeList = []	
	while not m_listIt.isDone():
		m_path        = OpenMaya.MDagPath()
		m_component   = OpenMaya.MObject()
		m_listIt.getDagPath( m_path, m_component ) 
		if ( not m_component.isNull() ):
			if ( OpenMaya.MFn.kMeshEdgeComponent == m_component.apiType() ):
				m_itEdge = OpenMaya.MItMeshEdge( m_path, m_component )
				while not m_itEdge.isDone():
					m_edgeList.append( m_itEdge.index() )
					m_itEdge.next()				
		m_listIt.next()
	return m_edgeList,len(m_edgeList)
	
	
print listOfSelectedEdgesIds()	