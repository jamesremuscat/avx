from avx.devices.SerialDevice import SerialDevice
from avx.devices.Device import Device, InvalidArgumentException
import logging
import time


class SerialRelayCard(SerialDevice):
    '''
    A serial relay card is a single serial device which may control multiple relays.
    For convenience, each relay on a card may have its own device which can be created by calling
    createDevice on the relay card.
    '''

    def __init__(self, deviceID, serialDevice, **others):
        SerialDevice.__init__(self, deviceID, serialDevice, **others)

    def createDevice(self, deviceID, channel):
        return RelayDevice(deviceID, self, channel)


class RelayDevice(Device):

    def __init__(self, deviceID, relayCard, channel, **kwargs):
        super(RelayDevice, self).__init__(deviceID, **kwargs)
        self.relayCard = relayCard
        self.channel = channel

    def on(self):
        return self.relayCard.on(self.channel)

    def off(self):
        return self.relayCard.off(self.channel)


class KMtronicSerialRelayCard(SerialRelayCard):

    def __init__(self, deviceID, serialDevice, **kwargs):
        SerialRelayCard.__init__(self, deviceID, serialDevice, **kwargs)

    def on(self, channel):
        return self.sendCommand(SerialDevice.byteArrayToString([0xFF, channel, 0x01]))

    def off(self, channel):
        return self.sendCommand(SerialDevice.byteArrayToString([0xFF, channel, 0x00]))


class JBSerialRelayCard(SerialRelayCard):

    sendDelay = 0.05

    def __init__(self, deviceID, serialDevice, **kwargs):
        SerialRelayCard.__init__(self, deviceID, serialDevice, baud=19200, **kwargs)

    def on(self, channel):
        result = self.sendCommand(SerialDevice.byteArrayToString([0x30 + 2 * channel]))
        time.sleep(self.sendDelay)
        return result

    def off(self, channel):
        result = self.sendCommand(SerialDevice.byteArrayToString([0x31 + 2 * channel]))
        time.sleep(self.sendDelay)
        return result


class ICStationSerialRelayCard(SerialRelayCard):

    def __init__(self, deviceID, serialDevice, channels=8, **kwargs):
        SerialRelayCard.__init__(self, deviceID, serialDevice, **kwargs)
        self.state = [False for _ in range(channels)]  # True = on, False = off
        self.initialised = False

    def initialise(self):
        if not self.initialised:
            SerialRelayCard.initialise(self)
            self.sendCommand("\x50")
            time.sleep(0.1)
            self.sendCommand("\x51")
            self.__sendStateCommand()
            self.initialised = True

    def __sendStateCommand(self):
        result = self.sendCommand(SerialDevice.byteArrayToString([self.__createStateByte()]))
        return result

    def __createStateByte(self):
        stateByte = 0x0
        for i in range(0, len(self.state)):
            if not self.state[i]:  # Card requires bit = 0 to turn relay on
                stateByte += 1 << i
        return stateByte

    def on(self, channel):
        self.__checkChannel(channel)
        self.state[channel - 1] = True
        self.__sendStateCommand()

    def off(self, channel):
        self.__checkChannel(channel)
        self.state[channel - 1] = False
        self.__sendStateCommand()

    def __checkChannel(self, channel):
        if channel > len(self.state):
            raise InvalidArgumentException()


class UpDownStopRelay(Device):

    def __init__(self, deviceID, controller, directionRelay, startStopRelay, **kwargs):
        super(UpDownStopRelay, self).__init__(deviceID, **kwargs)
        self.directionRelay = controller.getDevice(directionRelay[0]).createDevice(self.deviceID + "_direction", directionRelay[1])
        self.startStopRelay = controller.getDevice(startStopRelay[0]).createDevice(self.deviceID + "_startStop", startStopRelay[1])

    def raiseUp(self):
        self.directionRelay.on()
        self.startStopRelay.on()

    def lower(self):
        self.directionRelay.off()
        self.startStopRelay.on()

    def stop(self):
        self.startStopRelay.off()


class UpDownStopArray(Device):

    def __init__(self, deviceID, controller, relays={}, **kwargs):
        super(UpDownStopArray, self).__init__(deviceID, **kwargs)
        self.relays = {}
        for idx, devID in relays.iteritems():
            self.relays[int(idx)] = controller.getDevice(devID)

    def add(self, device, number):
        self.relays[number] = device

    def raiseUp(self, number):
        if number in self.relays.keys():
            self.relays[number].raiseUp()
        elif number == 0:
            for r in self.relays.values():
                r.raiseUp()
        else:
            logging.error("Tried to raise relay channel " + str(number) + " but no such device attached to " + self.deviceID)

    def lower(self, number):
        if number in self.relays.keys():
            self.relays[number].lower()
        elif number == 0:
            for r in self.relays.values():
                r.lower()
        else:
            logging.error("Tried to lower relay channel " + str(number) + " but no such device attached to " + self.deviceID)

    def stop(self, number):
        if number in self.relays.keys():
            self.relays[number].stop()
        elif number == 0:
            for r in self.relays.values():
                r.stop()
        else:
            logging.error("Tried to stop relay channel " + str(number) + " but no such device attached to " + self.deviceID)
