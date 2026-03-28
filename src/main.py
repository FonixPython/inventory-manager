from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QStackedWidget, QSizePolicy,QVBoxLayout
import sys

# file imports
from pages import *



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inventory manager")
        self.setStyleSheet("""
            QMainWindow {
                background-color: #030A1E;
            }
        """)
        central = QWidget()
        self.setCentralWidget(central)

        # Window layout
        self.layout = QVBoxLayout(central)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Multipage
        self.multipage = QStackedWidget()
        self.layout.addWidget(self.multipage)

        # Page 1
        self.connectionPage = ConnectionPage()
        self.multipage.addWidget(self.connectionPage)
        
        self.multipage.setCurrentIndex(0)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()