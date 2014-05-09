from org.muscat.avx.devices.Device import Device
from socket import socket


class Tivo(Device):
    '''
    A networked TiVo device. Developed against Virgin Media UK's TiVo boxes.
    '''

    socket = None

    def __init__(self, deviceID, ipAddress, port=31339, **kwargs):
        super(Tivo, self).__init__(deviceID)
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

    # On to the actual functions

    def pause(self):
        self.sendIRCode("PAUSE")

    def play(self):
        self.sendIRCode("PLAY")
