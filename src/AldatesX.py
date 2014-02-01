#!/usr/bin/python
'''
Created on 8 Nov 2012

@author: james
'''
from PySide.QtCore import Qt
from PySide.QtGui import QApplication
from org.muscat.staldates.aldatesx.Client import Client
from org.muscat.staldates.aldatesx.Controller import Controller
from org.muscat.staldates.aldatesx.ui.MainWindow import MainWindow
import Pyro4
import argparse
import atexit
import fcntl  # @UnresolvedImport
import logging
import sys
from Pyro4.errors import NamingError, CommunicationError
from org.muscat.staldates.aldatesx.ui.widgets import Dialogs


if __name__ == "__main__":

    pid_file = 'aldatesx.pid'
    fp = open(pid_file, 'w')
    try:
        fcntl.lockf(fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
    # another instance is running
        print "AldatesX is already running."
        sys.exit(1)

    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                        level=logging.INFO)
    app = QApplication(sys.argv)

    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--fullscreen",
                        help="Run in fullscreen mode and hide the mouse cursor",
                        action="store_true")
    args = parser.parse_args()

    try:
        stylesheet = open("AldatesX.qss", "r")
        app.setStyleSheet(stylesheet.read())
    except IOError:
        # never mind
        logging.warn("Cannot find stylesheet, using default system styles.")

    try:
        controller = Pyro4.Proxy("PYRONAME:" + Controller.pyroName)

        myapp = MainWindow(controller)

        client = Client(myapp)
        client.setDaemon(True)
        client.start()
        client.started.wait()
        atexit.register(lambda: controller.unregisterClient(client.uri))

        controller.registerClient(client.uri)

        if args.fullscreen:
            QApplication.setOverrideCursor(Qt.BlankCursor)
            myapp.showFullScreen()
        else:
            myapp.show()
        sys.exit(app.exec_())

    except (NamingError, CommunicationError):
        Dialogs.errorBox("Unable to connect to controller. Please check network connections and try again.")
