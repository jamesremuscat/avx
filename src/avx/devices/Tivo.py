from avx.devices import Device
from socket import socket


class Tivo(Device):
    '''
    A networked TiVo device. Developed against Virgin Media UK's TiVo boxes.
    '''

    socket = None

    def __init__(self, deviceID, ipAddress, port=31339, **kwargs):
        super(Tivo, self).__init__(deviceID, **kwargs)
        self.ipAddress = ipAddress
        self.port = port

    def initialise(self):
        self.socket = socket()
        self.socket.settimeout(5)
        self.socket.connect((self.ipAddress, self.port))

    def send(self, message):
        if not self.socket:
            self.initialise()
        self.socket.sendall(message)

    def sendIRCode(self, ircode):
        self.send('IRCODE %s\r' % ircode)

    # Playback functions

    def pause(self):
        self.sendIRCode("PAUSE")

    def play(self):
        self.sendIRCode("PLAY")

    def rewind(self):
        self.sendIRCode("REVERSE")

    def fastForward(self):
        self.sendIRCode("FORWARD")

    def replay(self):
        self.sendIRCode("REPLAY")

    def skip(self):
        self.sendIRCode("ADVANCE")

    def slow(self):
        self.sendIRCode("SLOW")
