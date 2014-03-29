'''
Created on 10 Nov 2012

@author: james
'''
from PySide.QtGui import QWidget, QGridLayout, QButtonGroup, QMessageBox
from org.staldates.ui.widgets.Buttons import InputButton, OutputButton
from Pyro4.errors import ProtocolError, NamingError
from org.muscat.avx.StringConstants import StringConstants
from org.staldates.ui.widgets.ScanConverterControls import OverscanFreezeWidget
import logging


class ExtrasSwitcher(QWidget):
    '''
    The extras switcher.
    '''

    def __init__(self, controller):
        super(ExtrasSwitcher, self).__init__()
        self.controller = controller
        self.initUI()

    def initUI(self):
        layout = QGridLayout()
        self.setLayout(layout)

        inputs = QButtonGroup()

        btnE1 = InputButton(self)
        btnE1.setText("Extras 1")
        layout.addWidget(btnE1, 0, 0)
        inputs.addButton(btnE1, 1)

        btnE2 = InputButton(self)
        btnE2.setText("Extras 2")
        layout.addWidget(btnE2, 0, 1)
        inputs.addButton(btnE2, 2)

        btnE3 = InputButton(self)
        btnE3.setText("Extras 3")
        layout.addWidget(btnE3, 0, 2)
        inputs.addButton(btnE3, 3)

        btnE4 = InputButton(self)
        btnE4.setText("Extras 4")
        layout.addWidget(btnE4, 0, 3)
        inputs.addButton(btnE4, 4)

        btnEVideo = InputButton(self)
        btnEVideo.setText("Visuals PC video")
        layout.addWidget(btnEVideo, 0, 4)
        inputs.addButton(btnEVideo, 8)

        self.inputs = inputs

        if self.controller.hasDevice("Extras Scan Converter"):
            scControl = OverscanFreezeWidget()
            layout.addWidget(scControl, 1, 4)
            scControl.btnOverscan.toggled.connect(self.toggleOverscan)
            scControl.btnFreeze.toggled.connect(self.toggleFreeze)

        btnPrevMix = OutputButton(1)
        btnPrevMix.setText("Preview / PC Mix")
        layout.addWidget(btnPrevMix, 2, 0, 1, 5)

        btnPrevMix.clicked.connect(self.takePreview)

    def takePreview(self):
        self.take(2)

    def take(self, output=1):
        '''Send the currently selected input to the main switcher's input. '''
        try:
            logging.debug("Extras: " + str(self.inputs.checkedId()) + " => " + str(output))
            self.controller.switch("Extras", self.inputs.checkedId(), output)
        except NamingError:
            self.errorBox(StringConstants.nameErrorText)
        except ProtocolError:
            self.errorBox(StringConstants.protocolErrorText)

    def toggleOverscan(self):
        try:
            self.controller.toggleOverscan("Extras Scan Converter", self.sender().isChecked())
        except NamingError:
            self.errorBox(StringConstants.nameErrorText)
        except ProtocolError:
            self.errorBox(StringConstants.protocolErrorText)

    def toggleFreeze(self):
        try:
            self.controller.toggleFreeze("Extras Scan Converter", self.sender().isChecked())
        except NamingError:
            self.errorBox(StringConstants.nameErrorText)
        except ProtocolError:
            self.errorBox(StringConstants.protocolErrorText)

    def errorBox(self, text):
        msgBox = QMessageBox()
        msgBox.setText(text)
        msgBox.setIcon(QMessageBox.Critical)
        msgBox.exec_()
