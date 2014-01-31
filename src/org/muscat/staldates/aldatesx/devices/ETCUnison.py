from org.muscat.staldates.aldatesx.devices.SerialDevice import SerialDevice


class UnisonDevice(SerialDevice):
    '''
    An ETC Unison lighting controller speaking Unison Serial Access Protocol (USAP).
    '''

    def __init__(self, deviceID, serialDevice):
        super(UnisonDevice, self).__init__(deviceID, serialDevice)


class UnisonCommand(object):
    '''
    Wrapper around a string command to add the binary bits to be sent.
    '''

    max_command_length = 200

    def __init__(self, command):
        self.command = command

    def getByteString(self):
        cmdLength = len(self.command)
        if cmdLength > self.max_command_length:
            return -1
        return '\xEE' + chr(cmdLength + 3) + '\x00\x00\x40' + self.command + '\x00\x00'
