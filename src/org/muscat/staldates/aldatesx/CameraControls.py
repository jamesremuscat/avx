from PySide.QtGui import QGridLayout, QWidget, QIcon
from PySide.QtCore import QSize
from org.muscat.staldates.aldatesx.Buttons import ExpandingButton
from org.muscat.staldates.aldatesx.Controller import CameraMove, CameraFocus,\
    CameraZoom

class CameraButton(ExpandingButton):
    def __init__(self, cameraBinding):
        super(CameraButton, self).__init__()
        self.cameraBinding = cameraBinding

class CameraControl(QWidget):
    '''
    GUI to control a camera.
    '''


    def __init__(self, controller, cameraID):
        super(CameraControl, self).__init__()
        self.controller = controller
        self.cameraID = cameraID
        self.initUI()
        
    def initUI(self):
        layout = QGridLayout()
        self.setLayout(layout)
        
        btnUp = CameraButton(CameraMove.Up)
        layout.addWidget(btnUp, 0, 1, 2, 1)
        btnUp.pressed.connect(self.move)
        btnUp.released.connect(self.stop)
        btnUp.setIcon(QIcon("/usr/share/icons/Tango/scalable/actions/up.svg"))
        btnUp.setIconSize(QSize(64,64))
        
        btnLeft = CameraButton(CameraMove.Left)
        layout.addWidget(btnLeft, 1, 0, 2, 1)
        btnLeft.pressed.connect(self.move)
        btnLeft.released.connect(self.stop)
        btnLeft.setIcon(QIcon("/usr/share/icons/Tango/scalable/actions/back.svg"))
        btnLeft.setIconSize(QSize(64,64))
        
        btnDown = CameraButton(CameraMove.Down)
        layout.addWidget(btnDown, 2, 1, 2, 1)
        btnDown.pressed.connect(self.move)
        btnDown.released.connect(self.stop)
        btnDown.setIcon(QIcon("/usr/share/icons/Tango/scalable/actions/down.svg"))
        btnDown.setIconSize(QSize(64,64))
        
        btnRight = CameraButton(CameraMove.Right)
        layout.addWidget(btnRight, 1, 2, 2, 1)
        btnRight.pressed.connect(self.move)
        btnRight.released.connect(self.stop)
        btnRight.setIcon(QIcon("/usr/share/icons/Tango/scalable/actions/forward.svg"))
        btnRight.setIconSize(QSize(64,64))
        
        btnZoomIn = CameraButton(CameraZoom.Tele)
        layout.addWidget(btnZoomIn, 0, 3, 2, 1)
        btnZoomIn.setText("Zoom+")
        btnZoomIn.pressed.connect(self.zoom)
        btnZoomIn.released.connect(self.stopZoom)
        
        btnZoomOut = CameraButton(CameraZoom.Wide)
        layout.addWidget(btnZoomOut, 2, 3, 2, 1)
        btnZoomOut.setText("Zoom-")
        btnZoomOut.pressed.connect(self.zoom)
        btnZoomOut.released.connect(self.stopZoom)
        
        btnFocusFar = CameraButton(CameraFocus.Far)
        layout.addWidget(btnFocusFar, 0, 4, 2, 1)
        btnFocusFar.setText("Focus+")
        btnFocusFar.pressed.connect(self.focus)
        btnFocusFar.released.connect(self.stopFocus)
        
        btnFocusNear = CameraButton(CameraFocus.Near)
        layout.addWidget(btnFocusNear, 2, 4, 2, 1)
        btnFocusNear.setText("Focus-")
        btnFocusNear.pressed.connect(self.focus)
        btnFocusNear.released.connect(self.stopFocus)
        
        btnBrightUp = ExpandingButton()
        layout.addWidget(btnBrightUp, 0, 5, 2, 1)
        btnBrightUp.setText("Bright+")

        btnBrightDown = ExpandingButton()
        layout.addWidget(btnBrightDown, 2, 5, 2, 1)
        btnBrightDown.setText("Bright+")
        
        for i in range(1,7):
            btnPresetRecall = CameraButton(i)
            layout.addWidget(btnPresetRecall, 4, i - 1, 2, 1)
            btnPresetRecall.setText(str(i))
            btnPresetRecall.clicked.connect(self.recallPreset)
            
            btnPresetSet = CameraButton(i)
            layout.addWidget(btnPresetSet, 6, i-1, 2, 1)
            btnPresetSet.setText("Set")
            btnPresetSet.clicked.connect(self.storePreset)
            
    def move(self):
        sender = self.sender()
        try:
            return self.controller.move(self.cameraID, sender.cameraBinding)
        except AttributeError:
            return -1
        
    def stop(self):
        self.controller.move(self.cameraID, CameraMove.Stop)
        
    def focus(self):
        sender = self.sender()
        try:
            return self.controller.focus(self.cameraID, sender.cameraBinding)
        except AttributeError:
            return -1
        
    def stopFocus(self):
        self.controller.focus(self.cameraID, CameraFocus.Stop)
        
    def zoom(self):
        sender = self.sender()
        try:
            return self.controller.zoom(self.cameraID, sender.cameraBinding)
        except AttributeError:
            return -1
        
    def stopZoom(self):
        self.controller.zoom(self.cameraID, CameraZoom.Stop)
        
    def storePreset(self):
        sender = self.sender()
        try:
            return self.controller.savePreset(self.cameraID, sender.cameraBinding)
        except AttributeError:
            return -1
        
    def recallPreset(self):
        sender = self.sender()
        try:
            return self.controller.recallPreset(self.cameraID, sender.cameraBinding)
        except AttributeError:
            return -1
        