from PySide.QtGui import QDialog

class PowerNotificationDialog(QDialog):
    '''
    Dialog to notify about system power changing state.
    '''

    def __init__(self):
        super(PowerNotificationDialog, self).__init__()
        