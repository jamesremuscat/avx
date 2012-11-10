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
        self.resize(1024, 768)
        self.centralwidget = QWidget(self)
        self.centralwidget.setGeometry(0, 0, 1024, 768)
        gridlayout = QGridLayout(self.centralwidget)
        
        self.btnDVD = ExpandingButton(self.centralwidget)
        #self.btnDVD.setGeometry(QRect(240, 0, 81, 81))
        gridlayout.addWidget(self.btnDVD, 0, 0)
        
        self.btnCamera1 = ExpandingButton(self.centralwidget)
        gridlayout.addWidget(self.btnCamera1, 0, 1)
        
        self.btnCamera2 = ExpandingButton(self.centralwidget)
        #self.btnCamera2.setGeometry(QRect(80, 0, 81, 81))
        gridlayout.addWidget(self.btnCamera2, 0, 2)
        
        self.btnCamera3 = ExpandingButton(self.centralwidget)
        #self.btnCamera3.setGeometry(QRect(160, 0, 81, 81))
        gridlayout.addWidget(self.btnCamera3, 0, 3)
        
        self.btnExtras = ExpandingButton(self.centralwidget)
        #self.btnExtras.setGeometry(QRect(320, 0, 81, 81))
        gridlayout.addWidget(self.btnExtras, 0, 4)
        
        self.btnVisualsPC = ExpandingButton(self.centralwidget)
        #self.btnVisualsPC.setGeometry(QRect(400, 0, 81, 81))
        gridlayout.addWidget(self.btnVisualsPC, 0, 5)
        
        blank = QWidget(self.centralwidget)
        gridlayout.addWidget(blank, 1, 0, 1, 5)
        
        outputs = QGridLayout()
        
        self.btnProjectors = ExpandingButton(self.centralwidget)
        outputs.addWidget(self.btnProjectors, 0, 1)

        self.btnChurch = ExpandingButton(self.centralwidget)
        outputs.addWidget(self.btnChurch, 1, 0)
        self.btnSpecial = ExpandingButton(self.centralwidget)
        self.btnSpecial.setText("Special")
        outputs.addWidget(self.btnSpecial, 1, 1)
        
        self.btnGallery = ExpandingButton(self.centralwidget)
        outputs.addWidget(self.btnGallery, 2, 0)
        self.btnWelcome = ExpandingButton(self.centralwidget)
        outputs.addWidget(self.btnWelcome, 2, 1)

        self.btnFont = ExpandingButton(self.centralwidget)
        outputs.addWidget(self.btnFont, 3, 0)
        self.btnRecord = ExpandingButton(self.centralwidget)
        outputs.addWidget(self.btnRecord, 3, 1)

        self.btnPCMix = ExpandingButton(self.centralwidget)
        outputs.addWidget(self.btnPCMix, 4, 0)
        self.btnAll = ExpandingButton(self.centralwidget)
        outputs.addWidget(self.btnAll, 4, 1)

        
        outputs.setColumnMinimumWidth(0, 100)
        outputs.setColumnMinimumWidth(1, 100)
        outputs.setColumnStretch(0, 1)
        outputs.setColumnStretch(1, 1)
        
        gridlayout.addLayout(outputs, 1, 6)

        gridlayout.setRowMinimumHeight(1, 500)      
        gridlayout.setRowStretch(0, 1)  
        gridlayout.setRowStretch(1, 5)  
        self.retranslateUi(self)
        QMetaObject.connectSlotsByName(self)

    def retranslateUi(self, VideoSwitcher):
        VideoSwitcher.setWindowTitle(QApplication.translate("VideoSwitcher", "Video Switcher", None, QApplication.UnicodeUTF8))
        self.btnCamera1.setText(QApplication.translate("VideoSwitcher", "Camera 1", None, QApplication.UnicodeUTF8))
        self.btnCamera2.setText(QApplication.translate("VideoSwitcher", "Camera 2", None, QApplication.UnicodeUTF8))
        self.btnCamera3.setText(QApplication.translate("VideoSwitcher", "Camera 3", None, QApplication.UnicodeUTF8))
        self.btnDVD.setText(QApplication.translate("VideoSwitcher", "DVD", None, QApplication.UnicodeUTF8))
        self.btnExtras.setText(QApplication.translate("VideoSwitcher", "Extras", None, QApplication.UnicodeUTF8))
        self.btnVisualsPC.setText(QApplication.translate("VideoSwitcher", "Visuals PC", None, QApplication.UnicodeUTF8))
        self.btnChurch.setText(QApplication.translate("VideoSwitcher", "Church", None, QApplication.UnicodeUTF8))
        self.btnWelcome.setText(QApplication.translate("VideoSwitcher", "Welcome", None, QApplication.UnicodeUTF8))
        self.btnAll.setText(QApplication.translate("VideoSwitcher", "All", None, QApplication.UnicodeUTF8))
        self.btnPCMix.setText(QApplication.translate("VideoSwitcher", "PC Mix", None, QApplication.UnicodeUTF8))
        self.btnGallery.setText(QApplication.translate("VideoSwitcher", "Gallery", None, QApplication.UnicodeUTF8))
        self.btnRecord.setText(QApplication.translate("VideoSwitcher", "Record", None, QApplication.UnicodeUTF8))
        self.btnFont.setText(QApplication.translate("VideoSwitcher", "Font", None, QApplication.UnicodeUTF8))
        self.btnProjectors.setText(QApplication.translate("VideoSwitcher", "Projectors", None, QApplication.UnicodeUTF8))

from PyKDE4.kdeui import KLed
