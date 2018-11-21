from avx.devices.Device import Device
from threading import Thread
from time import sleep

import socket


class TCPDevice(Device):
    def __init__(self, deviceID, ipAddress, port, **kwargs):
        super(TCPDevice, self).__init__(deviceID, *kwargs)
        self.remote = (ipAddress, port)
        self._recv_thread = None
        self._connect_thread = None
        self._isConnected = False
        self.socket = None

    def initialise(self):
        self.socket = socket.socket()
        self.socket.settimeout(1)
        self._run_recv_thread = True

        if not (self._connect_thread and self._connect_thread.is_alive()) and not self._isConnected:
            self._connect_thread = Thread(target=self._connect)
            self._connect_thread.daemon = True
            self._connect_thread.start()

    def _connect(self):
        while not self._isConnected and self._run_recv_thread:
            try:
                self.socket.connect(self.remote)
                if not (self._recv_thread and self._recv_thread.is_alive()):
                    self._recv_thread = Thread(target=self._receive)
                    self._recv_thread.daemon = True
                    self._recv_thread.start()
                self._isConnected = True
            except socket.error:
                self.log.warn("Could not connect to {}, will retry.".format(self.remote))
                sleep(5)

    def deinitialise(self):
        self._run_recv_thread = False
        self._isConnected = False
        if self.socket:
            self.socket.close()

    def _receive(self):
        while self._run_recv_thread:
            try:
                data = self.socket.recv(4096)
                if data == '':
                    self.log.warn("Connection closed - attempting to reconnect")
                    sleep(5)
                    self.initialise()
                else:
                    self.on_receive(data)
            except socket.timeout:
                pass

    def send(self, data):
        if self.socket:
            self.socket.send(data)
        else:
            self.log.warn("Tried to send data without a socket: {}".format(data))
