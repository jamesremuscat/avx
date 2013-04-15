'''
Created on 15 Apr 2013

@author: jrem
'''
from PySide.QtGui import QApplication
import unittest
from org.muscat.staldates.aldatesx.ui.CameraControls import CameraControl
from org.muscat.staldates.aldatesx.Controller import Controller
from org.muscat.staldates.aldatesx.devices.Device import Device


class Test(unittest.TestCase):


    def setUp(self):
        self.app = QApplication([])
        self.mockController = Controller()
        
        cam = Device("Test Camera")
        self.mockController.addDevice(cam)
        cam.moveDown = lambda: {}
        cam.stop = lambda: {}
        cam.focusStop = lambda: {}
        cam.recallPreset = lambda x: {}


    def testCannotSelectMultiplePresets(self):
        ''' See https://github.com/jamesremuscat/aldatesx/issues/23'''
        cc = CameraControl(self.mockController, "Test Camera")
        buttons = cc.presetGroup.buttons()
        
        self.assertEqual(-1, cc.presetGroup.checkedId())
        #cc.focusBtns.downButton.click()
        cc.btnDown.click()
        buttons[1].click()
        self.assertTrue(buttons[1].isChecked())
        self.assertFalse(buttons[0].isChecked())
        buttons[0].click()
        self.assertEqual(0, cc.presetGroup.checkedId())
        self.assertTrue(buttons[0].isChecked())
        self.assertFalse(buttons[1].isChecked())
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()