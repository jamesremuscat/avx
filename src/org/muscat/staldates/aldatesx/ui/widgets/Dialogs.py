from PySide.QtGui import QDialog, QVBoxLayout, QLabel
from PySide.QtCore import Qt

class PowerNotificationDialog(QDialog):
    '''
    Dialog to notify about system power changing state.
    '''
    
    message = "No message set"

    def __init__(self, parent = None):
        super(PowerNotificationDialog, self).__init__(parent)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        
        layout = QVBoxLayout()
        
        self.textBox = QLabel()
        layout.addWidget(self.textBox)
        
        self.setLayout(layout)
        
    def exec_(self):
        self.textBox.setText(self.message)
        super(PowerNotificationDialog, self).exec_()