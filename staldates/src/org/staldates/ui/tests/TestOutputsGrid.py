'''
Created on 24 Apr 2013

@author: jrem
'''
from org.staldates.ui.tests.GuiTest import GuiTest
from org.staldates.ui.widgets.OutputsGrid import OutputsGrid


class TestOutputsGrid(GuiTest):

    def setUp(self):
        GuiTest.setUp(self)

    def testDisplayInputNames(self):
        og = OutputsGrid()
        self.assertEqual("-", self.findButton(og, "Projectors").inputDisplay.text())

        og.updateOutputMappings({'Main': {2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 7: 6, 8: 0}})
        self.assertEqual("Camera 1", self.findButton(og, "Projectors").inputDisplay.text())
        self.assertEqual("Camera 2", self.findButton(og, "Font").inputDisplay.text())
        self.assertEqual("Camera 3", self.findButton(og, "Church").inputDisplay.text())
        self.assertEqual("DVD", self.findButton(og, "Welcome").inputDisplay.text())
        self.assertEqual("Extras", self.findButton(og, "Gallery").inputDisplay.text())
        self.assertEqual("Visuals PC", self.findButton(og, "Special").inputDisplay.text())
        self.assertEqual("Blank", self.findButton(og, "Record").inputDisplay.text())

    def testDisplayInputSentToAll(self):
        og = OutputsGrid()
        og.updateOutputMappings({'Main': {0: 1}})
        self.assertEqual("Camera 1", self.findButton(og, "Projectors").inputDisplay.text())
        self.assertEqual("Camera 1", self.findButton(og, "Font").inputDisplay.text())
        self.assertEqual("Camera 1", self.findButton(og, "Church").inputDisplay.text())
        self.assertEqual("Camera 1", self.findButton(og, "Welcome").inputDisplay.text())
        self.assertEqual("Camera 1", self.findButton(og, "Gallery").inputDisplay.text())
        self.assertEqual("Camera 1", self.findButton(og, "Special").inputDisplay.text())
        self.assertEqual("Camera 1", self.findButton(og, "Record").inputDisplay.text())

    def testDisplayInputSentToPCMix(self):
        og = OutputsGrid()
        og.updateOutputMappings({'Preview': {2: 4}})
        self.assertEqual("DVD", self.findButton(og, "PC Mix").inputDisplay.text())
        # And test that changing the preview side of the switcher doesn't update the PC Mix button!
        og.updateOutputMappings({'Preview': {1: 2}})
        self.assertEqual("DVD", self.findButton(og, "PC Mix").inputDisplay.text())
        # Buggy wiring means 6 is actually 5
        og.updateOutputMappings({'Preview': {2: 6}})
        self.assertEqual("Extras", self.findButton(og, "PC Mix").inputDisplay.text())
