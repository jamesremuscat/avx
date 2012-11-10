'''
Created on 10 Nov 2012

@author: james
'''
from PySide.QtGui import QWidget, QGridLayout, QButtonGroup
from org.muscat.staldates.aldatesx.VideoSwitcher import InputButton, OutputButton

class ExtrasSwitcher(QWidget):
    '''
    The extras switcher.
    '''

    def __init__(self, switcher):
        super(ExtrasSwitcher, self).__init__()
        self.switcher = switcher
        self.initUI()
        
    def initUI(self):
        layout = QGridLayout()
        self.setLayout(layout)
        
        inputs = QButtonGroup()
        
        btnE1 = InputButton(self)
        btnE1.setText("Extras 1")
        layout.addWidget(btnE1, 0, 0)
        inputs.addButton(btnE1, 1)
        
        btnE2 = InputButton(self)
        btnE2.setText("Extras 2")
        layout.addWidget(btnE2, 0, 1)
        inputs.addButton(btnE2, 2)
        
        btnE3 = InputButton(self)
        btnE3.setText("Extras 3")
        layout.addWidget(btnE3, 0, 2)
        inputs.addButton(btnE3, 3)
        
        btnE4 = InputButton(self)
        btnE4.setText("Extras 4")
        layout.addWidget(btnE4, 0, 3)
        inputs.addButton(btnE4, 4)
        
        btnEVideo = InputButton(self)
        btnEVideo.setText("Visuals PC video")
        layout.addWidget(btnEVideo, 0, 4)
        inputs.addButton(btnEVideo, 8)
        
        self.inputs = inputs
        
        btnPrevMix = OutputButton(self, 1)
        btnPrevMix.setText("Preview / PC Mix")
        layout.addWidget(btnPrevMix, 1, 0, 1, 5)
        
        btnPrevMix.clicked.connect(self.takePreview)
        
        
    def takePreview(self):
        self.take(1)
        
        
    def take(self, output=2):
        '''Send the currently selected input to the main switcher's input. '''
        self.switcher.sendInputToOutput(self.inputs.checkedId(), output)