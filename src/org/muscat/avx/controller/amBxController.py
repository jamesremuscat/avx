class amBxController(object):

    def setColour(self, device, light, red, green, blue):
        def reallySetColour():
            return self.devices[device].setColour(light, red, green, blue)
        return self.withDevice(device, reallySetColour)
