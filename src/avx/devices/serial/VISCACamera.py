'''
Created on 13 Nov 2012

@author: james
'''
from avx.devices import InvalidArgumentException
from avx.devices.serial import SerialDevice
from avx.CameraPosition import CameraPosition
from enum import Enum
from threading import Lock, ThreadError, Event

import logging
from avx.devices.Device import Device


# Pan speeds can vary from 0x01 - 0x18
DEFAULT_PAN_SPEED = 0x06
# Tilt speeds can vary from 0x01 - 0x14
DEFAULT_TILT_SPEED = 0x06
# Zoom speed can vary from 0x02-0x07
DEFAULT_ZOOM_SPEED = 0x06


def constrainPanTiltSpeed(func):
    def inner(elf, panSpeed=DEFAULT_PAN_SPEED, tiltSpeed=DEFAULT_TILT_SPEED):
        elf.checkPan(panSpeed)
        elf.checkTilt(tiltSpeed)
        func(elf, panSpeed, tiltSpeed)
    return inner


class VISCAPort(SerialDevice):
    '''
    A serial port through which one or more VISCA cameras are controlled.

    Note that, for backwards compatibility, in order to use a shared port,
    a VISCACamera needs a serialDevice specified as None, and a controller,
    in its constructor. If you're using a Controller, you only need
    worry about the former (the controller is passed in automatically).

    A controller is required as the viscaPort is passed in by device ID, and
    looked up in the controller. (This means you should define your VISCAPort
    first in your controller config, then any cameras attached to it.)
    '''

    def __init__(self, deviceID, serialDevice, **kwargs):
        super(VISCAPort, self).__init__(deviceID, serialDevice, **kwargs)
        self._cameras = {}
        self.portstr = self.port.portstr

    def addCamera(self, cameraID, camera):
        self._cameras[cameraID] = camera

    def hasFullMessage(self, recv_buffer):
        return len(recv_buffer) > 0 and recv_buffer[-1] == 0xFF

    def handleMessage(self, msgBytes):
        responseAddress = ((msgBytes[0] & 0xF0) >> 4) - 8
        if responseAddress in self._cameras:
            self._cameras[responseAddress].handleMessage(msgBytes)

    def write(self, data):
        self.port.write(data)

    def open(self):
        self.port.open()

    def close(self):
        self.port.close()


class VISCACamera(SerialDevice):
    '''
    A camera controlled by the Sony VISCA protocol e.g. Sony D31.
    '''

    def __init__(self, deviceID, serialDevice, cameraID, controller=None, viscaPort=None, waitForAck=True, **kwargs):
        if viscaPort is None or controller is None:
            super(VISCACamera, self).__init__(deviceID, serialDevice, **kwargs)
            self._isSharedPort = False
        else:
            Device.__init__(self, deviceID)
            self.port = controller.getDevice(viscaPort)
            self._isSharedPort = True
            self.port.addCamera(cameraID, self)
        self.cameraID = cameraID
        self._do_wait_for_ack = waitForAck
        self._wait_for_ack = Lock()
        self._wait_for_response = Lock()
        self._response_received = Event()
        self._last_response = None

    def initialise(self):
        if not self._isSharedPort:
            SerialDevice.initialise(self)

    def deinitialise(self):
        if not self._isSharedPort:
            SerialDevice.deinitialise(self)

    def sendVISCA(self, commandBytes):
        if self._do_wait_for_ack:
            self._wait_for_ack.acquire()
        return self.sendCommand(SerialDevice.byteArrayToString([0x80 + self.cameraID] + commandBytes + [0xFF]))

    def getVISCA(self, commandBytes):
        with self._wait_for_response:
            self.sendVISCA(commandBytes)
            logging.debug("Waiting for response.")
            self._response_received.wait()
            logging.debug("Received response")
            response = self._last_response
            self._response_received.clear()
            return response

    @constrainPanTiltSpeed
    def moveUp(self, pan=DEFAULT_PAN_SPEED, tilt=DEFAULT_TILT_SPEED):
        return self.sendVISCA([0x01, 0x06, 0x01, pan, tilt, 0x03, 0x01])

    @constrainPanTiltSpeed
    def moveUpLeft(self, pan=DEFAULT_PAN_SPEED, tilt=DEFAULT_TILT_SPEED):
        return self.sendVISCA([0x01, 0x06, 0x01, pan, tilt, 0x01, 0x01])

    @constrainPanTiltSpeed
    def moveLeft(self, pan=DEFAULT_PAN_SPEED, tilt=DEFAULT_TILT_SPEED):
        return self.sendVISCA([0x01, 0x06, 0x01, pan, tilt, 0x01, 0x03])

    @constrainPanTiltSpeed
    def moveDownLeft(self, pan=DEFAULT_PAN_SPEED, tilt=DEFAULT_TILT_SPEED):
        return self.sendVISCA([0x01, 0x06, 0x01, pan, tilt, 0x01, 0x02])

    @constrainPanTiltSpeed
    def moveDown(self, pan=DEFAULT_PAN_SPEED, tilt=DEFAULT_TILT_SPEED):
        return self.sendVISCA([0x01, 0x06, 0x01, pan, tilt, 0x03, 0x02])

    @constrainPanTiltSpeed
    def moveDownRight(self, pan=DEFAULT_PAN_SPEED, tilt=DEFAULT_TILT_SPEED):
        return self.sendVISCA([0x01, 0x06, 0x01, pan, tilt, 0x02, 0x02])

    @constrainPanTiltSpeed
    def moveRight(self, pan=DEFAULT_PAN_SPEED, tilt=DEFAULT_TILT_SPEED):
        return self.sendVISCA([0x01, 0x06, 0x01, pan, tilt, 0x02, 0x03])

    @constrainPanTiltSpeed
    def moveUpRight(self, pan=DEFAULT_PAN_SPEED, tilt=DEFAULT_TILT_SPEED):
        return self.sendVISCA([0x01, 0x06, 0x01, pan, tilt, 0x02, 0x01])

    @constrainPanTiltSpeed
    def stop(self, pan=DEFAULT_PAN_SPEED, tilt=DEFAULT_TILT_SPEED):
        return self.sendVISCA([0x01, 0x06, 0x01, pan, tilt, 0x03, 0x03])

    def zoomIn(self, speed=DEFAULT_ZOOM_SPEED):
        self.checkZoom(speed)
        return self.sendVISCA([0x01, 0x04, 0x07, 0x20 + speed])

    def zoomOut(self, speed=DEFAULT_ZOOM_SPEED):
        self.checkZoom(speed)
        return self.sendVISCA([0x01, 0x04, 0x07, 0x30 + speed])

    def zoomStop(self):
        return self.sendVISCA([0x01, 0x04, 0x07, 0x00])

    def focusFar(self):
        self.focusManual()
        return self.sendVISCA([0x01, 0x04, 0x08, 0x02])

    def focusNear(self):
        self.focusManual()
        return self.sendVISCA([0x01, 0x04, 0x08, 0x03])

    def focusStop(self):
        return self.sendVISCA([0x01, 0x04, 0x08, 0x00])

    def focusAuto(self):
        return self.sendVISCA([0x01, 0x04, 0x38, 0x02])

    def focusManual(self):
        return self.sendVISCA([0x01, 0x04, 0x38, 0x03])

    def brighter(self):
        self.sendVISCA([0x01, 0x04, 0x39, 0x0D])  # Put camera into manual exposure mode first!
        return self.sendVISCA([0x01, 0x04, 0x0D, 0x02])

    def darker(self):
        self.sendVISCA([0x01, 0x04, 0x39, 0x0D])  # Put camera into manual exposure mode first!
        return self.sendVISCA([0x01, 0x04, 0x0D, 0x03])

    def autoExposure(self):
        return self.sendVISCA([0x01, 0x04, 0x39, 0x00])

    def backlightCompOn(self):
        return self.sendVISCA([0x01, 0x04, 0x33, 0x02])

    def backlightCompOff(self):
        return self.sendVISCA([0x01, 0x04, 0x33, 0x03])

    def storePreset(self, preset):
        if preset < 0 or preset > 5:
            return -1
        self.sendVISCA([0x01, 0x04, 0x3F, 0x01, preset])

    def recallPreset(self, preset):
        if preset < 0 or preset > 5:
            return -1
        self.sendVISCA([0x01, 0x04, 0x3F, 0x02, preset])

    def whiteBalanceAuto(self):
        self.sendVISCA([0x01, 0x04, 0x35, 0x00])

    def whiteBalanceIndoor(self):
        self.sendVISCA([0x01, 0x04, 0x35, 0x01])

    def whiteBalanceOutdoor(self):
        self.sendVISCA([0x01, 0x04, 0x35, 0x02])

    def whiteBalanceOnePush(self):
        self.sendVISCA([0x01, 0x04, 0x35, 0x03])

    def whiteBalanceOnePushTrigger(self):
        self.sendVISCA([0x01, 0x04, 0x10, 0x05])

    def setAutoExposure(self):
        self.sendVISCA([0x01, 0x04, 0x39, 0x00])

    def setAperturePriority(self):
        self.sendVISCA([0x01, 0x04, 0x39, 0x0B])

    def setShutterPriority(self):
        self.sendVISCA([0x01, 0x04, 0x39, 0x0A])

    def setManualExposure(self):
        self.sendVISCA([0x01, 0x04, 0x39, 0x03])

    def setAperture(self, aperture):
        if isinstance(aperture, Aperture):
            av = aperture.code
        else:
            av = aperture
        self.sendVISCA([0x01, 0x04, 0x4B,
                        (av & 0xF000) >> 12,
                        (av & 0x0F00) >> 8,
                        (av & 0x00F0) >> 4,
                        (av & 0x000F)])

    def setShutter(self, shutter):
        if isinstance(shutter, Shutter):
            tv = shutter.code
        else:
            tv = shutter
        self.sendVISCA([0x01, 0x04, 0x4A,
                        (tv & 0xF000) >> 12,
                        (tv & 0x0F00) >> 8,
                        (tv & 0x00F0) >> 4,
                        (tv & 0x000F)])

    def setGain(self, gain):
        if isinstance(gain, Gain):
            h = gain.code
        else:
            h = gain
        self.sendVISCA([0x01, 0x04, 0x4C,
                        (h & 0xF000) >> 12,
                        (h & 0x0F00) >> 8,
                        (h & 0x00F0) >> 4,
                        (h & 0x000F)])

    def hasFullMessage(self, recv_buffer):
        return len(recv_buffer) > 0 and recv_buffer[-1] == 0xFF

    def handleMessage(self, msgBytes):
        responseType = (msgBytes[1] & 0x70) >> 4
        logging.debug("Response of type {}".format(responseType))
        if responseType >= 4 and responseType <= 6:  # ack, response or error
            try:
                self._wait_for_ack.release()
            except ThreadError:
                # We weren't blocked anyway
                pass
        if responseType == 5:
            self._last_response = msgBytes
            self._response_received.set()

    def getPosition(self):
        # returns Y0 50 0W 0W 0W 0W 0Z 0Z 0Z 0Z FF where WWWW = pan, ZZZZ = tilt
        pan_tilt_resp = self.getVISCA([0x09, 0x06, 0x12, 0xFF])

        # returns Y0 50 0Z 0Z 0Z 0Z FF where ZZZZ = zoom
        zoom_resp = self.getVISCA([0x09, 0x04, 0x47, 0xFF])

        pan = (pan_tilt_resp[2] << 12) + (pan_tilt_resp[3] << 8) + (pan_tilt_resp[4] << 4) + pan_tilt_resp[5]
        tilt = (pan_tilt_resp[6] << 12) + (pan_tilt_resp[7] << 8) + (pan_tilt_resp[8] << 4) + pan_tilt_resp[9]

        zoom = (zoom_resp[2] << 12) + (zoom_resp[3] << 8) + (zoom_resp[4] << 4) + zoom_resp[5]

        return CameraPosition(pan, tilt, zoom)

    def goto(self, pos, DEFAULT_PAN_SPEED, DEFAULT_TILT_SPEED):
        '''
        Takes a CameraPosition to directly set the required tilt, pan and zoom of the camera, and the speed at which to get there.
        VISCA somewhat arbitrarily limits these values to:
         - pan range: 0xFC90 to 0x0370 (centred on 0)
         - pan speed: 0x01-0x18
         - tilt range: 0xFED4 to 0x012C (centred on 0)
         - tilt speed: 0x01 - 0x14
         - zoom value: 0x00 (wide) to 0x03FF (tele)
        '''
        p = pos.pan
        t = pos.tilt
        z = pos.zoom

        setPT = [
            0x01,
            0x06,
            0x02,
            DEFAULT_PAN_SPEED & 0xFF,
            DEFAULT_TILT_SPEED & 0xFF,
            # Pan x 2 bytes, padded to four (ABCD -> 0A 0B 0C 0D)
            (p & 0xF000) >> 12,
            (p & 0x0F00) >> 8,
            (p & 0x00F0) >> 4,
            (p & 0x000F),
            # Tilt x 2 bytes, padded to four (ABCD -> 0A 0B 0C 0D)
            (t & 0xF000) >> 12,
            (t & 0x0F00) >> 8,
            (t & 0x00F0) >> 4,
            (t & 0x000F),
            0xFF,
        ]

        ret = self.sendVISCA(setPT)

        setZ = [
            0x01,
            0x04,
            0x47,
            (z & 0xF000) >> 12,
            (z & 0x0F00) >> 8,
            (z & 0x00F0) >> 4,
            (z & 0x000F),
            0xFF,
        ]

        ret += self.sendVISCA(setZ)

        return ret

    def checkPan(self, pan):
        if pan < 1 or pan > 0x18:
            raise InvalidArgumentException()

    def checkTilt(self, tilt):
        if tilt < 1 or tilt > 0x16:
            raise InvalidArgumentException()

    def checkZoom(self, zoom):
        if zoom < 2 or zoom > 7:
            raise InvalidArgumentException()


class Aperture(Enum):
    CLOSE = (0x00, "Closed")
    F28 = (0x01, "F28")
    F22 = (0x02, "F22")
    F19 = (0x03, "F19")
    F16 = (0x04, "F16")
    F14 = (0x05, "F14")
    F11 = (0x06, "F11")
    F9_6 = (0x07, "F9.6")
    F8 = (0x08, "F8")
    F6_8 = (0x09, "F6.8")
    F5_6 = (0x0A, "F5.6")
    F4_8 = (0x0B, "F4.8")
    F4 = (0x0C, "F4")
    F3_4 = (0x0D, "F3.4")
    F2_8 = (0x0E, "F2.8")
    F2_4 = (0x0F, "F2.4")
    F2 = (0x10, "F2")
    F1_8 = (0x11, "F1.8")

    def __init__(self, code, label):
        self.code = code
        self.label = label


class Shutter(Enum):
    T50 = (0x00, "1/50s")
    T60 = (0x01, "1/60s")
    T75 = (0x02, "1/75s")
    T90 = (0x03, "1/90s")
    T100 = (0x04, "1/100s")
    T120 = (0x05, "1/120s")
    T150 = (0x06, "1/150s")
    T180 = (0x07, "1/180s")
    T215 = (0x08, "1/215s")
    T250 = (0x09, "1/250s")
    T300 = (0x0A, "1/300s")
    T350 = (0x0B, "1/350s")
    T425 = (0x0C, "1/425s")
    T500 = (0x0D, "1/500s")
    T600 = (0x0E, "1/600s")
    T725 = (0x0F, "1/725s")
    T850 = (0x10, "1/850s")
    T1000 = (0x11, "1/1000s")
    T1250 = (0x12, "1/1250s")
    T1500 = (0x13, "1/1500s")
    T1750 = (0x14, "1/1750s")
    T2000 = (0x15, "1/2000s")
    T2500 = (0x16, "1/2500s")
    T3000 = (0x17, "1/3000s")
    T3500 = (0x18, "1/3500s")
    T4000 = (0x19, "1/4000s")
    T6000 = (0x1A, "1/6000s")
    T10000 = (0x1B, "1/10000s")

    def __init__(self, code, label):
        self.code = code
        self.label = label


class Gain(Enum):
    G_MINUS_3 = (0x00, "-3")
    G_0 = (0x01, "0")
    G_3 = (0x02, "3")
    G_6 = (0x03, "6")
    G_9 = (0x04, "9")
    G_12 = (0x05, "12")
    G_15 = (0x06, "15")
    G_18 = (0x07, "18")

    def __init__(self, code, label):
        self.code = code
        self.label = label
