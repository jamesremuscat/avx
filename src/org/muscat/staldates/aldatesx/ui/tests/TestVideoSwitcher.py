'''
Created on 16 Apr 2013

@author: jrem
'''
import unittest
from org.muscat.staldates.aldatesx.Controller import Controller
from org.muscat.staldates.aldatesx.devices.Device import Device
from org.muscat.staldates.aldatesx.ui.VideoSwitcher import VideoSwitcher
from org.muscat.staldates.aldatesx.ui.widgets.OutputsGrid import OutputsGrid
from mock import MagicMock
from org.muscat.staldates.aldatesx.ui.tests.GuiTest import GuiTest


class TestVideoSwitcher(GuiTest):

    def setUp(self):
        GuiTest.setUp(self)
        self.mockController = Controller()

        self.main = Device("Main")
        self.mockController.addDevice(self.main)
        self.main.sendInputToOutput = MagicMock(return_value=1)

        self.preview = Device("Preview")
        self.mockController.addDevice(self.preview)
        self.preview.sendInputToOutput = MagicMock(return_value=1)

        self.extras = Device("Extras")
        self.mockController.addDevice(self.extras)
        self.extras.sendInputToOutput = MagicMock(return_value=1)

        fakeMainWindow = object()
        self.vs = VideoSwitcher(self.mockController, fakeMainWindow)

    def testSendInputsToOutputs(self):
        outputsGrid = self.vs.findChild(OutputsGrid)
        self.assertTrue(outputsGrid != None)

        self.vs.btnCamera1.click()
        self.preview.sendInputToOutput.assert_called_with(1, 1)  # Camera 1 is previewed

        outputsGrid.btnChurch.click()
        self.main.sendInputToOutput.assert_called_with(1, 4)  # Camera 1 sent to output 4 (church)

        self.vs.btnCamera3.click()
        self.preview.sendInputToOutput.assert_called_with(3, 1)  # Camera 3 previewed
        outputsGrid.btnGallery.click()
        self.main.sendInputToOutput.assert_called_with(3, 6)  # Camera 3 sent to output 6 (gallery)
        outputsGrid.btnPCMix.click()
        self.preview.sendInputToOutput.assert_called_with(3, 2)  # Camera 3 sent to PC Mix

        self.vs.btnBlank.click()
        outputsGrid.btnAll.click()
        self.main.sendInputToOutput.assert_called_with(0, 0)  # Everything blanked

        self.vs.btnExtras.click()
        self.preview.sendInputToOutput.assert_called_with(6, 1)  # This is wired up the wrong way around - 5 vs 6
        self.vs.extrasSwitcher.inputs.buttons()[4].click()  # Visuals PC video
        outputsGrid.btnAll.click()  # This one click should trigger two takes, one on each switcher
        self.extras.sendInputToOutput.assert_called_with(8, 1)
        self.main.sendInputToOutput.assert_called_with(5, 0)  # Extras to everywhere

    def testCantSendPCMixToItself(self):
        outputsGrid = self.vs.findChild(OutputsGrid)

        self.vs.btnVisualsPC.click()
        self.preview.sendInputToOutput.assert_called_with(5, 1)
        self.preview.sendInputToOutput.reset_mock()
        outputsGrid.btnPCMix.click()
        self.assertFalse(self.preview.sendInputToOutput.called)
        self.assertFalse(self.main.sendInputToOutput.called)


if __name__ == "__main__":
    unittest.main()
