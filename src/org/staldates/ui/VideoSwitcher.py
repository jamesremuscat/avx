from PySide.QtGui import QLabel, QWidget, QGridLayout, QHBoxLayout, QButtonGroup, QIcon
from PySide.QtCore import QMetaObject, Qt
from org.staldates.ui.widgets.Buttons import InputButton, CameraSelectionButton
from org.staldates.ui.ExtrasSwitcher import ExtrasSwitcher
from org.staldates.ui.CameraControls import CameraControl, AdvancedCameraControl
from Pyro4.errors import ProtocolError, NamingError
from org.muscat.avx.StringConstants import StringConstants
from org.staldates.ui.EclipseControls import EclipseControls
import logging
from org.staldates.ui.widgets.OutputsGrid import OutputsGrid


class VideoSwitcher(QWidget):

    def __init__(self, controller, mainWindow):
        super(VideoSwitcher, self).__init__()
        self.controller = controller
        self.mainWindow = mainWindow
        self.setupUi()

    def setupUi(self):

        gridlayout = QGridLayout()
        self.setLayout(gridlayout)

        ''' Buttons added to inputs should have a numeric ID set equal to their input number on the Aldates main switcher. '''
        self.inputs = QButtonGroup()

        inputsGrid = QHBoxLayout()

        self.btnCamera1 = CameraSelectionButton()
        self.btnCamera1.setText("Camera 1")
        inputsGrid.addWidget(self.btnCamera1)
        self.inputs.addButton(self.btnCamera1, 1)
        self.btnCamera1.setIcon(QIcon("icons/camera-video.svg"))
        self.btnCamera1.longpress.connect(lambda: self.showCameraAdvanced("Camera 1"))

        self.btnCamera2 = CameraSelectionButton()
        self.btnCamera2.setText("Camera 2")
        inputsGrid.addWidget(self.btnCamera2)
        self.inputs.addButton(self.btnCamera2, 2)
        self.btnCamera2.setIcon(QIcon("icons/camera-video.svg"))
        self.btnCamera2.longpress.connect(lambda: self.showCameraAdvanced("Camera 2"))

        self.btnCamera3 = CameraSelectionButton()
        self.btnCamera3.setText("Camera 3")
        inputsGrid.addWidget(self.btnCamera3)
        self.inputs.addButton(self.btnCamera3, 3)
        self.btnCamera3.setIcon(QIcon("icons/camera-video.svg"))
        self.btnCamera3.longpress.connect(lambda: self.showCameraAdvanced("Camera 3"))

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

        self.outputsGrid = OutputsGrid()

        gridlayout.addWidget(self.outputsGrid, 1, 5, 1, 2)

        gridlayout.setRowStretch(0, 1)
        gridlayout.setRowStretch(1, 5)
        QMetaObject.connectSlotsByName(self)
        self.setInputClickHandlers()
        self.setOutputClickHandlers(self.outputsGrid)
        self.configureInnerControlPanels()
        self.gridlayout = gridlayout

    def configureInnerControlPanels(self):
        self.panels = [
                       QWidget(),  # Blank
                       CameraControl(self.controller, "Camera 1") if self.controller.hasDevice("Camera 1") else QLabel(StringConstants.noDevice),
                       CameraControl(self.controller, "Camera 2") if self.controller.hasDevice("Camera 2") else QLabel(StringConstants.noDevice),
                       CameraControl(self.controller, "Camera 3") if self.controller.hasDevice("Camera 3") else QLabel(StringConstants.noDevice),
                       QLabel(StringConstants.noDevice),  # DVD - no controls
                       self.extrasSwitcher if self.controller.hasDevice("Extras") else QLabel(StringConstants.noDevice),  # Extras
                       EclipseControls(self.controller, "Main Scan Converter") if self.controller.hasDevice("Main Scan Converter") else QLabel(StringConstants.noDevice),  # Visuals PC
                       ]

    def setInputClickHandlers(self):
        self.btnCamera1.clicked.connect(self.handleInputSelect)
        self.btnCamera2.clicked.connect(self.handleInputSelect)
        self.btnCamera3.clicked.connect(self.handleInputSelect)
        self.btnDVD.clicked.connect(self.handleInputSelect)
        self.btnExtras.clicked.connect(self.handleInputSelect)
        self.btnVisualsPC.clicked.connect(self.handleInputSelect)
        self.btnBlank.clicked.connect(self.handleInputSelect)

    def setOutputClickHandlers(self, outputsGrid):
        outputsGrid.connectMainOutputs(self.handleOutputSelect)
        ''' btnPCMix is a special case since that's on a different switcher '''
        outputsGrid.connectPreviewOutputs(self.handlePCMixSelect)

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
            self.outputsGrid.btnAll.click()
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
                self.mainWindow.errorBox(StringConstants.nameErrorText)
            except ProtocolError:
                self.mainWindow.errorBox(StringConstants.protocolErrorText)
        self.gridlayout.removeWidget(self.gridlayout.itemAtPosition(1, 0).widget())
        for p in self.panels:
            p.hide()
        chosenPanel = self.panels[inputID]
        self.gridlayout.addWidget(chosenPanel, 1, 0, 1, 5)
        chosenPanel.show()

        # Prevent certain options from being selectable
        if inputID == 6 or inputID == 0:
            self.outputsGrid.btnPCMix.setEnabled(False)
        else:
            self.outputsGrid.btnPCMix.setEnabled(True)

    def handleOutputSelect(self):
        outputChannel = self.sender().ID
        inputChannel = self.inputs.checkedId()

        if inputChannel == 5:
            self.extrasSwitcher.take()
        try:
            self.controller.switch("Main", inputChannel, outputChannel)
        except NamingError:
            self.mainWindow.errorBox(StringConstants.nameErrorText)
        except ProtocolError:
            self.mainWindow.errorBox(StringConstants.protocolErrorText)

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
            else:
                logging.error("Tried to send PC to PC Mix. Bad things would have happened!")
        except NamingError:
            self.mainWindow.errorBox(StringConstants.nameErrorText)
        except ProtocolError:
            self.mainWindow.errorBox(StringConstants.protocolErrorText)

    def showCameraAdvanced(self, camDevice):
        ctls = AdvancedCameraControl(self.controller, camDevice, self.mainWindow)
        self.mainWindow.showScreen(ctls)

    def updateOutputMappings(self, mapping):
        self.outputsGrid.updateOutputMappings(mapping)
