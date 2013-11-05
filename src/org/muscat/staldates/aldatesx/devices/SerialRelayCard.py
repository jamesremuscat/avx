from org.muscat.staldates.aldatesx.devices.SerialDevice import SerialDevice
from org.muscat.staldates.aldatesx.devices.Device import Device
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

    def __init__(self, deviceID, relayCard, channel):
        super(RelayDevice, self).__init__(deviceID)
        self.relayCard = relayCard
        self.channel = channel

    def on(self):
        return self.relayCard.on(self.channel)

    def off(self):
        return self.relayCard.off(self.channel)


class KMtronicSerialRelayCard(SerialRelayCard):

    def __init__(self, deviceID, serialDevice, **kwargs):
        SerialRelayCard.__init__(self, deviceID, serialDevice)

    def on(self, channel):
        return self.sendCommand(SerialDevice.byteArrayToString([0xFF, channel, 0x01]))

    def off(self, channel):
        return self.sendCommand(SerialDevice.byteArrayToString([0xFF, channel, 0x00]))


class JBSerialRelayCard(SerialRelayCard):

    sendDelay = 0.05

    def __init__(self, deviceID, serialDevice, **kwargs):
        SerialRelayCard.__init__(self, deviceID, serialDevice, baud=19200)

    def on(self, channel):
        result = self.sendCommand(SerialDevice.byteArrayToString([0x30 + 2 * channel]))
        time.sleep(self.sendDelay)
        return result

    def off(self, channel):
        result = self.sendCommand(SerialDevice.byteArrayToString([0x31 + 2 * channel]))
        time.sleep(self.sendDelay)
        return result


class UpDownStopRelay(Device):

    def __init__(self, deviceID, controller, directionRelay, startStopRelay):
        super(UpDownStopRelay, self).__init__(deviceID)
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
        super(UpDownStopArray, self).__init__(deviceID)
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
