from PySide.QtGui import QGridLayout, QIcon, QMainWindow, QStackedWidget, QWidget
from PySide.QtCore import Qt
from org.staldates.ui.widgets.Buttons import ExpandingButton
from org.staldates.ui.widgets.Clock import Clock
from org.staldates.ui.widgets.SystemPowerWidget import SystemPowerWidget
from org.staldates.ui.VideoSwitcher import VideoSwitcher
from org.staldates.ui.widgets.Dialogs import PowerNotificationDialog
from org.staldates.ui.widgets.BlindsControl import BlindsControl
from org.staldates.ui.widgets.ProjectorScreensControl import ProjectorScreensControl
from org.staldates.ui.widgets.AdvancedMenu import AdvancedMenu
from org.staldates.ui.widgets import Dialogs
from org.staldates.ui.widgets.LightingControl import LightingControl


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

        self.spc = SystemPowerWidget(controller, self)

        syspower = ExpandingButton()
        syspower.setText("Power")
        syspower.clicked.connect(self.showSystemPower)
        syspower.setIcon(QIcon("icons/system-shutdown.svg"))
        syspower.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        mainLayout.addWidget(syspower, 1, 0)

        self.bc = BlindsControl(controller, self)

        blinds = ExpandingButton()
        blinds.setText("Blinds")
        blinds.clicked.connect(lambda: self.showScreen(self.bc))
        blinds.setIcon(QIcon("icons/blinds.svg"))
        blinds.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        mainLayout.addWidget(blinds, 1, 2)

        self.sc = ProjectorScreensControl(self.controller, self)

        screens = ExpandingButton()
        screens.setText("Screens")
        screens.clicked.connect(lambda: self.showScreen(self.sc))
        screens.setIcon(QIcon("icons/screens.svg"))
        screens.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        mainLayout.addWidget(screens, 1, 3)

        self.lightsMenu = LightingControl(self.controller, self)

        lights = ExpandingButton()
        lights.setText("Lights")
        lights.clicked.connect(lambda: self.showScreen(self.lightsMenu))
        lights.setIcon(QIcon("icons/lightbulb_on.svg"))
        lights.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        mainLayout.addWidget(lights, 1, 4)

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
        self.pnd.accepted.connect(self.hidePowerDialog)

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
        Dialogs.errorBox(text)

    def showPowerDialog(self, message):
        self.pnd.message = message
        self.pnd.exec_()

    def hidePowerDialog(self):
        self.pnd.close()
        if self.stack.currentWidget() == self.spc:
            self.stepBack()

    def updateOutputMappings(self, mapping):
        self.mainScreen.updateOutputMappings(mapping)
