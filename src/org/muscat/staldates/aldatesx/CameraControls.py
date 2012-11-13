from PySide.QtGui import QGridLayout, QWidget
from org.muscat.staldates.aldatesx.Buttons import ExpandingButton
from org.muscat.staldates.aldatesx.Controller import CameraMove

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
        btnUp.setText("Up")
        btnUp.pressed.connect(self.move)
        btnUp.released.connect(self.stop)
        
        btnLeft = CameraButton(CameraMove.Left)
        layout.addWidget(btnLeft, 1, 0, 2, 1)
        btnLeft.setText("Left")
        btnLeft.pressed.connect(self.move)
        btnLeft.released.connect(self.stop)
        
        btnDown = CameraButton(CameraMove.Down)
        layout.addWidget(btnDown, 2, 1, 2, 1)
        btnDown.setText("Down")
        btnDown.pressed.connect(self.move)
        btnDown.released.connect(self.stop)
        
        btnRight = CameraButton(CameraMove.Right)
        layout.addWidget(btnRight, 1, 2, 2, 1)
        btnRight.setText("Right")
        btnRight.pressed.connect(self.move)
        btnRight.released.connect(self.stop)
        
        btnZoomIn = ExpandingButton()
        layout.addWidget(btnZoomIn, 0, 3, 2, 1)
        btnZoomIn.setText("Zoom+")
        
        btnZoomOut = ExpandingButton()
        layout.addWidget(btnZoomOut, 2, 3, 2, 1)
        btnZoomOut.setText("Zoom-")
        
        btnFocusFar = ExpandingButton()
        layout.addWidget(btnFocusFar, 0, 4, 2, 1)
        btnFocusFar.setText("Focus+")
        
        btnFocusNear = ExpandingButton()
        layout.addWidget(btnFocusNear, 2, 4, 2, 1)
        btnFocusNear.setText("Focus-")
        
        btnBrightUp = ExpandingButton()
        layout.addWidget(btnBrightUp, 0, 5, 2, 1)
        btnBrightUp.setText("Bright+")

        btnBrightDown = ExpandingButton()
        layout.addWidget(btnBrightDown, 2, 5, 2, 1)
        btnBrightDown.setText("Bright+")
        
        for i in range(1,7):
            btnPresetRecall = ExpandingButton()
            layout.addWidget(btnPresetRecall, 4, i - 1, 2, 1)
            btnPresetRecall.setText(str(i))
            
            btnPresetSet = ExpandingButton()
            layout.addWidget(btnPresetSet, 6, i-1, 2, 1)
            btnPresetSet.setText("Set")
            
    def move(self):
        sender = self.sender()
        try:
            return self.controller.move(self.cameraID, sender.cameraBinding)
        except AttributeError:
            return -1
        
    def stop(self):
        self.controller.move(self.cameraID, CameraMove.Stop)
        