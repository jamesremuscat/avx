from .constants import VideoSource
from .utils import requiresInit, assertTopology
from avx.devices.Device import InvalidArgumentException


#############
# Public ATEM control functions. Designed to be used as a mixin.
#############
class ATEMSender(object):

    def _resolveInputBytes(self, inputID):
        if isinstance(inputID, VideoSource):
            inputID = inputID.value
        if inputID not in self._system_config['inputs'].keys():
            raise InvalidArgumentException()
        return [(inputID >> 8), (inputID & 0xFF)]

    @requiresInit
    @assertTopology('aux_busses', 'auxChannel')
    def setAuxSource(self, auxChannel, inputID):
        self._sendCommand(
            "CAuS",
            [0x01, auxChannel - 1] + self._resolveInputBytes(inputID)
        )

    @requiresInit
    @assertTopology('mes', 'me')
    def setPreview(self, inputID, me=1):
        self._sendCommand(
            'CPvI',
            [me - 1, 0] + self._resolveInputBytes(inputID)
        )

    @requiresInit
    @assertTopology('mes', 'me')
    def setProgram(self, inputID, me=1):
        self._sendCommand(
            'CPgI',
            [me - 1, 0] + self._resolveInputBytes(inputID)
        )

    @requiresInit
    @assertTopology('mes', 'me')
    def performCut(self, me=1):
        self._sendCommand(
            'DCut',
            [me - 1, 0, 0, 0]
        )

    @requiresInit
    @assertTopology('mes', 'me')
    def performAutoTake(self, me=1):
        self._sendCommand(
            'DAut',
            [me - 1, 0, 0, 0]
        )

    @requiresInit
    @assertTopology('mes', 'me')
    def setNextTransition(self, transitionStyle, bkgd=None, key1=None, key2=None, key3=None, key4=None, me=1):
        if (bkgd is None and key1 is None and key2 is None and key3 is None and key4 is None):
            set_mask = 1
        else:
            set_mask = 3

        tie_mask = 0
        if bkgd:
            tie_mask |= 1
        if key1:
            tie_mask |= 2
        if key2:
            tie_mask |= 4
        if key3:
            tie_mask |= 8
        if key4:
            tie_mask |= 16

        self._sendCommand(
            'CTTp',
            [set_mask, me - 1, transitionStyle.value, tie_mask]
        )

    @requiresInit
    @assertTopology('mes', 'me')
    def setMixTransitionRate(self, frames, me=1):
        if frames <= 0 or frames > 250:
            raise InvalidArgumentException
        self._sendCommand(
            'CTMx',
            [me - 1, frames, 0x93, 0x07]
        )
