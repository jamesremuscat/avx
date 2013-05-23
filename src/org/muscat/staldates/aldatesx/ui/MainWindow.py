from PySide.QtGui import QGridLayout, QMainWindow, QMessageBox, QStackedWidget, QWidget
from org.muscat.staldates.aldatesx.ui.widgets.Buttons import ExpandingButton
from org.muscat.staldates.aldatesx.ui.widgets.Clock import Clock
from org.muscat.staldates.aldatesx.ui.widgets.LogViewer import LogViewer
from org.muscat.staldates.aldatesx.ui.widgets.SystemPowerWidget import SystemPowerWidget
from org.muscat.staldates.aldatesx.ui.VideoSwitcher import VideoSwitcher
import logging
from org.muscat.staldates.aldatesx.ui.widgets.Dialogs import PowerNotificationDialog


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
        syspower.setText("System Power")
        syspower.clicked.connect(self.showSystemPower)
        mainLayout.addWidget(syspower, 1, 0)

        self.bc = QWidget()

        blinds = ExpandingButton()
        blinds.setText("Blinds")
        blinds.clicked.connect(lambda: self.showScreen(self.bc))
        mainLayout.addWidget(blinds, 1, 2)

        self.lv = LogViewer()
        self.lv.b.clicked.connect(self.stepBack)

        log = ExpandingButton()
        log.setText("Log")
        log.clicked.connect(self.showLog)
        mainLayout.addWidget(log, 1, 5)

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

    def showLog(self):
        self.lv.displayLog(self.controller.getLog())
        self.showScreen(self.lv)

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
