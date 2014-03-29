'''
Created on 15 Apr 2013

@author: jrem
'''
from mock import MagicMock
from org.staldates.ui.CameraControls import CameraControl, AdvancedCameraControl
from org.muscat.avx.controller.Controller import Controller
from org.muscat.avx.controller.VISCAController import CameraMove, CameraWhiteBalance
from org.muscat.avx.devices.Device import Device
from org.staldates.ui.tests.GuiTest import GuiTest
from PySide.QtTest import QTest
from PySide.QtCore import Qt
from org.muscat.avx.CameraPosition import CameraPosition
from org.staldates.ui.MainWindow import MainWindow


class Test(GuiTest):

    def setUp(self):
        GuiTest.setUp(self)
        self.mockController = Controller()
        self.mockController.move = MagicMock(return_value=1)
        self.mockController.zoom = MagicMock(return_value=1)
        self.mockController.focus = MagicMock(return_value=1)

        self.mockMainWindow = MainWindow(self.mockController)

        cam = Device("Test Camera")
        self.mockController.addDevice(cam)
        cam.recallPreset = lambda x: {}

    def tearDown(self):
        self.app = None

    def testCannotSelectMultiplePresets(self):
        ''' See https://github.com/jamesremuscat/aldatesx/issues/23'''
        cc = CameraControl(self.mockController, "Test Camera")
        buttons = cc.presetGroup.buttons()

        self.assertEqual(-1, cc.presetGroup.checkedId())
        cc.btnDown.click()
        buttons[1].click()
        self.assertTrue(buttons[1].isChecked())
        self.assertFalse(buttons[0].isChecked())
        buttons[0].click()
        self.assertEqual(0, cc.presetGroup.checkedId())
        self.assertTrue(buttons[0].isChecked())
        self.assertFalse(buttons[1].isChecked())

    def testMoveCamera(self):
        cc = CameraControl(self.mockController, "Test Camera")
        cc.btnUp.pressed.emit()
        self.mockController.move.assert_called_with("Test Camera", CameraMove.Up)
        cc.btnUp.released.emit()
        self.mockController.move.assert_called_with("Test Camera", CameraMove.Stop)
        cc.btnDown.pressed.emit()
        self.mockController.move.assert_called_with("Test Camera", CameraMove.Down)
        cc.btnDown.released.emit()
        self.mockController.move.assert_called_with("Test Camera", CameraMove.Stop)
        cc.btnLeft.pressed.emit()
        self.mockController.move.assert_called_with("Test Camera", CameraMove.Left)
        cc.btnLeft.released.emit()
        self.mockController.move.assert_called_with("Test Camera", CameraMove.Stop)
        cc.btnRight.pressed.emit()
        self.mockController.move.assert_called_with("Test Camera", CameraMove.Right)
        cc.btnRight.released.emit()
        self.mockController.move.assert_called_with("Test Camera", CameraMove.Stop)

    def testMoveCameraWithKeyboard(self):
        cc = CameraControl(self.mockController, "Test Camera")
        QTest.keyPress(cc, Qt.Key_Up)
        self.mockController.move.assert_called_with("Test Camera", CameraMove.Up)
        QTest.keyRelease(cc, Qt.Key_Up)
        self.mockController.move.assert_called_with("Test Camera", CameraMove.Stop)
        QTest.keyPress(cc, Qt.Key_Down)
        self.mockController.move.assert_called_with("Test Camera", CameraMove.Down)
        QTest.keyRelease(cc, Qt.Key_Down)
        self.mockController.move.assert_called_with("Test Camera", CameraMove.Stop)
        QTest.keyPress(cc, Qt.Key_Left)
        self.mockController.move.assert_called_with("Test Camera", CameraMove.Left)
        QTest.keyRelease(cc, Qt.Key_Left)
        self.mockController.move.assert_called_with("Test Camera", CameraMove.Stop)
        QTest.keyPress(cc, Qt.Key_Right)
        self.mockController.move.assert_called_with("Test Camera", CameraMove.Right)
        QTest.keyRelease(cc, Qt.Key_Right)
        self.mockController.move.assert_called_with("Test Camera", CameraMove.Stop)

# Tests for advanced camera controls

    def testGetCameraPosition(self):
        fakePosition = CameraPosition(111, 222, 333)
        self.mockController.getPosition = MagicMock(return_value=fakePosition)
        acc = AdvancedCameraControl(self.mockController, "Test Camera", self.mockMainWindow)
        self.findButton(acc, "Get Position").click()
        self.mockController.getPosition.assert_called_once_with("Test Camera")
        self.assertEqual("111", acc.posDisplay.itemAtPosition(0, 1).widget().text())
        self.assertEqual("222", acc.posDisplay.itemAtPosition(1, 1).widget().text())
        self.assertEqual("333", acc.posDisplay.itemAtPosition(2, 1).widget().text())

    def testChangeWhiteBalance(self):
        self.mockController.whiteBalance = MagicMock(return_value=1)
        acc = AdvancedCameraControl(self.mockController, "Test Camera", self.mockMainWindow)
        self.assertFalse(self.findButton(acc, "Set").isEnabled())

        self.findButton(acc, "Auto").click()
        self.mockController.whiteBalance.assert_called_with("Test Camera", CameraWhiteBalance.Auto)
        self.assertFalse(self.findButton(acc, "Set").isEnabled())

        self.findButton(acc, "Indoor").click()
        self.mockController.whiteBalance.assert_called_with("Test Camera", CameraWhiteBalance.Indoor)
        self.assertFalse(self.findButton(acc, "Set").isEnabled())

        self.findButton(acc, "Outdoor").click()
        self.mockController.whiteBalance.assert_called_with("Test Camera", CameraWhiteBalance.Outdoor)
        self.assertFalse(self.findButton(acc, "Set").isEnabled())

        self.findButton(acc, "One Push").click()
        self.mockController.whiteBalance.assert_called_with("Test Camera", CameraWhiteBalance.OnePush)
        self.assertTrue(self.findButton(acc, "Set").isEnabled())

        self.findButton(acc, "Set").click()
        self.mockController.whiteBalance.assert_called_with("Test Camera", CameraWhiteBalance.Trigger)
