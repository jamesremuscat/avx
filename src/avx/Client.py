'''
Created on 8 Apr 2013

@author: jrem
'''
from avx import PyroUtils
import Pyro4
import atexit


class Client(Pyro4.threadutil.Thread):

    def __init__(self):
        Pyro4.threadutil.Thread.__init__(self)
        self.started = Pyro4.threadutil.Event()

    def run(self):
        PyroUtils.setHostname()
        daemon = Pyro4.Daemon()
        self.uri = daemon.register(self)
        self.started.set()
        atexit.register(lambda: daemon.shutdown())
        daemon.requestLoop()

    def getHostIP(self):
        return Pyro4.config.HOST
