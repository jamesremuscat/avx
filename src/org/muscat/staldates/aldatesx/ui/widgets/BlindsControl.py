from PySide.QtCore import Qt, QSize
from PySide.QtGui import QButtonGroup, QIcon, QLabel, QGridLayout, QWidget
from org.muscat.staldates.aldatesx.ui.widgets.Buttons import ExpandingButton,\
    IDedButton
from Pyro4.errors import NamingError, ProtocolError
from org.muscat.staldates.aldatesx.StringConstants import StringConstants


class BlindsControl(QWidget):
    '''
    Controls for the blinds.
    '''

    def __init__(self, controller, mainWindow):
        super(BlindsControl, self).__init__()
        self.controller = controller
        self.mainWindow = mainWindow

        layout = QGridLayout()

        title = QLabel("Blinds")
        title.setStyleSheet("font-size: 48px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title, 0, 0, 1, 7)

        self.blinds = QButtonGroup()

        for i in range(1, 7):
            btn = IDedButton(i)
            btn.setText(str(i))
            layout.addWidget(btn, 1, i - 1)
            btn.setCheckable(True)
            self.blinds.addButton(btn, i)

        btnAll = IDedButton(0)
        btnAll.setText("All")
        layout.addWidget(btnAll, 1, 6)
        btnAll.setCheckable(True)
        btnAll.setChecked(True)
        self.blinds.addButton(btnAll, 0)

        iconSize = QSize(96, 96)

        btnRaise = ExpandingButton()
        btnRaise.setText("Raise")
        btnRaise.setIcon(QIcon("icons/go-up.svg"))
        btnRaise.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        layout.addWidget(btnRaise, 2, 1, 1, 3)
        btnRaise.setIconSize(iconSize)
        btnRaise.clicked.connect(self.raiseUp)

        btnLower = ExpandingButton()
        btnLower.setText("Lower")
        btnLower.setIcon(QIcon("icons/go-down.svg"))
        btnLower.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        layout.addWidget(btnLower, 3, 1, 1, 3)
        btnLower.setIconSize(iconSize)
        btnLower.clicked.connect(self.lowerDown)

        btnStop = ExpandingButton()
        btnStop.setText("Stop")
        btnStop.setIcon(QIcon("icons/process-stop.svg"))
        btnStop.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        layout.addWidget(btnStop, 2, 4, 2, 2)
        btnStop.setIconSize(iconSize)
        btnStop.clicked.connect(self.stop)

        self.b = ExpandingButton()
        self.b.setText("Back")
        layout.addWidget(self.b, 4, 1, 1, 5)
        layout.setRowStretch(0, 1)
        layout.setRowStretch(1, 2)
        layout.setRowStretch(2, 2)
        layout.setRowStretch(3, 2)
        layout.setRowStretch(4, 1)

        self.setLayout(layout)

    def raiseUp(self):
        blindID = self.blinds.checkedId()
        try:
            self.controller.raiseUp("Blinds", blindID)
        except NamingError:
            self.mainWindow.errorBox(StringConstants.nameErrorText)
        except ProtocolError:
            self.mainWindow.errorBox(StringConstants.protocolErrorText)

    def lowerDown(self):
        blindID = self.blinds.checkedId()
        try:
            self.controller.lower("Blinds", blindID)
        except NamingError:
            self.mainWindow.errorBox(StringConstants.nameErrorText)
        except ProtocolError:
            self.mainWindow.errorBox(StringConstants.protocolErrorText)

    def stop(self):
        blindID = self.blinds.checkedId()
        try:
            self.controller.stop("Blinds", blindID)
        except NamingError:
            self.mainWindow.errorBox(StringConstants.nameErrorText)
        except ProtocolError:
            self.mainWindow.errorBox(StringConstants.protocolErrorText)
