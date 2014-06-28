'''
Created on 13 Nov 2012

@author: james
'''
from org.muscat.avx.devices.SerialDevice import SerialDevice
from org.muscat.avx.CameraPosition import CameraPosition
from org.muscat.avx.devices.VISCACommands import VISCACommand


class VISCACamera(SerialDevice):
    '''
    A camera controlled by the Sony VISCA protocol e.g. Sony D31.
    '''

    # Pan/tilt speeds can vary from 0x01 - 0x18; AMX uses 0x06
    panSpeed = 0x06
    tiltSpeed = 0x06

    # Zoom speed can vary from 0x02-0x07
    zoomSpeed = 0x06

    def __init__(self, deviceID, serialDevice, cameraID, **kwargs):
        super(VISCACamera, self).__init__(deviceID, serialDevice)
        self.cameraID = cameraID

    def sendVISCA(self, commandBytes):
        return self.sendCommand(SerialDevice.byteArrayToString([0x80 + self.cameraID] + commandBytes + [0xFF]))

    def execute(self, command):
        if isinstance(command, VISCACommand):
            return self.sendCommand(SerialDevice.byteArrayToString(command.getBytes(self.cameraID)))

    def moveUp(self):
        return self.sendVISCA([0x01, 0x06, 0x01, self.panSpeed, self.tiltSpeed, 0x03, 0x01])

    def moveUpLeft(self):
        return self.sendVISCA([0x01, 0x06, 0x01, self.panSpeed, self.tiltSpeed, 0x01, 0x01])

    def moveLeft(self):
        return self.sendVISCA([0x01, 0x06, 0x01, self.panSpeed, self.tiltSpeed, 0x01, 0x03])

    def moveDownLeft(self):
        return self.sendVISCA([0x01, 0x06, 0x01, self.panSpeed, self.tiltSpeed, 0x01, 0x02])

    def moveDown(self):
        return self.sendVISCA([0x01, 0x06, 0x01, self.panSpeed, self.tiltSpeed, 0x03, 0x02])

    def moveDownRight(self):
        return self.sendVISCA([0x01, 0x06, 0x01, self.panSpeed, self.tiltSpeed, 0x02, 0x02])

    def moveRight(self):
        return self.sendVISCA([0x01, 0x06, 0x01, self.panSpeed, self.tiltSpeed, 0x02, 0x03])

    def moveUpRight(self):
        return self.sendVISCA([0x01, 0x06, 0x01, self.panSpeed, self.tiltSpeed, 0x02, 0x01])

    def stop(self):
        return self.sendVISCA([0x01, 0x06, 0x01, self.panSpeed, self.tiltSpeed, 0x03, 0x03])

    def zoomIn(self):
        return self.sendVISCA([0x01, 0x04, 0x07, 0x20 + self.zoomSpeed])

    def zoomOut(self):
        return self.sendVISCA([0x01, 0x04, 0x07, 0x30 + self.zoomSpeed])

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

    def get(self, query, responseSize):
        self.port.flushInput()
        self.sendVISCA(query)
        return [int(elem.encode("hex"), base=16) for elem in self.port.read(responseSize)]

    def getPosition(self):
        cameraInfo = self.get([0x09, 0x06, 0x12, 0xFF], 11)  # returns Y0 50 0W 0W 0W 0W 0Z 0Z 0Z 0Z FF where WWWW = pan, ZZZZ = tilt
        pan = (cameraInfo[2] << 12) + (cameraInfo[3] << 8) + (cameraInfo[4] << 4) + cameraInfo[5]
        tilt = (cameraInfo[6] << 12) + (cameraInfo[7] << 8) + (cameraInfo[8] << 4) + cameraInfo[9]

        cameraInfo = self.get([0x09, 0x04, 0x47, 0xFF], 7)  # returns Y0 50 0Z 0Z 0Z 0Z FF where ZZZZ = zoom
        zoom = (cameraInfo[2] << 12) + (cameraInfo[3] << 8) + (cameraInfo[4] << 4) + cameraInfo[5]

        return CameraPosition(pan, tilt, zoom)

    def goto(self, pos, panSpeed, tiltSpeed):
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
                 panSpeed & 0xFF,
                 tiltSpeed & 0xFF,
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
