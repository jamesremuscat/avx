from PySide.QtCore import Qt, QSize
from PySide.QtGui import QButtonGroup, QIcon, QGridLayout
from org.staldates.ui.widgets.Buttons import ExpandingButton,\
    IDedButton
from Pyro4.errors import NamingError, ProtocolError
from org.muscat.avx.StringConstants import StringConstants
from org.staldates.ui.widgets.Screens import ScreenWithBackButton


class ProjectorScreensControl(ScreenWithBackButton):
    '''
    Controls for the projector screens.
    '''

    def __init__(self, controller, mainWindow):
        self.controller = controller
        ScreenWithBackButton.__init__(self, "Projector Screens", mainWindow)

    def makeContent(self):
        layout = QGridLayout()

        self.screens = QButtonGroup()

        btnLeft = IDedButton(1)
        btnLeft.setText("Left")
        layout.addWidget(btnLeft, 1, 0, 1, 2)
        btnLeft.setCheckable(True)
        self.screens.addButton(btnLeft, 1)

        btnAll = IDedButton(0)
        btnAll.setText("Both")
        layout.addWidget(btnAll, 1, 2, 1, 3)
        btnAll.setCheckable(True)
        btnAll.setChecked(True)
        self.screens.addButton(btnAll, 0)

        btnRight = IDedButton(2)
        btnRight.setText("Right")
        layout.addWidget(btnRight, 1, 5, 1, 2)
        btnRight.setCheckable(True)
        self.screens.addButton(btnRight, 2)

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

        return layout

    def raiseUp(self):
        screenID = self.screens.checkedId()
        try:
            self.controller.raiseUp("Screens", screenID)
        except NamingError:
            self.mainWindow.errorBox(StringConstants.nameErrorText)
        except ProtocolError:
            self.mainWindow.errorBox(StringConstants.protocolErrorText)

    def lowerDown(self):
        screenID = self.screens.checkedId()
        try:
            self.controller.lower("Screens", screenID)
        except NamingError:
            self.mainWindow.errorBox(StringConstants.nameErrorText)
        except ProtocolError:
            self.mainWindow.errorBox(StringConstants.protocolErrorText)

    def stop(self):
        screenID = self.screens.checkedId()
        try:
            self.controller.stop("Screens", screenID)
        except NamingError:
            self.mainWindow.errorBox(StringConstants.nameErrorText)
        except ProtocolError:
            self.mainWindow.errorBox(StringConstants.protocolErrorText)
