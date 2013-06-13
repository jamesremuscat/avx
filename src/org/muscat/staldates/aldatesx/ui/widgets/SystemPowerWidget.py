from PySide.QtGui import QIcon, QHBoxLayout
from PySide.QtCore import Qt, QSize
from org.muscat.staldates.aldatesx.ui.widgets.Buttons import ExpandingButton
from org.muscat.staldates.aldatesx.ui.widgets.Screens import ScreenWithBackButton


class SystemPowerWidget(ScreenWithBackButton):

    def __init__(self, controller, mainWindow):
        self.controller = controller
        ScreenWithBackButton.__init__(self, "System Power", mainWindow)

    def makeContent(self):

        buttons = QHBoxLayout()

        self.btnOff = ExpandingButton()
        self.btnOff.setText("Off")
        self.btnOff.setIcon(QIcon("icons/lightbulb_off.svg"))
        self.btnOff.setIconSize(QSize(128, 128))
        self.btnOff.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.btnOff.clicked.connect(self.controller.systemPowerOff)
        buttons.addWidget(self.btnOff)

        self.btnOn = ExpandingButton()
        self.btnOn.setText("On")
        self.btnOn.setIcon(QIcon("icons/lightbulb_on.svg"))
        self.btnOn.setIconSize(QSize(128, 128))
        self.btnOn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.btnOn.clicked.connect(self.controller.systemPowerOn)
        buttons.addWidget(self.btnOn)

        return buttons
