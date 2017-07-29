import unittest
from avx.devices.net.hyperdeck import HyperDeck, TransportState, SlotState
from mock import MagicMock, call


class TestHyperDeck(unittest.TestCase):
    def setUp(self):
        self.deck = HyperDeck("test", "127.0.0.1")
        self.deck.socket = MagicMock()
        self.deck.broadcast = MagicMock()
        self.deck._initialiseState()

    def _handle_data(self, msg):
        self.deck._handle_data(msg.replace('\n', '\r\n'))

    def testReceiveInit(self):
        self._handle_data(
            '''500 connection info:
protocol version: 1234
model: Test HyperDeck
'''
        )

        self.assertEqual('1234', self.deck._state['connection']['protocol version'])
        self.assertEqual('Test HyperDeck', self.deck._state['connection']['model'])
        self.assertEqual(
            [call.send('transport info\r\n'), call.send('slot info\r\n'), call.send('notify: transport: true slot: true\r\n')],
            self.deck.socket.method_calls
        )

    def testReceiveTransportInfo(self):
        self._handle_data(
            '''208 transport info:
status: preview
speed: 100
slot id: none
display timecode: 1:2:3
timecode: foo
clip id: none
video format: 1080p25
loop: false
'''
        )

        self.assertEqual(TransportState.PREVIEW, self.deck._state['transport']['status'])
        self.assertEqual(100, self.deck._state['transport']['speed'])
        self.assertEqual(False, self.deck._state['transport']['loop'])

        self._handle_data(
            '''508 transport info:
status: play
loop: true
'''
        )
        self.assertEqual(TransportState.PLAYING, self.deck._state['transport']['status'])
        self.assertEqual(True, self.deck._state['transport']['loop'])

    def testReceiveSlotInfo(self):
        self._handle_data(
            '''202 slot info:
slot id: 1
status: mounted
volume name: Media
recording time: 97
video format: 1080p25
'''
        )

        self.assertEqual(97, self.deck._state['slots'][1]['recording time'])
        self.assertEqual(SlotState.MOUNTED, self.deck._state['slots'][1]['status'])
        self.assertEqual('Media', self.deck._state['slots'][1]['volume name'])

        self._handle_data(
            '''502 slot info:
slot id: 1
status: error
'''
        )

        self.assertEqual(97, self.deck._state['slots'][1]['recording time'])
        self.assertEqual(SlotState.ERROR, self.deck._state['slots'][1]['status'])
