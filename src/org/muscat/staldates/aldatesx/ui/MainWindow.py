from PySide.QtGui import QGridLayout, QMainWindow, QStackedWidget, QWidget
from org.muscat.staldates.aldatesx.ui.widgets.Buttons import ExpandingButton
from org.muscat.staldates.aldatesx.ui.widgets.Clock import Clock
from org.muscat.staldates.aldatesx.ui.widgets.LogViewer import LogViewer
from org.muscat.staldates.aldatesx.ui.widgets.SystemPowerWidget import SystemPowerWidget
from org.muscat.staldates.aldatesx.ui.VideoSwitcher import VideoSwitcher

class MainWindow(QMainWindow):
    def __init__(self, controller):
        super(MainWindow, self).__init__()
        self.controller = controller

        self.setWindowTitle("AldatesX")
        self.resize(1024, 600)
        
        mainScreen = VideoSwitcher(controller, self)
        self.stack = QStackedWidget()
        self.stack.addWidget(mainScreen)
        
        outer = QWidget()
        mainLayout = QGridLayout()
        mainLayout.addWidget(self.stack, 0, 0, 1, 7)
        
        spc = SystemPowerWidget()
        self.powerControlIndex = self.stack.addWidget(spc)
        spc.b.clicked.connect(self.showMainScreen)
        
        spc.btnOn.clicked.connect(self.controller.systemPowerOn)
        spc.btnOff.clicked.connect(self.controller.systemPowerOff)
        
        syspower = ExpandingButton()
        syspower.setText("System Power")
        syspower.clicked.connect(self.showSystemPower)
        mainLayout.addWidget(syspower, 1, 0)
        
        self.lv = LogViewer()
        self.logIndex = self.stack.addWidget(self.lv)
        self.lv.b.clicked.connect(self.showMainScreen)
        
        log = ExpandingButton()
        log.setText("Log")
        log.clicked.connect(self.showLog)
        mainLayout.addWidget(log, 1, 5)
        
        mainLayout.addWidget(Clock(), 1, 6)
        
        mainLayout.setRowStretch(0, 8)  
        mainLayout.setRowStretch(1, 0)  
        
        outer.setLayout(mainLayout)
        
        self.setCentralWidget(outer)
        
    def showSystemPower(self):
        if hasattr(self, "powerControlIndex"):
            self.stack.setCurrentIndex(self.powerControlIndex)
        
    def showLog(self):
        self.stack.setCurrentIndex(self.logIndex)
        self.lv.displayLog(self.controller.getLog())
        
    
    def showMainScreen(self):
        self.stack.setCurrentIndex(0)