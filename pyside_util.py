import xml.etree.ElementTree as xml
from cStringIO import StringIO

import PySide.QtCore as QtCore
import PySide.QtGui as QtGui
import pysideuic
import shiboken

import maya.OpenMayaUI

'''
========================================================================
---->  Parse .ui File and Return PySide Class  <----
========================================================================
'''  
def get_pyside_class( ui_file ):
   """
   Pablo Winant
   """

   parsed = xml.parse( ui_file )
   #print parsed
   widget_class = parsed.find( 'widget' ).get( 'class' )
   form_class = parsed.find( 'class' ).text
   #print widget_class, form_class
   with open( ui_file, 'r' ) as f:
      print f
      o = StringIO()
      frame = {}
      try:
         pysideuic.compileUi( f, o, indent = 0 )
      except:
         print 'errroorrrrr'

      pyc = compile( o.getvalue(), '<string>', 'exec' )
      exec pyc in frame
      
      # Fetch the base_class and form class based on their type in the xml from designer
      form_class = frame['Ui_{0}'.format( form_class )]
      base_class = eval( 'QtGui.{0}'.format( widget_class ) )
      
   return form_class, base_class

'''
========================================================================
---->  Nathan Horne's wrapinstance  <----
========================================================================
'''  
def wrapinstance( ptr, base = None ):
   """
   Nathan Horne
   """
   if ptr is None:
      return None
   
   ptr = long( ptr ) #Ensure type
   if globals().has_key( 'shiboken' ):
      if base is None:
         qObj = shiboken.wrapInstance( long( ptr ), QtCore.QObject )
         metaObj = qObj.metaObject()
         cls = metaObj.className()
         superCls = metaObj.superClass().className()
         if hasattr( QtGui, cls ):
            base = getattr( QtGui, cls )
            
         elif hasattr( QtGui, superCls ):
            base = getattr( QtGui, superCls )
            
         else:
            base = QtGui.QWidget
            
      return shiboken.wrapInstance( long( ptr ), base )
   
   elif globals().has_key( 'sip' ):
      base = QtCore.QObject
      
      return sip.wrapinstance( long( ptr ), base )
   
   else:
      return None

'''
========================================================================
---->  Get Maya Window  <----
========================================================================
'''  
def get_maya_window():
   maya_window_util = maya.OpenMayaUI.MQtUtil.mainWindow()
   maya_window = wrapinstance( long( maya_window_util ), QtGui.QWidget )
   return maya_window
