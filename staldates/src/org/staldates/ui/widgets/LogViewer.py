from PySide.QtGui import QVBoxLayout, QTableWidget, QTableWidgetItem
from org.staldates.ui.widgets.Screens import ScreenWithBackButton


class LogViewer(ScreenWithBackButton):

    def __init__(self, controller, mainWindow):
        self.controller = controller
        ScreenWithBackButton.__init__(self, "System Log", mainWindow)

    def makeContent(self):

        layout = QVBoxLayout()

        self.table = QTableWidget()
        layout.addWidget(self.table)

        return layout

    def displayLog(self):
        entries = self.controller.getLog()
        self.table.clearContents()
        self.table.setRowCount(len(entries))
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Time", "Severity", "Message"])

        i = 0
        for entry in entries:
            self.table.setItem(i, 0, QTableWidgetItem(entry.asctime))
            self.table.setItem(i, 1, QTableWidgetItem(entry.levelname))
            self.table.setItem(i, 2, QTableWidgetItem(entry.message))
            i = i + 1

        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.scrollToBottom()
