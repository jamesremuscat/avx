'''
Created on 21 Mar 2018

@author: james
'''
from avx.devices.net import TCPDevice
from avx.devices.serial.SerialDevice import SerialDevice
from avx.devices.serial.VISCACamera import VISCACommandsMixin


class DVIPCamera(TCPDevice, VISCACommandsMixin):
    def __init__(self, deviceID, ipAddress, port=5002, **kwargs):
        super(DVIPCamera, self).__init__(deviceID, ipAddress, port, **kwargs)

    def on_receive(self, data):
        self.log.debug("Received: {}".format(data.encode('hex_codec')))

    def sendVISCA(self, data):
        data_bytes = [0x81] + data + [0xFF]
        length = len(data_bytes) + 2

        self.send(
            SerialDevice.byteArrayToString([
                length >> 8,
                length & 0xFF
            ] + data_bytes)
        )
