from unittest import TestCase
from org.muscat.staldates.aldatesx.Controller import Controller
from mock import MagicMock


class Test(TestCase):

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
