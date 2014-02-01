from org.muscat.staldates.aldatesx.ui.tests.GuiTest import GuiTest
from org.muscat.staldates.aldatesx.controller.Controller import Controller
from org.muscat.staldates.aldatesx.devices.Device import Device
from org.muscat.staldates.aldatesx.ui.widgets.BlindsControl import BlindsControl
from org.muscat.staldates.aldatesx.ui.MainWindow import MainWindow
from mock import MagicMock


class TestBlindsControl(GuiTest):

    def setUp(self):
        GuiTest.setUp(self)
        self.mockController = Controller()
        self.mockBlindsDevice = Device("Test")
        self.mockController.addDevice(self.mockBlindsDevice)
        self.mockMainWindow = MainWindow(self.mockController)

    def testBlinds(self):
        bc = BlindsControl(self.mockController, self.mockMainWindow)

        self.mockController.raiseUp = MagicMock()
        self.mockController.lower = MagicMock()
        self.mockController.stop = MagicMock()

        self.findButton(bc, "All").click()
        self.findButton(bc, "Raise").click()
        self.mockController.raiseUp.assert_called_once_with("Blinds", 0)
        self.findButton(bc, "Lower").click()
        self.mockController.lower.assert_called_once_with("Blinds", 0)
        self.findButton(bc, "Stop").click()
        self.mockController.stop.assert_called_once_with("Blinds", 0)

        self.mockController.raiseUp.reset_mock()
        self.mockController.lower.reset_mock()
        self.mockController.stop.reset_mock()

        self.findButton(bc, "3").click()
        self.findButton(bc, "Raise").click()
        self.mockController.raiseUp.assert_called_once_with("Blinds", 3)
        self.findButton(bc, "Lower").click()
        self.mockController.lower.assert_called_once_with("Blinds", 3)
        self.findButton(bc, "Stop").click()
        self.mockController.stop.assert_called_once_with("Blinds", 3)

        self.mockMainWindow.stepBack = MagicMock()
        self.findButton(bc, "Back").click()
        self.assertEqual(1, self.mockMainWindow.stepBack.call_count)
