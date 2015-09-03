'''
========================================================================
INSTRUCTIONS::
========================================================================

Unzip files into your script directory.
(Keep pyside_example.py, pyside_util.py, pyside_example_ui.py, and pyside_example.ui together )

Open Maya 2014

# To run .ui file
import pyside_example
pyside_example.show_ui()

# To run compiled .ui file
import pyside_example
pyside_example.show_compiled()

========================================================================
UI TO PYSIDE::
========================================================================

Install PySide

Open command line

Run:
PYTHONLOCATION\python PYTHONLOCATION\pyside-uic.exe SCRIPTLOCATION\pyside_example.ui -o SCRIPTLOCATION\pyside_example.py

========================================================================
---->  Import Modules  <----
========================================================================
'''
import os
import sys

import PySide.QtGui as QtGui

import maya.cmds as cmds

import pyside_util
reload(pyside_util)
import pyside_example_ui

'''
========================================================================
---->  Global Variables  <----
========================================================================
'''
TOOLS_PATH = os.path.dirname( __file__ )
print TOOLS_PATH 
WINDOW_TITLE = 'Environment Tool'
WINDOW_VERTION = 1.0
WINDOW_NAME = 'environment_tool_window'

UI_FILE_PATH = os.path.join( TOOLS_PATH, 'pyside_example.ui' )
UI_OBJECT, BASE_CLASS = pyside_util.get_pyside_class( UI_FILE_PATH )

'''
========================================================================
---->  Create/Connect UI Functionality  <----
========================================================================
'''
class Environment_Tool( BASE_CLASS, UI_OBJECT ):
   def __init__( self, parent = pyside_util.get_maya_window(), *args ):
      
      super( Environment_Tool, self ).__init__( parent )
      self.setupUi( self )
      
      self.setWindowTitle( '{0} {1}'.format( WINDOW_TITLE, str( WINDOW_VERTION ) ) )
      #self.add_path_button.clicked.connect( self.add_path )
      #self.remove_path_button.clicked.connect( self.remove_path )
      
      #self.load_paths()
      self.show()
   '''
   def load_paths( self ):      
      for path in sys.path:
         self.path_list.addItem( path )
         
   def add_path( self ):
      print 'ADD PATH'
		 
   def remove_path( self ):
      print 'REMOVE PATH'
   '''

'''
========================================================================
---->  Show .ui File  <----
========================================================================
'''
def show_ui():
   UI_FILE_PATH = os.path.join( TOOLS_PATH, 'pyside_example.ui' )
   UI_OBJECT, BASE_CLASS = pyside_util.get_pyside_class( UI_FILE_PATH )

   if cmds.window( WINDOW_NAME, exists = True, q = True ):
      cmds.deleteUI( WINDOW_NAME )
      
   Environment_Tool()
  
'''
========================================================================
---->  Show PySide File  <----
========================================================================
''' 
def show_compiled():
   print 'bla1'
   BASE_CLASS = QtGui.QMainWindow
   UI_OBJECT = pyside_example_ui.Ui_environment_tool_window
   print 'bla2'

   if cmds.window( WINDOW_NAME, exists = True, q = True ):
      cmds.deleteUI( WINDOW_NAME )
      
   Environment_Tool()
