
import sip,os, math
import maya.OpenMayaUI as mui
import maya.OpenMaya as om
import pymel.core as pm
import logging
from functools import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic

pyqtLoggers = ['PyQt4.uic.properties','PyQt4.uic.uiparser']

for log in pyqtLoggers:
	logger = logging.getLogger(log)
	logger.setLevel(logging.ERROR)

def getMayaWindow():
	ptr = mui.MQtUtil.mainWindow()
	return sip.wrapinstance(long(ptr), QObject)

charUIFile = os.path.join(os.path.dirname(__file__), 'bdCharUI.ui')

try:
	charUI_form,charUI_base = uic.loadUiType(charUIFile)
except:
	print 'Could not find the UI file'

class bdCharUIWindow(charUI_form,charUI_base):
	def __init__(self, parent=getMayaWindow()):
		super(bdCharUIWindow, self).__init__(parent)
		self.setupUi(self)
		
		self.scene = QGraphicsScene()
		self.charUI_graphicsView.setScene(self.scene)
		
		
		imagePath = os.path.join(os.path.dirname(__file__), 'kid.jpg')
		charBgImage = QImage(imagePath)
		
    
		self.charUI_graphicsView.setBackgroundBrush(QBrush(charBgImage))
		#self.charUI_graphicsView.setCacheMode(QGraphicsView.CacheBackground)
		self.charUI_graphicsView.setDragMode(QGraphicsView.ScrollHandDrag )
		self.charUI_graphicsView.setSceneRect(0, 0, charBgImage.width(), charBgImage.height())
		self.charUI_graphicsView.resize(charBgImage.width(),charBgImage.height())
		
		self.charUI_graphicsView.wheelEvent = self.charUI_graphicsView_wheelEvent


	def charUI_graphicsView_wheelEvent(self, event):
		factor = 1.41 ** ((event.delta()*.5) / 240.0)
		
		curScaleFactor = self.charUI_graphicsView.matrix().scale(factor,factor).m11() #guesstimate the scale by using directly the transformation matrix
		print curScaleFactor
		if ((curScaleFactor < 1) and (event.delta() < 0)) or (curScaleFactor > 1.5):
			return
		self.charUI_graphicsView.scale(factor, factor)			



def bdMain():
	global charUIWindow
	
	try:
		charUIWindow.close()
	except:
		print 'No prev window, opening one'
		pass
	
	charUIWindow = bdCharUIWindow()
	charUIWindow.show()

'''

import sip,os, math
import maya.OpenMayaUI as mui
import maya.OpenMaya as om
import pymel.core as pm
import logging
from functools import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic

pyqtLoggers = ['PyQt4.uic.properties','PyQt4.uic.uiparser']

for log in pyqtLoggers:
	logger = logging.getLogger(log)
	logger.setLevel(logging.ERROR)

def getMayaWindow():
	ptr = mui.MQtUtil.mainWindow()
	return sip.wrapinstance(long(ptr), QObject)

charUIFile = os.path.join(os.path.dirname(__file__), 'bdCharUI.ui')

try:
	charUI_form,charUI_base = uic.loadUiType(charUIFile)
except:
	print 'Could not find the UI file'

class bdWidget(QWidget):
	def __init__(self, parent=None):
		super(bdWidget, self).__init__(parent)
		
	def dragEnterEvent(self, e):
		print 'dragenterevent'
		e.accept()

	def dropEvent(self, e):
		print 'drop'
		# get the relative position from the mime data
		mime = e.mimeData().text()
		x, y = map(int, mime.split(','))

		if e.keyboardModifiers() & Qt.ShiftModifier:
			# copy
			# so create a new button
			button = Button('Button', self)
			# move it to the position adjusted with the cursor position at drag
			button.move(e.pos()-QPoint(x, y))
			# show it
			button.show()
			# store it
			self.buttons.append(button)
			# set the drop action as Copy
			e.setDropAction(Qt.CopyAction)
		else:
			# move
			# so move the dragged button (i.e. event.source())
			e.source().move(e.pos()-QPoint(x, y))
			# set the drop action as Move
			e.setDropAction(Qt.MoveAction)
			e.source().parent(self)
		# tell the QDrag we accepted it
		e.accept()	

class bdConButton(QPushButton):

	def mouseMoveEvent(self, e):
		print 'babababa'
		if e.buttons() != Qt.MidButton:
			return
		print 'babababa'
		# write the relative cursor position to mime data
		mimeData = QMimeData()
		# simple string with 'x,y'
		mimeData.setText('%d,%d' % (e.x(), e.y()))

		# let's make it fancy. we'll show a "ghost" of the button as we drag
		# grab the button to a pixmap

		pixmap = QPixmap.grabWidget(self)

		# below makes the pixmap half transparent
		painter = QPainter(pixmap)
		painter.setCompositionMode(painter.CompositionMode_DestinationIn)
		painter.fillRect(pixmap.rect(), QColor(0, 0, 0, 127))
		painter.end()

		# make a QDrag
		drag = QDrag(self)
		# put our MimeData
		drag.setMimeData(mimeData)
		# set its Pixmap
		drag.setPixmap(pixmap)
		# shift the Pixmap so that it coincides with the cursor position
		drag.setHotSpot(e.pos())

		# start the drag operation
		# exec_ will return the accepted action from dropEvent
		if drag.exec_(Qt.CopyAction | Qt.MoveAction) == Qt.MoveAction:
			print 'moved'
		else:
			print 'copied'

	def mousePressEvent(self, e):
		QPushButton.mousePressEvent(self, e)
		if e.button() == Qt.LeftButton:
			print 'press'		

class bdCharUIWindow(charUI_form,charUI_base):
	def __init__(self, parent=getMayaWindow()):
		super(bdCharUIWindow, self).__init__(parent)
		self.setupUi(self)

		self.scene = bdGraphicsScene()
		self.charUI_graphicsView.setScene(self.scene)

		imagePath = os.path.join(os.path.dirname(__file__), 'kid.jpg')
		charBgImage = QImage(imagePath)


		self.charUI_graphicsView.setBackgroundBrush(QBrush(charBgImage))
		#self.charUI_graphicsView.setCacheMode(QGraphicsView.CacheBackground)
		self.charUI_graphicsView.setDragMode(QGraphicsView.NoDrag )
		self.charUI_graphicsView.setSceneRect(0, 0, charBgImage.width(), charBgImage.height())
		self.charUI_graphicsView.resize(charBgImage.width(),charBgImage.height())

		self.charUI_graphicsView.wheelEvent = self.charUI_graphicsView_wheelEvent

		
		
		self.testWidget = bdWidget(parent = self.groupBox)
		self.testWidget.setFixedHeight(100)
		
		self.testButton = bdConButton('Test',parent = self.testWidget)
		self.testButton.move(20,10)
		self.testButton.clicked.connect(self.testClicked)

	def charUI_graphicsView_wheelEvent(self, event):
		factor = 1.41 ** ((event.delta()*.5) / 240.0)

		curScaleFactor = self.charUI_graphicsView.matrix().scale(factor,factor).m11() #guesstimate the scale by using directly the transformation matrix
		print curScaleFactor
		if ((curScaleFactor < 1) and (event.delta() < 0)) or (curScaleFactor > 1.5):
			return
		self.charUI_graphicsView.scale(factor, factor)			

	def testClicked(self):
		print 'button clicked'



def bdMain():
	global charUIWindow

	try:
		charUIWindow.close()
	except:
		print 'No prev window, opening one'
		pass

	charUIWindow = bdCharUIWindow()
	charUIWindow.show()
'''

# V03 #

'''
import sip,os, math
import maya.OpenMayaUI as mui
import maya.OpenMaya as om
import pymel.core as pm
import logging
from functools import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic

pyqtLoggers = ['PyQt4.uic.properties','PyQt4.uic.uiparser']

for log in pyqtLoggers:
	logger = logging.getLogger(log)
	logger.setLevel(logging.ERROR)

def getMayaWindow():
	ptr = mui.MQtUtil.mainWindow()
	return sip.wrapinstance(long(ptr), QObject)

charUIFile = os.path.join(os.path.dirname(__file__), 'bdCharUI.ui')

try:
	charUI_form,charUI_base = uic.loadUiType(charUIFile)
except:
	print 'Could not find the UI file'

class bdGraphicsScene(QGraphicsScene):
	def __init__(self, parent=None):
		super(bdGraphicsScene, self).__init__(parent)
		
	def dragEnterEvent(self, e):
		print 'dragenterevent'
		e.accept()

	def dropEvent(self, e):
		print 'drop'
		e.accept()	

class bdConGraphics(QGraphicsRectItem):
	def __init__(self, parent=None):
		super(bdConGraphics, self).__init__(parent)
		self.setPen(QPen(Qt.black))
		self.setBrush(QBrush(Qt.green))
		self.setRect(QRectF(0,0,20,20))
		#self.setFlags((QGraphicsItem.ItemIsMovable))
	
	def mousePressEvent(self,event):
		if (event.button() == Qt.MiddleButton):
			self.setFlag(QGraphicsItem.ItemIsMovable)
	


class bdCharUIWindow(charUI_form,charUI_base):
	def __init__(self, parent=getMayaWindow()):
		super(bdCharUIWindow, self).__init__(parent)
		self.setupUi(self)

		self.scene = bdGraphicsScene()
		self.charUI_graphicsView.setScene(self.scene)

		imagePath = os.path.join(os.path.dirname(__file__), 'kid.jpg')
		charBgImage = QImage(imagePath)


		self.charUI_graphicsView.setBackgroundBrush(QBrush(charBgImage))
		#self.charUI_graphicsView.setCacheMode(QGraphicsView.CacheBackground)
		self.charUI_graphicsView.setDragMode(QGraphicsView.ScrollHandDrag )
		self.charUI_graphicsView.setSceneRect(0, 0, charBgImage.width(), charBgImage.height())
		self.charUI_graphicsView.resize(charBgImage.width(),charBgImage.height())

		self.charUI_graphicsView.wheelEvent = self.charUI_graphicsView_wheelEvent

		
		self.scene.addItem(bdConGraphics())

	def charUI_graphicsView_wheelEvent(self, event):
		factor = 1.41 ** ((event.delta()*.5) / 240.0)

		curScaleFactor = self.charUI_graphicsView.matrix().scale(factor,factor).m11() #guesstimate the scale by using directly the transformation matrix
		print curScaleFactor
		if ((curScaleFactor < 1) and (event.delta() < 0)) or (curScaleFactor > 1.5):
			return
		self.charUI_graphicsView.scale(factor, factor)			

	def testClicked(self):
		print 'button clicked'



def bdMain():
	global charUIWindow

	try:
		charUIWindow.close()
	except:
		print 'No prev window, opening one'
		pass

	charUIWindow = bdCharUIWindow()
	charUIWindow.show()

'''