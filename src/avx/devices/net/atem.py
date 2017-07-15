from avx.devices import Device

import logging
import socket
import struct
import threading

# Standing on the shoulders of giants:
# Much of this module derives from previous work including:
# - http://skaarhoj.com/fileadmin/BMDPROTOCOL.html
# - https://github.com/mraerino/PyATEM


# size of header data
SIZE_OF_HEADER = 0x0c

# packet types
CMD_NOCOMMAND = 0x00
CMD_ACKREQUEST = 0x01
CMD_HELLOPACKET = 0x02
CMD_RESEND = 0x04
CMD_UNDEFINED = 0x08
CMD_ACK = 0x10


class ATEM(Device):

    def __init__(self, deviceID, ipAddr, port=9910, **kwargs):
        super(ATEM, self).__init__(deviceID, **kwargs)
        self.ipAddr = ipAddr
        self.port = port
        self.log = logging.getLogger(deviceID)
        self.recv_thread = None

    def initialise(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind(('0.0.0.0', self.port))

        self._packetCounter = 0
        self._isInitialized = False
        self._currentUid = 0x1337

        self._system_config = {'inputs': {}, 'audio': {}}
        self._status = {}
        self._config = {'multiviewers': {}, 'mediapool': {}}
        self._state = {
            'program': {},
            'preview': {},
            'keyers': {},
            'dskeyers': {},
            'aux': {},
            'mediaplayer': {},
            'mediapool': {},
            'audio': {},
            'tally_by_index': {},
            'tally': {}
        }
        self._cameracontrol = {}

        self._state['booted'] = True

        self.run_receive = True
        if not (self.recv_thread and self.recv_thread.is_alive()):
            self.recv_thread = threading.Thread(target=self._receivePackets)
            self.recv_thread.daemon = True
            self.recv_thread.start()

        self._connectToSwitcher()

    def deinitialise(self):
        self.run_receive = False
        self._state['booted'] = False

    def _receivePackets(self):
        while self.run_receive:
            data, remoteIP = self._socket.recvfrom(2048)
            self.log.debug("Received {} from {}".format(data.encode('hex_codec'), remoteIP))

            header = self._parseCommandHeader(data)
            if header:
                self._currentUid = header['uid']
                if header['bitmask'] & CMD_HELLOPACKET:
                    # print('not initialized, received HELLOPACKET, sending ACK packet')
                    self._isInitialized = False
                    ackDatagram = self._createCommandHeader(CMD_ACK, 0, header['uid'], 0x0)
                    self._sendDatagram(ackDatagram)

                elif (header['bitmask'] & CMD_ACKREQUEST) and (self._isInitialized or len(data) == SIZE_OF_HEADER):
                    # print('initialized, received ACKREQUEST, sending ACK packet')
                    # print("Sending ACK for packageId %d" % header['packageId'])
                    ackDatagram = self._createCommandHeader(CMD_ACK, 0, header['uid'], header['packageId'])
                    self._sendDatagram(ackDatagram)
                    if not self._isInitialized:
                        self._isInitialized = True

                if len(data) > SIZE_OF_HEADER + 2 and not (header['bitmask'] & CMD_HELLOPACKET):
                    self._handlePayload(data)

    def _parseCommandHeader(self, datagram):
        header = {}

        if len(datagram) >= SIZE_OF_HEADER:
            header['bitmask'] = struct.unpack('B', datagram[0:1])[0] >> 3
            header['size'] = struct.unpack('!H', datagram[0:2])[0] & 0x07FF
            header['uid'] = struct.unpack('!H', datagram[2:4])[0]
            header['ackId'] = struct.unpack('!H', datagram[4:6])[0]
            header['packageId'] = struct.unpack('!H', datagram[10:12])[0]
            return header
        return False

    def _handlePayload(self, data):
        pass

    def _connectToSwitcher(self):
        datagram = self._createCommandHeader(CMD_HELLOPACKET, 8, self._currentUid, 0x0)
        datagram += struct.pack('!I', 0x01000000)
        datagram += struct.pack('!I', 0x00)
        self._sendDatagram(datagram)

    def _createCommandHeader(self, bitmask, payloadSize, uid, ackId):
        buf = b''
        packageId = 0

        if not (bitmask & (CMD_HELLOPACKET | CMD_ACK)):
            self._packetCounter += 1
            packageId = self._packetCounter

        val = bitmask << 11
        val |= (payloadSize + SIZE_OF_HEADER)
        buf += struct.pack('!H', val)
        buf += struct.pack('!H', uid)
        buf += struct.pack('!H', ackId)
        buf += struct.pack('!I', 0)
        buf += struct.pack('!H', packageId)
        return buf

    def _sendDatagram(self, datagram):
        self.log.debug("Sending packet {} to {}:{}".format(datagram.encode('hex_codec'), self.ipAddr, self.port))
        self._socket.sendto(datagram, (self.ipAddr, self.port))
