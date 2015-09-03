import maya.OpenMaya as om
import maya.cmds as cmds
global cb_all

bdAnimControls = [ "left_arm_ikfk_anim" ]
bdAttrs = [ "IKFK" ] 


def bdAddCallbacks():
    global cb_all
    cb_all = []    
    
    for ctrl in bdAnimControls:
        mObj = bdGetObj( ctrl )
        if ( mObj ):
            try:
                cb_all.append( om.MNodeMessage.addAttributeChangedCallback( mObj, bdAddCB )  )
                print "Callback Added for Node %s" %mObj
            except:
                print "Error while adding Callback"
             

def bdAddCB( msg, plug1, plug2, clientData ):
    """
    Callback main function
    """
    if ( 2056 == msg ):
        if ( "left_arm_ikfk_anim.IKFK" == plug1.name() ):
            om.MGlobal.executeCommand( "bdMatchIKFK(\"left_arm_ikfk\")" )
          

def mainREM():
    for cb in cb_all:
        try:
            om.MMessage.removeCallback( m_cb )
            print "Callback Removed"  
        except:
            print "Error while removing Callback"

def bdGetObj( ctrl ):
    selectionList = om.MSelectionList()
    obj = om.MObject() 
    try:            
        selectionList.add(ctrl)               
        selectionList.getDependNode(0, obj)
    except:
        return None
    return obj

bdAddCallbacks()