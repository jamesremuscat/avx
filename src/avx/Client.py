'''
Created on 8 Apr 2013

@author: jrem
'''
from avx import PyroUtils

import Pyro4
import atexit
import threading


class Client(threading.Thread):

    def __init__(self):
        super(Client, self).__init__()
        self.started = threading.Event()

    def run(self):
        PyroUtils.setHostname()
        daemon = Pyro4.Daemon()
        self.uri = daemon.register(self)
        self.started.set()
        atexit.register(lambda: daemon.shutdown())
        daemon.requestLoop()

    def getHostIP(self):
        return Pyro4.config.HOST

    @Pyro4.expose
    def handleMessage(self, msgType, sourceDeviceID, data):
        pass


class MessageTypes(object):
    OUTPUT_MAPPING = "avx.client.OutputMapping"
