from PySide.QtGui import QWidget, QLabel, QVBoxLayout
from PySide.QtCore import QTimer, QTime, Qt

class Clock(QWidget):
    '''
    A clock.
    '''


    def __init__(self, parent = None):
        super(Clock, self).__init__(parent)
        self.label = QLabel("00:00")
        self.label.setAlignment(Qt.AlignRight)
        
        layout = QVBoxLayout()
        
        layout.addWidget(self.label)
        self.setLayout(layout)
        
        timer = QTimer(self)
        timer.timeout.connect(self.updateClock)
        timer.start(1000)
        self.updateClock()
        
    def updateClock(self):
        self.label.setText(QTime.currentTime().toString("hh:mm"))
        
        
        