from PySide.QtGui import QToolButton, QSizePolicy
from PySide.QtCore import Qt

class ExpandingButton(QToolButton):
    def __init__(self, parent = None):
        super(ExpandingButton, self).__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
class InputButton(ExpandingButton):
    def __init__(self, parent):
        super(InputButton, self).__init__(parent)
        self.setCheckable(True)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        
class OutputButton(ExpandingButton):
    def __init__(self, parent, ID):
        super(OutputButton, self).__init__(parent)
        self.ID = ID