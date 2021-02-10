from .constants import BevelType, ClipType, DownconverterMode, ExternalPortType, \
    KeyType, LABELS_PORTS_EXTERNAL, MessageTypes, MultiviewerLayout, PortType, \
    SuperSourceArtType, TransitionStyle, VideoMode, VideoSource
from .utils import parseBitmask, convert_cstring

import struct


#############
# Device-internal ATEM packet handling functions. Designed to be used as a mixin.
#############
class ATEMReceiver(object):

    def _recv__ver(self, data):
        major, minor = struct.unpack('!HH', data[0:4])
        self._system_config['version'] = "{}.{}".format(major, minor)

    def _recv__pin(self, data):
        self._system_config['name'] = data

    def _recv_Warn(self, text):
        self.log.warning(text)

    def _recv__top(self, data):
        self._system_config['topology'] = {}
        datalabels = ['mes', 'sources', 'color_generators', 'aux_busses', 'dsks', 'stingers', 'dves',
                      'supersources']
        for i, label in enumerate(datalabels):
            self._system_config['topology'][label] = data[i]

        self._system_config['topology']['hasSD'] = (data[9] > 0)

    def _recv__MeC(self, data):
        index = data[0]
        num_keyers = data[1]
        keyer_dict = self._system_config.setdefault('keyers', {}).setdefault(index, {})
        for i in range(num_keyers):
            keyer_dict[i] = {'on': False}

    def _recv__mpl(self, data):
        self._system_config['media_players'] = {}
        self._system_config['media_players']['still'] = data[0]
        self._system_config['media_players']['clip'] = data[1]

    def _recv__MvC(self, data):
        self._system_config['multiviewers'] = data[0]

    def _recv__SSC(self, data):
        self._system_config['super_source_boxes'] = data[0]

    def _recv__TlC(self, data):
        self._system_config['tally_channels'] = data[4]

    def _recv__AMC(self, data):
        self._system_config['audio_channels'] = data[0]
        self._system_config['has_monitor'] = (data[1] > 0)

    def _recv__VMC(self, data):
        videomodes = (data[1] << 16) | (data[2] << 8) | (data[3])
        for vidmode in VideoMode:
            has_mode = ((videomodes >> (24 - vidmode.value - 1)) & 0x1) > 0
            self._system_config.setdefault('video_modes', {})[vidmode] = has_mode

    def _recv__MAC(self, data):
        self._system_config['macro_banks'] = data[0]

    def _recv_Powr(self, data):
        self._status['power'] = parseBitmask(data[0], ['main', 'backup'])

    def _recv_DcOt(self, data):
        self._config['down_converter'] = DownconverterMode(data[0])

    def _recv_VidM(self, data):
        self._config['video_mode'] = VideoMode(data[0])

    def _recv_InPr(self, data):
        index = VideoSource(struct.unpack('!H', data[0:2])[0])
        self._system_config['inputs'][index] = {}
        input_setting = self._system_config['inputs'][index]
        input_setting['name_long'] = convert_cstring(data[2:22])
        input_setting['name_short'] = convert_cstring(data[22:26])
        input_setting['types_available'] = parseBitmask(data[27], LABELS_PORTS_EXTERNAL)
        input_setting['port_type_external'] = ExternalPortType(data[29])
        input_setting['port_type_internal'] = PortType(data[30])
        input_setting['availability'] = parseBitmask(data[32], ['Auxiliary', 'Multiviewer', 'SuperSourceArt',
                                                                'SuperSourceBox', 'KeySource'])
        input_setting['me_availability'] = parseBitmask(data[33], ['ME1', 'ME2'])
        if self._isInitialized:
            self.broadcast(MessageTypes.INPUTS_CHANGED, None)

    def _recv_MvPr(self, data):
        index = data[0]
        self._config['multiviewers'].setdefault(index, {})['layout'] = MultiviewerLayout(data[1])

    def _recv_MvIn(self, data):
        index = data[0]
        window = data[1]
        self._config['multiviewers'].setdefault(index, {}).setdefault('windows', {})[window] = VideoSource(struct.unpack('!H', data[2:4])[0])

    def _recv_PrgI(self, data):
        meIndex = data[0]
        self._state['program'][meIndex] = VideoSource(struct.unpack('!H', data[2:4])[0])
        self._broadcast_full_tally()

    def _recv_PrvI(self, data):
        meIndex = data[0]
        self._state['preview'][meIndex] = VideoSource(struct.unpack('!H', data[2:4])[0])
        self._broadcast_full_tally()

    def _recv_KeOn(self, data):
        meIndex = data[0]
        keyer = data[1]
        self._state['keyers'].setdefault(meIndex, {}).setdefault(keyer, {})['on'] = (data[2] != 0)
        if self._isInitialized:
            self.broadcast(MessageTypes.USK_STATE, self._state['keyers'])
            self._broadcast_full_tally()

    def _recv_KeBP(self, data):
        meIndex = data[0]
        keyerIndex = data[1]
        keyer = self._state['keyers'].setdefault(meIndex, {}).setdefault(keyerIndex, {})
        keyer['type'] = KeyType(data[2])
        keyer['enabled'] = (data[3] + data[4]) > 0
        keyer['fly_enabled'] = (data[5] > 0)
        keyer['fill'] = VideoSource(struct.unpack('!H', data[6:8])[0])
        keyer['key'] = VideoSource(struct.unpack('!H', data[8:10])[0])

        mask = keyer.setdefault('mask', {})
        mask['enabled'] = (data[10] > 0)
        mask['top'] = struct.unpack('!H', data[12:14])[0]
        mask['bottom'] = struct.unpack('!H', data[14:16])[0]
        mask['left'] = struct.unpack('!H', data[16:18])[0]
        mask['right'] = struct.unpack('!H', data[18:20])[0]

        if self._isInitialized:
            self._broadcast_full_tally()

    def _recv_DskB(self, data):
        keyer = data[0]
        keyer_setting = self._state['dskeyers'].setdefault(keyer, {})
        keyer_setting['fill'] = VideoSource(struct.unpack('!H', data[2:4])[0])
        keyer_setting['key'] = VideoSource(struct.unpack('!H', data[4:6])[0])
        self._broadcast_full_tally()

    def _recv_DskS(self, data):
        keyer = data[0]
        dsk_setting = self._state['dskeyers'].setdefault(keyer, {})
        dsk_setting['on_air'] = (data[1] != 0)
        dsk_setting['in_transition'] = (data[2] != 0)
        dsk_setting['auto_transitioning'] = (data[3] != 0)
        dsk_setting['frames_remaining'] = data[4]
        if self._isInitialized:
            self.broadcast(MessageTypes.DSK_STATE, self._state['dskeyers'])
            self._broadcast_full_tally()

    def _recv_DskP(self, data):
        keyer = data[0]
        dsk_setting = self._state['dskeyers'].setdefault(keyer, {})
        dsk_setting['tie'] = (data[1] > 0)
        dsk_setting['rate'] = data[2]
        dsk_setting['premultiplied'] = (data[3] > 0)
        dsk_setting['clip'] = struct.unpack('!H', data[4:6])[0]
        dsk_setting['gain'] = struct.unpack('!H', data[6:8])[0]
        dsk_setting['invert'] = (data[8] > 0)
        dsk_setting['masked'] = (data[9] > 0)
        dsk_setting['top'] = struct.unpack('!h', data[10:12])[0]
        dsk_setting['bottom'] = struct.unpack('!h', data[12:14])[0]
        dsk_setting['left'] = struct.unpack('!h', data[14:16])[0]
        dsk_setting['right'] = struct.unpack('!h', data[16:18])[0]

    def _recv_AuxS(self, data):  # Aux source set
        auxIndex = data[0]
        self._state['aux'][auxIndex] = VideoSource(struct.unpack('!H', data[2:4])[0])
        if self._isInitialized:
            self.broadcast(MessageTypes.AUX_OUTPUT_MAPPING, self._state['aux'])

    def _recv_CCdo(self, data):
        pass

    def _recv_CCdP(self, data):
        pass

    def _recv_RCPS(self, data):
        player_num = data[0]
        player = self._state['mediaplayer'].setdefault(player_num, {})
        player['playing'] = bool(data[1])
        player['loop'] = bool(data[2])
        player['beginning'] = bool(data[3])
        player['clip_frame'] = struct.unpack('!H', data[4:6])[0]

    def _recv_MPCE(self, data):
        player_num = data[0]
        player = self._state['mediaplayer'].setdefault(player_num, {})
        player['type'] = ClipType(data[1])
        player['still_index'] = data[2]
        player['clip_index'] = data[3]

    def _recv_MPSp(self, data):
        self._config['mediapool'].setdefault(0, {})['maxlength'] = struct.unpack('!H', data[0:2])[0]
        self._config['mediapool'].setdefault(1, {})['maxlength'] = struct.unpack('!H', data[2:4])[0]

    def _recv_MPCS(self, data):
        bank = data[0]
        clip_bank = self._state['mediapool'].setdefault('clips', {}).setdefault(bank, {})
        clip_bank['used'] = bool(data[1])
        clip_bank['filename'] = convert_cstring(data[2:18])
        clip_bank['length'] = struct.unpack('!H', data[66:68])[0]

    def _recv_MPAS(self, data):
        bank = data[0]
        audio_bank = self._state['mediapool'].setdefault('audio', {}).setdefault(bank, {})
        audio_bank['used'] = bool(data[1])
        audio_bank['filename'] = convert_cstring(data[18:34])

    def _recv_MPfe(self, data):
        if data[0] != 0:
            return
        bank = data[3]
        still_bank = self._state['mediapool'].setdefault('stills', {}).setdefault(bank, {})
        still_bank['used'] = bool(data[4])
        still_bank['hash'] = data[5:21]
        filename_length = data[23]
        still_bank['filename'] = data[24:(24 + filename_length)].decode("utf-8")

    def _recv_AMIP(self, data):
        channel = struct.unpack('!H', data[0:2])[0]
        channel_config = self._system_config['audio'].setdefault(channel, {})
        channel_config['fromMediaPlayer'] = bool(data[6])
        channel_config['plug'] = data[7]

        channel_state = self._state['audio'].setdefault(channel, {})
        channel_state['mix_option'] = data[8]
        channel_state['volume'] = struct.unpack('!H', data[10:12])[0]
        channel_state['balance'] = struct.unpack('!h', data[12:14])[0]

    def _recv_AMMO(self, data):
        self._state['audio']['master_volume'] = struct.unpack('!H', data[0:2])[0]

    def _recv_AMmO(self, data):
        monitor = self._state['audio'].setdefault('monitor', {})
        monitor['enabled'] = bool(data[0])
        monitor['volume'] = struct.unpack('!H', data[2:4])[0]
        monitor['mute'] = bool(data[4])
        monitor['solo'] = bool(data[5])
        monitor['solo_input'] = struct.unpack('!H', data[6:8])[0]
        monitor['dim'] = bool(data[8])

    def _recv_AMTl(self, data):
        src_count = struct.unpack('!H', data[0:2])[0]
        for i in range(src_count):
            num = 2 + i * 3
            channel = struct.unpack('!H', data[num:num + 2])[0]
            self._state['audio'].setdefault('tally', {})[channel] = bool(data[num + 2])

    def _recv_TlIn(self, data):
        src_count = struct.unpack('!H', data[0:2])[0]
        for i in range(2, src_count + 2):
            self._state['tally_by_index'][str(i - 1)] = parseBitmask(data[i], ['prv', 'pgm'])
        # TODO self.tallyHandler(self)

    def _recv_TlSr(self, data):
        src_count = struct.unpack('!H', data[0:2])[0]
        for i in range(2, src_count * 3 + 2, 3):
            source = VideoSource(struct.unpack('!H', data[i:i + 2])[0])
            self._state['tally'][source] = parseBitmask(data[i + 2], ['prv', 'pgm'])
        self.broadcast(MessageTypes.TALLY, self._state['tally'])

    def _recv_Time(self, data):
        self._state['last_state_change'] = struct.unpack('!BBBB', data[0:4])

    def _recv_TrSS(self, data):
        meIndex = data[0]
        current = self._state['transition'].setdefault(meIndex, {}).setdefault('current', {})
        nextT = self._state['transition'].setdefault(meIndex, {}).setdefault('next', {})

        current['style'] = TransitionStyle(data[1])
        current['tied'] = parseBitmask(data[2], ['key4', 'key3', 'key2', 'key1', 'bkgd'])

        nextT['style'] = TransitionStyle(data[3])
        nextT['tied'] = parseBitmask(data[4], ['key4', 'key3', 'key2', 'key1', 'bkgd'])

    def _recv_TrPs(self, data):
        meIndex = data[0]
        current = self._state['transition'].setdefault(meIndex, {}).setdefault('current', {})
        current['in_transition'] = (data[1] > 0)
        current['frames_remaining'] = data[2]
        current['position'] = struct.unpack('!H', data[4:6])[0]

    def _recv_TMxP(self, data):
        meIndex = data[0]
        self._config['transitions'].setdefault(meIndex, {}).setdefault('mix', {})['rate'] = data[1]
        if self._isInitialized:
            self.broadcast(MessageTypes.TRANSITION_MIX_PROPERTIES_CHANGED, {meIndex: {'rate': data[1]}})

    def _recv_FtbP(self, data):
        meIndex = data[0]
        self._config['transitions'].setdefault(meIndex, {}).setdefault('ftb', {})['rate'] = data[1]
        if self._isInitialized:
            self.broadcast(MessageTypes.FTB_RATE_CHANGED, {meIndex: data[1]})

    def _recv_FtbS(self, data):
        meIndex = data[0]
        ftb_state = self._state['transition'].setdefault(meIndex, {}).setdefault('ftb', {})
        ftb_state['full_black'] = (data[1] > 0)
        ftb_state['in_transition'] = (data[2] > 0)
        ftb_state['frames_remaining'] = data[3]
        if self._isInitialized:
            self.broadcast(MessageTypes.FTB_CHANGED, {meIndex: ftb_state})

########
# SuperSource
########

    def _recv_SSrc(self, data):
        ssrc = self._state['supersource']

        ssrc['fill'] = VideoSource(struct.unpack('!H', data[0:2])[0])
        ssrc['key'] = VideoSource(struct.unpack('!H', data[2:4])[0])
        ssrc['artType'] = SuperSourceArtType(data[4])

        ssrc['premultiplied'] = (data[5] > 0)
        ssrc['clip'] = struct.unpack('!H', data[6:8])[0]
        ssrc['gain'] = struct.unpack('!H', data[8:10])[0]
        ssrc['invert'] = (data[10] > 0)

        border = ssrc.setdefault('border', {})
        border['enabled'] = data[11] > 0
        border['bevel'] = BevelType(data[12])

        border['outer_width'] = struct.unpack('!H', data[14:16])[0]
        border['inner_width'] = struct.unpack('!H', data[16:18])[0]
        border['outer_softness'] = data[18]
        border['inner_softness'] = data[19]
        border['bevel_softness'] = data[20]
        border['bevel_position'] = data[21]
        border['hue'] = struct.unpack('!H', data[22:24])[0]
        border['saturation'] = struct.unpack('!H', data[24:26])[0]
        border['luma'] = struct.unpack('!H', data[26:28])[0]
        border['light_source_direction'] = struct.unpack('!H', data[28:30])[0]
        border['light_source_altitude'] = data[30]

        if self._isInitialized:
            self.broadcast(
                MessageTypes.SUPER_SOURCE_CHANGED,
                self._state['supersource']
            )

        self._broadcast_full_tally()

    def _recv_SSBP(self, data):
        ssrc = self._state['supersource']
        box = ssrc['boxes'][data[0]]

        box['enabled'] = (data[1] > 0)
        box['source'] = VideoSource(struct.unpack('!H', data[2:4])[0])
        box['x'] = struct.unpack('!h', data[4:6])[0]
        box['y'] = struct.unpack('!h', data[6:8])[0]
        box['scale'] = struct.unpack('!H', data[8:10])[0]

        crop = box.setdefault('crop', {})

        crop['enabled'] = (data[10] > 0)
        crop['top'] = struct.unpack('!H', data[12:14])[0]
        crop['bottom'] = struct.unpack('!H', data[14:16])[0]
        crop['left'] = struct.unpack('!H', data[16:18])[0]
        crop['right'] = struct.unpack('!H', data[18:20])[0]

        if self._isInitialized:
            self.broadcast(
                MessageTypes.SUPER_SOURCE_CHANGED,
                self._state['supersource']
            )

        self._broadcast_full_tally()

########
# Macros
########

    def _recv_MPrp(self, data):
        macro_idx = data[1]
        macro = self._config['macros'].setdefault(macro_idx, {})
        macro['used'] = (data[2] > 0)
        name_len = struct.unpack('!H', data[4:6])[0]
        desc_len = struct.unpack('!H', data[6:8])[0]
        macro['name'] = str(data[8:8 + name_len])
        macro['description'] = str(data[8 + name_len:8 + name_len + desc_len])

#######
# Synthetic tally
#######

# ATEM only provides tally information for M/E 1. In order to generate tally
# information for M/E 2 independently, we need to inspect the switcher state.

    def _generate_synthetic_tally(self):
        tally = {}

        for me_index in range(self._system_config.get('topology', {}).get('mes', 0)):
            this_me = {'prv': [], 'pgm': []}

            # These are the easy ones: program/preview for each M/E
            if me_index in self._state['preview']:
                prv_source = self._state['preview'][me_index]
                this_me['prv'].append(prv_source)
                if prv_source == VideoSource.SUPER_SOURCE:
                    this_me['prv'].extend(self._get_supersource_sources())

            if me_index in self._state['program']:
                pgm_source = self._state['program'][me_index]
                this_me['pgm'].append(pgm_source)
                if pgm_source == VideoSource.SUPER_SOURCE:
                    this_me['pgm'].extend(self._get_supersource_sources())

            # We also need to consider the upstream keyers...
            for usk in self._state['keyers'].get(me_index, {}).values():
                if usk.get('on', False):
                    this_me['pgm'].append(usk['fill'])
                    this_me['pgm'].append(usk['key'])

                    if VideoSource.SUPER_SOURCE in [usk['fill'], usk['key']]:
                        this_me['pgm'].extend(self._get_supersource_sources())

            # ... and transitions
            current_transition = self._state['transition'].get(me_index, {}).get('current', {})
            if current_transition.get('in_transition', False):
                target = 'pgm'
            else:
                target = 'prv'

            tie = current_transition.get('tied', {})
            if tie.get('bkgd'):
                bkgd_source = self._state['preview'][me_index]
                this_me[target].append(bkgd_source)
                if VideoSource.SUPER_SOURCE == bkgd_source:
                    this_me[target].extend(self._get_supersource_sources())
            if tie.get('key1'):
                key1 = self._state['keyers'][me_index][0]
                this_me[target].append(key1['fill'])
                this_me[target].append(key1['key'])
                if VideoSource.SUPER_SOURCE in [key1['fill'], key1['key']]:
                    this_me[target].extend(self._get_supersource_sources())
            if tie.get('key2'):
                key2 = self._state['keyers'][me_index][1]
                this_me[target].append(key2['fill'])
                this_me[target].append(key2['key'])
                if VideoSource.SUPER_SOURCE in [key2['fill'], key2['key']]:
                    this_me[target].extend(self._get_supersource_sources())
            if tie.get('key3'):
                key3 = self._state['keyers'][me_index][2]
                this_me[target].append(key3['fill'])
                this_me[target].append(key3['key'])
                if VideoSource.SUPER_SOURCE in [key3['fill'], key3['key']]:
                    this_me[target].extend(self._get_supersource_sources())
            if tie.get('key4'):
                key4 = self._state['keyers'][me_index][3]
                this_me[target].append(key4['fill'])
                this_me[target].append(key4['key'])
                if VideoSource.SUPER_SOURCE in [key4['fill'], key4['key']]:
                    this_me[target].extend(self._get_supersource_sources())

            tally[me_index] = this_me

        # DSKs always appear on M/E 1
        for dsk in self._state['dskeyers'].itervalues():
            if dsk.get('in_transition', False) or dsk.get('on_air', False):
                tally[0]['pgm'].append(dsk['key'])
                tally[0]['pgm'].append(dsk['fill'])

                if VideoSource.SUPER_SOURCE in [dsk['fill'], dsk['key']]:
                    tally[0]['pgm'].extend(self._get_supersource_sources())

        return tally

    def _broadcast_full_tally(self):
        if self._isInitialized:
            self.broadcast(
                MessageTypes.FULL_TALLY,
                self._generate_synthetic_tally()
            )
