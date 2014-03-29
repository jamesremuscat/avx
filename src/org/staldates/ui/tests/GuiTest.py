'''
Created on 16 Apr 2013

@author: jrem
'''
from PySide.QtGui import QApplication, QAbstractButton
import unittest


class GuiTest(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.app = QApplication.instance()  # checks if QApplication already exists
        if not self.app:  # create QApplication if it doesn't exist
            self.app = QApplication([])

    def findButton(self, parent, text):
        buttons = parent.findChildren(QAbstractButton)
        for b in buttons:
            if b.text() == text:
                return b
        return None
