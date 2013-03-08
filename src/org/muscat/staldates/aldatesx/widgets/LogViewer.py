from PySide.QtGui import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QSizePolicy
from PySide.QtCore import Qt
from org.muscat.staldates.aldatesx.widgets.Buttons import ExpandingButton

class LogViewer(QWidget):

    def __init__(self, parent = None):
        super(LogViewer, self).__init__(parent)
        
        layout = QVBoxLayout(self)
        
        title = QLabel("System Log")
        title.setStyleSheet("font-size: 48px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        self.table = QTableWidget()
        layout.addWidget(self.table)
        
        self.b = ExpandingButton()
        self.b.setText("Back")
        self.b.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(self.b)
        
    def displayLog(self, entries):
        self.table.clearContents();
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