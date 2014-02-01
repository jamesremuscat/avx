import logging


class VISCAController:
    def move(self, camDeviceID, direction):
        if self.hasDevice(camDeviceID):
            camera = self.devices[camDeviceID]
            if direction == CameraMove.Left:
                return camera.moveLeft()
            elif direction == CameraMove.Right:
                return camera.moveRight()
            elif direction == CameraMove.Up:
                return camera.moveUp()
            elif direction == CameraMove.Down:
                return camera.moveDown()
            elif direction == CameraMove.Stop:
                return camera.stop()
        else:
            logging.warn("No device with ID " + camDeviceID)
        return -1

    def zoom(self, camDeviceID, zoomType):
        if self.hasDevice(camDeviceID):
            camera = self.devices[camDeviceID]
            if zoomType == CameraZoom.Tele:
                return camera.zoomIn()
            elif zoomType == CameraZoom.Wide:
                return camera.zoomOut()
            elif zoomType == CameraZoom.Stop:
                return camera.zoomStop()
        else:
            logging.warn("No device with ID " + camDeviceID)
        return -1

    def focus(self, camDeviceID, focusType):
        if self.hasDevice(camDeviceID):
            camera = self.devices[camDeviceID]
            if focusType == CameraFocus.Auto:
                return camera.focusAuto()
            elif focusType == CameraFocus.Near:
                return camera.focusNear()
            elif focusType == CameraFocus.Far:
                return camera.focusFar()
            elif focusType == CameraFocus.Stop:
                return camera.focusStop()
        else:
            logging.warn("No device with ID " + camDeviceID)
        return -1

    def exposure(self, camDeviceID, exposureType):
        if self.hasDevice(camDeviceID):
            camera = self.devices[camDeviceID]
            if exposureType == CameraExposure.Brighter:
                return camera.brighter()
            elif exposureType == CameraExposure.Darker:
                return camera.darker()
            elif exposureType == CameraExposure.Auto:
                return camera.autoExposure()
        else:
            logging.warn("No device with ID " + camDeviceID)
        return -1

    def backlightComp(self, camDeviceID, compensation):
        if self.hasDevice(camDeviceID):
            camera = self.devices[camDeviceID]
            if compensation:
                return camera.backlightCompOn()
            else:
                return camera.backlightCompOff()
        else:
            logging.warn("No device with ID " + camDeviceID)
        return -1

    def savePreset(self, camDeviceID, preset):
        if self.hasDevice(camDeviceID):
            camera = self.devices[camDeviceID]
            logging.debug("Saving preset " + str(preset) + " on device " + camDeviceID)
            camera.storePreset(preset)
        else:
            logging.warn("No device with ID " + camDeviceID)
        return -1

    def recallPreset(self, camDeviceID, preset):
        if self.hasDevice(camDeviceID):
            camera = self.devices[camDeviceID]
            logging.debug("Recalling preset " + str(preset) + " on device " + camDeviceID)
            camera.recallPreset(preset)
        else:
            logging.warn("No device with ID " + camDeviceID)
        return -1

    def whiteBalance(self, camDeviceID, wbSetting):
        if self.hasDevice(camDeviceID):
            camera = self.devices[camDeviceID]
            if wbSetting == CameraWhiteBalance.Auto:
                return camera.whiteBalanceAuto()
            elif wbSetting == CameraWhiteBalance.Indoor:
                return camera.whiteBalanceIndoor()
            elif wbSetting == CameraWhiteBalance.Outdoor:
                return camera.whiteBalanceOutdoor()
            elif wbSetting == CameraWhiteBalance.OnePush:
                return camera.whiteBalanceOnePush()
            elif wbSetting == CameraWhiteBalance.Trigger:
                return camera.whiteBalanceOnePushTrigger()
        else:
            logging.warn("No device with ID " + camDeviceID)
        return -1

    def getPosition(self, camDeviceID):
        if self.hasDevice(camDeviceID):
            camera = self.devices[camDeviceID]
            logging.debug("Querying position of device " + camDeviceID)
            return camera.getPosition()
        else:
            logging.warn("No device with ID " + camDeviceID)
        return None

    def goto(self, camDeviceID, pos, panSpeed, tiltSpeed):
        if self.hasDevice(camDeviceID):
            camera = self.devices[camDeviceID]
            logging.debug("Setting position of device " + camDeviceID)
            return camera.goto(pos, panSpeed, tiltSpeed)
        else:
            logging.warn("No device with ID " + camDeviceID)
        return None

    def cameraCommand(self, camDeviceID, command):
        if self.hasDevice(camDeviceID):
            camera = self.devices[camDeviceID]
            return camera.execute(command)
        else:
            logging.warn("No device with ID " + camDeviceID)
        return -1


class CameraMove():
    Left, Right, Up, Down, Stop = range(5)


class CameraZoom():
    Tele, Wide, Stop = range(3)


class CameraFocus():
    Near, Far, Auto, Stop = range(4)


class CameraExposure():
    Brighter, Darker, Auto = range(3)


class CameraWhiteBalance():
    Auto, Indoor, Outdoor, OnePush, Trigger = range(5)
