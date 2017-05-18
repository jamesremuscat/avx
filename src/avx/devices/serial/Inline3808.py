from avx.Client import MessageTypes
from avx.devices.serial import SerialDevice


class Inline3808(SerialDevice):
    '''
    An Inline 3808 8x4 switcher.
    '''

    def __init__(self, deviceID, serialDevice, **kwargs):
        super(Inline3808, self).__init__(deviceID, serialDevice, baud=1200, **kwargs)

    def initialise(self):
        self.sendCommand("[CNF290000]")  # All boards to group 1. Copying what the AMX does currently though this should be the default.

    def sendInputToOutput(self, inChannel, outChannel):
        return self.sendCommand("[PT1O0" + str(outChannel) + "I0" + str(inChannel) + "]")

    def requestStatus(self):
        self.sendCommand("[VID]")

    def hasFullMessage(self, recv_buffer):
        return recv_buffer[-1] == "]"

    def handleMessage(self, msgBytes):
        msgString = ''.join(map(chr, msgBytes))
        if len(msgString) == 13 and msgString[1:4] == "VID":
            self.broadcast(
                MessageTypes.OUTPUT_MAPPING,
                {
                    1: int(msgString[5]),
                    2: int(msgString[7]),
                    3: int(msgString[9]),
                    4: int(msgString[11]),
                }
            )
