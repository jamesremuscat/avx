from avx.devices import Device
from .constants import CMD_ACK, CMD_ACKREQUEST, CMD_HELLOPACKET, SIZE_OF_HEADER, MessageTypes
from .utils import byteArrayToString
from .getter import ATEMGetter
from .sender import ATEMSender
from .receiver import ATEMReceiver

import socket
import struct
import threading
import time

# Standing on the shoulders of giants:
# Much of this module derives from previous work including:
# - http://skaarhoj.com/fileadmin/BMDPROTOCOL.html
# - https://github.com/mraerino/PyATEM


class ATEM(Device, ATEMGetter, ATEMSender, ATEMReceiver):

    def __init__(self, deviceID, ipAddr, port=9910, **kwargs):
        super(ATEM, self).__init__(deviceID, **kwargs)
        self.ipAddr = ipAddr
        self.port = port
        self.recv_thread = None
        self.connect_thread = None
        self._connect_thread_lock = threading.Lock()
        self._socket = None
        self._isInitialized = False

    def initialise(self):
        if not self._socket:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._socket.bind(('0.0.0.0', self.port))

        self.run_receive = True
        if not (self.recv_thread and self.recv_thread.is_alive()):
            self.recv_thread = threading.Thread(target=self._receivePackets)
            self.recv_thread.daemon = True
            self.recv_thread.start()

        if not (self.connect_thread and self.connect_thread.is_alive()) and not self._isInitialized:
            self._initialiseState()
            self.connect_thread = threading.Thread(target=self._connectToSwitcher)
            self.connect_thread.daemon = True
            self.connect_thread.start()
        else:
            self.log.warn("initialise called while already trying to connect to {} at {}".format(self.deviceID, self.ipAddr))

    def _initialiseState(self):
        self._packetCounter = 0
        self._isInitialized = False
        self._currentUid = 0x1337

        self._system_config = {'inputs': {}, 'audio': {}}
        self._status = {}
        self._config = {'macros': {}, 'multiviewers': {}, 'mediapool': {}, 'transitions': {}}
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
            'tally': {},
            'transition': {}
        }
        self._cameracontrol = {}

        self._state['booted'] = True

    def deinitialise(self):
        self.run_receive = False
        self._state['booted'] = False
        self._isInitialized = False
        if self._socket:
            self._socket.close()
            self._socket = None

    def _receivePackets(self):
        while self.run_receive:
            self.log.debug("Waiting to receive packet")
            data, remoteIP = self._socket.recvfrom(2048)
            self.log.debug("Received {} from {}:{}".format(data.encode('hex_codec'), *remoteIP))

            if remoteIP == (self.ipAddr, self.port) and self.run_receive:  # We might have deinitialised while blocked in recvfrom()
                self._handlePacket(data)
        self.broadcast(MessageTypes.ATEM_DISCONNECTED)
        self.log.info("No longer listening for packets from {}".format(self.deviceID))

    def _handlePacket(self, data):
        header = self._parseCommandHeader(data)
        if header:
            self.log.debug(header)
            self._currentUid = header['uid']
            if header['bitmask'] & CMD_HELLOPACKET:
                self.log.debug('not initialized, received HELLOPACKET, sending ACK packet')
                self._isInitialized = False
                ackDatagram = self._createCommandHeader(CMD_ACK, 0, header['uid'], 0x0)
                threading.Thread(target=self._sendDatagram, args=(ackDatagram,)).start()

            elif (header['bitmask'] & CMD_ACKREQUEST) and (self._isInitialized or len(data) == SIZE_OF_HEADER):
                self.log.debug('initialized, received ACKREQUEST, sending ACK packet')
                self.log.info("Sending ACK for packageId %d" % header['packageId'])
                ackDatagram = self._createCommandHeader(CMD_ACK, 0, header['uid'], header['packageId'])
                threading.Thread(target=self._sendDatagram, args=(ackDatagram,)).start()
                if not self._isInitialized:
                    self._isInitialized = True
                    self.broadcast(MessageTypes.ATEM_CONNECTED, None)
                    self.log.info("Connection to ATEM initialised")

            if len(data) > SIZE_OF_HEADER + 2 and not (header['bitmask'] & CMD_HELLOPACKET):
                threading.Thread(target=self._handlePayload, args=(data[SIZE_OF_HEADER:],)).start()

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
        while len(data) > 0:
            size = struct.unpack('!H', data[0:2])[0]
            packet = data[0:size]
            data = data[size:]

            # skip size and 2 unknown bytes
            packet = packet[4:]
            ptype = packet[:4]
            payload = packet[4:]
            self.log.debug("{}: {}".format(ptype, payload.encode('hex_codec')))
            handler_method = "_recv_{}".format(ptype.encode('utf-8'))
            if handler_method in dir(self):
                func = getattr(self, handler_method)
                if callable(func):
                    payload_bytes = bytearray()
                    payload_bytes.extend(payload)  # Note: In Python2 need to ensure we have a byte array - or else it's a string
                    func(payload_bytes)
                else:
                    self.log.debug("Received {} but method {} is not callable".format(ptype, handler_method))
            else:
                self.log.debug("Unhandled ATEM packet type {}".format(ptype))

    def _connectToSwitcher(self):
        with self._connect_thread_lock:
            while not self._isInitialized and self._state['booted']:
                self.log.info("Attempting to connect to ATEM at {}:{}".format(self.ipAddr, self.port))
                datagram = self._createCommandHeader(CMD_HELLOPACKET, 8, self._currentUid, 0x0)
                datagram += struct.pack('!I', 0x01000000)
                datagram += struct.pack('!I', 0x00)
                self._sendDatagram(datagram)

                time.sleep(5)

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

    def _sendCommand(self, command, payload):

        if not isinstance(payload, str):
            payload = byteArrayToString(payload)

        size = len(command) + len(payload) + 4
        dg = self._createCommandHeader(CMD_ACKREQUEST, size, self._currentUid, 0)
        dg += struct.pack('!H', size)
        dg += "\x00\x00"
        dg += command
        dg += payload
        self._sendDatagram(dg)

    def _sendDatagram(self, datagram):
        if self._socket:
            self.log.debug("Sending packet {} to {}:{}".format(datagram.encode('hex_codec'), self.ipAddr, self.port))
            self._socket.sendto(datagram, (self.ipAddr, self.port))
        else:
            self.log.warn("Tried to send packet to {}:{} but socket was None".format(self.ipAddr, self.port))
