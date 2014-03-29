from PySide.QtGui import QVBoxLayout
from org.staldates.ui.widgets.LogViewer import LogViewer
from org.staldates.ui.widgets.Buttons import ExpandingButton
from org.staldates.ui.widgets.Screens import ScreenWithBackButton


class AdvancedMenu(ScreenWithBackButton):
    '''
    Place to hide magical advanced system features.
    '''

    def __init__(self, controller, mainWindow):
        self.controller = controller
        self.mainWindow = mainWindow
        super(AdvancedMenu, self).__init__("Advanced Options", mainWindow)

    def makeContent(self):
        layout = QVBoxLayout()

        self.lv = LogViewer(self.controller, self.mainWindow)

        log = ExpandingButton()
        log.setText("Log")
        log.clicked.connect(self.showLog)
        layout.addWidget(log)

        btnAutoTrack = ExpandingButton()
        btnAutoTrack.setText("Recalibrate Extras scan converter")
        btnAutoTrack.clicked.connect(lambda: self.controller.recalibrate("Extras Scan Converter"))
        layout.addWidget(btnAutoTrack)

        btnQuit = ExpandingButton()
        btnQuit.setText("Exit AldatesX")
        btnQuit.clicked.connect(self.mainWindow.close)
        layout.addWidget(btnQuit)

        return layout

    def showLog(self):
        self.lv.displayLog()
        self.mainWindow.showScreen(self.lv)
