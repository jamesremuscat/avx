import logging


class VISCAController:
    def move(self, camDeviceID, direction):
        def reallyMove():
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
        return self.withDevice(camDeviceID, reallyMove)

    def zoom(self, camDeviceID, zoomType):
        def reallyZoom():
            camera = self.devices[camDeviceID]
            if zoomType == CameraZoom.Tele:
                return camera.zoomIn()
            elif zoomType == CameraZoom.Wide:
                return camera.zoomOut()
            elif zoomType == CameraZoom.Stop:
                return camera.zoomStop()
        return self.withDevice(camDeviceID, reallyZoom)

    def focus(self, camDeviceID, focusType):
        def reallyFocus():
            camera = self.devices[camDeviceID]
            if focusType == CameraFocus.Auto:
                return camera.focusAuto()
            elif focusType == CameraFocus.Near:
                return camera.focusNear()
            elif focusType == CameraFocus.Far:
                return camera.focusFar()
            elif focusType == CameraFocus.Stop:
                return camera.focusStop()
        return self.withDevice(camDeviceID, reallyFocus)

    def exposure(self, camDeviceID, exposureType):
        def reallyExpose():
            camera = self.devices[camDeviceID]
            if exposureType == CameraExposure.Brighter:
                return camera.brighter()
            elif exposureType == CameraExposure.Darker:
                return camera.darker()
            elif exposureType == CameraExposure.Auto:
                return camera.autoExposure()
        return self.withDevice(camDeviceID, reallyExpose)

    def backlightComp(self, camDeviceID, compensation):
        def reallyBacklight():
            camera = self.devices[camDeviceID]
            if compensation:
                return camera.backlightCompOn()
            else:
                return camera.backlightCompOff()
        return self.withDevice(camDeviceID, reallyBacklight)

    def savePreset(self, camDeviceID, preset):
        def reallySave():
            camera = self.devices[camDeviceID]
            logging.debug("Saving preset " + str(preset) + " on device " + camDeviceID)
            camera.storePreset(preset)
        return self.withDevice(camDeviceID, reallySave)

    def recallPreset(self, camDeviceID, preset):
        def reallyRecall():
            camera = self.devices[camDeviceID]
            logging.debug("Recalling preset " + str(preset) + " on device " + camDeviceID)
            camera.recallPreset(preset)
        return self.withDevice(camDeviceID, reallyRecall)

    def whiteBalance(self, camDeviceID, wbSetting):
        def reallyBalance():
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
        return self.withDevice(camDeviceID, reallyBalance)

    def getPosition(self, camDeviceID):
        def reallyGetPos():
            camera = self.devices[camDeviceID]
            logging.debug("Querying position of device " + camDeviceID)
            return camera.getPosition()
        return self.withDevice(camDeviceID, reallyGetPos)

    def goto(self, camDeviceID, pos, panSpeed, tiltSpeed):
        def reallyGoto():
            camera = self.devices[camDeviceID]
            logging.debug("Setting position of device " + camDeviceID)
            return camera.goto(pos, panSpeed, tiltSpeed)
        return self.withDevice(camDeviceID, reallyGoto)

    def cameraCommand(self, camDeviceID, command):
        def reallyCommand():
            camera = self.devices[camDeviceID]
            return camera.execute(command)
        return self.withDevice(camDeviceID, reallyCommand)


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
