'''
Created on 8 Nov 2012

@author: james
'''
from PySide.QtGui import *
from PySide.QtCore import *
from org.muscat.staldates.aldatesx.VideoSwitcher import VideoSwitcher
from org.muscat.staldates.aldatesx.Controller import Controller
from org.muscat.staldates.aldatesx.devices.KramerVP88 import KramerVP88
import sys
from org.muscat.staldates.aldatesx.devices.Inline3808 import Inline3808

class AldatesX(VideoSwitcher):
    
    def __init__(self, controller):
        super(AldatesX, self).__init__(controller)
            
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    controller = Controller()
    
    mainSwitcher = KramerVP88("Main", "/dev/ttyUSB0", 1)
    controller.addDevice(mainSwitcher)
    
    extrasSwitcher = Inline3808("Extras", "/dev/ttyUSB0")
    controller.addDevice(extrasSwitcher)
    
    myapp = AldatesX(controller)
    myapp.show()
    sys.exit(app.exec_())
