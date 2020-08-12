from avx.devices.net.atem.constants import SIZE_OF_HEADER, AudioSource, VideoSource,\
    TransitionStyle, MacroAction, MultiviewerLayout
from avx.devices.net.atem.tests import BaseATEMTest
from avx.devices.net.atem.utils import byteArrayToString, bytes_of, \
    NotInitializedException
from avx.devices.Device import InvalidArgumentException


class TestATEMSender(BaseATEMTest):
    def assert_sent_packet(self, cmd, payload):
        self.assertFalse(self.atem._socket.sendto.call_args is None, '_socket.sendto never called!')
        args = self.atem._socket.sendto.call_args[0]
        self.assertEqual(2, len(args))
        packet = args[0]

        if not isinstance(payload, str):
            payload = byteArrayToString(payload)

        self.assertEqual(cmd, packet[SIZE_OF_HEADER + 4:SIZE_OF_HEADER + 8])
        self.assertEqual(payload, packet[SIZE_OF_HEADER + 8:])

    def setUp(self):
        BaseATEMTest.setUp(self)
        self.atem._handlePacket(byteArrayToString([0x08, 0x0c, 0xab, 0x09, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x12]))
        self.send_command('_top', [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
        self.send_command('_MvC', [1, 0, 0, 0])  # One MVW
        self.send_command(
            'InPr',
            bytes_of(VideoSource.COLOUR_BARS.value) +
            map(ord, 'Input Long Name') + [0, 0, 0, 0, 0] +  # Long name always 20 bytes
            map(ord, 'InLN') +  # Short name always 4 bytes
            [0, 0x0F, 0, 1, 2, 0, 0x1E, 0x02, 0, 0]
        )
        self.atem._socket.reset_mock()

    def testSetMultiviewerLayout(self):
        self.atem.setMultiviewerLayout(MultiviewerLayout.BOTTOM)
        self.assert_sent_packet(
            'CMvP',
            [0x1, 0x0, 0x1, 0]
        )

        with self.assertRaises(InvalidArgumentException):
            self.atem.setMultiviewerLayout('Bottom')

        with self.assertRaises(InvalidArgumentException):
            self.atem.setMultiviewerLayout(MultiviewerLayout.TOP, 7)

    def testSetMultiviewerInput(self):
        self.atem.setMultiviewerWindowSource(3, VideoSource.COLOUR_BARS)
        self.assert_sent_packet(
            'CMvI',
            [0, 3, 0x03, 0xE8]
        )
        self.atem._socket.reset_mock()

        try:
            self.atem.setMultiviewerWindowSource(22, VideoSource.AUX_1)
            self.fail("Should have thrown an exception")
        except InvalidArgumentException:
            pass

    def testSetAuxSourceWithoutInit(self):
        self.atem._isInitialized = False

        try:
            self.atem.setPreview("Not initialised so going to fail", 0)
            self.fail("Should have thrown an exception as not initialised")
        except NotInitializedException:
            pass

    def testSetAuxSource(self):
        try:
            self.atem.setAuxSource(2, 0)
            self.fail("Aux 2 shouldn't exist!")
        except InvalidArgumentException:
            pass

        self.atem.setAuxSource(1, VideoSource.COLOUR_BARS)
        self.assert_sent_packet('CAuS', [1, 0] + bytes_of(VideoSource.COLOUR_BARS.value))

    def testSetPreview(self):
        try:
            self.atem.setPreview(VideoSource.COLOUR_BARS, 2)
            self.fail("ME 2 shouldn't exist!")
        except InvalidArgumentException:
            pass

        self.atem.setPreview(VideoSource.COLOUR_BARS, 1)
        self.assert_sent_packet('CPvI', [0, 0] + bytes_of(VideoSource.COLOUR_BARS.value))

# OK, I think we've tested the @requiresInit and @assertTopology decorators enough now...

    def testSetProgram(self):
        self.atem.setProgram(VideoSource.COLOUR_BARS)
        self.assert_sent_packet('CPgI', [0, 0] + bytes_of(VideoSource.COLOUR_BARS.value))

    def testPerformCut(self):
        self.atem.performCut(1)
        self.assert_sent_packet('DCut', [0, 0, 0, 0])

    def testPerformAutoTake(self):
        self.atem.performAutoTake()
        self.assert_sent_packet('DAut', [0, 0, 0, 0])

    def testSetNextTransition(self):
        self.atem.setNextTransition(TransitionStyle.MIX, bkgd=True, key1=True, key2=False, key3=False, key4=False, me=1)
        self.assert_sent_packet('CTTp', [0x03, 0, 0, 0x03])

        self.atem._socket.reset_mock()
        self.atem.setNextTransition(TransitionStyle.WIPE)
        self.assert_sent_packet('CTTp', [0x01, 0, 2, 0x00])

        self.atem._socket.reset_mock()
        self.atem.setNextTransition(TransitionStyle.DIP, True, True, True, True, True)
        self.assert_sent_packet('CTTp', [0x03, 0, 1, 0x1F])

    def testSetMixTransitionRate(self):
        self.atem.setMixTransitionRate(128)
        self.assert_sent_packet('CTMx', [0, 128, 0x93, 0x07])  # 0x93 0x07 are magic numbers...

    def testPerformDSKAuto(self):
        self.atem.performDSKAuto(1)
        self.assert_sent_packet('DDsA', [0, 0, 0, 0])

    def testSetDSKOnAir(self):
        self.atem.setDSKOnAir(1, True)
        self.assert_sent_packet('CDsL', [0, 1, 0xBE, 0x07])

    def testSetDSKRate(self):
        self.atem.setDSKRate(1, 200)
        self.assert_sent_packet('CDsR', [0, 200, 0xAA, 0X07])

    def testSetDSKKeySource(self):
        self.atem.setDSKKeySource(1, VideoSource.COLOUR_BARS)
        self.assert_sent_packet('CDsC', [0, 0] + bytes_of(VideoSource.COLOUR_BARS.value))

    def testSetDSKFillSource(self):
        self.atem.setDSKFillSource(1, VideoSource.COLOUR_BARS)
        self.assert_sent_packet('CDsF', [0, 0] + bytes_of(VideoSource.COLOUR_BARS.value))

    def testSetDSKParams(self):
        self.atem.setDSKParams(1, clip=250, gain=750, preMultiplied=False)
        self.assert_sent_packet('CDsG', [0x07, 0, 0, 0, 0, 0xFA, 0x02, 0xEE, 0, 0, 0, 0])

    def testSetFadeToBlackRate(self):
        self.atem.setFadeToBlackRate(127)
        self.assert_sent_packet('FtbC', [1, 0, 127, 0])

    def testPerformFadeToBlack(self):
        self.atem.performFadeToBlack()
        self.assert_sent_packet('FtbA', [0, 0xA7, 0x59, 0x08])

########
# Macros
########
    def testExecuteMacro(self):
        # First let there be a macro to begin with
        macro_name = "Awesome macro"
        macro_description = "So awesome it will blow your mind. But not your circuitry."
        self.send_command(
            'MPrp',
            [
                0,
                42,
                1,
                0
            ] +
            bytes_of(len(macro_name)) +
            bytes_of(len(macro_description)) +
            map(ord, macro_name) +
            map(ord, macro_description)
        )

        self.atem.executeMacro(42)
        self.assert_sent_packet('MAct', [42, MacroAction.RUN.value, 0])
        self.atem._socket.reset_mock()

        self.atem.executeMacroByName(macro_name)
        self.assert_sent_packet('MAct', [42, MacroAction.RUN.value, 0])
        self.atem._socket.reset_mock()

        try:
            self.atem.executeMacro(77)
            self.fail("Should have failed to execute a non-existent macro")
        except InvalidArgumentException:
            pass
########
# Audio
########

    def testResetAudioMixerPeaks(self):
        self.atem.resetAudioMixerPeaks()  # Default = master
        self.assert_sent_packet('RAMP', [0x4, 0, 0, 0, 0x1, 0, 0, 0])
        self.atem._socket.reset_mock()

        self.atem.resetAudioMixerPeaks(AudioSource.XLR)
        self.assert_sent_packet('RAMP', [0x2, 0, 0x3, 0xE9, 0, 0, 0, 0])
        self.atem._socket.reset_mock()

########
# Super Source
########

    def testSetSuperSourceFill(self):
        self.atem.setSuperSourceFill(VideoSource.COLOUR_BARS)
        self.assert_sent_packet(
            'CSSc',
            [
                0x1,
                0,
                0,
                0
            ] +
            bytes_of(VideoSource.COLOUR_BARS.value) +
            ([0] * 30)
        )

    def testSetSuperSourceKey(self):
        self.atem.setSuperSourceKey(VideoSource.COLOUR_BARS)
        self.assert_sent_packet(
            'CSSc',
            [
                0x2,
                0,
                0,
                0,
                0, 0
            ] +
            bytes_of(VideoSource.COLOUR_BARS.value) +
            ([0] * 28)
        )

    def testSetSuperSourceParams(self):
        self.atem.setSuperSourceParams(
            foreground=True,
            clip=500,
            gain=250,
            border_outer_softness=42
        )
        self.assert_sent_packet(
            'CSSc',
            [
                0x34,
                0x08,
                0,
                0,
                0, 0, 0, 0,
                1,
                0,
                0x01, 0xF4,
                0x00, 0xFA,
                0,
                0,
                0,
                0,
                0, 0,
                0, 0,
                42
            ] + ([0] * 13)
        )

    def testSetSuperSourceBoxSource(self):
        self.atem.setSuperSourceBoxSource(3, VideoSource.COLOUR_BARS)
        self.assert_sent_packet(
            'CSBP',
            [
                2, 0,
                3,
                0
            ] +
            bytes_of(VideoSource.COLOUR_BARS.value) +
            [0] * 17
        )

    def testSetSuperSourceBoxParams(self):
        self.atem.setSuperSourceBoxParams(
            2,
            enabled=True,
            position_x=0,
            position_y=1234,
            cropped=False,
            crop_left=12345
        )
        self.assert_sent_packet(
            'CSBP',
            [
                0x2D,
                0x01,
                2,
                1,
                0, 0,
                0, 0,
                0x04, 0xD2,
                0, 0,
                0,
                0,
                0, 0,
                0, 0,
                0x30, 0x39,
                0, 0,
                0
            ]
        )
