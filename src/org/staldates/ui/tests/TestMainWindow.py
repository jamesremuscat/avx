'''
Created on 17 Apr 2013

@author: jrem
'''
from org.staldates.ui.tests.GuiTest import GuiTest
from org.muscat.avx.controller.Controller import Controller
from org.staldates.ui.MainWindow import MainWindow
from org.staldates.ui.widgets.SystemPowerWidget import SystemPowerWidget
from mock import MagicMock
from org.staldates.ui.VideoSwitcher import VideoSwitcher
from org.staldates.ui.widgets.LogViewer import LogViewer
from org.staldates.ui.widgets.ProjectorScreensControl import ProjectorScreensControl


class TestMainWindow(GuiTest):

    def setUp(self):
        GuiTest.setUp(self)
        self.mockController = Controller()
        self.mockController.sequence = MagicMock(return_value=1)

        self.main = MainWindow(self.mockController)

    def getCurrentScreen(self):
        return self.main.stack.currentWidget()

    def testSystemPower(self):
        spcButton = self.findButton(self.main, "Power")
        self.assertFalse(spcButton == None)

        spcButton.click()
        spc = self.getCurrentScreen()
        self.assertTrue(isinstance(spc, SystemPowerWidget))
        self.findButton(spc, "On").click()
        self.assertEquals(self.mockController.sequence.call_count, 1)

        self.findButton(spc, "Off").click()
        self.assertEquals(self.mockController.sequence.call_count, 2)
        # Probably ought to verify exactly what has been sequenced...

        self.findButton(spc, "Back").click()
        self.assertTrue(isinstance(self.main.stack.currentWidget(), VideoSwitcher))

    def testLog(self):
        entry = FakeLogEntry("2013-04-17 18:45:38", "ERROR", "This is a test message")
        self.mockController.getLog = MagicMock(return_value=[entry])

        advMenuButton = self.findButton(self.main, "Advanced")
        advMenuButton.click()
        top = self.getCurrentScreen()

        logButton = self.findButton(top, "Log")
        logButton.click()
        lw = self.main.stack.currentWidget()
        self.assertTrue(isinstance(lw, LogViewer))
        self.assertEqual(self.mockController.getLog.call_count, 1)

    def testScreens(self):
        self.findButton(self.main, "Screens").click()
        top = self.getCurrentScreen()
        self.assertTrue(isinstance(top, ProjectorScreensControl))

        self.mockController.raiseUp = MagicMock(return_value=0)
        self.findButton(top, "Raise").click()
        self.mockController.raiseUp.assert_called_once_with("Screens", 0)

        self.mockController.lower = MagicMock(return_value=0)
        self.findButton(top, "Lower").click()
        self.mockController.lower.assert_called_once_with("Screens", 0)

        self.mockController.stop = MagicMock(return_value=0)
        self.findButton(top, "Stop").click()
        self.mockController.stop.assert_called_once_with("Screens", 0)

        self.mockController.raiseUp.reset_mock()
        self.mockController.lower.reset_mock()
        self.findButton(top, "Left").click()
        self.findButton(top, "Raise").click()
        self.mockController.raiseUp.assert_called_once_with("Screens", 1)
        self.findButton(top, "Right").click()
        self.findButton(top, "Lower").click()
        self.mockController.lower.assert_called_once_with("Screens", 2)


class FakeLogEntry(object):

    def __init__(self, asctime, level, message):
        self.asctime = asctime
        self.levelname = level
        self.message = message
