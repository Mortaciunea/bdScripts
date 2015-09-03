'''
    File:       lpDynamicChains.py
     
    Author:     Luiz Philippe Moreira
     
    Contact:    lmoreira2012@gmail.com
                luizmoreira2012br.blogspot.com
     
    Versions:   1.0  -  06/28/2013  -  first version created
                1.1  -  07/02/2013  -  changed curve degree to 1 to work with chains with 2 or 3 joints
                                       fixed complete removal of dynamic nodes for delete dynamic
                2.0  -  07/13/2013  -  added create collision object
                2.1  -  08/15/2013  -  updated collision feature and entire tool to use nDynamics and the nucleus solver
                                       unifying all dynamic simulations under one solver
                 
                2.2  -  08/19/2013  -  added option to bake sim onto joint
 
    How to use:
 
        1.     Place script in
                    Windows:    C:/Program Files/Autodesk/Maya2013/Python/lib/site-packages/ 
                    Mac:        Users/yourUserName/Library/Preferences/Autodesk/maya/2013-x64/scripts/
         
        2.   To open the UI:
                    import lpDynamicChains
                    reload(lpDynamicChains)
                    lpDynamicChains.UI()                    
'''
# load libraries to be used
try:
    import maya.cmds as cmds
    import maya.mel
except Exception as e:
    print "Error while loading python modules"
    print "Exception: ", e
 
TITLE = "lpDynamicChains.py"
VERSION = "2.2"
 
WIDTH = 360
HEIGHT = 300
 
#----------------------------------------
# lpDynamicChains - User Interface
#----------------------------------------
def UI():
    '''
    Create UI for tool to create dynamic joint chains
    '''
    # check if window already exists
    if cmds.window("dynamicChainsUI", exists=True):
        cmds.deleteUI("dynamicChainsUI")
     
    # create new window
    cmds.window("dynamicChainsUI", title="%s - v%s" % (TITLE,VERSION), width=WIDTH, height=HEIGHT, menuBar=True, sizeable=True)
     
    # create a help option menu
    cmds.menu(helpMenu=True, l="Help", parent="dynamicChainsUI")
    cmds.menuItem(l="About", c=r"cmds.confirmDialog(messageAlign='left', title='About - " + TITLE + r" - v" + VERSION + r"', message='This tool allows for the creation of a dynamic joint chain.\n\nUser can specify joints to become dynamic, and can also turn any geometry into a collision object.\n\nSimulations can be cached to a file or baked as animation onto joints, and dynamic nods can be removed when done.\n\nSuggested use: for tails, appendages, for secondary delayed movement - ex: jiggle', button=['Close'], defaultButton='Close')")
    cmds.menuItem(l="Author", c=r"cmds.confirmDialog(messageAlign='left', title='Author - " + TITLE + r" - v" + VERSION + r"', message='Luiz Philippe Moreira\n\nRigger and Tools Developer\n\nContact Information:\n\nblog:\thttp://luizmoreira2012br.blogspot.com\nemail:\tlmoreira2012@gmail.com\n\nAny feedback will be very appreciated.', button=['Close'], defaultButton='Close')")
    cmds.menuItem(l="Help", c="import webbrowser\nwebbrowser.open('http://luizmoreira2012br.blogspot.com')")
     
    # create main layout
    main = cmds.columnLayout(adj=True, co=("both", 5), columnAlign="left")
     
    cmds.frameLayout(l="Main", cll=True)
    cmds.columnLayout(adj=True)
     
    cmds.separator(h=10, style="none")
    cmds.button(l="Make Joints Dynamic", c=dynamicChainCmd)
    cmds.button(l="Remove Dynamic", c=removeDynamicCmd)
    cmds.separator(h=10, style="none")
     
    cmds.setParent(main)
     
    cmds.frameLayout(l="Options", cll=True)
    cmds.columnLayout(adj=True)
     
    cmds.separator(h=10, style="none")
    cmds.button(l="Create Collision Object", c=collisionDynamicCmd)
    cmds.separator(h=10, style="none")
     
    cmds.setParent(main)
     
    cmds.frameLayout(l="Advanced", cll=True, cl=True)
    advCol = cmds.columnLayout(adj=True)
     
    cmds.frameLayout(l="nCache", cll=True)
    cmds.columnLayout(adj=True)
     
    cmds.separator(h=10, style="none")
    cmds.button(l="Cache Simulation", c=cacheSimulationCmd)
    cmds.button(l="Delete Cache", c=deleteCacheCmd)
    cmds.separator(h=10, style="none")
     
    cmds.setParent(advCol)
     
    cmds.frameLayout(l="Animation", cll=True)
    cmds.columnLayout(adj=True)
     
    cmds.separator(h=10, style="none")
    cmds.checkBoxGrp("useTimeSliderCBG", l="Use Time Slider: ")
    cmds.separator(h=10, style="none") 
     
    cmds.intFieldGrp("frameRangeIFG", l="Frame Range: ", numberOfFields=2)
     
    cmds.separator(h=10, style="none")
     
    cmds.button(l="Bake Simulation", c=bakeDynamicCmd)
     
    # callbacks
    minTime = int(cmds.playbackOptions(q=True, minTime=True))
    maxTime = int(cmds.playbackOptions(q=True, maxTime=True))
     
    cmds.intFieldGrp("frameRangeIFG", e=True, value1=minTime, value2=maxTime)
    cmds.checkBoxGrp("useTimeSliderCBG", e=True, onc="cmds.intFieldGrp('frameRangeIFG', e=True, en=0)",
                     ofc="cmds.intFieldGrp('frameRangeIFG', e=True, en=1)")
     
    cmds.showWindow("dynamicChainsUI")
 
#----------------------------------------
# lpDynamicChains - UI Commands
#----------------------------------------
 
def dynamicChainCmd(*args):
    '''
    Get information and create dynamic joint chain network
    '''   
    from time import gmtime, strftime
     
    verified = True
    log = ""
         
    # get the selected joints
    joints = cmds.ls(sl=True)
    if len(joints) != 2:
        log += "- Need to select the start joint and the end joint\n"
        verified = False
         
    if verified:
        # create class instance
        dynChain = lpDynamicChain(joints[0], joints[1])
        # create the dynamic network
        nodes = dynChain.create()
         
        if nodes:
            dateTime = strftime("%a, %b %d %Y - %X", gmtime())
            nodesString = ""
            # build string for feedback
            for i,node in enumerate(nodes):
                nodesString += "%d. %s\n" % (i,node) 
             
            cmds.confirmDialog(messageAlign="left", title="lpDynamicChains", message="%s\n------------------\n\nNew dynamic nodes:\n\n%s\n\nThank you!" % (dateTime, nodesString), button=["Accept"], defaultButton="Accept")
         
        # select the custom node last
        cmds.select(dynChain.mNode) 
    else:
        cmds.confirmDialog(messageAlign="left", title="lpDynamicChains", message="Log:\n" + log, button=["Accept"], defaultButton="Accept")
 
def removeDynamicCmd(*args):
    '''
    Find if selected object has a dynamic chain attached to it and delete the dynamic nodes
    '''
    # get selected object
    selected = cmds.ls(sl=True)
    # check if selected is dynamic
    if selected:
        node = ""
        selected = selected[0]
        # create instance
        dynChain = lpDynamicChain()
        # get all dynamic nodes in the scene
        dynChains = dynChain.Iter()
        # check for connections
        conn = cmds.listConnections(selected + ".message")
         
        if selected in dynChains:
            node = selected
        if conn:
            if conn[0] in dynChains:
                node = conn[0]
         
        if node:
            # delete dynamic node
            dynChain = lpDynamicChain(node=node)
            dynChain.delete()
            # delete unused nucleus nodes and unused nRigid nodes
            deleteUnusedNucleusSolvers()
            deleteUnusedNRigidNodes()
            # delete the dynamic chain instance now that we are done
            del(dynChain)
 
def collisionDynamicCmd(*args):
    '''
    Make the selected object a collision object of the dynamic chain
    UPDATED: all dynamics done under the nucleus solver (one solver)
    '''
    # get selected object
    selected = cmds.ls(sl=True)
     
    if selected:
        ''' Need to change this to accept any of the nodes that belongs to the dynamic chain, and look for the dynNode '''
        # manage the dynamic node
        dNode = lpDynamicChain(node=selected[0])
        hair = dNode.hairSystemShape[0]
        nucleus = getConnectedNucleusNode(selected[0])
 
        for i,s in enumerate(selected):
            if i > 0:
                # get the shape for the object to collide
                #shape = cmds.listRelatives(s, shapes=True)[0]
                # create a nRigid node - could also do this via the makeCollideNCloth - but need to be able to track new nodes
                nRigid = createNRigid(s, nucleus)
                #nRigidShape = cmds.listRelatives(nRigid, shapes=True)[0]
                '''
                # connect nodes
                index = findNextAvailableColliderIndex(nucleus)
                cmds.connectAttr(shape + ".worldMesh[0]", nRigid + ".inputMesh")
                cmds.connectAttr(nucleus + ".startFrame", nRigid + ".startFrame")
                cmds.connectAttr(nRigidShape + ".currentState", nucleus + ".inputPassive[%s]" % str(index))
                cmds.connectAttr(nRigidShape + ".startState", nucleus + ".inputPassiveStart[%s]" % str(index))
                cmds.connectAttr("time1.outTime", nRigid + ".currentTime")
                '''
                # add nRigid to the dynamic chain node
                #colliders = findNumberOfCollisionObjects(dNode.mNode)
                #dNode.connectAttr(nRigid, "collider0" + str(colliders + 1))
 
def cacheSimulationCmd(*args):
    '''
    Call for the Create new nCache option window
    '''
    # get selected object
    selected = cmds.ls(sl=True)
     
    nodes = []
     
    if selected:
        for s in selected:
            if isDynamicChain(s):
                # manage the dynamic node
                dNode = lpDynamicChain(node=s)
                # select hair system shape node
                hairShape = dNode.hairSystemShape[0]
                # add it to the list
                nodes.append(hairShape)
     
    # select all nodes
    if nodes:
        cmds.select(nodes, r=True)
        cmds.nClothCacheOpt()
 
def deleteCacheCmd(*args):
    '''
    Call for the Delete nCache option window
    '''
    # get selected object
    selected = cmds.ls(sl=True)
     
    if selected:
        selected = selected[0]
        if isDynamicChain(selected):
            # manage the dynamic node
            dNode = lpDynamicChain(node=selected)
            # select hair system shape node
            hairShape = dNode.hairSystemShape[0]
            cmds.select(hairShape, r=True)
            cmds.nClothDeleteCacheOpt()
 
def bakeDynamicCmd(*args):
    '''
    Bake the dynamic simulation as key frames on the joints rotations for the specified frame range
    '''
    # display warning message
    result = cmds.confirmDialog(messageAlign="left", title="Bake Simulation", message="Baking simulation will replace the dynamics\nfor keyframe animation. Action is undoable. Do you wish to continue?", button=["Yes", "No"])
     
    if result == "Yes":
        # get selected object
        selected = cmds.ls(sl=True)
         
        if selected:
            # manage the dynamic node
            dNode = lpDynamicChain(node=selected[0])
            startJoint = dNode.startJoint[0]
            endJoint = dNode.endJoint[0]
             
            # get frame range
            startFrame = cmds.intFieldGrp("frameRangeIFG", q=True, v1=True)
            endFrame = cmds.intFieldGrp("frameRangeIFG", q=True, v2=True)
             
            if cmds.checkBoxGrp("useTimeSliderCBG", q=True, v1=True):
                startFrame = cmds.playbackOptions(q=True, minTime=True)
                endFrame = cmds.playbackOptions(q=True, maxTime=True)
             
            # get the joints
            joints = [startJoint]
            joints.extend( findAllJointsFromTo(startJoint, endJoint) )
             
        # bake the simulation for the frame range - this action is undoable
        cmds.bakeResults(joints, t=(startFrame, endFrame), dic=False, preserveOutsideKeys=True, simulation=True)
 
 
#----------------------------------------
# lpDynamicChain - Base Class Definition
#----------------------------------------
 
class lpDynamicChain():
    '''
    Base class for dynamic chain node
    '''
    @classmethod
    def Iter(self):
        '''
        Iterates over all dynamic chain nodes in the current scene
        '''
        cmds.select("lpDynamicChain*", r=True)
        for node in cmds.ls(sl=True, type="transform"):
            if isDynamicChain(node):
                yield node
     
    def __init__(self, startJoint="", endJoint="", node=""):
        '''
        Create the custom node
         
        Parameters:
            startJoint         - Name of the first joint in the chain
            endJoint           - Name of the last joint in the chain
            node               - Name of the node to manage by the class
             
        Returns:
            Nothing
        '''
        # to store our custom node
        self.mNode = ""
         
        if startJoint and endJoint:
            # create custom node
            loc = cmds.createNode("locator", name="lpDynamicChainShape1")
            self.mNode = cmds.listRelatives(loc, p=True)[0]
            self.mNode = cmds.rename(self.mNode, "lpDynamicChain1")
             
            # create custom attributes
            cmds.addAttr(self.mNode, ln="nodeType", dt="string")
            cmds.setAttr(self.mNode + ".nodeType", "lpDynamicChain", type="string")
             
            cmds.addAttr(self.mNode, ln="startJoint", at="message")
            cmds.addAttr(self.mNode, ln="endJoint", at="message")
             
            cmds.connectAttr(startJoint + ".message", self.mNode + ".startJoint", f=True)
            cmds.connectAttr(endJoint + ".message", self.mNode + ".endJoint", f=True)
     
            cmds.addAttr(self.mNode, ln="joints", at="message", m=True)
                     
            # get all joints from start to end
            # if nothing is returned, joints are not in the same joint chain - Return
            joints = findAllJointsFromTo(startJoint, endJoint)
            if not joints:
                return None
            joints.pop(-1)
             
            # connect all the joints to the multi attribute 'joints'
            for i,joint in enumerate(joints):
                cmds.connectAttr(joint + ".message", self.mNode + ".joints[%d]" % i)
     
            # create keyable attributes
            cmds.addAttr(self.mNode, ln="stiffness", at="double", min=0, max=1, dv=.1, k=True)
            cmds.addAttr(self.mNode, ln="lengthFlex", at="double", min=0, max=1, dv=0, k=True)
            cmds.addAttr(self.mNode, ln="damp", at="double", min=0, max=100, dv=0, k=True)
            cmds.addAttr(self.mNode, ln="drag", at="double", min=0, max=1, dv=0.1, k=True)
            cmds.addAttr(self.mNode, ln="friction", at="double", min=0, max=1, dv=0.1, k=True)
            cmds.addAttr(self.mNode, ln="gravity", at="double", min=0, max=10, dv=1, k=True)
            cmds.addAttr(self.mNode, ln="turbulenceSettings", at="double", k=True)
            cmds.setAttr(self.mNode + ".turbulenceSettings", lock=True)
            cmds.addAttr(self.mNode, ln="strength", at="double", min=0, max=1, dv=0, k=True)
            cmds.addAttr(self.mNode, ln="speed", at="double", min=0, max=1, dv=0.2, k=True)
            cmds.addAttr(self.mNode, ln="frequency", at="double", min=0, max=1, dv=0.2, k=True)
             
            self.cleanNode()
             
        # if node is provided manage the mNode
        if node:
            # check if it is a dynamic chain node
            if isDynamicChain(node):
                self.mNode = node
 
    def cleanNode(self):
        '''
        Hide unecessary attributes on mNode
        '''
        shape = cmds.listRelatives(self.mNode, shapes=True)[0]
        attrs = ["localPositionX", "localPositionY", "localPositionZ", "localScaleX", "localScaleY", "localScaleZ"]
         
        cmds.parentConstraint(self.startJoint[0], self.mNode)
         
        parent = cmds.listRelatives(self.startJoint[0], p=True)
        if parent:
            cmds.parent(self.mNode, parent[0])
         
        attributeDisplayOptions(shape, attrs, 0, 1)
        attributeDisplayOptions(self.mNode, ["all"], 1, 1)
         
    def __getattr__(self, attr):
        '''
        Overload of the _getattr_ method
         
        Parameters:
            attr         - Name of the attribute on the mNode to get the value or connection for
         
        Returns:
            List of connections or value at the given attribute
        '''
        # check if attribute exists first
        if cmds.attributeQuery(attr, exists=True, node=self.mNode):
            plug = self.mNode + "." + attr
            # find attribute type
            attrType = cmds.getAttr(plug, type=True)
            # return the appropriate connection or value
            if attrType == "message":
                return cmds.listConnections(plug)
            # return a list to keep things consistent
            return [cmds.gettAttr(self.mNode + "." + attr)]
        raise AttributeError("%r object has no attribute %r" % (type(self).__name__, attr))
     
    def connectAttr(self, node, srcAttr, destAttr="message"):
        ''' 
        Wrapper for connecting the attribute on the mNode. For simplicity.
        If the srcAttr doesn't exist, create a message attribute to connect it
             
        Parameters:
            node         - Name of node to connect to the custom node
            srcAttr      - Name of the attribute on the custom node to make the connection at
            destAttr     - Name of the attribute on the node to make the connection at
         
        Returns:
            Nothing
        '''
        # if attribute doesn't exist create the attribute on the mNode
        if not cmds.attributeQuery(srcAttr, exists=True, node=self.mNode):
            cmds.addAttr(self.mNode, ln=srcAttr, at="message")
        try:
            # connect the attributes
            if destAttr != "message":
                cmds.connectAttr(self.mNode + "." + srcAttr, node + "." + destAttr, f=True)
            else:
                cmds.connectAttr(node + ".message", self.mNode + "." + srcAttr, f=True)
        except Exception, e:
            print "Error while connecting attributes"
            print "Exception: ", e
            raise
 
    def create(self):
        '''
        Creates the actual dynamic joint chain node network
      
        Parameters:
            Nothing
             
        Returns:
            List of all new created nodes
        '''
        # save all the nodes in the current scene
        currentNodes = cmds.ls()
         
        # get joints
        startJoint = self.startJoint[0]
        endJoint = self.endJoint[0]
         
        # create the dynamic chain
        dynamicNodes = createDynamicChain(startJoint, endJoint)
        solvers = findAllNucleusSolvers()
        solvers.append("New Solver")
         
        # prompt user for 
        result = cmds.confirmDialog(messageAlign="left", title="Assign Solver", message="Select nucleus to assign to", button=solvers, defaultButton="nucleus1")
         
        # if requested new solver
        if result == "New Solver":
            dynamicNodes["nucleus"] = createNucleus()
         
        elif result != "dismiss":
            dynamicNodes["nucleus"] = result
         
        ikHandle = dynamicNodes["ikHandle"]
        follicle = dynamicNodes["follicle"]
        follicleShape = dynamicNodes["follicleShape"]
        hairSystem = dynamicNodes["hairSystem"]
        hairSystemShape = dynamicNodes["hairSystemShape"]
        dynamicCurve = dynamicNodes["dynamicCurve"]
        dynamicCurveShape = dynamicNodes["dynamicCurveShape"]
        nucleus = dynamicNodes["nucleus"]
         
        dynamicNodes["follicleGrp"] = cmds.listRelatives(follicle, p=True)[0]
        dynamicNodes["curveGrp"] = cmds.listRelatives(dynamicCurve, p=True)[0]
         
        # parent follicle node to the parent of the start joint if its parent ins't world
        # this will put the follicle together with the joint hierarchy so it stays together with it
        parent = cmds.listRelatives(startJoint, p=True)
        if parent:
            cmds.parent(follicle, parent[0])
 
        # connect and set attributes in meta node
        # connect the attributes
        self.connectAttr(follicleShape, "stiffness", "stiffness")
        self.connectAttr(follicleShape, "lengthFlex", "lengthFlex")
        self.connectAttr(follicleShape, "damp", "damp")
        self.connectAttr(hairSystem, "drag", "drag")
        self.connectAttr(hairSystem, "friction", "friction")
        self.connectAttr(hairSystem, "gravity", "gravity")
        self.connectAttr(hairSystem, "strength", "turbulenceStrength")
        self.connectAttr(hairSystem, "speed", "turbulenceSpeed")
        self.connectAttr(hairSystem, "frequency", "turbulenceFrequency")
         
        # find the new nodes that were created - to help with deletion later
        newNodes = cmds.ls()
        for node in currentNodes:
            newNodes.remove(node)
         
        # connect the remaining nodes
        for key in dynamicNodes:
            if key != "nucleus":
                self.connectAttr(dynamicNodes[key], key)
         
        # connect node to nucleus
        connectToNucleus(self.mNode, nucleus)
         
        return newNodes
 
    def listConnections(self):
        '''
        Wrapper to get all connections to the node to message attributes
         
        Parameters:
            Nothing
         
        Returns:
            List of connected nodes to all custom message attributes
        '''
        # to store connections
        connections = []
        # get all attributes
        attrs = cmds.listAttr(self.mNode, ud=True)
        # we only want the message attributes
        for attr in attrs:
            if cmds.getAttr(self.mNode + "." + attr, type=True) == "message":                
                # find connections
                connections.extend(cmds.listConnections(self.mNode + "." + attr))
         
        return connections
 
    def delete(self):
        '''
        Delete all dynamic nodes
        '''
        # check if mNode still exists
        if self.mNode:
            if cmds.objExists(self.mNode):
                # nodes not to delete
                startJoint = self.startJoint
                endJoint = self.endJoint
                joints = self.joints
                # to store nodes to keep
                nodes = []
                for node in [startJoint, endJoint, joints]:
                    nodes.extend(node)
                # get all the connections
                connections = self.listConnections()
                # delete all custom attributes - if any node connected to it is deleted the node is deleted
                # so delete attributes first, then delete nodes to avoid runtime errors
                attrs = cmds.listAttr(self.mNode, ud=True, u=True)
                 
                for attr in attrs:
                    cmds.deleteAttr(self.mNode + "." + attr)
 
                # now lets delete the nodes 
                for conn in connections:
                    if conn not in nodes:
                        # check if node exists to avoid errors
                        if cmds.objExists(conn):
                            cmds.delete(conn)
                 
                # finally delete the mNode
                cmds.delete(self.mNode)
 
#----------------------------------------
# Delete
#----------------------------------------
 
def deleteUnusedNucleusSolvers():
    '''
    Delete all nucleus nodes not being used
      
    Parameters:
        Nothing
      
    Returns:
        List of nucleus node deleted
    '''
    # get all nucleus nodes
    solvers = cmds.ls(type="nucleus")
     
    # list to store nodes to delete
    toDelete = []
     
    for s in solvers:
        conn = cmds.listConnections(s, s=False, d=True)
        if conn:
            if len(conn) <= 1:
                toDelete.append(s)
        else:
            toDelete.append(s)
     
    if toDelete:        
    # delete unused nucleus nodes
        cmds.delete(toDelete)
 
    return toDelete
 
def deleteUnusedNRigidNodes():
    '''
    Delete all nRigid nodes not being used
     
    Parameters:
        Nothing
     
    Returns:
        List of nRigid nodes deleted
    '''
    # get all nRigid ndoes
    nodes = cmds.ls(type="nRigid")
     
    # list to store nodes to delete
    toDelete = []
     
    for n in nodes:
        conn = cmds.listConnections(n, type="nucleus", s=True, d=True)
        n = cmds.listRelatives(n, p=True)[0]
        if conn:
            if len(conn) <= 1:
                toDelete.append(n)
        else:
            toDelete.append(n)
 
    if toDelete:
        # delete unused nRigid nodes
        cmds.delete(toDelete)
     
    return toDelete
 
#----------------------------------------
# Utility Checks
#----------------------------------------
 
def isDynamicChain(node):
    '''
    Look for the identifier to check if node is 'dynamic' 
     
    Parameters:
        node         -  Name of node to check for 'nodeType'
     
    Returns:
        Boolean value if node is dynamic or not, True or False
    '''
    if cmds.attributeQuery("nodeType", exists=True, node=node):
        if cmds.getAttr(node + ".nodeType") == "lpDynamicChain":
            return True
    return False
 
def isNType(node, nodeType):
    '''
    Check if the given node is a nucleus compatible nDynamics node
      
    Parameters:
        node        - Name of node to check for 'NType' compatibility
        nodeType    - Node type to check
      
    Returns:
        Boolean value if node is compatible with nDynamics solver
    '''
    # check if node exists
    if not cmds.objExists(node):
        return False
     
    # check shape
    if cmds.objectType(node) == "transform":
        node = cmds.listRelatives(node, s=True, ni=True, pa=True)[0]
    if cmds.objectType(node) != nodeType:
        return False
     
    return True
 
def findNextAvailableColliderIndex(nucleus):
    '''
    Find number of passive colliders associated with given nucleus node
     
    Parameters:
        nucleus         - Name of nucleus node
     
    Returns:
         Integer of last available index
    '''
    inPassive = cmds.getAttr(nucleus + ".inputPassive", size=True)
    return inPassive
     
def findNumberOfCollisionObjects(node):
    '''
    Find the number of collision objects attached to the node
     
    Parameters:
        node         - Name of the node t o check for collision objects
     
    Returns:
        Integer number of collision objects attached to the node
    '''
    attributes = cmds.listAttr(node)
    colliders = 0
     
    for attr in attributes:
        if "collider" in attr:
            colliders += 1
     
    return colliders
 
def findAllNucleusSolvers():
    '''
    Find all nucleus nodes in the scene
     
    Parameters:
        Nothing
     
    Returns:
        List with names of all nucleus nodes in the scene
    '''
    # get all nucleus nodes
    solvers = cmds.ls(type="nucleus")
    return solvers
 
 
#----------------------------------------
# Get and Set Commands - Active Nucleus
#----------------------------------------
 
def getActiveNucleus():
    '''
    Query the active nucleus node
      
    Parameters:
        Nothing
      
    Returns:
        Name of active nucleus node
    '''
    # get the current active nucleus
    nucleus = maya.mel.eval('getActiveNucleusNode(true,false)')
    return nucleus
 
def setActiveNucleus(nucleus):
    '''
    Set the active nucleus node
      
    Parameters:
        nucleus        - Name of nucleus node to set as current active nucleus
      
    Returns:
        Nothing
    '''
    # check nucleus
    if not isNType(nucleus, "nucleus"):
        raise Exception("Object " + nucleus + " is not a valid nucleus node")
     
    # set active nucleus
    maya.mel.eval('source getActiveNucleusNode')
    maya.mel.eval('setActiveNucleusNode("' + nucleus + '")')
 
 
#----------------------------------------
# Connection Check Commands
#----------------------------------------
 
def getConnectedDynamicChain(node):
    '''
    Look for a valid DynamicChain node connected to the given node
      
    Parameters:
        node             - Name of the node to find connection to DynamicChain
      
    Returns:
        Name of DynamicChain node connected to given node
    '''
     
    # check if node exsits
    if not cmds.objExists(node):
        raise Exception("Object " + node + " does not exists")
     
    # find all DynamicChains nodes in the scene
    dNode =  lpDynamicChain()
    dynChains = dNode.Iter()
     
    # check connections
    conn = cmds.listConnections(node + ".message", s=True, d=True)
     
    if conn:
        if conn[0] in dynChains:
            return conn[0] 
     
    return ""
     
def getConnectedNucleusNode(node):
    '''
    Look for the nucleus node connected to the given node
      
    Parameters:
        node             - Name of the node to find connection to nucleus
      
    Returns:
        Name of the nucleus node connected to the given node
    '''
    # check if node exists
    if not cmds.objExists(node):
        raise Exception("Object " + node + " does not exist")
     
    # check if node is dynamicChain
    if not isDynamicChain(node):
        raise Exception("Object " + node + " is not a valid DynamicChain node")
 
    # check for nucleus connections
    dNode = lpDynamicChain(node=node)
    hair = dNode.hairSystem[0]
     
    hairShape = cmds.listRelatives(hair, shapes=True)[0]
     
    nucleus = cmds.listConnections(hairShape, type="nucleus", s=True)
     
    if nucleus:
        return nucleus[0]
     
    return ""
 
 
#----------------------------------------
# Creation Commands
#----------------------------------------
 
def createNucleus(name="", setActive=True):
    '''
    Create nucleus node
      
    Parameters:
        name             - Name for the new nucleus node
        setActive        - Boolean to set the new nucleus as the current active nucleus
          
    Returns:
        Name of new nucleus node
    '''
    # check name
    if not name:
        name = "nucleus#"
 
    # create nucleus node
    nucleus = cmds.createNode("nucleus", n=name)
    cmds.connectAttr("time1.outTime", nucleus + ".currentTime")
     
    if setActive:
        setActiveNucleus(nucleus)
     
    return nucleus
  
def createNRigid(obj, nucleus=""):
    '''
    Create a nRigig node from the given obj
      
    Parameters:
        obj              - Name of the geo to create nRigid from
        nucleus          - Name of the nucleus to connect nRigid to
          
    Returns:
        Name of new nRigid node
    '''
    # check if object exists
    if not cmds.objExists(obj):
        raise Exception("Object " + obj + " does not exists")
     
    # check shape
    if cmds.objectType(obj) == "transform":
        obj = cmds.listRelatives(obj, s=True, ni=True, pa=True)[0]
    if cmds.objectType(obj) != "mesh":
        raise Exception("Object " + obj + " is not a valid mesh for nRigid")
     
    # check the nucleus
    if nucleus:
        if not isNType(nucleus, "nucleus"):
            cmds.warning("Object " + nucleus + " is not a valid nucleus node. Will use current active nucleus") 
            nucleus = getActiveNucleus()
         
        setActiveNucleus(nucleus)
     
    # check connections for obj - see if is already an nRigid
    conn = cmds.listConnections(obj, type="nRigid", d=True)
    nRigid = ""
     
    if conn:
        nRigid = conn[0]
        # just connect the nRigid to the nucleus
        connectNRigidToNucleus(nRigid, nucleus)
    else:    
        # create nRigid from obj
        cmds.select(obj, r=True)
        nRigidShape = maya.mel.eval('makeCollideNCloth')
        nRigid = cmds.listRelatives(nRigidShape, p=True, pa=True)[0]
 
    return nRigid
 
def createDynamicChain(startJoint, endJoint):
    '''
    Create the dynamic chain nodes and setup the hair system driven joint chain for each connected joint
      
    Parameters:
        startJoint   - Name of the first joint in the chain
        endJoint     - Name of the last joint in the chain
  
    Returns:
        List of created dynamic nodes
    '''
    # to store nodes to return
    returnNodes = {}
     
    # get all joints
    joints = [startJoint]
    joints.extend( findAllJointsFromTo(startJoint, endJoint) )
     
    # to store position of each joint to build curve
    pos = []
     
    for joint in joints:
        pos.append( cmds.xform(joint, q=True, ws=True, rp=True) )
     
    # create CV curve to drive joints - snap CVs at every joint
    curve = cmds.curve(d=1, p=pos) # degree needs to be 1 to avoid curve rebuild errors for chains with 2-3 joints
    cmds.select(curve)
         
    # make the curve dynamic - command only available in MEL
    maya.mel.eval('makeCurvesDynamicHairs 1 0 1;')
             
    # MEL command doesn't return anything for us, so we have to get the new dynamic nodes some other way
    # this will be importing for storing all the nodes so that we can quickly access them later - specially when
    # we need to delete all the dynamic nodes
    follicle = cmds.listConnections(curve + ".worldMatrix[0]", s=False, d=True)[0]
    follicleShape = cmds.listRelatives(follicle, s=True)[0]
     
    hairSystem = cmds.listConnections(follicleShape + ".outHair", s=False, d=True)[0]
    hairSystemShape = cmds.listRelatives(hairSystem, s=True)[0]
     
    dynamicCurve = cmds.listConnections(follicleShape + ".outCurve", s=False, d=True)[0]
    dynamicCurveShape = cmds.listRelatives(dynamicCurve, s=True)[0]
          
    plug = cmds.listConnections(hairSystemShape + ".startFrame", s=True, d=False, p=True)[0]
    nucleus = plug.split(".")[0]
     
    cmds.select(dynamicCurve)
     
    maya.mel.eval('displayHairCurves "current" 1;')
     
    # override the nHair dynamics so the follicle can control the curve dynamics
    cmds.setAttr(follicleShape + ".overrideDynamics", 1)
    cmds.setAttr(follicleShape + ".pointLock", 1) # base only
         
    # create spline IK - no auto curve - we have our own dynamic curve to drive it
    ikHandle = cmds.ikHandle(sj=startJoint, ee=endJoint, solver="ikSplineSolver", curve=dynamicCurve, ccv=False, pcv=False)[0]
     
    # store nodes to return
    returnNodes["ikHandle"] = ikHandle
    returnNodes["dynamicCurve"] = dynamicCurve
    returnNodes["dynamicCurveShape"] = dynamicCurveShape
    returnNodes["follicle"] = follicle
    returnNodes["follicleShape"] = follicleShape
    returnNodes["hairSystem"] = hairSystem
    returnNodes["hairSystemShape"] = hairSystemShape
    returnNodes["nucleus"] = nucleus
     
    return returnNodes
 
#----------------------------------------
# Connection Commands
#----------------------------------------
 
def connectToNucleus(node, nucleus):
    '''
    Connect the given node to the nucleus node
      
    Parameters:
        node             - Name of the node to connect to the nucleus solver
        nucleus          - Name of nucleus solver to connect to
      
    Returns:
        Name of nucleus node (debug)
    '''
    # check nucleus
    if not isNType(nucleus, "nucleus"):
        preNucleusList = cmds.ls(type="nucleus")
     
    # check nDynamics node
    if not isDynamicChain(node):
        raise Exception("Object " + node + " is not a valid DynamicChain node")
     
    dNode = lpDynamicChain(node=node)
    hairShape = dNode.hairSystemShape[0]
     
    # assign node to nucleus solver
    cmds.select(hairShape)
    maya.mel.eval('assignNSolver ' + nucleus)
 
    # rename nucleus node
    if not cmds.objExists(nucleus):
        postNucleusList= cmds.ls(type="nucleus")
        newNucleus = list(set(postNucleusList) - set(preNucleusList))
        if not newNucleus:
            raise Exception("Unable to determine new nucleus node attached to " + node)
        nucleus = cmds.rename(newNucleus[0], nucleus)
 
    cmds.select(nucleus, r=True)
    return nucleus
 
def connectNRigidToNucleus(nRigid, nucleus, newNucleus=True):
    '''
    Connect the given nRigid node to the nucleus node, maintaining prior connections to
    other nucleus nodes
      
    Parameters:
        nRigid         - Name of nRigid node to connect to nucleus
        nucleus        - Name of nucleus node to connect
        newNucleus     - Boolean to create a new nucleus node if the specified nucleus doesn't exist
      
    Returns:
        Integer index of next available passive nRigid for the given nucleus
    '''
    # check nRigid node
    if not isNType(nRigid, "nRigid"):
        raise Exception("Object " + nRigid + " is not a valid nRigid node")
     
    # check nucleus node
    if not isNType(nucleus, "nucleus"):
        if newNucleus:
            nucleus = createNucleus(nucleus)
        else:
            raise Excpetion("Object " + nucleus + " is not a valid nucleus node")
 
    # get the next available index
    index = findNextAvailableColliderIndex(nucleus)
     
    # connect to nucleus
    cmds.connectAttr(nRigid + ".currentState", nucleus + ".inputPassive[" + str(index) + "]")
    cmds.connectAttr(nRigid + ".startState", nucleus + ".inputPassiveStart[" + str(index) + "]")
     
    return index
 
#----------------------------------------
# Extra Commands
#----------------------------------------
 
def attributeDisplayOptions(objects, attrs=[], lock=False, hide=False):
    '''
    Support for locking and hiding attributes
     
    Parameters:
        objects      - List of objects to modify attributes for
        attrs        - List of attribute names to edit
        lock         - Boolean to lock the attribute
        hide         - Boolean to hide the attribute in the channelBox
     
    Returns:
        Nothing
    '''
    if "all" in attrs:
        index = attrs.index("all")
        attrs.pop(index)
        attrs.extend(["t", "r", "s", "v"])
    if "t" in attrs:
        index = attrs.index("t")
        attrs.pop(index)
        attrs.extend(["tx", "ty", "tz"])
    if "r" in attrs:
        index = attrs.index("r")
        attrs.pop(index)
        attrs.extend(["rx", "ry", "rz"])
    if "s" in attrs:
        index = attrs.index("s")
        attrs.pop(index)
        attrs.extend(["sx", "sy", "sz"])
 
    keyable = True
    channelBox = True
     
    if hide:
        keyable = False
        channelBox = False
 
    objectList = []
     
    if type(objects) is list:
        objectList = list(objects)
    else:
        objectList = [objects]
         
    if attrs:
        for obj in objectList:
            for attr in attrs:
                cmds.setAttr(obj + "." + attr, keyable=keyable, channelBox=channelBox, lock=lock)
    else:
        cmds.error("No attributes specified.")
 
 
def findAllJointsFromTo(startJoint, endJoint):
    '''
    Recursive method to get all joints from the start joint to the end joint
      
    Parameters:
        startJoint   - Name of the first joint in the chain
        endJoint     - Name of the last joint in the chain
  
    Returns:
        List of joints from start to end joint
    '''   
    joints = []
    children = cmds.listRelatives(startJoint, c=True)
     
    if children:
        for child in children:
            if cmds.objectType(child) == "joint":
                joints.append(child)
                 
                if child == endJoint:
                    return joints
                else: 
                    joints.extend( findAllJointsFromTo(child,endJoint) )
    return joints