from PySide.QtGui import QWidget, QVBoxLayout
from org.staldates.ui.widgets.ScanConverterControls import EclipseWidget
from Pyro4.errors import ProtocolError, NamingError
from org.muscat.avx.StringConstants import StringConstants


class EclipseControls(QWidget):

    def __init__(self, controller, deviceID):
        super(EclipseControls, self).__init__()
        self.controller = controller
        self.deviceID = deviceID

        if controller.hasDevice(deviceID):
            layout = QVBoxLayout(self)
            eclipse = EclipseWidget()
            layout.addWidget(eclipse)

            eclipse.btnOverscan.toggled.connect(self.toggleOverscan)
            eclipse.btnFreeze.toggled.connect(self.toggleFreeze)
            eclipse.btnFade.toggled.connect(self.toggleFade)
            eclipse.btnOverlay.toggled.connect(self.toggleOverlay)

    def toggleOverscan(self):
        try:
            self.controller.toggleOverscan(self.deviceID, self.sender().isChecked())
        except NamingError:
            self.errorBox(StringConstants.nameErrorText)
        except ProtocolError:
            self.errorBox(StringConstants.protocolErrorText)

    def toggleFreeze(self):
        try:
            self.controller.toggleFreeze(self.deviceID, self.sender().isChecked())
        except NamingError:
            self.errorBox(StringConstants.nameErrorText)
        except ProtocolError:
            self.errorBox(StringConstants.protocolErrorText)

    def toggleOverlay(self):
        try:
            self.controller.toggleOverlay(self.deviceID, self.sender().isChecked())
        except NamingError:
            self.errorBox(StringConstants.nameErrorText)
        except ProtocolError:
            self.errorBox(StringConstants.protocolErrorText)

    def toggleFade(self):
        try:
            self.controller.toggleFade(self.deviceID, self.sender().isChecked())
        except NamingError:
            self.errorBox(StringConstants.nameErrorText)
        except ProtocolError:
            self.errorBox(StringConstants.protocolErrorText)
