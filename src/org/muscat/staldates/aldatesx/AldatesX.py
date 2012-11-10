'''
Created on 8 Nov 2012

@author: james
'''
from PySide.QtGui import *
from PySide.QtCore import *
from PySide.QtUiTools import QUiLoader
import sys
from org.muscat.staldates.aldatesx.VideoSwitcher import VideoSwitcher

class AldatesX(QMainWindow, VideoSwitcher):
    
    def __init__(self):
        super(AldatesX, self).__init__()
        self.setupUi(self)
            
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    myapp = AldatesX()
    myapp.show()
    sys.exit(app.exec_())
