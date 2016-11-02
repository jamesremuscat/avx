'''
Created on 2 Nov 2016

@author: james
'''
import unittest
from avx.controller.ControllerHttp import handleRequest
from mock import MagicMock


class TestControllerHttp(unittest.TestCase):

    def testInvalidRequests(self):
        m = MagicMock()
        handleRequest("not-a-valid-path", None, m)
        m.assert_called_once_with(400, "Incorrectly formatted URL: not-a-valid-path")
        m.reset_mock()

        c = MagicMock()
        c.hasDevice = MagicMock(return_value=False)

        handleRequest("/not-a-device/method/arg", c, m)
        c.hasDevice.assert_called_once_with('not-a-device')
        m.assert_called_once_with(404, "No such device: not-a-device")
        m.reset_mock()

        d = MagicMock()
        d.httpAccessible = False
        c2 = MagicMock()
        c2.hasDevice = MagicMock(return_value=True)
        c2.getDevice = MagicMock(return_value=d)

        handleRequest("/testDevice/method/arg", c2, m)
        c2.hasDevice.assert_called_once_with('testDevice')
        c2.getDevice.assert_called_once_with('testDevice')
        m.assert_called_once_with(403, "Not permitted to access device testDevice over HTTP.")
        m.reset_mock()

        d3 = MagicMock()
        d3.httpAccessible = True
        d3.method = None
        c3 = MagicMock()
        c3.hasDevice = MagicMock(return_value=True)
        c3.getDevice = MagicMock(return_value=d3)

        handleRequest("/testDevice/method/arg", c3, m)
        c2.hasDevice.assert_called_once_with('testDevice')
        c2.getDevice.assert_called_once_with('testDevice')
        m.assert_called_once_with(400, "No such function: method")

    def testValidRequest(self):
        d = MagicMock()
        d.httpAccessible = True
        d.method = MagicMock(return_value="Happy times")
        c = MagicMock()
        c.hasDevice = MagicMock(return_value=True)
        c.getDevice = MagicMock(return_value=d)

        m = MagicMock()

        handleRequest("/testDevice/method/arg", c, m)
        c.hasDevice.assert_called_once_with('testDevice')
        c.getDevice.assert_called_once_with('testDevice')
        d.method.assert_called_once_with('arg')
        m.assert_called_once_with(200, "OK Happy times")
