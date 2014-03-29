'''
Created on 18 Apr 2013

@author: james
'''
from org.staldates.ui.tests.GuiTest import GuiTest
from org.muscat.avx.controller.Controller import Controller
from org.muscat.avx.devices.Device import Device
from org.staldates.ui.EclipseControls import EclipseControls
from mock import MagicMock


class TestEclipseControls(GuiTest):

    def setUp(self):
        GuiTest.setUp(self)
        self.mockController = Controller()

        conv = Device("Test Scan Converter")
        self.mockController.addDevice(conv)

    def testControls(self):
        self.mockController.toggleFade = MagicMock(return_value=1)
        self.mockController.toggleFreeze = MagicMock(return_value=1)
        self.mockController.toggleOverlay = MagicMock(return_value=1)
        self.mockController.toggleOverscan = MagicMock(return_value=1)

        ec = EclipseControls(self.mockController, "Test Scan Converter")
        self.findButton(ec, "Overscan").click()
        self.mockController.toggleOverscan.assert_called_once_with("Test Scan Converter", False)
        self.findButton(ec, "Overscan").click()
        self.mockController.toggleOverscan.assert_called_with("Test Scan Converter", True)

        self.findButton(ec, "Freeze").click()
        self.mockController.toggleFreeze.assert_called_once_with("Test Scan Converter", True)
        self.findButton(ec, "Freeze").click()
        self.mockController.toggleFreeze.assert_called_with("Test Scan Converter", False)

        self.findButton(ec, "Fade").click()
        self.mockController.toggleFade.assert_called_once_with("Test Scan Converter", True)
        self.findButton(ec, "Fade").click()
        self.mockController.toggleFade.assert_called_with("Test Scan Converter", False)

        self.findButton(ec, "Overlay").click()
        self.mockController.toggleOverlay.assert_called_once_with("Test Scan Converter", True)
        self.findButton(ec, "Overlay").click()
        self.mockController.toggleOverlay.assert_called_with("Test Scan Converter", False)
