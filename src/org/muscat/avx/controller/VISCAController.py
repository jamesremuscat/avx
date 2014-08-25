from org.muscat.avx.controller.ControllerHelpers import deviceMethod
import logging
from org.muscat.avx.controller.ControllerHttp import httpAccessible


class VISCAController:

    defaultSpeed = 6

    @deviceMethod
    @httpAccessible
    def move(self, camDeviceID, direction, pan=defaultSpeed, tilt=defaultSpeed):
        camera = self.devices[camDeviceID]
        if direction == CameraMove.Left:
            return camera.moveLeft(pan, tilt)
        elif direction == CameraMove.UpLeft:
            return camera.moveUpLeft(pan, tilt)
        elif direction == CameraMove.Up:
            return camera.moveUp(pan, tilt)
        elif direction == CameraMove.UpRight:
            return camera.moveUpRight(pan, tilt)
        elif direction == CameraMove.Right:
            return camera.moveRight(pan, tilt)
        elif direction == CameraMove.DownRight:
            return camera.moveDownRight(pan, tilt)
        elif direction == CameraMove.Down:
            return camera.moveDown(pan, tilt)
        elif direction == CameraMove.DownLeft:
            return camera.moveDownLeft(pan, tilt)
        elif direction == CameraMove.Stop:
            return camera.stop()

    @deviceMethod
    @httpAccessible
    def zoom(self, camDeviceID, zoomType):
        camera = self.devices[camDeviceID]
        if zoomType == CameraZoom.Tele:
            return camera.zoomIn()
        elif zoomType == CameraZoom.Wide:
            return camera.zoomOut()
        elif zoomType == CameraZoom.Stop:
            return camera.zoomStop()

    @deviceMethod
    @httpAccessible
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
    @httpAccessible
    def exposure(self, camDeviceID, exposureType):
        camera = self.devices[camDeviceID]
        if exposureType == CameraExposure.Brighter:
            return camera.brighter()
        elif exposureType == CameraExposure.Darker:
            return camera.darker()
        elif exposureType == CameraExposure.Auto:
            return camera.autoExposure()

    @deviceMethod
    @httpAccessible
    def backlightComp(self, camDeviceID, compensation):
            camera = self.devices[camDeviceID]
            if compensation:
                return camera.backlightCompOn()
            else:
                return camera.backlightCompOff()

    @deviceMethod
    @httpAccessible
    def savePreset(self, camDeviceID, preset):
        camera = self.devices[camDeviceID]
        logging.debug("Saving preset " + str(preset) + " on device " + camDeviceID)
        camera.storePreset(preset)

    @deviceMethod
    @httpAccessible
    def recallPreset(self, camDeviceID, preset):
        camera = self.devices[camDeviceID]
        logging.debug("Recalling preset " + str(preset) + " on device " + camDeviceID)
        return camera.recallPreset(preset)

    @deviceMethod
    @httpAccessible
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
    @httpAccessible
    def setAutoExposure(self, camDeviceID):
        camera = self.devices[camDeviceID]
        camera.setAutoExposure()

    @deviceMethod
    @httpAccessible
    def setAperturePriority(self, camDeviceID):
        camera = self.devices[camDeviceID]
        camera.setAperturePriority()

    @deviceMethod
    @httpAccessible
    def setAperture(self, camDeviceID, aperture):
        camera = self.devices[camDeviceID]
        camera.setAperture(aperture)

    @deviceMethod
    @httpAccessible
    def getPosition(self, camDeviceID):
        camera = self.devices[camDeviceID]
        logging.debug("Querying position of device " + camDeviceID)
        return camera.getPosition()

    @deviceMethod
    @httpAccessible
    def goto(self, camDeviceID, pos, panSpeed, tiltSpeed):
        camera = self.devices[camDeviceID]
        logging.debug("Setting position of device " + camDeviceID)
        return camera.goto(pos, panSpeed, tiltSpeed)

    @deviceMethod
    @httpAccessible
    def cameraCommand(self, camDeviceID, command):
        camera = self.devices[camDeviceID]
        return camera.execute(command)


class CameraMove():
    Left, UpLeft, Up, UpRight, Right, DownRight, Down, DownLeft, Stop = range(9)


class CameraZoom():
    Tele, Wide, Stop = range(3)


class CameraFocus():
    Near, Far, Auto, Stop = range(4)


class CameraExposure():
    Brighter, Darker, Auto = range(3)


class CameraWhiteBalance():
    Auto, Indoor, Outdoor, OnePush, Trigger = range(5)
