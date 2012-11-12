from PySide.QtGui import QGridLayout, QWidget
from org.muscat.staldates.aldatesx.Buttons import ExpandingButton

class CameraControl(QWidget):
    '''
    GUI to control a camera.
    '''


    def __init__(self, controller, cameraID):
        super(CameraControl, self).__init__()
        self.controller = controller
        self.initUI()
        
    def initUI(self):
        layout = QGridLayout()
        self.setLayout(layout)
        
        btnUp = ExpandingButton()
        layout.addWidget(btnUp, 0, 1, 2, 1)
        btnUp.setText("Up")
        
        btnLeft = ExpandingButton()
        layout.addWidget(btnLeft, 1, 0, 2, 1)
        btnLeft.setText("Left")
        
        btnDown = ExpandingButton()
        layout.addWidget(btnDown, 2, 1, 2, 1)
        btnDown.setText("Down")
        
        btnRight = ExpandingButton()
        layout.addWidget(btnRight, 1, 2, 2, 1)
        btnRight.setText("Right")
        
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
        