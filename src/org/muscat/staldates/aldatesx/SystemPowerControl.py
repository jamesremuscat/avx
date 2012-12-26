from PySide.QtGui import QWidget, QGridLayout, QLabel
from org.muscat.staldates.aldatesx.widgets.Buttons import ExpandingButton

class SystemPowerControl(QWidget):


    def __init__(self):
        super(SystemPowerControl, self).__init__()

        layout = QGridLayout(self)
        
        title = QLabel("System Power")
        layout.addWidget(title, 0, 0, 1, 2)
        
        self.b = ExpandingButton()
        self.b.setText("Test")
        layout.addWidget(self.b, 1,0,1,1)
        
