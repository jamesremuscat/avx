from avx.devices.serial import SerialDevice


max_command_length = 200


def wrapUnisonCommand(func):
    '''
    Decorator for a function which should return the USAP command string to be sent.
    The resulting function requires `self.sendCommand` to resolve to an appropriate function.
    '''
    def unisonCommandInner(self, *args):
        cmd = UnisonCommand(func(self, *args))
        return self.sendCommand(cmd.getByteString())
    return unisonCommandInner


class UnisonDevice(SerialDevice):
    '''
    An ETC Unison lighting controller speaking Unison Serial Access Protocol (USAP).
    '''

    def __init__(self, deviceID, serialDevice, **kwargs):
        super(UnisonDevice, self).__init__(deviceID, serialDevice, **kwargs)

    # Commands for presets

    @wrapUnisonCommand
    def activate(self, unisonObject):
        return "{}.ACTI".format(unisonObject)

    @wrapUnisonCommand
    def activateWithFade(self, preset, fadeTime):
        return "{}.nDFT={}".format(preset, fadeTime)

    @wrapUnisonCommand
    def deactivate(self, unisonObject):
        return "{}.DACT".format(unisonObject)

    # Commands for walls

    @wrapUnisonCommand
    def open(self, wall):
        return "{}.OPEN".format(wall)

    @wrapUnisonCommand
    def close(self, wall):
        return "{}.CLOS".format(wall)

    @wrapUnisonCommand
    def toggleOpen(self, wall):
        return "{}.TOGL".format(wall)

    # Commands for zones

    @wrapUnisonCommand
    def setZoneIntensity(self, zone, intensity):
        # 0 <= intensity <= 100, command needs a percentage of 65535
        return "{}.nINT={:0.0f}".format(zone, intensity * 655.35)

    # Commands for macros

    @wrapUnisonCommand
    def execute(self, macroName):
        return "{}.EXEC".format(macroName)

    @wrapUnisonCommand
    def stop(self, macroName):
        return "{}.STOP".format(macroName)

    # Commands for section masters

    @wrapUnisonCommand
    def master(self, section, level):
        return "{}.Master.nVAL={:0.0f}".format(section, level * 655.35)


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
