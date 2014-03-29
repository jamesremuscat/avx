from PySide.QtGui import QLabel
from PySide.QtCore import QTimer, QTime, Qt


class Clock(QLabel):
    '''
    A clock.
    '''

    def __init__(self, parent=None):
        super(Clock, self).__init__(parent)
        self.setAlignment(Qt.AlignCenter)

        timer = QTimer(self)
        timer.timeout.connect(self.updateClock)
        timer.start(1000)
        self.updateClock()

    def updateClock(self):
        self.setText(QTime.currentTime().toString("hh:mm"))
