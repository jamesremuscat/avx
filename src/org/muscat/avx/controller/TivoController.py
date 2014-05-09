from org.muscat.avx.controller.ControllerHelpers import deviceMethod
from org.muscat.avx.controller.ControllerHttp import httpAccessible


class TivoController(object):

    @deviceMethod
    @httpAccessible
    def play(self, deviceID):
        return self.devices[deviceID].play()

    @deviceMethod
    @httpAccessible
    def pause(self, deviceID):
        return self.devices[deviceID].pause()

    @deviceMethod
    @httpAccessible
    def rewind(self, deviceID):
        return self.devices[deviceID].rewind()

    @deviceMethod
    @httpAccessible
    def fastForward(self, deviceID):
        return self.devices[deviceID].fastForward()

    @deviceMethod
    @httpAccessible
    def replay(self, deviceID):
        return self.devices[deviceID].replay()

    @deviceMethod
    @httpAccessible
    def skip(self, deviceID):
        return self.devices[deviceID].skip()

    @deviceMethod
    @httpAccessible
    def slow(self, deviceID):
        return self.devices[deviceID].slow()
