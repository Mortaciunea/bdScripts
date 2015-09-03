# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file
#
# Created: Tue Oct 08 21:47:19 2013
#      by: pyside-uic 0.2.15 running on PySide 1.2.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_environment_tool_window(object):
    def setupUi(self, environment_tool_window):
        environment_tool_window.setObjectName("environment_tool_window")
        environment_tool_window.resize(483, 319)
        environment_tool_window.setWindowTitle("")
        self.centralwidget = QtGui.QWidget(environment_tool_window)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.centralwidget)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.path_list = QtGui.QListWidget(self.centralwidget)
        self.path_list.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.path_list.setObjectName("path_list")
        self.verticalLayout.addWidget(self.path_list)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.add_path_line = QtGui.QLineEdit(self.centralwidget)
        self.add_path_line.setObjectName("add_path_line")
        self.horizontalLayout.addWidget(self.add_path_line)
        self.add_path_button = QtGui.QPushButton(self.centralwidget)
        self.add_path_button.setObjectName("add_path_button")
        self.horizontalLayout.addWidget(self.add_path_button)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.remove_path_button = QtGui.QPushButton(self.centralwidget)
        self.remove_path_button.setObjectName("remove_path_button")
        self.verticalLayout.addWidget(self.remove_path_button)
        self.horizontalLayout_2.addLayout(self.verticalLayout)
        environment_tool_window.setCentralWidget(self.centralwidget)
        self.statusbar = QtGui.QStatusBar(environment_tool_window)
        self.statusbar.setObjectName("statusbar")
        environment_tool_window.setStatusBar(self.statusbar)

        self.retranslateUi(environment_tool_window)
        QtCore.QMetaObject.connectSlotsByName(environment_tool_window)

    def retranslateUi(self, environment_tool_window):
        self.add_path_button.setText(QtGui.QApplication.translate("environment_tool_window", "Add Path", None, QtGui.QApplication.UnicodeUTF8))
        self.remove_path_button.setText(QtGui.QApplication.translate("environment_tool_window", "Remove Selected", None, QtGui.QApplication.UnicodeUTF8))

