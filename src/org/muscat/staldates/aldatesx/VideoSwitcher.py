# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/VideoSwitcher.ui'
#
# Created: Sat Nov 10 00:10:27 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PySide.QtGui import *
from PySide.QtCore import *

class ExpandingButton(QPushButton):
    def __init__(self, others):
        super(ExpandingButton, self).__init__(others)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

class VideoSwitcher(QWidget):
    def __init__(self):
        super(VideoSwitcher, self).__init__()
        self.setupUi(self)
        
    def setupUi(self, VideoSwitcher):
        self.setWindowTitle("Video Switcher")
        self.resize(1024, 768)
        self.centralwidget = QWidget(self)
        self.centralwidget.setGeometry(0, 0, 1024, 768)
        gridlayout = QGridLayout(self.centralwidget)
        
        self.btnDVD = ExpandingButton(self.centralwidget)
        self.btnDVD.setText("DVD")
        gridlayout.addWidget(self.btnDVD, 0, 0)
        
        self.btnCamera1 = ExpandingButton(self.centralwidget)
        self.btnCamera1.setText("Camera 1")
        gridlayout.addWidget(self.btnCamera1, 0, 1)
        
        self.btnCamera2 = ExpandingButton(self.centralwidget)
        self.btnCamera2.setText("Camera 2")
        gridlayout.addWidget(self.btnCamera2, 0, 2)
        
        self.btnCamera3 = ExpandingButton(self.centralwidget)
        self.btnCamera3.setText("Camera 3")
        gridlayout.addWidget(self.btnCamera3, 0, 3)
        
        self.btnExtras = ExpandingButton(self.centralwidget)
        self.btnExtras.setText("Extras")
        gridlayout.addWidget(self.btnExtras, 0, 4)
        
        self.btnVisualsPC = ExpandingButton(self.centralwidget)
        self.btnVisualsPC.setText("Visuals PC")
        gridlayout.addWidget(self.btnVisualsPC, 0, 5)
        
        blank = QWidget(self.centralwidget)
        gridlayout.addWidget(blank, 1, 0, 1, 5)
        
        outputs = QGridLayout()
        
        self.btnProjectors = ExpandingButton(self.centralwidget)
        self.btnProjectors.setText("Projectors")
        outputs.addWidget(self.btnProjectors, 0, 1)

        self.btnChurch = ExpandingButton(self.centralwidget)
        self.btnChurch.setText("Church")
        outputs.addWidget(self.btnChurch, 1, 0)
        self.btnSpecial = ExpandingButton(self.centralwidget)
        self.btnSpecial.setText("Special")
        outputs.addWidget(self.btnSpecial, 1, 1)
        
        self.btnGallery = ExpandingButton(self.centralwidget)
        self.btnGallery.setText("Gallery")
        outputs.addWidget(self.btnGallery, 2, 0)
        self.btnWelcome = ExpandingButton(self.centralwidget)
        self.btnWelcome.setText("Welcome")
        outputs.addWidget(self.btnWelcome, 2, 1)

        self.btnFont = ExpandingButton(self.centralwidget)
        self.btnFont.setText("Font")
        outputs.addWidget(self.btnFont, 3, 0)
        self.btnRecord = ExpandingButton(self.centralwidget)
        self.btnRecord.setText("Record")
        outputs.addWidget(self.btnRecord, 3, 1)

        self.btnPCMix = ExpandingButton(self.centralwidget)
        self.btnPCMix.setText("PC Mix")
        outputs.addWidget(self.btnPCMix, 4, 0)
        self.btnAll = ExpandingButton(self.centralwidget)
        self.btnAll.setText("All")
        outputs.addWidget(self.btnAll, 4, 1)
        
        outputs.setColumnMinimumWidth(0, 100)
        outputs.setColumnMinimumWidth(1, 100)
        outputs.setColumnStretch(0, 1)
        outputs.setColumnStretch(1, 1)
        
        gridlayout.addLayout(outputs, 1, 6)

        gridlayout.setRowMinimumHeight(1, 500)      
        gridlayout.setRowStretch(0, 1)  
        gridlayout.setRowStretch(1, 5)  
        QMetaObject.connectSlotsByName(self)
