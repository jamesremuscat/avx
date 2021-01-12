'''
Created on 21 Mar 2018

@author: james
'''
from avx.devices.net import TCPDevice
from avx.devices.serial.SerialDevice import SerialDevice
from avx.devices.serial.VISCACamera import VISCACommandsMixin
from threading import Event, Lock, ThreadError


def _split_response(response_bytes):
    packets = []

    remaining = map(ord, response_bytes[2:])
    while True:
        try:
            idx = remaining.index(0xFF)
            packet, remaining = remaining[0:idx + 1], remaining[idx + 1:]
            packets.append(packet)
        except ValueError:
            return packets


class DVIPCamera(TCPDevice, VISCACommandsMixin):

    ACK_TIMEOUT = 0.25  # If we don't get an ack in this time, we're probably not getting one.

    def __init__(self, deviceID, ipAddress, port=5002, **kwargs):
        super(DVIPCamera, self).__init__(deviceID, ipAddress, port, **kwargs)
        self._send_lock = Lock()
        self._ack = Event()
        self._await_response = Lock()
        self._response_received = Event()
        self._last_response = None

    def on_receive(self, data):
        self.log.debug("Received: {}".format(data.encode('hex_codec')))
        packets = _split_response(data)
        for packet in packets:
            response_type = (packet[1] & 0x70) >> 4
            if response_type in [4, 5, 6]:  # 4 = ack, 5 = response, 6 = nack
                try:
                    self._ack.set()
                except ThreadError:
                    pass
            if response_type == 5:
                self._last_response = packet
                self._response_received.set()

    def sendVISCA(self, data):
        with self._send_lock:
            self._ack.clear()
            data_bytes = [0x81] + data + [0xFF]
            length = len(data_bytes) + 2

            self.send(
                SerialDevice.byteArrayToString([
                    length >> 8,
                    length & 0xFF
                ] + data_bytes)
            )
            self._ack.wait(self.ACK_TIMEOUT)

    def getVISCA(self, commandBytes):
        with self._await_response:
            self._response_received.clear()
            self.sendVISCA(commandBytes)
            self._response_received.wait()
            response = self._last_response
            self._last_response = None
            self._response_received.clear()
            return response
