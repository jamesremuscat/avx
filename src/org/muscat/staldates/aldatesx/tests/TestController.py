from unittest import TestCase
from org.muscat.staldates.aldatesx.Controller import Controller
from mock import MagicMock
from org.muscat.staldates.aldatesx.devices.SerialRelayCard import UpDownStopArray


class TestController(TestCase):

    def testTalkToClients(self):
        c = Controller()

        class DummyClient:

            def ping(self):
                pass

            def getHostIP(self):
                return "None"

        def pingClient(client):
            client.ping()

        client1 = DummyClient()
        client1.ping = MagicMock()
        client2 = DummyClient()
        client2.ping = MagicMock()

        # Directly inject these, bypassing Pyro
        c.clients[1] = client1
        c.clients[2] = client2

        c.callAllClients(pingClient)
        self.assertEqual(client1.ping.call_count, 1)
        self.assertEqual(client2.ping.call_count, 1)

        client1.ping.reset_mock()
        client2.ping.reset_mock()
        c.unregisterClient(2)

        c.callAllClients(pingClient)
        client1.ping.assert_called_once_with()
        self.assertEqual(client1.ping.call_count, 1)
        self.assertEqual(client2.ping.call_count, 0)

    def testSendControlSignalsToBlinds(self):
        c = Controller()

        blinds = UpDownStopArray("Blinds")
        blinds.lower = MagicMock(return_value=0)
        blinds.raiseUp = MagicMock(return_value=0)
        blinds.stop = MagicMock(return_value=0)

        c.addDevice(blinds)

        c.lower("Blinds", 1)
        blinds.lower.assert_called_once_with(1)

        c.raiseUp("Blinds", 256)
        blinds.raiseUp.assert_called_once_with(256)

        c.stop("Blinds", 1138)
        blinds.stop.assert_called_once_with(1138)
