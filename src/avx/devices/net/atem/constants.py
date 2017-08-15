from enum import Enum

# size of header data
SIZE_OF_HEADER = 0x0c

# packet types
CMD_NOCOMMAND = 0x00
CMD_ACKREQUEST = 0x01
CMD_HELLOPACKET = 0x02
CMD_RESEND = 0x04
CMD_UNDEFINED = 0x08
CMD_ACK = 0x10

LABELS_PORTS_EXTERNAL = {0: 'SDI', 1: 'HDMI', 2: 'Component', 3: 'Composite', 4: 'SVideo'}


class VideoSource(Enum):
    BLACK = 0
    INPUT_1 = 1
    INPUT_2 = 2
    INPUT_3 = 3
    INPUT_4 = 4
    INPUT_5 = 5
    INPUT_6 = 6
    INPUT_7 = 7
    INPUT_8 = 8
    INPUT_9 = 9
    INPUT_10 = 10
    INPUT_11 = 11
    INPUT_12 = 12
    INPUT_13 = 13
    INPUT_14 = 14
    INPUT_15 = 15
    INPUT_16 = 16
    INPUT_17 = 17
    INPUT_18 = 18
    INPUT_19 = 19
    INPUT_20 = 20
    COLOUR_BARS = 1000
    COLOUR_1 = 2001
    COLOUR_2 = 2002
    MEDIA_PLAYER_1 = 3010
    MEDIA_PLAYER_1_KEY = 3011
    MEDIA_PLAYER_2 = 3020
    MEDIA_PLAYER_2_KEY = 3021
    KEY_1_MASK = 4010
    KEY_2_MASK = 4020
    KEY_3_MASK = 4030
    KEY_4_MASK = 4040
    DSK_1_MASK = 5010
    DSK_2_MASK = 5020
    SUPER_SOURCE = 6000
    CLEAN_FEED_1 = 7001
    CLEAN_FEED_2 = 7002
    AUX_1 = 8001
    AUX_2 = 8002
    AUX_3 = 8003
    AUX_4 = 8004
    AUX_5 = 8005
    AUX_6 = 8006
    ME_1_PROGRAM = 10010
    ME_1_PREVIEW = 10011
    ME_2_PROGRAM = 10020
    ME_2_PREVIEW = 10021


class VideoMode(Enum):
    NTSC_525I = 0
    PAL_625I = 1
    NTSC_525I_16_9 = 2
    PAL_625I_16_9 = 3
    HD_720_50 = 4
    HD_720_59 = 5
    HD_1080I_50 = 6
    HD_1080I_59 = 7
    HD_1080P_23 = 8
    HD_1080P_24 = 9
    HD_1080P_25 = 10
    HD_1080P_29 = 11
    HD_1080P_50 = 12
    HD_1080P_59 = 13
    HD_4K_23 = 14
    HD_4K_24 = 15
    HD_4K_25 = 16
    HD_4K_29 = 17


class DownconverterMode(Enum):
    CENTER_CUT = 0
    LETTERBOX = 1
    ANAMORPHIC = 2


class ExternalPortType(Enum):
    INTERNAL = 0
    SDI = 1
    HDMI = 2
    COMPOSITE = 3
    COMPONENT = 4
    SVIDEO = 5


class PortType(Enum):
    EXTERNAL = 0
    BLACK = 1
    COLOR_BARS = 2
    COLOR_GENERATOR = 3
    MEDIA_PLAYER_FILL = 4
    MEDIA_PLAYER_KEY = 5
    SUPER_SOURCE = 6
    ME_OUTPUT = 128
    AUXILIARY = 129
    MASK = 130


class MultiviewerLayout(Enum):
    TOP = 0
    BOTTOM = 1
    LEFT = 2
    RIGHT = 3


class ClipType(Enum):
    STILL = 1
    CLIP = 2


class TransitionStyle(Enum):
    MIX = 0
    DIP = 1
    WIPE = 2
    DVE = 3
    STING = 4


class MacroAction(Enum):
    RUN = 0
    STOP = 1
    STOP_RECORD = 2
    INSERT_WAIT = 3
    CONTINUE = 4
    DELETE = 5


class MessageTypes(object):
    _PREFIX = "avx.devices.net.atem."
    ATEM_CONNECTED = _PREFIX + "Connected"
    ATEM_DISCONNECTED = _PREFIX + "Disconnected"
    AUX_OUTPUT_MAPPING = _PREFIX + "AuxOutputMapping"
    TALLY = _PREFIX + "Tally"
    DSK_STATE = _PREFIX + "DownstreamKeyerState"
    INPUTS_CHANGED = _PREFIX + "InputsChanged"
    FTB_CHANGED = _PREFIX + "FadeToBlackChanged"
    FTB_RATE_CHANGED = _PREFIX + "FtBRateChanged"
    TRANSITION_MIX_PROPERTIES_CHANGED = _PREFIX + "TrMxPropsChanged"
