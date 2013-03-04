from PySide.QtGui import QMainWindow, QFrame, QLabel, QWidget, QGridLayout, QHBoxLayout, QButtonGroup, QIcon, QMessageBox, QStackedWidget
from PySide.QtCore import QMetaObject, Qt
from org.muscat.staldates.aldatesx.widgets.Buttons import InputButton, OutputButton, ExpandingButton
from org.muscat.staldates.aldatesx.widgets.Clock import Clock
from org.muscat.staldates.aldatesx.ExtrasSwitcher import ExtrasSwitcher
from org.muscat.staldates.aldatesx.CameraControls import CameraControl
from Pyro4.errors import ProtocolError, NamingError
from org.muscat.staldates.aldatesx.StringConstants import StringConstants
from org.muscat.staldates.aldatesx.EclipseControls import EclipseControls
from org.muscat.staldates.aldatesx.widgets.SystemPowerWidget import SystemPowerWidget
import logging

class OutputsHolderPanel(QFrame):
    def __init__(self, parent = None):
        super(OutputsHolderPanel, self).__init__(parent)

class VideoSwitcher(QMainWindow):
    def __init__(self, controller):
        super(VideoSwitcher, self).__init__()
        self.controller = controller
        self.setupUi()
        
    def setupUi(self):
        self.setWindowTitle("Video Switcher")
        self.resize(1024, 600)
        
        mainScreen = QWidget()
        
        self.stack = QStackedWidget()
        self.stack.addWidget(mainScreen)
        
        self.setCentralWidget(self.stack)
        
        gridlayout = QGridLayout()
        mainScreen.setLayout(gridlayout)
        
        ''' Buttons added to inputs should have a numeric ID set equal to their input number on the Aldates main switcher. '''
        self.inputs = QButtonGroup()
        
        inputsGrid = QHBoxLayout()
        
        self.btnCamera1 = InputButton()
        self.btnCamera1.setText("Camera 1")
        inputsGrid.addWidget(self.btnCamera1)
        self.inputs.addButton(self.btnCamera1, 1)
        self.btnCamera1.setIcon(QIcon("icons/camera-video.svg"))
        
        self.btnCamera2 = InputButton()
        self.btnCamera2.setText("Camera 2")
        inputsGrid.addWidget(self.btnCamera2)
        self.inputs.addButton(self.btnCamera2, 2)
        self.btnCamera2.setIcon(QIcon("icons/camera-video.svg"))
        
        self.btnCamera3 = InputButton()
        self.btnCamera3.setText("Camera 3")
        inputsGrid.addWidget(self.btnCamera3)
        self.inputs.addButton(self.btnCamera3, 3)
        self.btnCamera3.setIcon(QIcon("icons/camera-video.svg"))
        
        self.btnDVD = InputButton()
        self.btnDVD.setText("DVD")
        inputsGrid.addWidget(self.btnDVD)
        self.inputs.addButton(self.btnDVD, 4)
        self.btnDVD.setIcon(QIcon("icons/media-optical.svg"))
        
        self.btnExtras = InputButton()
        self.btnExtras.setText("Extras")
        inputsGrid.addWidget(self.btnExtras)
        self.btnExtras.setIcon(QIcon("icons/video-display.svg"))
        self.inputs.addButton(self.btnExtras, 5)
        
        self.btnVisualsPC = InputButton()
        self.btnVisualsPC.setText("Visuals PC")
        inputsGrid.addWidget(self.btnVisualsPC)
        self.inputs.addButton(self.btnVisualsPC, 6)
        self.btnVisualsPC.setIcon(QIcon("icons/computer.svg"))
        
        self.btnBlank = InputButton()
        self.btnBlank.setText("Blank")
        inputsGrid.addWidget(self.btnBlank)
        self.inputs.addButton(self.btnBlank, 0)
        
        gridlayout.addLayout(inputsGrid, 0, 0, 1, 7)
        
        self.extrasSwitcher = ExtrasSwitcher(self.controller)
        self.blank = QWidget(self)
        gridlayout.addWidget(self.blank, 1, 0, 1, 5)
        
        outputsGrid = QGridLayout()
        
        self.btnProjectors = OutputButton(ID=2)
        self.btnProjectors.setText("Projectors")
        outputsGrid.addWidget(self.btnProjectors, 0, 1)

        self.btnChurch = OutputButton(ID=4)
        self.btnChurch.setText("Church")
        outputsGrid.addWidget(self.btnChurch, 1, 0)
        self.btnSpecial = OutputButton(ID=7)
        self.btnSpecial.setText("Special")
        outputsGrid.addWidget(self.btnSpecial, 1, 1)
        
        self.btnGallery = OutputButton(ID=6)
        self.btnGallery.setText("Gallery")
        outputsGrid.addWidget(self.btnGallery, 2, 0)
        self.btnWelcome = OutputButton(ID=5)
        self.btnWelcome.setText("Welcome")
        outputsGrid.addWidget(self.btnWelcome, 2, 1)

        self.btnFont = OutputButton(ID=3)
        self.btnFont.setText("Font")
        outputsGrid.addWidget(self.btnFont, 3, 0)
        self.btnRecord = OutputButton(ID=8)
        self.btnRecord.setText("Record")
        outputsGrid.addWidget(self.btnRecord, 3, 1)

        self.btnPCMix = OutputButton(ID=2)
        self.btnPCMix.setText("PC Mix")
        outputsGrid.addWidget(self.btnPCMix, 4, 0)
        self.btnAll = OutputButton(ID=0)
        self.btnAll.setText("All")
        outputsGrid.addWidget(self.btnAll, 4, 1)
        
        outputsGrid.setColumnMinimumWidth(0, 100)
        outputsGrid.setColumnMinimumWidth(1, 100)
        outputsGrid.setColumnStretch(0, 1)
        outputsGrid.setColumnStretch(1, 1)
        
        outputsHolder = OutputsHolderPanel()
        outputsHolder.setLayout(outputsGrid)
        
        gridlayout.addWidget(outputsHolder, 1, 5, 1, 2)
        
        syspower = ExpandingButton()
        syspower.setText("System Power")
        syspower.clicked.connect(self.showSystemPower)
        gridlayout.addWidget(syspower, 2, 0, 1, 2)
        
        gridlayout.addWidget(Clock(), 2, 6)

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
                       CameraControl(self.controller, "Camera 1") if self.controller.hasDevice("Camera 1") else QLabel("No Device"),
                       CameraControl(self.controller, "Camera 2") if self.controller.hasDevice("Camera 2") else QLabel("No Device"),
                       CameraControl(self.controller, "Camera 3") if self.controller.hasDevice("Camera 3") else QLabel("No Device"),
                       QWidget(), # DVD - no controls
                       self.extrasSwitcher, # Extras
                       EclipseControls(self.controller, "Main Scan Converter") if self.controller.hasDevice("Main Scan Converter") else QLabel("No Device") # Visuals PC
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
        self.btnPCMix.clicked.connect(self.handlePCMixSelect)
        
        
    def keyPressEvent(self, e):
        if e.key() == Qt.Key_0:
            self.btnBlank.click()
        elif e.key() == Qt.Key_1:
            self.btnCamera1.click()
        elif e.key() == Qt.Key_2:
            self.btnCamera2.click()
        elif e.key() == Qt.Key_3:
            self.btnCamera3.click()
        elif e.key() == Qt.Key_4:
            self.btnDVD.click()
        elif e.key() == Qt.Key_5:
            self.btnExtras.click()
        elif e.key() == Qt.Key_6:
            self.btnVisualsPC.click()
        elif e.key() == Qt.Key_Space:
            self.btnAll.click()
        else:
            self.panels[self.inputs.checkedId()].keyPressEvent(e)

    def keyReleaseEvent(self, e):
        self.panels[self.inputs.checkedId()].keyReleaseEvent(e)

        
    def handleInputSelect(self):
        inputID = self.inputs.checkedId()
        logging.debug("Input selected: " + str(inputID))
        if inputID > 0:
            try:
                # HACK HACK HACK someone wired these up the wrong way around
                if inputID == 5:
                    self.controller.switch("Preview", 6, 1)
                elif inputID == 6:
                    self.controller.switch("Preview", 5, 1)
                else:
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
            
    def handlePCMixSelect(self):
        outputChannel = self.sender().ID
        inputChannel = self.inputs.checkedId()
        
        if outputChannel != 2:
            raise RuntimeError("This isn't PC Mix...")
        
        try:
            if inputChannel == 5:
                self.extrasSwitcher.takePreview()
                # HACK HACK HACK someone wired these up the wrong way
                self.controller.switch("Preview", 6, outputChannel)
            elif inputChannel != 6:
                self.controller.switch("Preview", inputChannel, outputChannel)
            else :
                logging.error("Tried to send PC to PC Mix. Bad things would have happened!")
        except NamingError:
            self.errorBox(StringConstants.nameErrorText)
        except ProtocolError:
            self.errorBox(StringConstants.protocolErrorText)
            
    def showSystemPower(self):
        spc = SystemPowerWidget()
        self.stack.insertWidget(0, spc)
        spc.b.clicked.connect(self.hideSystemPower)
        
        spc.btnOn.clicked.connect(self.controller.systemPowerOn)
        spc.btnOff.clicked.connect(self.controller.systemPowerOff)
        
        self.stack.setCurrentIndex(0)

    def hideSystemPower(self):
        self.stack.removeWidget(self.stack.widget(0))
        
    def errorBox(self, text):
        logging.error(text)
        msgBox = QMessageBox()
        msgBox.setText(text)
        msgBox.setIcon(QMessageBox.Critical)
        msgBox.exec_()
        
