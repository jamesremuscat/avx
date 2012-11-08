'''
Created on 8 Nov 2012

@author: james
'''
from PySide.QtGui import *
from PySide.QtCore import *
from PySide.QtUiTools import QUiLoader
import sys

class AldatesX(QWidget):
    def initUI(self):
        loader = QUiLoader()
        file = QFile("/home/james/workspace/AldatesX/ui/VideoSwitcher.ui")
        file.open(QFile.ReadOnly)
        ui = loader.load(file, self)
        file.close()
        ui.show()

if __name__ == "__main__":
    

    app = QApplication(sys.argv)
    myapp = AldatesX()
    myapp.initUI()
    myapp.show()
    sys.exit(app.exec_())
