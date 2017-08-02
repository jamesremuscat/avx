from .constants import MacroAction, VideoSource
from .utils import requiresInit, assertTopology, bytes_of
from avx.devices.Device import InvalidArgumentException


#############
# Public ATEM control functions. Designed to be used as a mixin.
#############
class ATEMSender(object):

    def _resolveInputBytes(self, inputID):
        if not isinstance(inputID, VideoSource):
            inputID = VideoSource(inputID)
        if inputID not in self._system_config['inputs'].keys():
            raise InvalidArgumentException()
        return [(inputID.value >> 8), (inputID.value & 0xFF)]

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

    @requiresInit
    @assertTopology('mes', 'me')
    def setFadeToBlackRate(self, frames, me=1):
        if frames <= 0 or frames > 250:
            raise InvalidArgumentException
        self._sendCommand(
            'FtbC',
            [1, me - 1, frames, 0]
        )

    @requiresInit
    @assertTopology('mes', 'me')
    def performFadeToBlack(self, me=1):
        self._sendCommand('FtbA', [me - 1, 0xA7, 0x59, 0x08])

########
# DSK
########

    @requiresInit
    # @assertTopology('dsks', 'dsk')  # FSR the ATEM 2 M/E is reporting 0 DSKs rather than 2 :(
    def performDSKAuto(self, dsk):
        if dsk <= 0 or dsk > 2:
            raise InvalidArgumentException
        self._sendCommand(
            'DDsA',
            [dsk - 1, 0, 0, 0]
        )

    @requiresInit
    # @assertTopology('dsks', 'dsk')  # FSR the ATEM 2 M/E is reporting 0 DSKs rather than 2 :(
    def setDSKOnAir(self, dsk, onAir):
        if dsk <= 0 or dsk > 2:
            raise InvalidArgumentException
        self._sendCommand(
            'CDsL',
            [dsk - 1, 1 if onAir else 0, 0xBE, 0x07]
        )

    @requiresInit
    # @assertTopology('dsks', 'dsk')  # FSR the ATEM 2 M/E is reporting 0 DSKs rather than 2 :(
    def setDSKRate(self, dsk, rate):
        if dsk <= 0 or dsk > 2:
            raise InvalidArgumentException
        if rate <= 0 or rate > 250:
            raise InvalidArgumentException
        self._sendCommand(
            'CDsR',
            [dsk - 1, rate, 0xAA, 0x07]
        )

    @requiresInit
    # @assertTopology('dsks', 'dsk')  # FSR the ATEM 2 M/E is reporting 0 DSKs rather than 2 :(
    def setDSKKeySource(self, dsk, source):
        if dsk <= 0 or dsk > 2:
            raise InvalidArgumentException
        self._sendCommand(
            'CDsC',
            [dsk - 1, 0] + self._resolveInputBytes(source)
        )

    @requiresInit
    # @assertTopology('dsks', 'dsk')  # FSR the ATEM 2 M/E is reporting 0 DSKs rather than 2 :(
    def setDSKFillSource(self, dsk, source):
        if dsk <= 0 or dsk > 2:
            raise InvalidArgumentException
        self._sendCommand(
            'CDsF',
            [dsk - 1, 0] + self._resolveInputBytes(source)
        )

    @requiresInit
    # @assertTopology('dsks', 'dsk')  # FSR the ATEM 2 M/E is reporting 0 DSKs rather than 2 :(
    def setDSKParams(self, dsk, preMultiplied=None, clip=None, gain=None):
        if dsk <= 0 or dsk > 2:
            raise InvalidArgumentException
        if clip:
            if clip < 0 or clip > 1000:
                raise InvalidArgumentException
        if gain:
            if gain < 0 or gain > 1000:
                raise InvalidArgumentException

        set_mask = 0
        if preMultiplied is not None:
            set_mask |= 1
        if clip is not None:
            set_mask |= 2
        else:
            clip = 0
        if gain is not None:
            set_mask |= 4
        else:
            gain = 0

        self._sendCommand(
            'CDsG',
            [
                set_mask,
                dsk - 1,
                1 if preMultiplied else 0,
                0
            ] +
            bytes_of(clip) +
            bytes_of(gain) +
            [
                0, 0, 0, 0
            ]
        )

########
# Macros
########

    @requiresInit
    def executeMacro(self, macro_index):
        if macro_index not in self._config['macros']:
            raise InvalidArgumentException
        self._sendCommand(
            'MAct',
            [macro_index, MacroAction.RUN.value, 0]
        )

    @requiresInit
    def executeMacroByName(self, macro_name):
        for idx, macro in self._config['macros'].iteritems():
            if macro['name'] == macro_name:
                self.executeMacro(idx)
                return True
        raise InvalidArgumentException
