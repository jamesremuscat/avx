from PySide.QtGui import QMainWindow, QWidget, QGridLayout, QHBoxLayout, QButtonGroup, QIcon, QMessageBox
from PySide.QtCore import QMetaObject, QSize
from org.muscat.staldates.aldatesx.widgets.Buttons import InputButton, OutputButton, ExpandingButton
from org.muscat.staldates.aldatesx.widgets.Clock import Clock
from org.muscat.staldates.aldatesx.ExtrasSwitcher import ExtrasSwitcher
from org.muscat.staldates.aldatesx.CameraControls import CameraControl
from Pyro4.errors import ProtocolError, NamingError
from org.muscat.staldates.aldatesx.StringConstants import StringConstants

class VideoSwitcher(QMainWindow):
    def __init__(self, controller):
        super(VideoSwitcher, self).__init__()
        self.controller = controller
        self.setupUi()
        
    def setupUi(self):
        self.setWindowTitle("Video Switcher")
        self.resize(1024, 768)
        self.centralwidget = QWidget(self)
        self.centralwidget.setGeometry(0, 0, 1024, 768)
        gridlayout = QGridLayout(self.centralwidget)
        
        ''' Buttons added to inputs should have a numeric ID set equal to their input number on the Aldates main switcher. '''
        self.inputs = QButtonGroup()
        
        inputsGrid = QHBoxLayout()
        
        self.btnDVD = InputButton(self.centralwidget)
        self.btnDVD.setText("DVD")
        inputsGrid.addWidget(self.btnDVD)
        self.inputs.addButton(self.btnDVD, 4)
        self.btnDVD.setIcon(QIcon("/usr/share/icons/Tango/scalable/devices/media-cdrom.svg"))
        self.btnDVD.setIconSize(QSize(64, 64))
        
        self.btnCamera1 = InputButton(self.centralwidget)
        self.btnCamera1.setText("Camera 1")
        inputsGrid.addWidget(self.btnCamera1)
        self.inputs.addButton(self.btnCamera1, 1)
        self.btnCamera1.setIcon(QIcon("/usr/share/icons/Tango/scalable/devices/camera-video.svg"))
        self.btnCamera1.setIconSize(QSize(64, 64))
        
        self.btnCamera2 = InputButton(self.centralwidget)
        self.btnCamera2.setText("Camera 2")
        inputsGrid.addWidget(self.btnCamera2)
        self.inputs.addButton(self.btnCamera2, 2)
        self.btnCamera2.setIcon(QIcon("/usr/share/icons/Tango/scalable/devices/camera-video.svg"))
        self.btnCamera2.setIconSize(QSize(64, 64))
        
        self.btnCamera3 = InputButton(self.centralwidget)
        self.btnCamera3.setText("Camera 3")
        inputsGrid.addWidget(self.btnCamera3)
        self.inputs.addButton(self.btnCamera3, 3)
        self.btnCamera3.setIcon(QIcon("/usr/share/icons/Tango/scalable/devices/camera-video.svg"))
        self.btnCamera3.setIconSize(QSize(64, 64))
        
        self.btnExtras = InputButton(self.centralwidget)
        self.btnExtras.setText("Extras")
        inputsGrid.addWidget(self.btnExtras)
        self.btnExtras.setIcon(QIcon("/usr/share/icons/Tango/scalable/devices/video-display.svg"))
        self.btnExtras.setIconSize(QSize(64, 64))
        self.inputs.addButton(self.btnExtras, 5)
        
        self.btnVisualsPC = InputButton(self.centralwidget)
        self.btnVisualsPC.setText("Visuals PC")
        inputsGrid.addWidget(self.btnVisualsPC)
        self.inputs.addButton(self.btnVisualsPC, 6)
        self.btnVisualsPC.setIcon(QIcon("/usr/share/icons/Tango/scalable/devices/computer.svg"))
        self.btnVisualsPC.setIconSize(QSize(64, 64))
        
        self.btnBlank = InputButton(self.centralwidget)
        self.btnBlank.setText("Blank")
        inputsGrid.addWidget(self.btnBlank)
        self.inputs.addButton(self.btnBlank, 0)
        
        gridlayout.addLayout(inputsGrid, 0, 0, 1, 7)
        
        self.extrasSwitcher = ExtrasSwitcher(self.controller)
        self.blank = QWidget(self)
        gridlayout.addWidget(self.blank, 1, 0, 1, 5)
        
        outputsGrid = QGridLayout()
        
        self.btnProjectors = OutputButton(self.centralwidget, ID=2)
        self.btnProjectors.setText("Projectors")
        outputsGrid.addWidget(self.btnProjectors, 0, 1)

        self.btnChurch = OutputButton(self.centralwidget, ID=4)
        self.btnChurch.setText("Church")
        outputsGrid.addWidget(self.btnChurch, 1, 0)
        self.btnSpecial = OutputButton(self.centralwidget, ID=7)
        self.btnSpecial.setText("Special")
        outputsGrid.addWidget(self.btnSpecial, 1, 1)
        
        self.btnGallery = OutputButton(self.centralwidget, ID=6)
        self.btnGallery.setText("Gallery")
        outputsGrid.addWidget(self.btnGallery, 2, 0)
        self.btnWelcome = OutputButton(self.centralwidget, ID=5)
        self.btnWelcome.setText("Welcome")
        outputsGrid.addWidget(self.btnWelcome, 2, 1)

        self.btnFont = OutputButton(self.centralwidget, ID=3)
        self.btnFont.setText("Font")
        outputsGrid.addWidget(self.btnFont, 3, 0)
        self.btnRecord = OutputButton(self.centralwidget, ID=8)
        self.btnRecord.setText("Record")
        outputsGrid.addWidget(self.btnRecord, 3, 1)

        self.btnPCMix = ExpandingButton(self.centralwidget)
        self.btnPCMix.setText("PC Mix")
        outputsGrid.addWidget(self.btnPCMix, 4, 0)
        self.btnAll = OutputButton(self.centralwidget, ID=0)
        self.btnAll.setText("All")
        outputsGrid.addWidget(self.btnAll, 4, 1)
        
        outputsGrid.setColumnMinimumWidth(0, 100)
        outputsGrid.setColumnMinimumWidth(1, 100)
        outputsGrid.setColumnStretch(0, 1)
        outputsGrid.setColumnStretch(1, 1)
        
        gridlayout.addLayout(outputsGrid, 1, 5, 1, 2)
        
        gridlayout.addWidget(Clock(), 2, 6)

        gridlayout.setRowMinimumHeight(1, 500)      
        gridlayout.setRowStretch(0, 1)  
        gridlayout.setRowStretch(1, 5)  
        QMetaObject.connectSlotsByName(self)
        self.setInputClickHandlers()
        self.setOutputClickHandlers()
        self.configureInnerControlPanels()
        self.gridlayout = gridlayout
        
    def configureInnerControlPanels(self):
        self.panels = [
                       QWidget(), # Blank
                       CameraControl(self.controller, "Camera 1"),
                       CameraControl(self.controller, "Camera 2"),
                       CameraControl(self.controller, "Camera 3"),
                       QWidget(), # DVD - no controls
                       ExtrasSwitcher(self.controller), # Extras
                       QWidget() # Visuals PC - no controls - yet...
                       ]
        
        
    def setInputClickHandlers(self):
        self.btnCamera1.clicked.connect(self.handleInputSelect)
        self.btnCamera2.clicked.connect(self.handleInputSelect)
        self.btnCamera3.clicked.connect(self.handleInputSelect)
        self.btnDVD.clicked.connect(self.handleInputSelect)
        self.btnExtras.clicked.connect(self.handleInputSelect)
        self.btnVisualsPC.clicked.connect(self.handleInputSelect)
        self.btnBlank.clicked.connect(self.handleInputSelect)
        
    def setOutputClickHandlers(self):
        self.btnProjectors.clicked.connect(self.handleOutputSelect)
        self.btnChurch.clicked.connect(self.handleOutputSelect)
        self.btnSpecial.clicked.connect(self.handleOutputSelect)
        self.btnGallery.clicked.connect(self.handleOutputSelect)
        self.btnWelcome.clicked.connect(self.handleOutputSelect)
        self.btnFont.clicked.connect(self.handleOutputSelect)
        self.btnRecord.clicked.connect(self.handleOutputSelect)
        self.btnAll.clicked.connect(self.handleOutputSelect)
        ''' btnPCMix is a special case since that's on a different switcher '''
        
    def handleInputSelect(self):
        inputID = self.inputs.checkedId()
        print "Input selected: " + str(inputID)
        if inputID > 0:
            try:
                self.controller.switch("Preview", inputID, 1)
            except NamingError:
                self.errorBox(StringConstants.nameErrorText)
            except ProtocolError:
                self.errorBox(StringConstants.protocolErrorText)
        self.gridlayout.removeWidget(self.gridlayout.itemAtPosition(1,0).widget())
        for p in self.panels:
            p.hide()
        chosenPanel = self.panels[inputID]
        self.gridlayout.addWidget(chosenPanel, 1, 0, 1, 5)
        chosenPanel.show()
        
    def handleOutputSelect(self):
        outputChannel = self.sender().ID
        inputChannel = self.inputs.checkedId()
        
        if inputChannel == 5:
            self.extrasSwitcher.take()
        try:
            self.controller.switch("Main", inputChannel, outputChannel)
        except NamingError:
            self.errorBox(StringConstants.nameErrorText)
        except ProtocolError:
            self.errorBox(StringConstants.protocolErrorText)
        
    def errorBox(self, text):
        msgBox = QMessageBox()
        msgBox.setText(text)
        msgBox.setIcon(QMessageBox.Critical)
        msgBox.exec_()
        
