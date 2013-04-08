'''
Created on 8 Apr 2013

@author: jrem
'''
import Pyro4
import atexit
from PySide import QtCore
from org.muscat.staldates.aldatesx import PyroUtils

class Client(Pyro4.threadutil.Thread):

    def __init__(self, aldatesx):
        Pyro4.threadutil.Thread.__init__(self)
        self.aldatesx = aldatesx
        self.started=Pyro4.threadutil.Event()
        
    def run(self):
        PyroUtils.setHostname()
        daemon=Pyro4.Daemon()
        self.uri=daemon.register(self)
        self.started.set()
        atexit.register(lambda : daemon.shutdown())
        daemon.requestLoop()
        
    def errorBox(self, text):
        invoke_in_main_thread(self.aldatesx.errorBox, text)


class InvokeEvent(QtCore.QEvent):
    EVENT_TYPE = QtCore.QEvent.Type(QtCore.QEvent.registerEventType())

    def __init__(self, fn, *args, **kwargs):
        QtCore.QEvent.__init__(self, InvokeEvent.EVENT_TYPE)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs


class Invoker(QtCore.QObject):
    def event(self, event):
        event.fn(*event.args, **event.kwargs)

        return True

_invoker = Invoker()


def invoke_in_main_thread(fn, *args, **kwargs):
    QtCore.QCoreApplication.postEvent(_invoker,
        InvokeEvent(fn, *args, **kwargs))