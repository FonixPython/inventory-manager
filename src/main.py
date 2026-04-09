from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QStackedWidget, QSizePolicy,QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFontDatabase, QFont
from PyQt6.QtGui import QIcon
import sys
import os

# file imports
from connectionPage import ConnectionPage
from homePage import HomePage

def resource_path(relative_path):
    try:base_path = sys._MEIPASS
    except AttributeError:base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(1200, 800)        
        self.setWindowTitle("Inventory manager")
        self.setWindowIcon(QIcon(resource_path("assets/icon.png")))
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