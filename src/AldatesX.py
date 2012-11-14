#!/usr/bin/python
'''
Created on 8 Nov 2012

@author: james
'''
from PySide.QtGui import QApplication
from org.muscat.staldates.aldatesx.VideoSwitcher import VideoSwitcher
import sys
import Pyro4

class AldatesX(VideoSwitcher):
    
    def __init__(self, controller):
        super(AldatesX, self).__init__(controller)
            
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    controller = Pyro4.Proxy("PYRONAME:aldates.alix")
    
    myapp = AldatesX(controller)
    myapp.show()
    sys.exit(app.exec_())
