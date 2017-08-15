# Getters for ATEM. To be used as a mixin with main ATEM class.
from avx.devices.net.atem.utils import assertTopology, requiresInit


class ATEMGetter(object):

    def isConnected(self):
        return self._isInitialized

    def getInputs(self):
        return self._system_config['inputs']

    def getAuxState(self):
        return self._state['aux']

    def getTally(self):
        return self._state['tally']

    def getDSKState(self):
        return self._state['dskeyers']

    @requiresInit
    @assertTopology("mes", "me")
    def getFadeToBlackState(self, me=1):
        return self._state['transition'][me - 1]['ftb']

    @requiresInit
    @assertTopology("mes", "me")
    def getFadeToBlackProperties(self, me=1):
        return self._config['transitions'][me - 1]['ftb']

    @requiresInit
    @assertTopology("mes", "me")
    def getMixTransitionProps(self, me=1):
        return self._config['transitions'][me - 1]['mix']
