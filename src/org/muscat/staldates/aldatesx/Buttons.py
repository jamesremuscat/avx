from PySide.QtGui import QPushButton, QSizePolicy

class ExpandingButton(QPushButton):
    def __init__(self, parent):
        super(ExpandingButton, self).__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
class InputButton(ExpandingButton):
    def __init__(self, parent):
        super(InputButton, self).__init__(parent)
        self.setCheckable(True)
        
class OutputButton(ExpandingButton):
    def __init__(self, parent, ID):
        super(OutputButton, self).__init__(parent)
        self.ID = ID