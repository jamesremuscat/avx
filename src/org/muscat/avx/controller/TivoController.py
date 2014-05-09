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
