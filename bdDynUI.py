import functools

import maya.cmds as cmds

import maya.OpenMayaUI as mui
from PyQt4 import QtCore, QtGui
import sip

def getMayaWindow():
    '''
    Get the maya main window as a QMainWindow instance
    '''
    ptr = mui.MQtUtil.mainWindow()
    return sip.wrapinstance(long(ptr), QtCore.QObject)

class PolyShapeMaker(QtGui.QWidget):
    '''
    A custom widget for adding poly shapes to Maya
    '''
    def __init__(self, parent=None):
        '''
        Initialize
        '''
        super(PolyShapeMaker, self).__init__(parent)

        ########################################################################
        #Create Widgets
        ########################################################################
        #: A QCheckBox for enabling/disabling this widget
        self.enableCheckbox = QtGui.QCheckBox(parent=self)

        #: A QComboBox (i.e., drop-down menu) for displaying the possible shape
        #: types.
        self.shapeTypeCB = QtGui.QComboBox(parent=self)

        #: A QLineEdit (i.e., input text box) for allowing the user to specify
        #: a name for the new shape.
        self.nameLE = QtGui.QLineEdit('newShape', parent=self)

        #: A descriptive label for letting the user know what his current settings
        #: will do.
        self.descLabel = QtGui.QLabel("This is a description", parent=self)

        #: A remove button
        self.removeButton = QtGui.QPushButton("Remove", parent=self)

        ########################################################################
        #Populate and format the widgets as necessary
        ########################################################################
        #Make sure the enableCheckbox is checked initially
        self.enableCheckbox.setChecked(True)

        #Add the desired options to our shape type combo box
        self.shapeTypeCB.addItems(['Sphere', 'Cube', 'Cylinder', 'Cone', 'Plane', 'Torus', 'Pyramid', 'Pipe'])

        ########################################################################
        #Layout the widgets
        ########################################################################
        actionLayout = QtGui.QBoxLayout(QtGui.QBoxLayout.LeftToRight)
        actionLayout.setSpacing(5)
        actionLayout.addWidget(self.enableCheckbox)
        actionLayout.addSpacing(-5)
        actionLayout.addWidget(self.shapeTypeCB)
        actionLayout.addWidget(self.nameLE, 1)
        actionLayout.addWidget(self.removeButton)

        self.layout = QtGui.QBoxLayout(QtGui.QBoxLayout.TopToBottom, self)
        self.layout.setSpacing(5)
        self.layout.addLayout(actionLayout)
        self.layout.addWidget(self.descLabel)

        ########################################################################
        #Add connections so that things happen when the user makes changes to the
        #different widgets
        ########################################################################
        #Set up a signal to call the updateDescription method whenever the user
        #changes the shapeTypeCB
        self.connect(self.shapeTypeCB, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateDescription)

        #Set up a signal to call the updateDescription method whenever the text
        #in the nameLE is changed.
        self.connect(self.nameLE, QtCore.SIGNAL("textChanged(const QString&)"), self.updateDescription)

        ########################################################################
        #Trigger an update of the description label for the starting condition
        ########################################################################
        self.updateDescription()

    def updateDescription(self):
        '''
        Update the descriptive label. This method gets called when either the
        shapeTypeCB or nameLE get modified by the user.
        '''
        description = 'Make a %s named "%s"' % (self.shapeTypeCB.currentText(), self.nameLE.text())
        self.descLabel.setText(description)

################################################################################
#Main Dialog
################################################################################
class CustomWidgetDialog(QtGui.QDialog):
    '''
    Dialog for demoing custom PyQt Widget development.
    '''
    def __init__(self, parent=getMayaWindow()):
        '''
        Initialize the window
        '''
        super(CustomWidgetDialog, self).__init__(parent)

        #Window initial size
        self.resize(320, 150)

        #Window title
        self.setWindowTitle("PyQt Demo w/ Custom Widgets")
        #: Store the PolyShapeMaker widgets in this array
        self.pShapeMakers = []        
        
        ########################################################################
        #Create widgets
        ########################################################################
        #: A button for adding new PolyShapeMakers
        self.addShapeButton = QtGui.QPushButton("Add Poly Shape", parent=self)

        #: A button for when the user is ready to make all the new shapes
        self.makeButton = QtGui.QPushButton("Make Shapes", parent=self)

        #: A descriptive label letting the user know how many poly shapes will be
        #: created.
        self.descCountLabel = QtGui.QLabel("Make 0 shapes.", parent=self)
        ########################################################################
        #Add connections for the buttons
        ########################################################################
   
        #Connect the addShapeButton to the addShape method
        self.connect(self.addShapeButton, QtCore.SIGNAL("clicked()"), self.addShape)        
        ########################################################################
        #Layout the widgets
        ########################################################################
        addShapeLayout = QtGui.QBoxLayout(QtGui.QBoxLayout.LeftToRight)

        #Explicitly specify the outer margins of the layout
        addShapeLayout.setContentsMargins(5, 0, 0, 5)

        addShapeLayout.addWidget(self.descCountLabel, 1)
        addShapeLayout.addWidget(self.addShapeButton)

        #Separate the makeButton into its own layout so that we can
        #better control its width.
        makeLayout = QtGui.QBoxLayout(QtGui.QBoxLayout.LeftToRight)
        makeLayout.setContentsMargins(0, 5, 0, 0)
        makeLayout.addStretch(1)
        makeLayout.addWidget(self.makeButton)

        self.layout = QtGui.QBoxLayout(QtGui.QBoxLayout.TopToBottom, self)
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(5,5,5,5)
        self.layout.addLayout(addShapeLayout)
        self.layout.addLayout(makeLayout)
        self.layout.addStretch(1)
        
        self.addShape()
        
    def addShape(self):
        '''
        Add a polyShapeMaker widget to the UI
        '''
        #Create the widget and append it to our pShapeMakers list
        self.pShapeMakers.append(PolyShapeMaker(parent=self))

        #Insert the widget into the UI
        self.layout.insertWidget(self.layout.count()-2, self.pShapeMakers[-1])        
        
CustomWidgetDialog().show()