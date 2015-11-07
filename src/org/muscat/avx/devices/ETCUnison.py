from org.muscat.avx.devices.SerialDevice import SerialDevice


max_command_length = 200


class UnisonDevice(SerialDevice):
    '''
    An ETC Unison lighting controller speaking Unison Serial Access Protocol (USAP).
    '''

    def __init__(self, deviceID, serialDevice, **kwargs):
        super(UnisonDevice, self).__init__(deviceID, serialDevice, **kwargs)

    def activate(self, unisonObject):
        cmd = UnisonCommand(unisonObject + ".ACTI")
        return self.sendCommand(cmd.getByteString())

    def deactivate(self, unisonObject):
        cmd = UnisonCommand(unisonObject + ".DACT")
        return self.sendCommand(cmd.getByteString())


class UnisonCommand(object):
    '''
    Wrapper around a string command to add the binary bits to be sent.
    '''

    def __init__(self, command):
        self.checkLength(command)
        self.command = command

    def getByteString(self):
        self.checkLength(self.command)
        return '\xEE' + chr(len(self.command) + 3) + '\x00\x00\x40' + self.command + '\x00\x00'

    def checkLength(self, cmdString):
        cmdLength = len(cmdString)
        if cmdLength > max_command_length:
            raise CommandStringTooLongError(cmdLength)


class CommandStringTooLongError(Exception):

    def __init__(self, length):
        super(CommandStringTooLongError, self).__init__("Length " + str(length) + " too long (limit " + str(max_command_length) + ")")
