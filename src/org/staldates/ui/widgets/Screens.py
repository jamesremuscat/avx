from PySide.QtGui import QIcon, QLabel, QGridLayout, QWidget, QVBoxLayout
from PySide.QtCore import Qt
from org.staldates.ui.widgets.Buttons import ExpandingButton


class ScreenWithBackButton(QWidget):

    def __init__(self, title, mainWindow):
        super(ScreenWithBackButton, self).__init__()
        self.title = title
        self.mainWindow = mainWindow

        layout = QGridLayout()

        title = QLabel(title)
        title.setStyleSheet("font-size: 48px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title, 0, 0, 1, 7)

        layout.addLayout(self.makeContent(), 1, 0, 1, 7)

        b = ExpandingButton()
        b.setText("Back")
        b.setIcon(QIcon("icons/go-previous.svg"))
        b.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        b.clicked.connect(mainWindow.stepBack)
        layout.addWidget(b, 2, 0, 1, 3)
        layout.setRowStretch(0, 1)
        layout.setRowStretch(1, 6)
        layout.setRowStretch(2, 1)
        self.setLayout(layout)

    def makeContent(self):
        '''
        Override this method to return the layout with the contents of this screen.
        '''
        l = QVBoxLayout()
        l.addWidget(QLabel("This Screen Intentionally Left Blank"))
        return l
