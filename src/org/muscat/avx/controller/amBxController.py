from org.muscat.avx.controller.ControllerHelpers import deviceMethod
from org.muscat.avx.controller.ControllerHttp import httpAccessible


class amBxController(object):

    @deviceMethod
    @httpAccessible
    def setColour(self, device, light, red, green, blue):
        return self.devices[device].setColour(int(light), int(red), int(green), int(blue))

    @deviceMethod
    @httpAccessible
    def allOff(self, device):
        return self.devices[device].allOff()
