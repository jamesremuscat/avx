'''
Created on 16 Apr 2013

@author: jrem
'''
import unittest
from org.muscat.avx.controller.Controller import Controller
from org.muscat.avx.devices.Device import Device
from org.staldates.ui.VideoSwitcher import VideoSwitcher
from org.staldates.ui.widgets.OutputsGrid import OutputsGrid
from mock import MagicMock
from org.staldates.ui.tests.GuiTest import GuiTest
from PySide.QtTest import QTest
from PySide.QtCore import Qt


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
        self.preview.sendInputToOutput.assert_called_with(6, 1)  # This is wired up the wrong way around - 5 on main vs 6 on preview
        self.vs.extrasSwitcher.inputs.buttons()[4].click()  # Visuals PC video
        outputsGrid.btnAll.click()  # This one click should trigger two takes, one on each switcher
        self.extras.sendInputToOutput.assert_called_with(8, 1)
        self.main.sendInputToOutput.assert_called_with(5, 0)  # Extras to everywhere
        outputsGrid.btnPCMix.click()
        self.extras.sendInputToOutput.assert_called_with(8, 2)
        self.preview.sendInputToOutput.assert_called_with(6, 2)  # Extras to PC Mix

    def testCantSendPCMixToItself(self):
        outputsGrid = self.vs.findChild(OutputsGrid)

        self.vs.btnVisualsPC.click()
        self.preview.sendInputToOutput.assert_called_with(5, 1)
        self.preview.sendInputToOutput.reset_mock()
        outputsGrid.btnPCMix.click()
        self.assertFalse(self.preview.sendInputToOutput.called)
        self.assertFalse(self.main.sendInputToOutput.called)
        self.assertFalse(outputsGrid.btnPCMix.isEnabled())

    def testCantBlankPCMix(self):
        outputsGrid = self.vs.findChild(OutputsGrid)

        self.vs.btnBlank.click()
        outputsGrid.btnPCMix.click()
        self.assertFalse(self.preview.sendInputToOutput.called)
        self.assertFalse(self.main.sendInputToOutput.called)
        self.assertFalse(outputsGrid.btnPCMix.isEnabled())

    def testKeyboardControls(self):
        QTest.keyClick(self.vs, Qt.Key_0)
        QTest.keyClick(self.vs, Qt.Key_Space)
        self.main.sendInputToOutput.assert_called_with(0, 0)

        QTest.keyClick(self.vs, Qt.Key_1)
        self.preview.sendInputToOutput.assert_called_with(1, 1)
        QTest.keyClick(self.vs, Qt.Key_Space)
        self.main.sendInputToOutput.assert_called_with(1, 0)

        QTest.keyClick(self.vs, Qt.Key_2)
        self.preview.sendInputToOutput.assert_called_with(2, 1)
        QTest.keyClick(self.vs, Qt.Key_Space)
        self.main.sendInputToOutput.assert_called_with(2, 0)

        QTest.keyClick(self.vs, Qt.Key_3)
        self.preview.sendInputToOutput.assert_called_with(3, 1)
        QTest.keyClick(self.vs, Qt.Key_Space)
        self.main.sendInputToOutput.assert_called_with(3, 0)

        QTest.keyClick(self.vs, Qt.Key_4)
        self.preview.sendInputToOutput.assert_called_with(4, 1)
        QTest.keyClick(self.vs, Qt.Key_Space)
        self.main.sendInputToOutput.assert_called_with(4, 0)

        QTest.keyClick(self.vs, Qt.Key_5)
        self.preview.sendInputToOutput.assert_called_with(6, 1)
        QTest.keyClick(self.vs, Qt.Key_Space)
        self.main.sendInputToOutput.assert_called_with(5, 0)

        QTest.keyClick(self.vs, Qt.Key_6)
        self.preview.sendInputToOutput.assert_called_with(5, 1)
        QTest.keyClick(self.vs, Qt.Key_Space)
        self.main.sendInputToOutput.assert_called_with(6, 0)

        self.main.sendInputToOutput.reset_mock()
        self.preview.sendInputToOutput.reset_mock()
        QTest.keyClick(self.vs, Qt.Key_7)
        self.assertFalse(self.preview.sendInputToOutput.called)
        QTest.keyClick(self.vs, Qt.Key_Space)
        self.main.sendInputToOutput.assert_called_with(6, 0)  # which was the last valid input key pressed


if __name__ == "__main__":
    unittest.main()
