import unittest
from avx.devices.net.hyperdeck import HyperDeck
from mock import MagicMock, call


class TestHyperDeck(unittest.TestCase):
    def setUp(self):
        self.deck = HyperDeck("test", "127.0.0.1")
        self.deck.socket = MagicMock()
        self.deck._initialiseState()

    def testReceiveInit(self):
        self.deck._handle_data(
            '''500 connection info:\r
protocol version: 1234\r
model: Test HyperDeck\r
\r
\r
'''
        )

        self.assertEqual('1234', self.deck._state['connection']['protocol version'])
        self.assertEqual('Test HyperDeck', self.deck._state['connection']['model'])
        self.assertEqual(
            [call.send('transport info\r\n'), call.send('notify: transport: true\r\n')],
            self.deck.socket.method_calls
        )
