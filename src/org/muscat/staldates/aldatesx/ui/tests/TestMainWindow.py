'''
Created on 17 Apr 2013

@author: jrem
'''
from org.muscat.staldates.aldatesx.ui.tests.GuiTest import GuiTest
from org.muscat.staldates.aldatesx.Controller import Controller
from org.muscat.staldates.aldatesx.ui.MainWindow import MainWindow
from org.muscat.staldates.aldatesx.ui.widgets.SystemPowerWidget import SystemPowerWidget
from mock import MagicMock
from org.muscat.staldates.aldatesx.ui.VideoSwitcher import VideoSwitcher
from org.muscat.staldates.aldatesx.ui.widgets.LogViewer import LogViewer


class TestMainWindow(GuiTest):

    def setUp(self):
        GuiTest.setUp(self)
        self.mockController = Controller()
        self.mockController.systemPowerOn = MagicMock(return_value=1)
        self.mockController.systemPowerOff = MagicMock(return_value=1)

        self.main = MainWindow(self.mockController)

    def testSystemPower(self):
        spcButton = self.findButton(self.main, "Power")
        self.assertFalse(spcButton == None)

        spcButton.click()
        spc = self.main.stack.currentWidget()
        self.assertTrue(isinstance(spc, SystemPowerWidget))
        spc.btnOn.click()
        self.assertEquals(self.mockController.systemPowerOn.call_count, 1)

        spc.btnOff.click()
        self.assertEquals(self.mockController.systemPowerOff.call_count, 1)

        spc.b.click()
        self.assertTrue(isinstance(self.main.stack.currentWidget(), VideoSwitcher))

    def testLog(self):
        entry = FakeLogEntry("2013-04-17 18:45:38", "ERROR", "This is a test message")
        self.mockController.getLog = MagicMock(return_value=[entry])

        advMenuButton = self.findButton(self.main, "Advanced")
        advMenuButton.click()
        top = self.main.stack.currentWidget()

        logButton = self.findButton(top, "Log")
        logButton.click()
        lw = self.main.stack.currentWidget()
        self.assertTrue(isinstance(lw, LogViewer))
        self.assertEqual(self.mockController.getLog.call_count, 1)


class FakeLogEntry(object):

    def __init__(self, asctime, level, message):
        self.asctime = asctime
        self.levelname = level
        self.message = message
