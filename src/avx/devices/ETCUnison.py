from avx.devices.SerialDevice import SerialDevice


max_command_length = 200


class UnisonDevice(SerialDevice):
    '''
    An ETC Unison lighting controller speaking Unison Serial Access Protocol (USAP).
    '''

    def __init__(self, deviceID, serialDevice, **kwargs):
        super(UnisonDevice, self).__init__(deviceID, serialDevice, **kwargs)

    # Commands for presets

    def activate(self, unisonObject):
        cmd = UnisonCommand(unisonObject + ".ACTI")
        return self.sendCommand(cmd.getByteString())

    def activateWithFade(self, preset, fadeTime):
        cmd = UnisonCommand("{}.nDFT={}".format(preset, fadeTime))
        return self.sendCommand(cmd.getByteString())

    def deactivate(self, unisonObject):
        cmd = UnisonCommand(unisonObject + ".DACT")
        return self.sendCommand(cmd.getByteString())

    # Commands for walls

    def open(self, wall):
        cmd = UnisonCommand(wall + ".OPEN")
        return self.sendCommand(cmd.getByteString())

    def close(self, wall):
        cmd = UnisonCommand(wall + ".CLOS")
        return self.sendCommand(cmd.getByteString())

    def toggleOpen(self, wall):
        cmd = UnisonCommand(wall + ".TOGL")
        return self.sendCommand(cmd.getByteString())

    # Commands for zones

    def setZoneIntensity(self, zone, intensity):
        # 0 <= intensity <= 100, command needs a percentage of 65535
        cmd = UnisonCommand("{}.nINT={:0.0f}".format(zone, intensity * 655.35))
        return self.sendCommand(cmd.getByteString())

    # Commands for macros

    def execute(self, macroName):
        cmd = UnisonCommand("{}.EXEC".format(macroName))
        return self.sendCommand(cmd.getByteString())

    def stop(self, macroName):
        cmd = UnisonCommand("{}.STOP".format(macroName))
        return self.sendCommand(cmd.getByteString())

    # Commands for section masters

    def master(self, section, level):
        cmd = UnisonCommand("{}.Master.nVAL={:0.0f}".format(section, level * 655.35))
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
