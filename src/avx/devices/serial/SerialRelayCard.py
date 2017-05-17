from avx.devices.serial import SerialDevice
from avx.devices import Device, InvalidArgumentException
from time import sleep
from threading import Thread, Lock

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
        self.run_send_thread = False
        self.prevState = None

    def initialise(self):
        if not self.initialised:
            SerialRelayCard.initialise(self)
            self.sendCommand("\x50")
            time.sleep(0.1)
            self.sendCommand("\x51")
            self.initialised = True
        self.run_send_thread = True

        def run():
            while self.run_send_thread:
                self._sendStateCommand()
                sleep(0.1)

        runner = Thread(target=run)
        runner.setDaemon(True)
        runner.start()

    def deinitialise(self):
        self.run_send_thread = False

    def _sendStateCommand(self):
        toSend = self._createStateByte()
        if toSend != self.prevState:
            self.prevState = toSend
            result = self.sendCommand(SerialDevice.byteArrayToString([toSend]))
            return result

    def _createStateByte(self):
        stateByte = 0x0
        for i in range(0, len(self.state)):
            if not self.state[i]:  # Card requires bit = 0 to turn relay on
                stateByte += 1 << i
        return stateByte

    def _checkSenderState(self):
        if not self.run_send_thread:
            logging.warn("State change requested for {} but run_send_thread is False - device uninitialised?".format(self.deviceID))

    def on(self, channel):
        self.__checkChannel(channel)
        self._checkSenderState()
        self.state[channel - 1] = True

    def off(self, channel):
        self.__checkChannel(channel)
        self._checkSenderState()
        self.state[channel - 1] = False

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


class MomentaryUpDownStopRelay(Device):
    def __init__(self, deviceID, controller, upRelay, downRelay, stopRelay, **kwargs):
        super(MomentaryUpDownStopRelay, self).__init__(deviceID, **kwargs)
        self.upRelay = controller.getDevice(upRelay[0]).createDevice(self.deviceID + "_up", upRelay[1])
        self.downRelay = controller.getDevice(downRelay[0]).createDevice(self.deviceID + "_down", downRelay[1])
        self.stopRelay = controller.getDevice(stopRelay[0]).createDevice(self.deviceID + "_stop", stopRelay[1])
        self.lock = Lock()

    def _touch(self, relay):
        # We don't want to block the calling thread, so waiting for our lock happens in its own thread.
        # Thus, UpDownStopArray still works quickly, but you can't force multiple relays to be on for a single MUDS.
        def inner():
            with self.lock:
                relay.on()
                time.sleep(0.5)
                relay.off()
        Thread(target=inner).start()

    def raiseUp(self):
        self._touch(self.upRelay)

    def lower(self):
        self._touch(self.downRelay)

    def stop(self):
        self._touch(self.stopRelay)


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
