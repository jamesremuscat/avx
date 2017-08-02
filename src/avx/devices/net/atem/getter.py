# Getters for ATEM. To be used as a mixin with main ATEM class.
from avx.devices.net.atem.utils import assertTopology


class ATEMGetter(object):

    def getInputs(self):
        return self._system_config['inputs']

    def getAuxState(self):
        return self._state['aux']

    def getTally(self):
        return self._state['tally']

    def getDSKState(self):
        return self._state['dskeyers']

    @assertTopology("mes", "me")
    def getFadeToBlackState(self, me=1):
        return self._state['transition'][me]['ftb']
