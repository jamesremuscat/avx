import unittest
from avx.devices.net.hyperdeck import HyperDeck, TransportMode, TransportState, SlotState,\
    MessageTypes
from mock import MagicMock, call
from threading import Thread
from avx.devices.Device import InvalidArgumentException


class TestHyperDeck(unittest.TestCase):
    def setUp(self):
        self.deck = HyperDeck("test", "127.0.0.1")
        self.deck.socket = MagicMock()
        self.deck.broadcast = MagicMock()
        self.deck._initialiseState()

    def _handle_data(self, msg):
        self.deck._handle_data(msg.replace('\n', '\r\n'))

    def testSocketRead(self):
        self.deck.socket = MagicMock()
        self.deck._run_recv_thread = True
        self.deck._data_buffer = ''
        self.deck._handle_data = MagicMock()

        messages = [
            '999 mock message 1:\r\nparam: value\r\n',
            '901 mock message 2:\r\nparam2: value2\r\nparam3: value3\r\n',
            ''
        ]  # Check that we can deal with multiple messages in one recv() call

        def do_recv(*args):
            self.deck._run_recv_thread = False
            return '\r\n'.join(messages)
        self.deck.socket.recv.side_effect = do_recv
        runner = Thread(target=self.deck._receive)
        runner.start()
        runner.join()

        self.assertEqual(2, self.deck._handle_data.call_count)
        self.deck._handle_data.assert_has_calls([
            call('999 mock message 1:\r\nparam: value'),
            call('901 mock message 2:\r\nparam2: value2\r\nparam3: value3')
        ])

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

        self.deck.broadcast.reset_mock()

        self._handle_data(
            '''508 transport info:
status: play
loop: true
'''
        )
        self.assertEqual(TransportState.PLAYING, self.deck._state['transport']['status'])
        self.assertEqual(True, self.deck._state['transport']['loop'])

        expected = {
            'status': TransportState.PLAYING,
            'speed': 100,
            'slot id': None,
            'display timecode': '1:2:3',
            'timecode': 'foo',
            'clip id': None,
            'video format': '1080p25',
            'loop': True
        }
        self.assertEqual(expected, self.deck.getTransportState())
        self.deck.broadcast.assert_called_once_with(MessageTypes.TRANSPORT_STATE_CHANGED, expected)

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

        self.deck.broadcast.reset_mock()

        self._handle_data(
            '''502 slot info:
slot id: 1
status: error
'''
        )

        self.assertEqual(97, self.deck._state['slots'][1]['recording time'])
        self.assertEqual(SlotState.ERROR, self.deck._state['slots'][1]['status'])

        expected = {
            1: {
                'slot id': 1,
                'status': SlotState.ERROR,
                'volume name': 'Media',
                'recording time': 97,
                'video format': '1080p25'
            }
        }
        self.assertEqual(expected, self.deck.getSlotsState())
        self.deck.broadcast.assert_called_once_with(MessageTypes.SLOT_STATE_CHANGED, expected)

    def testRequestClipListing(self):
        self.deck.broadcastClipsList()
        self.deck.socket.send.assert_called_once_with('disk list\r\n')

    def testReceiveClipListing(self):
        self._handle_data(
            '''206 disk list:
slot id: 1
0: clip1_name clip1_fileformat clip1_videoformat 00:01:23:04
1: clip2_name clip2_fileformat clip2_videoformat 08:08:28:06
'''
        )

        expected = {
            0: {
                'name': 'clip1_name',
                'file_format': 'clip1_fileformat',
                'video_format': 'clip1_videoformat',
                'duration': '00:01:23:04'
            },
            1: {
                'name': 'clip2_name',
                'file_format': 'clip2_fileformat',
                'video_format': 'clip2_videoformat',
                'duration': '08:08:28:06'
            }
        }
        self.deck.broadcast.assert_called_once_with(MessageTypes.CLIP_LISTING, expected)

    def testSlotSelect(self):
        self.deck.selectSlot(1)
        self.deck.socket.send.assert_called_once_with('slot select: slot id: 1\r\n')
        self.deck.socket.send.reset_mock()

        try:
            self.deck.selectSlot(0)
            self.fail('Should have thrown exception for invalid slot')
        except InvalidArgumentException:
            pass

    def testSetTransportMode(self):
        self.deck.setTransportMode(TransportMode.PLAYBACK)
        self.deck.socket.send.assert_called_once_with('preview: enable: false\r\n')
        self.deck.socket.send.reset_mock()

        self.deck.setTransportMode(TransportMode.RECORD)
        self.deck.socket.send.assert_called_once_with('preview: enable: true\r\n')
        self.deck.socket.send.reset_mock()

        try:
            self.deck.setTransportMode('Record')
            self.fail('Should have thrown exception for invalid transport mode')
        except InvalidArgumentException:
            pass

    def testRecord(self):
        self.deck.record()
        self.deck.socket.send.assert_called_once_with('record\r\n')
        self.deck.socket.send.reset_mock()

        self.deck.record('my clip name')
        self.deck.socket.send.assert_called_once_with('record: name: my clip name\r\n')

    def testStop(self):
        self.deck.stop()
        self.deck.socket.send.assert_called_once_with('stop\r\n')
        self.assertEqual(TransportState.STOPPED, self.deck._state['transport']['status'])

    def testPlay(self):
        self.deck.play()
        self.deck.socket.send.assert_called_once_with('play\r\n')
        self.deck.socket.send.reset_mock()

        self.deck.play(single_clip=False, speed=20, loop=True)
        self.deck.socket.send.assert_called_once_with('play: single clip: false speed: 20 loop: true\r\n')
        self.deck.socket.send.reset_mock()

    def testNext(self):
        self.deck.next()
        self.deck.socket.send.assert_called_once_with('goto: clip id: +1\r\n')

    def testPrev(self):
        self.deck.prev()
        self.deck.socket.send.assert_called_once_with('goto: clip id: -1\r\n')
