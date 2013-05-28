from PySide.QtCore import Qt
from PySide.QtGui import QIcon, QLabel, QVBoxLayout, QWidget
from org.muscat.staldates.aldatesx.ui.widgets.Buttons import ExpandingButton


class BlindsControl(QWidget):
    '''
    Controls for the blinds.
    '''

    def __init__(self, controller):
        super(BlindsControl, self).__init__()
        self.controller = controller

        layout = QVBoxLayout()

        title = QLabel("Blinds")
        title.setStyleSheet("font-size: 48px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        btnRaise = ExpandingButton()
        btnRaise.setText("Raise")
        btnRaise.setIcon(QIcon("icons/go-up.svg"))
        btnRaise.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        layout.addWidget(btnRaise)
        btnRaise.clicked.connect(lambda: controller.raiseUp("Blinds"))

        btnLower = ExpandingButton()
        btnLower.setText("Lower")
        btnLower.setIcon(QIcon("icons/go-down.svg"))
        btnLower.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        layout.addWidget(btnLower)
        btnLower.clicked.connect(lambda: controller.lower("Blinds"))

        self.b = ExpandingButton()
        self.b.setText("Back")
        layout.addWidget(self.b)

        layout.setStretchFactor(title, 3)
        layout.setStretchFactor(btnRaise, 2)
        layout.setStretchFactor(btnLower, 2)

        self.setLayout(layout)
