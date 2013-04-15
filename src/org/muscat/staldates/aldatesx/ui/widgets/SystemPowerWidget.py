from PySide.QtGui import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide.QtCore import Qt
from org.muscat.staldates.aldatesx.ui.widgets.Buttons import ExpandingButton


class SystemPowerWidget(QWidget):

    def __init__(self):
        super(SystemPowerWidget, self).__init__()

        layout = QVBoxLayout(self)

        title = QLabel("System Power")
        title.setStyleSheet("font-size: 48px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        buttons = QHBoxLayout()

        self.btnOff = ExpandingButton()
        self.btnOff.setText("Off")
        buttons.addWidget(self.btnOff)

        self.btnOn = ExpandingButton()
        self.btnOn.setText("On")
        buttons.addWidget(self.btnOn)

        layout.addLayout(buttons)

        self.b = ExpandingButton()
        self.b.setText("Back")
        layout.addWidget(self.b)

        layout.setStretch(0, 1)
        layout.setStretch(1, 3)
        layout.setStretch(2, 2)
