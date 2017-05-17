import unittest
from mock import MagicMock, call, patch
from avx.controller.Controller import Controller
from avx.Sequencer import Sequencer, Event, ControllerEvent, DeviceEvent,\
    SleepEvent, LogEvent, CompositeEvent, BroadcastEvent
from time import sleep


class TestSequencer(unittest.TestCase):

    def setUp(self):
        self.controller = Controller()
        self.sequencer = Sequencer(self.controller)

    def performSequenceTest(self, *events):
        self.sequencer.sequence(*events)
        self.sequencer.start()
        sleep(len(events) + 1)

    def testSimpleEvent(self):
        m = MagicMock()
        m.deviceID = "Mock"

        e1 = Event(m.frobnicate, "badger")

        self.performSequenceTest(e1)

        m.frobnicate.assert_called_once_with("badger")

    def testControllerEvent(self):
        self.controller.frobnicate = MagicMock(return_value=True)
        e = ControllerEvent("frobnicate", "badger")

        self.performSequenceTest(e)

        self.controller.frobnicate.assert_called_once_with("badger")

    def testDeviceEvent(self):
        m = MagicMock()
        m.deviceID = "Mock"

        self.controller.addDevice(m)

        e = DeviceEvent("Mock", "frobnicate", "badger")

        self.performSequenceTest(e)

        m.frobnicate.assert_called_once_with("badger")

    def testCompositeEvent(self):
        m = MagicMock()
        e1 = Event(m, "one")
        e2 = Event(m, "two")
        ce = CompositeEvent(e1, e2)

        self.performSequenceTest(ce)

        m.assert_has_calls([
            call("one"),
            call("two")
        ])

    @patch('avx.Sequencer.time')
    def testSleepEvent(self, time):
        e = SleepEvent(5)
        self.performSequenceTest(e)
        # N.B. time.sleep is also called by the sequencer itself
        time.sleep.assert_has_calls([call(5)])

    @patch('avx.Sequencer.logging')
    def testLogEvent(self, logging):
        e = LogEvent(logging.INFO, "This is informational")
        self.performSequenceTest(e)
        logging.log.assert_called_once_with(logging.INFO, "This is informational")

    def testBroadcastEvent(self):
        self.controller.broadcast = MagicMock()
        e = BroadcastEvent("TYPE", "SOURCE", "DATA")
        self.performSequenceTest(e)
        self.controller.broadcast.assert_called_once_with("TYPE", "SOURCE", "DATA")
