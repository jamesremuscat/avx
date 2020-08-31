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

    def getUSKState(self):
        return self._state['keyers']

    def getSuperSourceState(self):
        return self._state['supersource']

    def _get_supersource_sources(self):
        result = []
        ssrc = self.getSuperSourceState()
        if 'fill' in ssrc:
            result.append(ssrc['fill'])
        if 'key' in ssrc:
            result.append(ssrc['key'])

        for box in ssrc.get('boxes', []):
            if box.get('enabled', False):
                result.append(box['source'])

        return result

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
