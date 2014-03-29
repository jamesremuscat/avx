from PySide.QtGui import QDialog, QGridLayout, QLabel, QMessageBox, QMovie
from PySide.QtCore import Qt
from org.staldates.ui.widgets.Buttons import ExpandingButton
import logging


class PowerNotificationDialog(QDialog):
    '''
    Dialog to notify about system power changing state.
    '''

    message = "No message set"

    def __init__(self, parent=None):
        super(PowerNotificationDialog, self).__init__(parent)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)

        layout = QGridLayout()

        spinBox = QLabel()
        spinner = QMovie("icons/spinner.gif")
        spinner.start()
        spinBox.setMovie(spinner)
        layout.addWidget(spinBox, 0, 0)

        self.textBox = QLabel()

        layout.addWidget(self.textBox, 0, 1, 1, 3)

        btnOK = ExpandingButton()
        btnOK.setText("OK")
        btnOK.clicked.connect(self.accept)
        layout.addWidget(btnOK, 1, 1, 1, 2)

        self.setLayout(layout)

    def exec_(self):
        self.textBox.setText(self.message)
        super(PowerNotificationDialog, self).exec_()


def errorBox(text):
    logging.error(text)
    msgBox = QMessageBox()
    msgBox.setText('<span style="color: white;">' + text + '</span>')
    msgBox.setIcon(QMessageBox.Critical)
    msgBox.exec_()
