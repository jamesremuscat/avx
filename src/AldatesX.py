#!/usr/bin/python
'''
Created on 8 Nov 2012

@author: james
'''
from PySide.QtGui import QApplication
from PySide.QtCore import Qt
from org.muscat.staldates.aldatesx.Controller import Controller
from org.muscat.staldates.aldatesx.ui.VideoSwitcher import VideoSwitcher
import Pyro4
import sys
import logging
import argparse
import fcntl  # @UnresolvedImport
import atexit
from org.muscat.staldates.aldatesx.Client import Client

class AldatesX(VideoSwitcher):
    
    def __init__(self, controller):
        super(AldatesX, self).__init__(controller)
            
if __name__ == "__main__":
    
    pid_file = 'aldatesx.pid'
    fp = open(pid_file, 'w')
    try:
        fcntl.lockf(fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
    # another instance is running
        print "AldatesX is already running."
        sys.exit(1)
    
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.INFO)
    app = QApplication(sys.argv)
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--fullscreen", help="Run in fullscreen mode and hide the mouse cursor", action="store_true")
    args = parser.parse_args()

    try:
        stylesheet = open("AldatesX.qss", "r")
        app.setStyleSheet(stylesheet.read())
    except IOError:
        # never mind
        logging.warn("Cannot find stylesheet, using default system styles.")
    
    controller = Pyro4.Proxy("PYRONAME:" + Controller.pyroName)
    
    myapp = AldatesX(controller)
    
    client = Client(myapp)
    client.setDaemon(True)
    client.start()
    client.started.wait()
    atexit.register(lambda : controller.unregisterClient(client.uri))
    
    controller.registerClient(client.uri)
    
    
    if args.fullscreen:
        QApplication.setOverrideCursor(Qt.BlankCursor)
        myapp.showFullScreen()
    else:
        myapp.show()
    sys.exit(app.exec_())
