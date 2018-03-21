from avx.devices.net import TCPDevice


class Tivo(TCPDevice):
    '''
    A networked TiVo device. Developed against Virgin Media UK's TiVo boxes.
    '''

    socket = None

    def __init__(self, deviceID, ipAddress, port=31339, **kwargs):
        super(Tivo, self).__init__(deviceID, ipAddress, port, **kwargs)

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
