from .constants import AudioSource, MacroAction, VideoSource, KeyType
from .utils import requiresInit, assertTopology, bytes_of, array_pack
from avx.devices.Device import InvalidArgumentException
from avx.devices.net.atem.constants import MultiviewerLayout

import struct


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

    def _resolveAudioInputBytes(self, inputID):
        if not isinstance(inputID, AudioSource):
            inputID = AudioSource(inputID)
        return [(inputID.value >> 8), (inputID.value & 0xFF)]

    @requiresInit
    def setMultiviewerLayout(self, layout, mv=1):
        mv_count = self._system_config.get('multiviewers', 0)
        if mv > mv_count or mv <= 0:
            raise InvalidArgumentException('Tried to set multiviewer {} but we have {} available'.format(mv, mv_count))
        if not isinstance(layout, MultiviewerLayout):
            raise InvalidArgumentException('{} is not a MultiviewerLayout'.format(mv))
        self._sendCommand(
            'CMvP',
            [0x1, mv - 1, layout.value, 0]
        )

    @requiresInit
    def setMultiviewerWindowSource(self, window, source, mv=1):
        mv_count = self._system_config.get('multiviewers', 0)
        if window < 0 or window > 9:
            raise InvalidArgumentException('Multiviewer window should be in range 0-9 but got {}', window)
        if mv <= mv_count:
            self._sendCommand(
                'CMvI',
                [
                    mv - 1,
                    window
                ] + self._resolveInputBytes(source)
            )
        else:
            raise InvalidArgumentException('Tried to set multiviewer {} but we have {} available'.format(mv, mv_count))

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
# USK
########

    @requiresInit
    @assertTopology('mes', 'me')
    def setUSKOnAir(self, me, usk, onAir):
        me_keyers = len(self._system_config['keyers'].get(me - 1, {}))
        if usk > me_keyers:
            raise InvalidArgumentException

        self._sendCommand(
            'CKOn',
            [me - 1, usk - 1, 1 if onAir else 0, 0x0A]
        )
        # Not sure about those magic values

    @requiresInit
    @assertTopology('mes', 'me')
    def setUSKType(self, me, usk, type, flying):
        me_keyers = len(self._system_config['keyers'].get(me - 1, {}))
        if usk > me_keyers:
            raise InvalidArgumentException

        if not isinstance(type, KeyType):
            raise InvalidArgumentException

        self._sendCommand(
            'CKTp',
            [
                me - 1,
                usk - 1,
                type.value,
                1 if flying else 0,
                0, 0, 0, 0
            ]
        )

    @requiresInit
    @assertTopology('mes', 'me')
    def setUSKKeySource(self, me, usk, source):
        me_keyers = len(self._system_config['keyers'].get(me - 1, {}))
        if usk > me_keyers:
            raise InvalidArgumentException

        if not isinstance(source, VideoSource):
            raise InvalidArgumentException

        self._sendCommand(
            'CKeC',
            [
                me - 1,
                usk - 1
            ] + self._resolveInputBytes(source)
        )

    @requiresInit
    @assertTopology('mes', 'me')
    def setUSKFillSource(self, me, usk, source):
        me_keyers = len(self._system_config['keyers'].get(me - 1, {}))
        if usk > me_keyers:
            raise InvalidArgumentException

        if not isinstance(source, VideoSource):
            raise InvalidArgumentException

        self._sendCommand(
            'CKeF',
            [
                me - 1,
                usk - 1
            ] + self._resolveInputBytes(source)
        )

    @requiresInit
    @assertTopology('mes', 'me')
    def setUSKLumaParams(self, me, usk, preMultiplied=None, clip=None, gain=None, invert=None):
        me_keyers = len(self._system_config['keyers'].get(me - 1, {}))
        if usk > me_keyers:
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
        if invert is not None:
            set_mask |= 8

        self._sendCommand(
            'KeLm',
            [
                set_mask,
                me - 1,
                usk - 1,
                1 if preMultiplied else 0
            ] +
            bytes_of(clip) +
            bytes_of(gain) +
            [
                1 if invert else 0,
                0,
                0,
                0
            ]
        )

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

########
# Audio
########

    @requiresInit
    def resetAudioMixerPeaks(self, source=None):
        if source:
            mask = 0x2
            source_bytes = self._resolveAudioInputBytes(source)
        else:
            mask = 0x4
            source_bytes = [0, 0]

        self._sendCommand(
            'RAMP',
            [mask, 0] + source_bytes + [(1 if source is None else 0), 0, 0, 0]
        )

########
# Super Source
########

    @requiresInit
    def setSuperSourceFill(self, source):
        return self.setSuperSourceParams(
            fill=source
        )

    @requiresInit
    def setSuperSourceKey(self, source):
        return self.setSuperSourceParams(
            key=source
        )

    @requiresInit
    def setSuperSourceParams(
        self,
        fill=None,
        key=None,
        foreground=None,
        preMultiplied=None,
        clip=None,
        gain=None,
        invert=None,
        border_enabled=None,
        border_bevel=None,
        border_outer_width=None,
        border_inner_width=None,
        border_outer_softness=None,
        border_inner_softness=None,
        border_bevel_softness=None,
        border_bevel_position=None,
        border_hue=None,
        border_saturation=None,
        border_luma=None,
        light_source_direction=None,
        light_source_attitude=None
    ):

        if fill is not None:
            if not isinstance(fill, VideoSource):
                raise InvalidArgumentException
        if key is not None:
            if not isinstance(key, VideoSource):
                raise InvalidArgumentException

        mask = [0, 0, 0, 0]
        if fill is not None:
            mask[3] |= 1
        if key is not None:
            mask[3] |= 2
        if foreground is not None:
            mask[3] |= 4
        if preMultiplied is not None:
            mask[3] |= 8
        if clip is not None:
            mask[3] |= 16
        if gain is not None:
            mask[3] |= 32
        if invert is not None:
            mask[3] |= 64
        if border_enabled is not None:
            mask[3] |= 128
        if border_bevel is not None:
            mask[2] |= 1
        if border_outer_width is not None:
            mask[2] |= 2
        if border_inner_width is not None:
            mask[2] |= 4
        if border_outer_softness is not None:
            mask[2] |= 8
        if border_inner_softness is not None:
            mask[2] |= 16
        if border_bevel_softness is not None:
            mask[2] |= 32
        if border_bevel_position is not None:
            mask[2] |= 64
        if border_hue is not None:
            mask[2] |= 128
        if border_saturation is not None:
            mask[1] |= 1
        if border_luma is not None:
            mask[1] |= 2
        if light_source_direction is not None:
            mask[1] |= 4
        if light_source_attitude is not None:
            mask[1] |= 8

        return self._sendCommand(
            'CSSc',
            mask +
            (self._resolveInputBytes(fill) if fill is not None else [0, 0]) +
            (self._resolveInputBytes(key) if key is not None else [0, 0]) +
            [
                1 if foreground else 0,
                1 if preMultiplied else 0
            ] +
            array_pack('!H', clip or 0) +
            array_pack('!H', gain or 0) +
            [
                1 if invert else 0,
                1 if border_enabled else 0,
                border_bevel or 0,
                0x65
            ] +
            array_pack('!H', border_outer_width or 0) +
            array_pack('!H', border_inner_width or 0) +
            [
                border_outer_softness or 0,
                border_inner_softness or 0,
                border_bevel_softness or 0,
                border_bevel_position or 0
            ] +
            array_pack('!H', border_hue or 0) +
            array_pack('!H', border_saturation or 0) +
            array_pack('!H', border_luma or 0) +
            array_pack('!H', light_source_direction or 0) +
            [
                light_source_attitude or 0,
                0x01
            ]
        )

    @requiresInit
    def setSuperSourceBoxSource(self, box, source):
        return self.setSuperSourceBoxParams(
            box,
            source=source
        )

    @requiresInit
    def setSuperSourceBoxParams(
        self,
        box,
        enabled=None,
        source=None,
        position_x=None,
        position_y=None,
        size=None,
        cropped=None,
        crop_top=None,
        crop_bottom=None,
        crop_left=None,
        crop_right=None
    ):

        if 0 > box or box > 3:
            raise InvalidArgumentException
        if source is not None:
            if not isinstance(source, VideoSource):
                raise InvalidArgumentException
        if position_x is not None:
            if position_x < -4800 or position_x > 4800:
                raise InvalidArgumentException()
        if position_y is not None:
            if position_y < -4800 or position_y > 4800:
                raise InvalidArgumentException()
        if size is not None:
            if size < 70 or size > 1000:
                raise InvalidArgumentException()
        if crop_top is not None:
            if crop_top < 0 or crop_top > 18000:
                raise InvalidArgumentException()
        if crop_bottom is not None:
            if crop_bottom < 0 or crop_bottom > 18000:
                raise InvalidArgumentException()
        if crop_left is not None:
            if crop_left < 0 or crop_left > 18000:
                raise InvalidArgumentException()
        if crop_right is not None:
            if crop_right < 0 or crop_right > 18000:
                raise InvalidArgumentException()

        mask_1 = 0
        mask_2 = 0
        if enabled is not None:
            mask_1 |= 1
        if source is not None:
            mask_1 |= 2
        if position_x is not None:
            mask_1 |= 4
        if position_y is not None:
            mask_1 |= 8
        if size is not None:
            mask_1 |= 16
        if cropped is not None:
            mask_1 |= 32
        if crop_top is not None:
            mask_1 |= 64
        if crop_bottom is not None:
            mask_1 |= 128
        if crop_left is not None:
            mask_2 |= 1
        if crop_right is not None:
            mask_2 |= 2

        return self._sendCommand(
            'CSBP',
            [
                mask_2,
                mask_1,
                box,
                1 if enabled is True else 0 if enabled is False else 128
            ] +
            (self._resolveInputBytes(source) if source else [0, 0]) +
            bytes_of(position_x or 0) +
            bytes_of(position_y or 0) +
            array_pack('!h', size or 0) +
            [
                1 if cropped is True else 0 if cropped is False else 0xb8,
                0x5B
            ] +
            array_pack('!H', crop_top or 0) +
            array_pack('!H', crop_bottom or 0) +
            array_pack('!H', crop_left or 0) +
            array_pack('!H', crop_right or 0) +
            [
                0x33,
                0
            ]
        )
