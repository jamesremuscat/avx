import unittest
from avx.devices.net.hyperdeck import HyperDeck, TransportState
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
            [call.send('transport info\r\n'), call.send('notify: transport: true\r\n')],
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
