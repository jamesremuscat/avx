from PySide.QtGui import QLabel, QSizePolicy, QVBoxLayout, QWidget
from PySide.QtCore import Qt
from org.muscat.staldates.aldatesx.ui.widgets.LogViewer import LogViewer
from org.muscat.staldates.aldatesx.ui.widgets.Buttons import ExpandingButton


class AdvancedMenu(QWidget):
    '''
    Place to hide magical advanced system features.
    '''

    def __init__(self, controller, mainWindow):
        super(AdvancedMenu, self).__init__()
        self.controller = controller
        self.mainWindow = mainWindow

        layout = QVBoxLayout()

        title = QLabel("Advanced Options")
        title.setStyleSheet("font-size: 48px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.lv = LogViewer()
        self.lv.b.clicked.connect(mainWindow.stepBack)

        log = ExpandingButton()
        log.setText("Log")
        log.clicked.connect(self.showLog)
        layout.addWidget(log)

        btnQuit = ExpandingButton()
        btnQuit.setText("Exit AldatesX")
        btnQuit.clicked.connect(mainWindow.close)
        layout.addWidget(btnQuit)

        b = ExpandingButton()
        b.setText("Back")
        b.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(b)
        b.clicked.connect(mainWindow.stepBack)

        self.setLayout(layout)

    def showLog(self):
        self.lv.displayLog(self.controller.getLog())
        self.mainWindow.showScreen(self.lv)
