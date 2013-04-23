'''
Created on 15 Apr 2013

@author: jrem
'''
from mock import MagicMock
from org.muscat.staldates.aldatesx.ui.CameraControls import CameraControl
from org.muscat.staldates.aldatesx.Controller import Controller, CameraMove
from org.muscat.staldates.aldatesx.devices.Device import Device
from org.muscat.staldates.aldatesx.ui.tests.GuiTest import GuiTest
from PySide.QtTest import QTest
from PySide.QtCore import Qt


class Test(GuiTest):

    def setUp(self):
        GuiTest.setUp(self)
        self.mockController = Controller()
        self.mockController.move = MagicMock(return_value=1)
        self.mockController.zoom = MagicMock(return_value=1)
        self.mockController.focus = MagicMock(return_value=1)

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
