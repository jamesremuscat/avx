from org.muscat.avx.controller.ControllerHelpers import deviceMethod
import logging


class VISCAController:

    @deviceMethod
    def move(self, camDeviceID, direction):
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

    @deviceMethod
    def zoom(self, camDeviceID, zoomType):
        camera = self.devices[camDeviceID]
        if zoomType == CameraZoom.Tele:
            return camera.zoomIn()
        elif zoomType == CameraZoom.Wide:
            return camera.zoomOut()
        elif zoomType == CameraZoom.Stop:
            return camera.zoomStop()

    @deviceMethod
    def focus(self, camDeviceID, focusType):
        camera = self.devices[camDeviceID]
        if focusType == CameraFocus.Auto:
            return camera.focusAuto()
        elif focusType == CameraFocus.Near:
            return camera.focusNear()
        elif focusType == CameraFocus.Far:
            return camera.focusFar()
        elif focusType == CameraFocus.Stop:
            return camera.focusStop()

    @deviceMethod
    def exposure(self, camDeviceID, exposureType):
        camera = self.devices[camDeviceID]
        if exposureType == CameraExposure.Brighter:
            return camera.brighter()
        elif exposureType == CameraExposure.Darker:
            return camera.darker()
        elif exposureType == CameraExposure.Auto:
            return camera.autoExposure()

    @deviceMethod
    def backlightComp(self, camDeviceID, compensation):
            camera = self.devices[camDeviceID]
            if compensation:
                return camera.backlightCompOn()
            else:
                return camera.backlightCompOff()

    @deviceMethod
    def savePreset(self, camDeviceID, preset):
        camera = self.devices[camDeviceID]
        logging.debug("Saving preset " + str(preset) + " on device " + camDeviceID)
        camera.storePreset(preset)

    @deviceMethod
    def recallPreset(self, camDeviceID, preset):
        camera = self.devices[camDeviceID]
        logging.debug("Recalling preset " + str(preset) + " on device " + camDeviceID)
        return camera.recallPreset(preset)

    @deviceMethod
    def whiteBalance(self, camDeviceID, wbSetting):
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

    @deviceMethod
    def getPosition(self, camDeviceID):
        camera = self.devices[camDeviceID]
        logging.debug("Querying position of device " + camDeviceID)
        return camera.getPosition()

    @deviceMethod
    def goto(self, camDeviceID, pos, panSpeed, tiltSpeed):
        camera = self.devices[camDeviceID]
        logging.debug("Setting position of device " + camDeviceID)
        return camera.goto(pos, panSpeed, tiltSpeed)

    @deviceMethod
    def cameraCommand(self, camDeviceID, command):
        camera = self.devices[camDeviceID]
        return camera.execute(command)


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
