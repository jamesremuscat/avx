from PySide.QtGui import *
from PySide.QtCore import *
from Buttons import InputButton, OutputButton, ExpandingButton
from org.muscat.staldates.aldatesx.ExtrasSwitcher import ExtrasSwitcher
from org.muscat.staldates.aldatesx.CameraControls import CameraControl

class VideoSwitcher(QMainWindow):
    def __init__(self, controller):
        super(VideoSwitcher, self).__init__()
        self.controller = controller
        self.setupUi()
        
    def setupUi(self):
        self.setWindowTitle("Video Switcher")
        self.resize(1024, 768)
        self.centralwidget = QWidget(self)
        self.centralwidget.setGeometry(0, 0, 1024, 768)
        gridlayout = QGridLayout(self.centralwidget)
        
        ''' Buttons added to inputs should have a numeric ID set equal to their input number on the Aldates main switcher. '''
        self.inputs = QButtonGroup()
        
        self.btnDVD = InputButton(self.centralwidget)
        self.btnDVD.setText("DVD")
        gridlayout.addWidget(self.btnDVD, 0, 0)
        self.inputs.addButton(self.btnDVD, 4)
        
        self.btnCamera1 = InputButton(self.centralwidget)
        self.btnCamera1.setText("Camera 1")
        gridlayout.addWidget(self.btnCamera1, 0, 1)
        self.inputs.addButton(self.btnCamera1, 1)
        
        self.btnCamera2 = InputButton(self.centralwidget)
        self.btnCamera2.setText("Camera 2")
        gridlayout.addWidget(self.btnCamera2, 0, 2)
        self.inputs.addButton(self.btnCamera2, 2)
        
        self.btnCamera3 = InputButton(self.centralwidget)
        self.btnCamera3.setText("Camera 3")
        gridlayout.addWidget(self.btnCamera3, 0, 3)
        self.inputs.addButton(self.btnCamera3, 3)
        
        self.btnExtras = InputButton(self.centralwidget)
        self.btnExtras.setText("Extras")
        gridlayout.addWidget(self.btnExtras, 0, 4)
        self.inputs.addButton(self.btnExtras, 5)
        
        self.btnVisualsPC = InputButton(self.centralwidget)
        self.btnVisualsPC.setText("Visuals PC")
        gridlayout.addWidget(self.btnVisualsPC, 0, 5)
        self.inputs.addButton(self.btnVisualsPC, 6)
        
        self.btnBlank = InputButton(self.centralwidget)
        self.btnBlank.setText("Blank")
        gridlayout.addWidget(self.btnBlank, 0, 6)
        self.inputs.addButton(self.btnBlank, 0)
        
        self.extrasSwitcher = ExtrasSwitcher(self.controller)
        self.blank = QWidget(self)
        gridlayout.addWidget(self.blank, 1, 0, 1, 5)
        
        outputsGrid = QGridLayout()
        
        self.btnProjectors = OutputButton(self.centralwidget, ID=2)
        self.btnProjectors.setText("Projectors")
        outputsGrid.addWidget(self.btnProjectors, 0, 1)

        self.btnChurch = OutputButton(self.centralwidget, ID=4)
        self.btnChurch.setText("Church")
        outputsGrid.addWidget(self.btnChurch, 1, 0)
        self.btnSpecial = OutputButton(self.centralwidget, ID=7)
        self.btnSpecial.setText("Special")
        outputsGrid.addWidget(self.btnSpecial, 1, 1)
        
        self.btnGallery = OutputButton(self.centralwidget, ID=6)
        self.btnGallery.setText("Gallery")
        outputsGrid.addWidget(self.btnGallery, 2, 0)
        self.btnWelcome = OutputButton(self.centralwidget, ID=5)
        self.btnWelcome.setText("Welcome")
        outputsGrid.addWidget(self.btnWelcome, 2, 1)

        self.btnFont = OutputButton(self.centralwidget, ID=3)
        self.btnFont.setText("Font")
        outputsGrid.addWidget(self.btnFont, 3, 0)
        self.btnRecord = OutputButton(self.centralwidget, ID=8)
        self.btnRecord.setText("Record")
        outputsGrid.addWidget(self.btnRecord, 3, 1)

        self.btnPCMix = ExpandingButton(self.centralwidget)
        self.btnPCMix.setText("PC Mix")
        outputsGrid.addWidget(self.btnPCMix, 4, 0)
        self.btnAll = OutputButton(self.centralwidget, ID=0)
        self.btnAll.setText("All")
        outputsGrid.addWidget(self.btnAll, 4, 1)
        
        outputsGrid.setColumnMinimumWidth(0, 100)
        outputsGrid.setColumnMinimumWidth(1, 100)
        outputsGrid.setColumnStretch(0, 1)
        outputsGrid.setColumnStretch(1, 1)
        
        gridlayout.addLayout(outputsGrid, 1, 6)

        gridlayout.setRowMinimumHeight(1, 500)      
        gridlayout.setRowStretch(0, 1)  
        gridlayout.setRowStretch(1, 5)  
        QMetaObject.connectSlotsByName(self)
        self.setInputClickHandlers()
        self.setOutputClickHandlers()
        self.gridlayout = gridlayout
        
    def setInputClickHandlers(self):
        self.btnCamera1.clicked.connect(self.handleInputSelect)
        self.btnCamera2.clicked.connect(self.handleInputSelect)
        self.btnCamera3.clicked.connect(self.handleInputSelect)
        self.btnDVD.clicked.connect(self.handleInputSelect)
        self.btnExtras.clicked.connect(self.handleInputSelect)
        self.btnVisualsPC.clicked.connect(self.handleInputSelect)
        
    def setOutputClickHandlers(self):
        self.btnProjectors.clicked.connect(self.handleOutputSelect)
        self.btnChurch.clicked.connect(self.handleOutputSelect)
        self.btnSpecial.clicked.connect(self.handleOutputSelect)
        self.btnGallery.clicked.connect(self.handleOutputSelect)
        self.btnWelcome.clicked.connect(self.handleOutputSelect)
        self.btnFont.clicked.connect(self.handleOutputSelect)
        self.btnRecord.clicked.connect(self.handleOutputSelect)
        self.btnAll.clicked.connect(self.handleOutputSelect)
        ''' btnPCMix is a special case since that's on a different switcher '''
        
    def handleInputSelect(self):
        print "Input selected: " + str(self.inputs.checkedId())
        # Eventually switch the preview switcher here too
        self.gridlayout.removeWidget(self.gridlayout.itemAtPosition(1,0).widget())
        if self.inputs.checkedId() == 5:
            self.blank.hide()
            self.gridlayout.addWidget(self.extrasSwitcher, 1, 0, 1, 5)
            self.extrasSwitcher.show()
        elif self.inputs.checkedId() == 1:
            self.gridlayout.addWidget(CameraControl(self.controller, 1), 1, 0, 1, 5)
        else:
            self.extrasSwitcher.hide()
            self.blank.hide()
            self.gridlayout.addWidget(self.blank, 1, 0, 1, 5)
        
    def handleOutputSelect(self):
        outputChannel = self.sender().ID
        inputChannel = self.inputs.checkedId()
        
        if inputChannel == 5:
            self.extrasSwitcher.take()
        
        self.controller.switch("Main", inputChannel, outputChannel)
        
