'''
Created on 8 Apr 2013

@author: jrem
'''
from avx import PyroUtils
from avx.controller.messagebus import Subscriber

import Pyro4
import atexit
import threading


class Client(Subscriber, threading.Thread):
    def __init__(self):
        super(Client, self).__init__()
        self.started = threading.Event()

    def run(self):
        PyroUtils.setHostname()
        daemon = Pyro4.Daemon()
        self.uri = daemon.register(self)
        self.bus.subscribe('avx', self)
        self.started.set()

        def shutdown():
            self.bus.unsubscribe('avx', self)
            daemon.shutdown()

        atexit.register(shutdown)
        daemon.requestLoop()

    def getHostIP(self):
        return Pyro4.config.HOST

    def consume_message(self, topic, message):
        msgType, source, data = message.data
        self.handleMessage(msgType, source, data)

    def handleMessage(self, msgType, sourceDeviceID, data):
        pass


class MessageTypes(object):
    OUTPUT_MAPPING = "avx.client.OutputMapping"
