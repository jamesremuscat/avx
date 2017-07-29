from avx.devices.Device import Device
from socket import socket
from threading import Thread
from time import sleep


class HyperDeck(Device):
    def __init__(self, deviceID, ipAddress, port=9993):
        super(HyperDeck, self).__init__(deviceID)
        self.remote = (ipAddress, port)
        self._recv_thread = None

    def initialise(self):
        self.socket = socket()
        self.socket.connect(self.remote)
        self._run_recv_thread = True
        self._data_buffer = ''
        if not (self._recv_thread and self._recv_thread.is_alive()):
            self._recv_thread = Thread(target=self._receive)
            self._recv_thread.daemon = True
            self._recv_thread.start()

    def deinitialise(self):
        self._run_recv_thread = False

    def _receive(self):
        while self._run_recv_thread:
            data = self.socket.recv(4096)
            if data == '':
                self.log.warn("Connection closed - attempting to reconnect")
                sleep(5)
                self.initialise()
            else:
                # In case the response is larger than the recv buffer
                # we need to check for a completed message - that is,
                # one with an empty line at the end
                self._data_buffer += data
                if self._data_buffer[-4:] == "\r\n\r\n":
                    self._handle_data(self._data_buffer)
                    self._data_buffer = ''

    def _handle_data(self, data):
        # data packets are of form '000 payload text[:\r\nextra text]\r\n\r\n'
        code = data[0:3]
        payload = data[4:].strip().split("\r\n")
        extra = []
        if payload[0][-1] == ":":
            extra = payload[1:]
            payload = payload[0]

        handler_method_name = "_recv_{}".format(code)
        if hasattr(self, handler_method_name) and callable(getattr(self, handler_method_name)):
            getattr(self, handler_method_name)(payload, extra)
        else:
            self.log.debug("Unhandled packet type {}: {}".format(code, payload))

    def _recv_500(self, payload, extra):
        print payload, extra
