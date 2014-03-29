from PySide.QtGui import QLabel, QToolButton, QSizePolicy, QVBoxLayout
from PySide.QtCore import Qt, QSize, Signal, QEvent


class ExpandingButton(QToolButton):

    def __init__(self, parent=None):
        super(ExpandingButton, self).__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setIconSize(QSize(48, 48))
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)


class InputButton(ExpandingButton):

    def __init__(self, parent=None):
        super(InputButton, self).__init__(parent)
        self.setCheckable(True)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)


class IDedButton(ExpandingButton):

    def __init__(self, ID, parent=None):
        super(IDedButton, self).__init__(parent)
        self.ID = ID


class OutputButton(IDedButton):

    def __init__(self, ID, parent=None):
        super(OutputButton, self).__init__(ID, parent)
        self.inputDisplay = QLabel()
        self.inputDisplay.setText("-")
        layout = QVBoxLayout()
        layout.addWidget(self.inputDisplay)
        layout.setAlignment(Qt.AlignBottom | Qt.AlignHCenter)
        self.setLayout(layout)

    def setInputText(self, text):
        self.inputDisplay.setText(text)


class OptionButton(ExpandingButton):

    def __init__(self, parent=None):
        super(OptionButton, self).__init__(parent)
        self.setCheckable(True)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)


class CameraSelectionButton(InputButton):

    longpress = Signal()

    def __init__(self, parent=None):
        super(CameraSelectionButton, self).__init__(parent)
        self.grabGesture(Qt.TapAndHoldGesture)

    def event(self, evt):
        if evt.type() == QEvent.Gesture:
            gesture = evt.gesture(Qt.TapAndHoldGesture)
            if gesture:
                if gesture.state() == Qt.GestureState.GestureFinished:
                    self.longpress.emit()
                    return True
        return super(CameraSelectionButton, self).event(evt)
