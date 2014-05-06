from org.muscat.avx.controller.ControllerHelpers import deviceMethod


class amBxController(object):

    @deviceMethod
    def setColour(self, device, light, red, green, blue):
        return self.devices[device].setColour(int(light), int(red), int(green), int(blue))

    @deviceMethod
    def allOff(self, device):
        return self.devices[device].allOff()
