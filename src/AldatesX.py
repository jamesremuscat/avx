#!/usr/bin/python
'''
Created on 8 Nov 2012

@author: james
'''
from PySide.QtGui import QApplication
from org.muscat.staldates.aldatesx.Controller import Controller
from org.muscat.staldates.aldatesx.VideoSwitcher import VideoSwitcher
import Pyro4
import sys

class AldatesX(VideoSwitcher):
    
    def __init__(self, controller):
        super(AldatesX, self).__init__(controller)
            
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    controller = Pyro4.Proxy("PYRONAME:" + Controller.pyroName)
    
    myapp = AldatesX(controller)
    myapp.show()
    sys.exit(app.exec_())
