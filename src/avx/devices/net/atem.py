from avx.devices import Device

import ctypes
import logging
import socket
import struct
import threading
import time
from avx.devices.Device import InvalidArgumentException
from avx.Client import MessageTypes

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

# labels
LABELS_VIDEOMODES = ['525i59.94NTSC', '625i50PAL', '525i59.94NTSC16:9', '625i50PAL16:9',
                     '720p50', '720p59.94', '1080i50', '1080i59.94',
                     '1080p23.98', '1080p24', '1080p25', '1080p29.97', '1080p50', '1080p59.94',
                     '2160p23.98', '2160p24', '2160p25', '2160p29.97']
LABELS_PORTS_EXTERNAL = {0: 'SDI', 1: 'HDMI', 2: 'Component', 3: 'Composite', 4: 'SVideo'}
LABELS_PORTS_INTERNAL = {0: 'External', 1: 'Black', 2: 'Color Bars', 3: 'Color Generator', 4: 'Media Player Fill',
                         5: 'Media Player Key', 6: 'SuperSource', 128: 'ME Output', 129: 'Auxilary', 130: 'Mask'}
LABELS_MULTIVIEWER_LAYOUT = ['top', 'bottom', 'left', 'right']
LABELS_AUDIO_PLUG = ['Internal', 'SDI', 'HDMI', 'Component', 'Composite', 'SVideo', 'XLR', 'AES/EBU', 'RCA']
LABELS_VIDEOSRC = {0: 'Black', 1: 'Input 1', 2: 'Input 2', 3: 'Input 3', 4: 'Input 4', 5: 'Input 5', 6: 'Input 6', 7: 'Input 7', 8: 'Input 8', 9: 'Input 9', 10: 'Input 10', 11: 'Input 11', 12: 'Input 12', 13: 'Input 13', 14: 'Input 14', 15: 'Input 15', 16: 'Input 16', 17: 'Input 17', 18: 'Input 18', 19: 'Input 19', 20: 'Input 20', 1000: 'Color Bars', 2001: 'Color 1', 2002: 'Color 2', 3010: 'Media Player 1', 3011: 'Media Player 1 Key', 3020: 'Media Player 2', 3021: 'Media Player 2 Key', 4010: 'Key 1 Mask', 4020: 'Key 2 Mask', 4030: 'Key 3 Mask', 4040: 'Key 4 Mask', 5010: 'DSK 1 Mask', 5020: 'DSK 2 Mask', 6000: 'Super Source', 7001: 'Clean Feed 1', 7002: 'Clean Feed 2', 8001: 'Auxilary 1', 8002: 'Auxilary 2', 8003: 'Auxilary 3', 8004: 'Auxilary 4', 8005: 'Auxilary 5', 8006: 'Auxilary 6', 10010: 'ME 1 Prog', 10011: 'ME 1 Prev', 10020: 'ME 2 Prog', 10021: 'ME 2 Prev'}
LABELS_AUDIOSRC = {1: 'Input 1', 2: 'Input 2', 3: 'Input 3', 4: 'Input 4', 5: 'Input 5', 6: 'Input 6', 7: 'Input 7', 8: 'Input 8', 9: 'Input 9', 10: 'Input 10', 11: 'Input 11', 12: 'Input 12', 13: 'Input 13', 14: 'Input 14', 15: 'Input 15', 16: 'Input 16', 17: 'Input 17', 18: 'Input 18', 19: 'Input 19', 20: 'Input 20', 1001: 'XLR', 1101: 'AES/EBU', 1201: 'RCA', 2001: 'MP1', 2002: 'MP2'}
# cc
LABELS_CC_DOMAIN = {0: 'lens', 1: 'camera', 8: 'chip'}
LABELS_CC_LENS_FEATURE = {0: 'focus', 1: 'auto_focused', 3: 'iris', 9: 'zoom'}
LABELS_CC_CAM_FEATURE = {1: 'gain', 2: 'white_balance', 5: 'shutter'}
LABELS_CC_CHIP_FEATURE = {0: 'lift', 1: 'gamma', 2: 'gain', 3: 'aperture', 4: 'contrast', 5: 'luminance', 6: 'hue-saturation'}

# value options
VALUES_CC_GAIN = {512: '0db', 1024: '6db', 2048: '12db', 4096: '18db'}
VALUES_CC_WB = {3200: '3200K', 4500: '4500K', 5000: '5000K', 5600: '5600K', 6500: '6500K', 7500: '7500K'}
VALUES_CC_SHUTTER = {20000: '1/50', 16667: '1/60', 13333: '1/75', 11111: '1/90', 10000: '1/100', 8333: '1/120', 6667: '1/150', 5556: '1/180', 4000: '1/250', 2778: '1/360', 2000: '1/500', 1379: '1/725', 1000: '1/1000', 690: '1/1450', 500: '1/2000'}
VALUES_AUDIO_MIX = {0: 'off', 1: 'on', 2: 'AFV'}


def convert_cstring(bs):
    return ctypes.create_string_buffer(str(bs)).value.decode('utf-8')


def parseBitmask(num, labels):
    states = {}
    for i, label in enumerate(labels):
        states[label] = bool(num & (1 << len(labels) - i - 1))
    return states


def byteArrayToString(byteArray):
    return ''.join(chr(b) for b in byteArray)


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

        threading.Thread(target=self._connectToSwitcher).start()

    def deinitialise(self):
        self.run_receive = False
        self._state['booted'] = False

    def _receivePackets(self):
        while self.run_receive:
            data, remoteIP = self._socket.recvfrom(2048)
            # self.log.debug("Received {} from {}:{}".format(data.encode('hex_codec'), *remoteIP))

            if remoteIP == (self.ipAddr, self.port):
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
        size = 18
        for i in range(size):
            self._system_config.setdefault('video_modes', {})[i] = bool(data[0] & (1 << size - i - 1))

    def _recv__MAC(self, data):
        self._system_config['macro_banks'] = data[0]

    def _recv_Powr(self, data):
        self._status['power'] = parseBitmask(data[0], ['main', 'backup'])

    def _recv_DcOt(self, data):
        self._config['down_converter'] = data[0]

    def _recv_VidM(self, data):
        self._config['video_mode'] = data[0]

    def _recv_InPr(self, data):
        index = struct.unpack('!H', data[0:2])[0]
        self._system_config['inputs'][index] = {}
        input_setting = self._system_config['inputs'][index]
        input_setting['name_long'] = convert_cstring(data[2:22])
        input_setting['name_short'] = convert_cstring(data[22:26])
        input_setting['types_available'] = parseBitmask(data[27], LABELS_PORTS_EXTERNAL)
        input_setting['port_type_external'] = data[29]
        input_setting['port_type_internal'] = data[30]
        input_setting['availability'] = parseBitmask(data[32], ['Auxilary', 'Multiviewer', 'SuperSourceArt',
                                                                'SuperSourceBox', 'KeySource'])
        input_setting['me_availability'] = parseBitmask(data[33], ['ME1', 'ME2'])

    def _recv_MvPr(self, data):
        index = data[0]
        self._config['multiviewers'].setdefault(index, {})['layout'] = data[1]

    def _recv_MvIn(self, data):
        index = data[0]
        window = data[1]
        self._config['multiviewers'].setdefault(index, {}).setdefault('windows', {})[window] = struct.unpack('!H', data[2:4])[0]

    def _recv_PrgI(self, data):
        meIndex = data[0]
        self._state['program'][meIndex] = struct.unpack('!H', data[2:4])[0]
        # TODO self.pgmInputHandler(self)

    def _recv_PrvI(self, data):
        meIndex = data[0]
        self._state['preview'][meIndex] = struct.unpack('!H', data[2:4])[0]

    def _recv_KeOn(self, data):
        meIndex = data[0]
        keyer = data[1]
        self._state['keyers'].setdefault(meIndex, {})[keyer] = (data[2] != 0)

    def _recv_DskB(self, data):
        keyer = data[0]
        keyer_setting = self._state['dskeyers'].setdefault(keyer, {})
        keyer_setting['fill'] = struct.unpack('!H', data[2:4])[0]
        keyer_setting['key'] = struct.unpack('!H', data[4:6])[0]

    def _recv_DskS(self, data):
        keyer = data[0]
        dsk_setting = self._state['dskeyers'].setdefault(keyer, {})
        dsk_setting['onAir'] = (data[1] != 0)
        dsk_setting['inTransition'] = (data[2] != 0)
        dsk_setting['autoTransitioning'] = (data[3] != 0)
        dsk_setting['framesRemaining'] = data[4]

    def _recv_AuxS(self, data):  # Aux source set
        auxIndex = data[0]
        self._state['aux'][auxIndex] = struct.unpack('!H', data[2:4])[0]
        self.broadcast(MessageTypes.AUX_OUTPUT_MAPPING, self._state['aux'])

    def _recv_CCdo(self, data):
        input_num = data[1]
        domain = data[2]
        feature = data[3]
        feature_label = feature
        try:
            if domain == 0:
                feature_label = LABELS_CC_LENS_FEATURE[feature]
            elif domain == 1:
                feature_label = LABELS_CC_CAM_FEATURE[feature]
            elif domain == 8:
                feature_label = LABELS_CC_CHIP_FEATURE[feature]
            self.cameracontrol.setdefault(input_num, {}).setdefault('features', {}).setdefault(LABELS_CC_DOMAIN[domain], {})[feature_label] = bool(data[4])
        except KeyError:
            self.log.warning("CC Feature not recognized (no label)")

    def _recv_CCdP(self, data):
        input_num = data[1]
        domain = data[2]
        feature = data[3]
        feature_label = feature
        val = None
        val_translated = None
        if domain == 0:  # lens
            if feature == 0:  # focus
                val = val_translated = struct.unpack('!h', data[16:18])[0]
            elif feature == 1:  # auto focused
                pass
            elif feature == 3:  # iris
                val = val_translated = struct.unpack('!h', data[16:18])[0]
            elif feature == 9:  # zoom
                val = val_translated = struct.unpack('!h', data[16:18])[0]
        elif domain == 1:  # camera
            if feature == 1:  # gain
                val = struct.unpack('!h', data[16:18])[0]
                val_translated = VALUES_CC_GAIN.get(val, 'unknown')
            elif feature == 2:  # white balance
                val = struct.unpack('!h', data[16:18])[0]
                val_translated = VALUES_CC_WB.get(val, val + 'K')
            elif feature == 5:  # shutter
                val = struct.unpack('!h', data[18:20])[0]
                val_translated = VALUES_CC_SHUTTER.get(val, 'off')
        elif domain == 8:  # chip
            val_keys_color = ['R', 'G', 'B', 'Y']
            if feature == 0:  # lift
                val = dict(zip(val_keys_color, struct.unpack('!hhhh', data[16:24])))
                val_translated = {k: float(v) / 4096 for k, v in val.items()}
            elif feature == 1:  # gamma
                val = dict(zip(val_keys_color, struct.unpack('!hhhh', data[16:24])))
                val_translated = {k: float(v) / 8192 for k, v in val.items()}
            elif feature == 2:  # gain
                val = dict(zip(val_keys_color, struct.unpack('!hhhh', data[16:24])))
                val_translated = {k: float(v) * 16 / 32767 for k, v in val.items()}
            elif feature == 3:  # aperture
                pass  # no idea - todo
            elif feature == 4:  # contrast
                val = struct.unpack('!h', data[18:20])[0]
                val_translated = float(val) / 4096
            elif feature == 5:  # luminance
                val = struct.unpack('!h', data[16:18])[0]
                val_translated = float(val) / 2048
            elif feature == 6:  # hue-saturation
                val_keys = ['hue', 'saturation']
                val = dict(zip(val_keys, struct.unpack('!hh', data[16:20])))
                val_translated = {}
                val_translated['hue'] = float(val['hue']) * 360 / 2048 + 180
                val_translated['saturation'] = float(val['saturation']) / 4096
        try:
            if domain == 0:
                feature_label = LABELS_CC_LENS_FEATURE[feature]
            elif domain == 1:
                feature_label = LABELS_CC_CAM_FEATURE[feature]
            elif domain == 8:
                feature_label = LABELS_CC_CHIP_FEATURE[feature]
            self.cameracontrol.setdefault(input_num, {}).setdefault('state_raw', {}).setdefault(LABELS_CC_DOMAIN[domain], {})[feature_label] = val
            self.cameracontrol.setdefault(input_num, {}).setdefault('state', {}).setdefault(LABELS_CC_DOMAIN[domain], {})[feature_label] = val_translated
        except KeyError:
            print("Warning: CC Feature not recognized (no label)")

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
        player['type'] = {1: 'still', 2: 'clip'}.get(data[1])
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
        for i in range(2, src_count * 3 + 2):
            source = struct.unpack('!H', data[i:i + 2])[0]
            self._state['tally'][source] = parseBitmask(data[i + 2], ['prv', 'pgm'])
        # TODO self.tallyHandler(self)

    def _recv_Time(self, data):
        self._state['last_state_change'] = struct.unpack('!BBBB', data[0:4])

#############
# Public control functions
#############

    def setAuxSource(self, auxChannel, inputID):
        if not self._isInitialized:
            raise NotInitializedException()
        if auxChannel <= 0 or auxChannel > self._system_config['topology']['aux_busses']:
            raise InvalidArgumentException()
        self._sendCommand(
            "CAuS",
            byteArrayToString([0x01, auxChannel - 1, (inputID >> 8), (inputID & 0xFF)])
        )
