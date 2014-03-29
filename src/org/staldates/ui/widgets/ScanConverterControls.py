from PySide.QtGui import QWidget, QGridLayout, QVBoxLayout, QIcon
from org.staldates.ui.widgets.Buttons import OptionButton


class OverscanFreezeWidget(QWidget):

    def __init__(self, parent=None):
        super(OverscanFreezeWidget, self).__init__(parent)

        self.btnOverscan = OptionButton()
        self.btnOverscan.setText("Overscan")
        self.btnOverscan.setChecked(True)
        self.btnOverscan.setIcon(QIcon("icons/view-fullscreen.svg"))

        self.btnFreeze = OptionButton()
        self.btnFreeze.setText("Freeze")
        self.btnFreeze.setIcon(QIcon("icons/media-playback-pause.svg"))

        self.layout()

    def layout(self):
        layout = QVBoxLayout()
        layout.addWidget(self.btnOverscan)
        layout.addWidget(self.btnFreeze)

        self.setLayout(layout)


class EclipseWidget(OverscanFreezeWidget):

    def __init__(self, parent=None):
        self.btnFade = OptionButton()
        self.btnFade.setText("Fade")
        self.btnFade.setIcon(QIcon("icons/preferences-desktop-screensaver.svg"))

        self.btnOverlay = OptionButton()
        self.btnOverlay.setText("Overlay")
        self.btnOverlay.setIcon(QIcon("icons/preferences-system-windows.svg"))

        super(EclipseWidget, self).__init__(parent)

    def layout(self):
        layout = QGridLayout()
        layout.addWidget(self.btnOverlay, 0, 0)
        layout.addWidget(self.btnOverscan, 0, 1)
        layout.addWidget(self.btnFreeze, 1, 0)
        layout.addWidget(self.btnFade, 1, 1)
        self.setLayout(layout)
