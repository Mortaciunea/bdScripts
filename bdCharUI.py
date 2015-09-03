
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
		self.moveEnable = False
	
	def keyPressEvent(self,event):
		modifiers = QApplication.keyboardModifiers()
		if modifiers == Qt.ControlModifier:
			print('CTRL')	
			self.moveEnable = True
			
	def keyReleaseEvent(self,event):
		modifiers = QApplication.keyboardModifiers()
		if modifiers == Qt.ControlModifier:
			print('CTRL')	
			#self.moveEnable = False
		
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
		self.setRect(QRectF(50,50,20,20))
		#self.setFlags((QGraphicsItem.ItemIsMovable))
		self.setFlags((QGraphicsItem.ItemIsSelectable))
		self.curentPos = QPointF(self.pos())
		
	def mousePressEvent(self,event):
		modifiers = QApplication.keyboardModifiers()
		if modifiers == Qt.ControlModifier:
			self.setPos(event.scenePos())
			self.setFlag(QGraphicsItem.ItemIsMovable)
	def mouseReleaseEvent(self,event):
		self.curentPos = event.scenePos()
		self.setFlag(QGraphicsItem.ItemIsMovable,False)
	
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
		self.charUI_graphicsView.setDragMode(QGraphicsView.RubberBandDrag )
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