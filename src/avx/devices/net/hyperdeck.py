from avx.devices.Device import InvalidArgumentException
from avx.devices.net import TCPDevice
from enum import Enum

import socket


class TransportState(Enum):
    PREVIEW = 'preview'
    STOPPED = 'stopped'
    PLAYING = 'play'
    FORWARD = 'forward'
    REWIND = 'rewind'
    JOG = 'jog'
    SHUTTLE = 'shuttle'
    RECORD = 'record'


class SlotState(Enum):
    EMPTY = 'empty'
    MOUNTING = 'mounting'
    ERROR = 'error'
    MOUNTED = 'mounted'


class MessageTypes(object):
    _PREFIX = "avx.devices.net.hyperdeck."
    CONNECTED = _PREFIX + "Connected"
    DISCONNECTED = _PREFIX + "Disconnected"
    TRANSPORT_STATE_CHANGED = _PREFIX + "TransportStateChanged"
    SLOT_STATE_CHANGED = _PREFIX + "SlotStateChanged"
    CLIP_LISTING = _PREFIX + "ClipListing"


class TransportMode(Enum):
    # These are the values passed to the `preview: enable:` command to switch
    RECORD = 'true'
    PLAYBACK = 'false'


def _bool(string):
    if string == "true":
        return True
    return False


def _int(string):
    if string == "none":
        return None
    try:
        return int(string)
    except ValueError:
        return string


class HyperDeck(TCPDevice):
    def __init__(self, deviceID, ipAddress, port=9993, **kwargs):
        super(HyperDeck, self).__init__(deviceID, ipAddress, port, **kwargs)

    def initialise(self):
        super(HyperDeck, self).initialise()
        self._data_buffer = ''
        self._initialiseState()

    def _initialiseState(self):
        self._state = {
            'connection': {},
            'slots': {},
            'transport': {}
        }

    def deinitialise(self):
        if self.socket:
            try:
                self.send("quit\r\n")
            except socket.error:
                pass
        super(HyperDeck, self).deinitialise()

    def on_receive(self, data):
        # In case the response is larger than the recv buffer
        # we need to check for a completed message - that is,
        # one with an empty line at the end
        self._data_buffer += data
        if self._data_buffer[-2:] == "\r\n":
            for msg in self._data_buffer.split('\r\n\r\n'):
                if msg != '':
                    self._handle_data(msg)
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
            self.log.debug("Unhandled packet type {}: {} <{}>".format(code, payload, extra))

    def _store_state(self, store, paramlines, mapping={}):
        for paramline in paramlines:
            param, value = paramline.split(": ")
            store[param] = mapping.get(param, lambda a: a)(value)

    def _recv_200(self, payload, extra):
        pass  # OK

    def _recv_500(self, payload, extra):
        self._store_state(self._state['connection'], extra)
        self.send('transport info\r\n')
        self.send('slot info\r\n')
        self.send('notify: transport: true slot: true\r\n')

    def _recv_208(self, payload, extra):
        mapping = {
            'clip id': _int,
            'status': TransportState,
            'loop': _bool,
            'single clip': _bool,
            'speed': _int,
            'slot id': _int,
            'active slot': _int
        }
        self._store_state(self._state['transport'], extra, mapping)
        self.broadcast(MessageTypes.TRANSPORT_STATE_CHANGED, self._state['transport'])

    def _recv_508(self, payload, extra):
        self._recv_208(payload, extra)

    def _recv_202(self, payload, extra):
        slot = -1
        for e in extra:
            if e.startswith('slot id:'):
                slot = int(e[8:])

        mapping = {
            'recording time': _int,
            'slot id': _int,
            'status': SlotState
        }

        self._store_state(self._state['slots'].setdefault(slot, {}), extra, mapping)
        self.broadcast(MessageTypes.SLOT_STATE_CHANGED, self._state['slots'])

    def _recv_502(self, payload, extra):
        self._recv_202(payload, extra)

    def _recv_206(self, payload, extra):
        listing = {}
        cliplines = extra[1:]  # Ignore the 'slot id:' line
        for line in cliplines:
            idx, data = line.split(': ')
            parts = data.split(' ')
            duration = parts.pop()
            video_format = parts.pop()
            file_format = parts.pop()
            name = ' '.join(parts)

            listing[int(idx)] = {
                'name': name,
                'file_format': file_format,
                'video_format': video_format,
                'duration': duration
            }

        self.broadcast(MessageTypes.CLIP_LISTING, listing)

########
# Getters
########
    def isConnected(self):
        return self._isConnected

    def getTransportState(self):
        return self._state['transport']

    def getSlotsState(self):
        return self._state['slots']

    def broadcastClipsList(self):
        '''
        This behaves asynchronously: the list of clips will be returned via a broadcast
        of type MessageTypes.CLIP_LISTING.
        '''
        self.send('disk list\r\n')

########
# State setters
########

    def selectSlot(self, slot_id):
        if slot_id in [1, 2]:
            self.send('slot select: slot id: {}\r\n'.format(slot_id))
        else:
            raise InvalidArgumentException('Slot {} does not exist'.format(slot_id))

    def setTransportMode(self, mode):
        if not isinstance(mode, TransportMode):
            raise InvalidArgumentException('{} is not a TransportMode'.format(mode))
        self.send('preview: enable: {}\r\n'.format(mode.value))

########
# Transport controls
########
    def record(self, clip_name=None):
        if clip_name:
            self.send('record: name: {}\r\n'.format(clip_name))
        else:
            self.send('record\r\n')
        self._state['transport']['status'] = TransportState.RECORD  # Otherwise we don't get a notification about it

    def stop(self):
        self.send('stop\r\n')
        self._state['transport']['status'] = TransportState.STOPPED  # Otherwise we don't get a notification about it

    def play(self, single_clip=None, speed=None, loop=None):
        if single_clip is None and speed is None and loop is None:
            self.send('play\r\n')
        else:
            cmd = 'play: '
            if single_clip is not None:
                cmd += 'single clip: {} '.format('true' if single_clip else 'false')
            if speed is not None:
                cmd += 'speed: {} '.format(speed)
            if loop is not None:
                cmd += 'loop: {} '.format('true' if loop else 'false')
            self.send(cmd.strip() + '\r\n')
        self._state['transport']['status'] = TransportState.PLAYING  # Otherwise we don't get a notification about it

    def gotoClip(self, clipID):
        self.send('goto: clip id: {}\r\n'.format(clipID))

    def next(self):
        self.gotoClip('+1')

    def prev(self):
        self.gotoClip('-1')
