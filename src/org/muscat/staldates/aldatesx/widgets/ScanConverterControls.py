from PySide.QtGui import QWidget, QGridLayout, QVBoxLayout, QIcon
from org.muscat.staldates.aldatesx.widgets.Buttons import OptionButton

class OverscanFreezeControl(QWidget):

    def __init__(self, parent = None):
        super(OverscanFreezeControl, self).__init__(parent)
        
        
        self.btnOverscan = OptionButton()
        self.btnOverscan.setText("Overscan")
        self.btnOverscan.setChecked(True)
        self.btnOverscan.setIcon(QIcon("/usr/share/icons/Tango/scalable/actions/gtk-fullscreen.svg"))
        
        self.btnFreeze = OptionButton()
        self.btnFreeze.setText("Freeze")
        self.btnFreeze.setIcon(QIcon("/usr/share/icons/Tango/scalable/actions/player_pause.svg"))
        
        self.layout()
        
    def layout(self):
        layout = QVBoxLayout()
        layout.addWidget(self.btnOverscan)
        layout.addWidget(self.btnFreeze)
        
        self.setLayout(layout)
        
class EclipseControl(OverscanFreezeControl):
    
    def __init__(self, parent = None):        
        self.btnFade = OptionButton()
        self.btnFade.setText("Fade")
        self.btnFade.setIcon(QIcon("/usr/share/icons/Tango/scalable/apps/screensaver.svg"))
        
        self.btnOverlay = OptionButton()
        self.btnOverlay.setText("Overlay")
        self.btnOverlay.setIcon(QIcon("/usr/share/icons/Tango/scalable/apps/preferences-system-windows.svg"))
        
        super(EclipseControl, self).__init__(parent)
        
    def layout(self):
        layout = QGridLayout()
        layout.addWidget(self.btnOverlay, 0, 0)
        layout.addWidget(self.btnOverscan, 0, 1)
        layout.addWidget(self.btnFreeze, 1, 0)
        layout.addWidget(self.btnFade, 1, 1)
        self.setLayout(layout)