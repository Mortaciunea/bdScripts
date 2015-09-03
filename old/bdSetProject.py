import pymel.core as pm
import os, shutil,platform,fnmatch
import maya.OpenMaya as OpenMaya
import logging

from PySide import QtCore
from PySide import QtGui

from shiboken import wrapInstance

import maya.cmds as cmds
import maya.OpenMayaUI as omui

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)

def getProjects():
    projects = []
    excludeDirs = set(['p:\@Recycle','p:\___-ProjectName-___EMPTY','p:\___-ProjectName-___EMPTY-Copy','p:\___-ProjectName-___NAMING CONVENTIONS','p:\_Export','p:\_to_BACKUP','p:\ogre_export','p:\OLD'])
    for root, dirnames, filenames in os.walk('p:\\'):
        for filename in fnmatch.filter(filenames, 'workspace.mel'):
            projects.append(os.path.abspath(root) + '\n')
            print os.path.abspath(root)
            break
    createProjectsFile(projects)

def createProjectsFile(projectsList):
    with open('p:/projectsList.txt','w') as f:
        f.writelines(projectsList)

    
def createProjectsFile():
    projects = []
    for root, dirnames, filenames in os.walk('src'):
        for filename in fnmatch.filter(filenames, '*.c'):
            matches.append(os.path.join(root, filename))    

class ProjectUI(QtGui.QDialog):

    def __init__(self, parent=maya_main_window()):
        super(ProjectUI, self).__init__(parent)
        self.projectList = []

        self.setWindowTitle("Projects")
        self.setWindowFlags(QtCore.Qt.Tool)

        # Delete UI on close to avoid winEvent error
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.create_layout()
        self.create_connections()

    def create_layout(self):
        self.projects_cb = QtGui.QComboBox()
        self.populateProjects()
        self.setProject_btn = QtGui.QPushButton("Set Project")


        main_layout = QtGui.QVBoxLayout()
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(2)
        main_layout.addWidget(self.projects_cb)
        main_layout.addWidget(self.setProject_btn)
        main_layout.addStretch()

        self.setLayout(main_layout)

    def create_connections(self):
        print 'connections'
        #self.cube_btn.clicked.connect(ProjectUI.make_cube)
        #self.sphere_btn.clicked.connect(ProjectUI.make_sphere)


    def populateProjects(self):
        projectFile = 'p:\projectsList.txt'
        if os.path.isfile(projectFile):
            with open(projectFile,'r') as f:
                for line in f:
                    self.projects_cb.addItem(line.split('\\')[1])
                    self.projectList.append(line)

    @classmethod
    def make_cube(cls):
        cmds.polyCube()

    @classmethod
    def make_sphere(cls):
        cmds.polySphere()



def main():

    # Development workaround for winEvent error when running
    # the script multiple times
    try:
        ui.close()
    except:
        pass

    ui = ProjectUI()
    ui.show()

main()