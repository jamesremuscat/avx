from PySide.QtGui import QGridLayout, QIcon, QMainWindow, QMessageBox, QStackedWidget, QWidget
from PySide.QtCore import Qt
from org.muscat.staldates.aldatesx.ui.widgets.Buttons import ExpandingButton
from org.muscat.staldates.aldatesx.ui.widgets.Clock import Clock
from org.muscat.staldates.aldatesx.ui.widgets.LogViewer import LogViewer
from org.muscat.staldates.aldatesx.ui.widgets.SystemPowerWidget import SystemPowerWidget
from org.muscat.staldates.aldatesx.ui.VideoSwitcher import VideoSwitcher
import logging
from org.muscat.staldates.aldatesx.ui.widgets.Dialogs import PowerNotificationDialog
from org.muscat.staldates.aldatesx.ui.widgets.BlindsControl import BlindsControl
from org.muscat.staldates.aldatesx.ui.widgets.ProjectorScreensControl import ProjectorScreensControl
from org.muscat.staldates.aldatesx.ui.widgets.AdvancedMenu import AdvancedMenu


class MainWindow(QMainWindow):

    def __init__(self, controller):
        super(MainWindow, self).__init__()
        self.controller = controller

        self.setWindowTitle("AldatesX")
        self.resize(1024, 600)

        self.mainScreen = VideoSwitcher(controller, self)
        self.stack = QStackedWidget()
        self.stack.addWidget(self.mainScreen)

        outer = QWidget()
        mainLayout = QGridLayout()
        mainLayout.addWidget(self.stack, 0, 0, 1, 7)

        self.spc = SystemPowerWidget()
        self.spc.b.clicked.connect(self.stepBack)
        self.spc.btnOn.clicked.connect(self.controller.systemPowerOn)
        self.spc.btnOff.clicked.connect(self.controller.systemPowerOff)

        syspower = ExpandingButton()
        syspower.setText("Power")
        syspower.clicked.connect(self.showSystemPower)
        syspower.setIcon(QIcon("icons/system-shutdown.svg"))
        syspower.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        mainLayout.addWidget(syspower, 1, 0)

        self.bc = BlindsControl(self.controller, self)
        self.bc.b.clicked.connect(self.stepBack)

        blinds = ExpandingButton()
        blinds.setText("Blinds")
        blinds.clicked.connect(lambda: self.showScreen(self.bc))
        blinds.setIcon(QIcon("icons/blinds.svg"))
        blinds.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        mainLayout.addWidget(blinds, 1, 2)

        self.sc = ProjectorScreensControl(self.controller, self)
        self.sc.b.clicked.connect(self.stepBack)

        screens = ExpandingButton()
        screens.setText("Screens")
        screens.clicked.connect(lambda: self.showScreen(self.sc))
        screens.setIcon(QIcon("icons/screens.svg"))
        screens.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        mainLayout.addWidget(screens, 1, 3)

        self.advMenu = AdvancedMenu(self.controller, self)

        adv = ExpandingButton()
        adv.setText("Advanced")
        adv.setIcon(QIcon("icons/applications-system.svg"))
        adv.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        adv.clicked.connect(lambda: self.showScreen(self.advMenu))
        mainLayout.addWidget(adv, 1, 5)

        mainLayout.addWidget(Clock(), 1, 6)

        mainLayout.setRowStretch(0, 8)
        mainLayout.setRowStretch(1, 0)

        outer.setLayout(mainLayout)

        self.setCentralWidget(outer)

        self.pnd = PowerNotificationDialog(self)

    def showScreen(self, screenWidget):
        if self.stack.currentWidget() == screenWidget:
            self.stepBack()
        else:
            self.stack.insertWidget(0, screenWidget)
            self.stack.setCurrentWidget(screenWidget)

    def showSystemPower(self):
        self.showScreen(self.spc)

    def stepBack(self):
        self.stack.removeWidget(self.stack.currentWidget())

    def errorBox(self, text):
        logging.error(text)
        msgBox = QMessageBox()
        msgBox.setText(text)
        msgBox.setIcon(QMessageBox.Critical)
        msgBox.exec_()

    def showPowerDialog(self, message):
        self.pnd.message = message
        self.pnd.exec_()

    def hidePowerDialog(self):
        self.pnd.close()
        if self.stack.currentWidget() == self.spc:
            self.stepBack()

    def updateOutputMappings(self, mapping):
        self.mainScreen.updateOutputMappings(mapping)
