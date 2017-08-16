from avx.devices.Device import Device
from enum import Enum
from threading import Thread
from time import sleep

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


class HyperDeck(Device):
    def __init__(self, deviceID, ipAddress, port=9993, **kwargs):
        super(HyperDeck, self).__init__(deviceID, *kwargs)
        self.remote = (ipAddress, port)
        self._recv_thread = None
        self._connect_thread = None
        self._isConnected = False

    def initialise(self):
        self.socket = socket.socket()
        self.socket.settimeout(1)
        self._run_recv_thread = True
        self._data_buffer = ''
        self._initialiseState()

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

    def _initialiseState(self):
        self._state = {
            'connection': {},
            'slots': {},
            'transport': {}
        }

    def deinitialise(self):
        self._run_recv_thread = False
        self._isConnected = False
        if self.socket:
            try:
                self.socket.send("quit\r\n")
            except socket.error:
                pass
            self.socket.close()

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
        self.socket.send('transport info\r\n')
        self.socket.send('slot info\r\n')
        self.socket.send('notify: transport: true slot: true\r\n')

    def _recv_208(self, payload, extra):
        mapping = {
            'clip id': _int,
            'status': TransportState,
            'loop': _bool,
            'single clip': _bool,
            'speed': _int,
            'slot id': _int
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

########
# Getters
########
    def isConnected(self):
        return self._isConnected

    def getTransportState(self):
        return self._state['transport']

    def getSlotsState(self):
        return self._state['slots']

########
# Transport controls
########
    def record(self, clip_name=None):
        if clip_name:
            self.socket.send('record: name: {}\r\n'.format(clip_name))
        else:
            self.socket.send('record\r\n')
        self._state['transport']['status'] = TransportState.RECORD  # Otherwise we don't get a notification about it

    def stop(self):
        self.socket.send('stop\r\n')
        self._state['transport']['status'] = TransportState.STOPPED  # Otherwise we don't get a notification about it

    def play(self, single_clip=None, speed=None, loop=None):
        if single_clip is None and speed is None and loop is None:
            self.socket.send('play\r\n')
        else:
            cmd = 'play: '
            if single_clip is not None:
                cmd += 'single clip: {} '.format('true' if single_clip else 'false')
            if speed is not None:
                cmd += 'speed: {} '.format(speed)
            if loop is not None:
                cmd += 'loop: {} '.format('true' if loop else 'false')
            self.socket.send(cmd.strip() + '\r\n')
        self._state['transport']['status'] = TransportState.PLAYING  # Otherwise we don't get a notification about it

    def gotoClip(self, clipID):
        self.socket.send('goto: clip id: {}\r\n'.format(clipID))

    def next(self):
        self.gotoClip('+1')

    def prev(self):
        self.gotoClip('-1')
