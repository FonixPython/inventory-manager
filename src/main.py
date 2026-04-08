from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QStackedWidget, QSizePolicy,QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFontDatabase, QFont
import sys

# file imports
from connectionPage import ConnectionPage
from homePage import HomePage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inventory Manager")
        self.setMinimumSize(1200, 800)
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0d1117;
            }
            QWidget {
                font-family: 'Segoe UI', 'SF Pro Display', -apple-system, sans-serif;
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
        self.connectionPage = ConnectionPage(self.goToApp)
        self.multipage.addWidget(self.connectionPage)

        self.multipage.setCurrentIndex(0)

    def goToApp(self):
        self.homePage = None
        self.homePage = HomePage(self.logOut)
        self.multipage.addWidget(self.homePage)
        self.multipage.setCurrentIndex(1)

    def logOut(self):
        self.homePage = None
        self.multipage.setCurrentIndex(0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()