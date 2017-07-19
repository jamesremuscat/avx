from avx.devices import Device
from avx.devices.Device import InvalidArgumentException
from avx.devices.net.atem_constants import ClipType, DownconverterMode, ExternalPortType, MessageTypes, MultiviewerLayout, PortType, VideoMode, VideoSource

import ctypes
import logging
import socket
import struct
import threading
import time

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

LABELS_PORTS_EXTERNAL = {0: 'SDI', 1: 'HDMI', 2: 'Component', 3: 'Composite', 4: 'SVideo'}


def convert_cstring(bs):
    return ctypes.create_string_buffer(str(bs)).value.decode('utf-8')


def parseBitmask(num, labels):
    states = {}
    for i, label in enumerate(labels):
        states[label] = bool(num & (1 << len(labels) - i - 1))
    return states


def byteArrayToString(byteArray):
    return ''.join(chr(b) for b in byteArray)


def requiresInit(func):
    def inner(self, *args):
        if not self._isInitialized:
            raise NotInitializedException()
        func(self, *args)
    return inner


def assertTopology(topType, argIndex):
    def wrap(func):
        def wrapped_func(self, *args):
            if argIndex >= len(args):
                value = func.__defaults__[argIndex - len(args)]
            else:
                value = args[argIndex]
            limit = self._system_config['topology'][topType]

            if value <= 0 or value > limit:
                raise InvalidArgumentException

            func(self, *args)
        return wrapped_func
    return wrap


class NotInitializedException(Exception):
    pass


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

        self._initialiseState()

        self.run_receive = True
        if not (self.recv_thread and self.recv_thread.is_alive()):
            self.recv_thread = threading.Thread(target=self._receivePackets)
            self.recv_thread.daemon = True
            self.recv_thread.start()

        threading.Thread(target=self._connectToSwitcher).start()

    def _initialiseState(self):
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

    def deinitialise(self):
        self.run_receive = False
        self._state['booted'] = False

    def _receivePackets(self):
        while self.run_receive:
            data, remoteIP = self._socket.recvfrom(2048)
            # self.log.debug("Received {} from {}:{}".format(data.encode('hex_codec'), *remoteIP))

            if remoteIP == (self.ipAddr, self.port):
                self._handlePacket(data)

    def _handlePacket(self, data):
                header = self._parseCommandHeader(data)
                if header:
                    self.log.debug(data.encode('hex_codec'))
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
                            self.log.info("Connection to ATEM initialised")

                    if len(data) > SIZE_OF_HEADER + 2 and not (header['bitmask'] & CMD_HELLOPACKET):
                        self._handlePayload(data[SIZE_OF_HEADER:])

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
                    self.log.warning("Received {} but method {} is not callable".format(ptype, handler_method))
            else:
                self.log.warning("Unhandled ATEM packet type {}".format(ptype))

    def _connectToSwitcher(self):
        while not self._isInitialized:
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
        self.log.debug("Sending packet {} to {}:{}".format(datagram.encode('hex_codec'), self.ipAddr, self.port))
        self._socket.sendto(datagram, (self.ipAddr, self.port))

#############
# Device-internal ATEM packet handling functions
#############

    def _recv__ver(self, data):
        major, minor = struct.unpack('!HH', data[0:4])
        self._system_config['version'] = "{}.{}".format(major, minor)

    def _recv__pin(self, data):
        self._system_config['name'] = data

    def _recv_Warn(self, text):
        self.log.warning(text)

    def _recv__top(self, data):
        self._system_config['topology'] = {}
        datalabels = ['mes', 'sources', 'color_generators', 'aux_busses', 'dsks', 'stingers', 'dves',
                      'supersources']
        for i, label in enumerate(datalabels):
            self._system_config['topology'][label] = data[i]

        self._system_config['topology']['hasSD'] = (data[9] > 0)

    def _recv__MeC(self, data):
        index = data[0]
        self._system_config.setdefault('keyers', {})[index] = data[1]

    def _recv__mpl(self, data):
        self._system_config['media_players'] = {}
        self._system_config['media_players']['still'] = data[0]
        self._system_config['media_players']['clip'] = data[1]

    def _recv__MvC(self, data):
        self._system_config['multiviewers'] = data[0]

    def _recv__SSC(self, data):
        self._system_config['super_source_boxes'] = data[0]

    def _recv__TlC(self, data):
        self._system_config['tally_channels'] = data[4]

    def _recv__AMC(self, data):
        self._system_config['audio_channels'] = data[0]
        self._system_config['has_monitor'] = (data[1] > 0)

    def _recv__VMC(self, data):
        videomodes = (data[1] << 16) | (data[2] << 8) | (data[3])
        for vidmode in VideoMode:
            has_mode = ((videomodes >> (24 - vidmode.value - 1)) & 0x1) > 0
            self._system_config.setdefault('video_modes', {})[vidmode] = has_mode

    def _recv__MAC(self, data):
        self._system_config['macro_banks'] = data[0]

    def _recv_Powr(self, data):
        self._status['power'] = parseBitmask(data[0], ['main', 'backup'])

    def _recv_DcOt(self, data):
        self._config['down_converter'] = DownconverterMode(data[0])

    def _recv_VidM(self, data):
        self._config['video_mode'] = VideoMode(data[0])

    def _recv_InPr(self, data):
        index = struct.unpack('!H', data[0:2])[0]
        self._system_config['inputs'][index] = {}
        input_setting = self._system_config['inputs'][index]
        input_setting['name_long'] = convert_cstring(data[2:22])
        input_setting['name_short'] = convert_cstring(data[22:26])
        input_setting['types_available'] = parseBitmask(data[27], LABELS_PORTS_EXTERNAL)
        input_setting['port_type_external'] = ExternalPortType(data[29])
        input_setting['port_type_internal'] = PortType(data[30])
        input_setting['availability'] = parseBitmask(data[32], ['Auxilary', 'Multiviewer', 'SuperSourceArt',
                                                                'SuperSourceBox', 'KeySource'])
        input_setting['me_availability'] = parseBitmask(data[33], ['ME1', 'ME2'])

    def _recv_MvPr(self, data):
        index = data[0]
        self._config['multiviewers'].setdefault(index, {})['layout'] = MultiviewerLayout(data[1])

    def _recv_MvIn(self, data):
        index = data[0]
        window = data[1]
        self._config['multiviewers'].setdefault(index, {}).setdefault('windows', {})[window] = VideoSource(struct.unpack('!H', data[2:4])[0])

    def _recv_PrgI(self, data):
        meIndex = data[0]
        self._state['program'][meIndex] = VideoSource(struct.unpack('!H', data[2:4])[0])
        # TODO self.pgmInputHandler(self)

    def _recv_PrvI(self, data):
        meIndex = data[0]
        self._state['preview'][meIndex] = VideoSource(struct.unpack('!H', data[2:4])[0])

    def _recv_KeOn(self, data):
        meIndex = data[0]
        keyer = data[1]
        self._state['keyers'].setdefault(meIndex, {})[keyer] = (data[2] != 0)

    def _recv_DskB(self, data):
        keyer = data[0]
        keyer_setting = self._state['dskeyers'].setdefault(keyer, {})
        keyer_setting['fill'] = VideoSource(struct.unpack('!H', data[2:4])[0])
        keyer_setting['key'] = VideoSource(struct.unpack('!H', data[4:6])[0])

    def _recv_DskS(self, data):
        keyer = data[0]
        dsk_setting = self._state['dskeyers'].setdefault(keyer, {})
        dsk_setting['on_air'] = (data[1] != 0)
        dsk_setting['in_transition'] = (data[2] != 0)
        dsk_setting['auto_transitioning'] = (data[3] != 0)
        dsk_setting['frames_remaining'] = data[4]

    def _recv_AuxS(self, data):  # Aux source set
        auxIndex = data[0]
        self._state['aux'][auxIndex] = VideoSource(struct.unpack('!H', data[2:4])[0])
        self.broadcast(MessageTypes.AUX_OUTPUT_MAPPING, self._state['aux'])

    def _recv_CCdo(self, data):
        pass

    def _recv_CCdP(self, data):
        pass

    def _recv_RCPS(self, data):
        player_num = data[0]
        player = self._state['mediaplayer'].setdefault(player_num, {})
        player['playing'] = bool(data[1])
        player['loop'] = bool(data[2])
        player['beginning'] = bool(data[3])
        player['clip_frame'] = struct.unpack('!H', data[4:6])[0]

    def _recv_MPCE(self, data):
        player_num = data[0]
        player = self._state['mediaplayer'].setdefault(player_num, {})
        player['type'] = ClipType(data[1])
        player['still_index'] = data[2]
        player['clip_index'] = data[3]

    def _recv_MPSp(self, data):
        self._config['mediapool'].setdefault(0, {})['maxlength'] = struct.unpack('!H', data[0:2])[0]
        self._config['mediapool'].setdefault(1, {})['maxlength'] = struct.unpack('!H', data[2:4])[0]

    def _recv_MPCS(self, data):
        bank = data[0]
        clip_bank = self._state['mediapool'].setdefault('clips', {}).setdefault(bank, {})
        clip_bank['used'] = bool(data[1])
        clip_bank['filename'] = convert_cstring(data[2:18])
        clip_bank['length'] = struct.unpack('!H', data[66:68])[0]

    def _recv_MPAS(self, data):
        bank = data[0]
        audio_bank = self._state['mediapool'].setdefault('audio', {}).setdefault(bank, {})
        audio_bank['used'] = bool(data[1])
        audio_bank['filename'] = convert_cstring(data[18:34])

    def _recv_MPfe(self, data):
        if data[0] != 0:
            return
        bank = data[3]
        still_bank = self._state['mediapool'].setdefault('stills', {}).setdefault(bank, {})
        still_bank['used'] = bool(data[4])
        still_bank['hash'] = data[5:21].decode("utf-8")
        filename_length = data[23]
        still_bank['filename'] = data[24:(24 + filename_length)].decode("utf-8")

    def _recv_AMIP(self, data):
        channel = struct.unpack('!H', data[0:2])[0]
        channel_config = self._system_config['audio'].setdefault(channel, {})
        channel_config['fromMediaPlayer'] = bool(data[6])
        channel_config['plug'] = data[7]

        channel_state = self._state['audio'].setdefault(channel, {})
        channel_state['mix_option'] = data[8]
        channel_state['volume'] = struct.unpack('!H', data[10:12])[0]
        channel_state['balance'] = struct.unpack('!h', data[12:14])[0]

    def _recv_AMMO(self, data):
        self._state['audio']['master_volume'] = struct.unpack('!H', data[0:2])[0]

    def _recv_AMmO(self, data):
        monitor = self._state['audio'].setdefault('monitor', {})
        monitor['enabled'] = bool(data[0])
        monitor['volume'] = struct.unpack('!H', data[2:4])[0]
        monitor['mute'] = bool(data[4])
        monitor['solo'] = bool(data[5])
        monitor['solo_input'] = struct.unpack('!H', data[6:8])[0]
        monitor['dim'] = bool(data[8])

    def _recv_AMTl(self, data):
        src_count = struct.unpack('!H', data[0:2])[0]
        for i in range(src_count):
            num = 2 + i * 3
            channel = struct.unpack('!H', data[num:num + 2])[0]
            self._state['audio'].setdefault('tally', {})[channel] = bool(data[num + 2])

    def _recv_TlIn(self, data):
        src_count = struct.unpack('!H', data[0:2])[0]
        for i in range(2, src_count + 2):
            self._state['tally_by_index'][str(i - 1)] = parseBitmask(data[i], ['prv', 'pgm'])
        # TODO self.tallyHandler(self)

    def _recv_TlSr(self, data):
        src_count = struct.unpack('!H', data[0:2])[0]
        for i in range(2, src_count * 3 + 2, 3):
            source = VideoSource(struct.unpack('!H', data[i:i + 2])[0])
            self._state['tally'][source] = parseBitmask(data[i + 2], ['prv', 'pgm'])
        self.broadcast(MessageTypes.TALLY, self._state['tally'])

    def _recv_Time(self, data):
        self._state['last_state_change'] = struct.unpack('!BBBB', data[0:4])

########
# Input validation
########

    def _assertInitialised(self):
        if not self._isInitialized:
            raise NotInitializedException()

    def _resolveInputBytes(self, inputID):
        if isinstance(inputID, VideoSource):
            inputID = inputID.value
        if inputID not in self._system_config['inputs'].keys():
            raise InvalidArgumentException()
        return [(inputID >> 8), (inputID & 0xFF)]

#############
# Public control functions
#############

    @requiresInit
    @assertTopology('aux_busses', 0)
    def setAuxSource(self, auxChannel, inputID):
        self._sendCommand(
            "CAuS",
            [0x01, auxChannel - 1] + self._resolveInputBytes(inputID)
        )

    @requiresInit
    @assertTopology('mes', 1)
    def setPreview(self, inputID, me=1):
        self._sendCommand(
            'CPvI',
            [me - 1, 0] + self._resolveInputBytes(inputID)
        )

    @requiresInit
    @assertTopology('mes', 1)
    def setProgram(self, inputID, me=1):
        self._sendCommand(
            'CPgI',
            [me - 1, 0] + self._resolveInputBytes(inputID)
        )

    @requiresInit
    @assertTopology('mes', 0)
    def performCut(self, me=1):
        self._sendCommand(
            'DCut',
            [me - 1, 0, 0, 0]
        )

    @requiresInit
    @assertTopology('mes', 0)
    def performAutoTake(self, me=1):
        self._sendCommand(
            'DAut',
            [me - 1, 0, 0, 0]
        )
