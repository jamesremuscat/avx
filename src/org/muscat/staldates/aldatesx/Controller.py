from org.muscat.staldates.aldatesx.Sequencer import Sequencer, Event
import logging
from logging import Handler
class Controller(object):
    '''
    A Controller is essentially a bucket of devices, each identified with a string deviceID.
    '''
    pyroName = "aldates.alix.controller"

    def __init__(self):
        self.devices = {}
        self.sequencer = Sequencer()
        self.sequencer.start()
        self.logHandler = ControllerLogHandler()
        logging.getLogger().addHandler(self.logHandler)
    
    def addDevice(self, device):
        self.devices[device.deviceID] = device
        
    def hasDevice(self, deviceID):
        return self.devices.has_key(deviceID)
    
    def initialise(self):
        for device in self.devices.itervalues():
            device.initialise()
        
    def switch(self, deviceID, inChannel, outChannel):
        '''If a device with the given ID exists, perform a video switch. If not then return -1.'''
        if self.devices.has_key(deviceID) :
            logging.debug("Switching device " + deviceID + ": " + str(inChannel) + "=>" + str(outChannel))
            return self.devices[deviceID].sendInputToOutput(inChannel, outChannel)
        else:
            logging.warn("No device with ID " + deviceID)
            return -1
        
    def move(self, camDeviceID, direction):
        if self.devices.has_key(camDeviceID):
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
        if self.devices.has_key(camDeviceID):
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
        if self.devices.has_key(camDeviceID):
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
        if self.devices.has_key(camDeviceID):
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
        if self.devices.has_key(camDeviceID):
            camera = self.devices[camDeviceID]
            if compensation:
                return camera.backlightCompOn()
            else:
                return camera.backlightCompOff()
        else:
            logging.warn("No device with ID " + camDeviceID)
        return -1
    
    def savePreset(self, camDeviceID, preset):
        if self.devices.has_key(camDeviceID):
            camera = self.devices[camDeviceID]
            logging.debug("Saving preset " + str(preset) + " on device " + camDeviceID)
            camera.storePreset(preset)
        else:
            logging.warn("No device with ID " + camDeviceID)
        return -1
    
    def recallPreset(self, camDeviceID, preset):
        if self.devices.has_key(camDeviceID):
            camera = self.devices[camDeviceID]
            logging.debug("Recalling preset " + str(preset) + " on device " + camDeviceID)
            camera.recallPreset(preset)
        else:
            logging.warn("No device with ID " + camDeviceID)
        return -1
    
    def getPosition(self, camDeviceID):
        if self.devices.has_key(camDeviceID):
            camera = self.devices[camDeviceID]
            logging.debug("Querying position of device " + camDeviceID)
            return camera.getPosition()
        else:
            logging.warn("No device with ID " + camDeviceID)
        return None
    
    def toggleOverscan(self, scDevice, overscan):
        if self.devices.has_key(scDevice):
            sc = self.devices[scDevice]
            if overscan:
                sc.overscanOn()
            else:
                sc.overscanOff()
        else:
            logging.warn("No device with ID " + scDevice)
        return -1
    
    def toggleFreeze(self, scDevice, freeze):
        if self.devices.has_key(scDevice):
            sc = self.devices[scDevice]
            if freeze:
                sc.freeze()
            else:
                sc.unfreeze()
        else:
            logging.warn("No device with ID " + scDevice)
        return -1
    
    def toggleOverlay(self, scDevice, overlay):
        if self.devices.has_key(scDevice):
            sc = self.devices[scDevice]
            if overlay:
                sc.overlayOn()
            else:
                sc.overlayOff()
        else:
            logging.warn("No device with ID " + scDevice)
        return -1
    
    def toggleFade(self, scDevice, fade):
        if self.devices.has_key(scDevice):
            sc = self.devices[scDevice]
            if fade:
                sc.fadeOut()
            else:
                sc.fadeIn()
        else:
            logging.warn("No device with ID " + scDevice)
        return -1
    
    def systemPowerOn(self):
        if self.devices.has_key("Power"):
            power = self.devices["Power"]
        
            self.sequencer.sequence(
                Event(power.on, 1),
                self.sequencer.wait(3),
                Event(power.on, 2),
                self.sequencer.wait(3),
                Event(power.on, 3),
                self.sequencer.wait(10),
                Event(power.on, 4)
            )
    
    def systemPowerOff(self):
        if self.devices.has_key("Power"):
            power = self.devices["Power"]
        
            self.sequencer.sequence(
                Event(power.off, 4),
                self.sequencer.wait(3),
                Event(power.off, 2),
                self.sequencer.wait(3),
                Event(power.off, 3),
                self.sequencer.wait(3),
                Event(power.off, 4)
            )
            
    def getLog(self):
        return self.logHandler.entries
    
    
class CameraMove():
    Left, Right, Up, Down, Stop = range(5)
    
class CameraZoom():
    Tele, Wide, Stop = range(3)
    
class CameraFocus():
    Near, Far, Auto, Stop = range(4)
    
class CameraExposure():
    Brighter, Darker, Auto = range(3)
    
class ControllerLogHandler(Handler):
    
    def __init__(self):
        super(ControllerLogHandler, self).__init__()
        self.entries = []
            
    def emit(self, record):
        self.entries.append(record)
        if len(self.entries) > 100:
            self.entries.pop(0)
