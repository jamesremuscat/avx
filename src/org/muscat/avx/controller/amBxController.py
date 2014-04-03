class amBxController(object):

    def setColour(self, device, light, red, green, blue):
        def reallySetColour():
            return self.devices[device].setColour(int(light), int(red), int(green), int(blue))
        return self.withDevice(device, reallySetColour)

    def allOff(self, device):
        def reallyAllOff():
            return self.devices[device].allOff()
        return self.withDevice(device, reallyAllOff)
