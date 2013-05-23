from PySide.QtCore import Qt
from PySide.QtGui import QGridLayout, QLabel, QWidget


class BlindsControl(QWidget):
    '''
    Controls for the blinds.
    '''

    def __init__(self, controller):
        super(BlindsControl, self).__init__()
        self.controller = controller

        layout = QGridLayout()

        title = QLabel("Blinds")
        title.setStyleSheet("font-size: 48px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title, 0, 1, 6, 1)

        self.setLayout(layout)
