from PySide.QtGui import QWidget, QVBoxLayout
from org.muscat.staldates.aldatesx.widgets.Buttons import InputButton

class OverscanFreezeControl(QWidget):

    def __init__(self, parent = None):
        super(OverscanFreezeControl, self).__init__(parent)
        
        self.layout = QVBoxLayout()
        
        self.btnOverscan = InputButton()
        self.btnOverscan.setText("Overscan")
        self.layout.addWidget(self.btnOverscan)
        self.btnOverscan.setChecked(True)
        
        self.btnFreeze = InputButton()
        self.btnFreeze.setText("Freeze")
        self.layout.addWidget(self.btnFreeze)
        
        self.setLayout(self.layout)
        
class OverscanFreezeFadeControl(OverscanFreezeControl):
    
    def __init__(self, parent = None):
        super(OverscanFreezeFadeControl, self).__init__(parent)
        
        self.btnFade = InputButton()
        self.btnFade.setText("Fade")
        self.layout.addWidget(self.btnFade)