from PyQt6.QtWidgets import QApplication, QMainWindow,QLineEdit, QWidget,QLabel, QPushButton,QHBoxLayout,QVBoxLayout,QSizePolicy
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIntValidator

import os
import json

class ConnectionPage(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout = QVBoxLayout(self)
        
        self.login_box = QWidget()
        self.login_box.setFixedSize(500,600)
        self.login_box.setObjectName("login_box")
        self.layout.addWidget(self.login_box, alignment=Qt.AlignmentFlag.AlignCenter)
        self.box_layout = QVBoxLayout(self.login_box)
        self.box_layout.setSpacing(5)
        self.box_layout.setContentsMargins(0,0,0,0)
        # Widgets
        self.titleLabel = QLabel("Connect to a server")
        self.titleLabel.setObjectName("titleLabel")
        self.box_layout.addWidget(self.titleLabel,alignment= Qt.AlignmentFlag.AlignHCenter)

        self.hostWidget = QWidget()
        self.hostWidget.setObjectName("hostWidget")
        self.hostWidgetLayout = QHBoxLayout(self.hostWidget)
        self.hostWidgetLayout.addWidget(QLabel("Host:"),alignment=Qt.AlignmentFlag.AlignHCenter)
        
        self.addressEntry = QLineEdit()
        self.addressEntry.setObjectName("addressEntry")
        self.addressEntry.setText("localhost")
        self.hostWidgetLayout.addWidget(self.addressEntry)

        self.portEntry = QLineEdit()
        self.portEntry.setObjectName("portEntry")
        self.portEntry.setValidator(QIntValidator(0, 99999))
        self.portEntry.setText("3306")
        self.hostWidgetLayout.addWidget(self.portEntry)

        self.box_layout.addWidget(self.hostWidget, alignment=Qt.AlignmentFlag.AlignHCenter)


        self.userWidget = QWidget()
        self.box_layout.addWidget(self.userWidget)
        self.userWidgetLayout = QHBoxLayout(self.userWidget)
        self.userWidgetLayout.addWidget(QLabel("User:"),alignment=Qt.AlignmentFlag.AlignHCenter)
        
        self.userEntry = QLineEdit()
        self.userEntry.setObjectName("userEntry")
        self.userEntry.setPlaceholderText("username")
        self.userWidgetLayout.addWidget(self.userEntry)

        self.passwordWidget = QWidget()
        self.box_layout.addWidget(self.passwordWidget)
        self.passwordWidgetLayout = QHBoxLayout(self.passwordWidget)
        self.passwordWidgetLayout.addWidget(QLabel("Password:"),alignment=Qt.AlignmentFlag.AlignHCenter)
        
        self.passwordEntry = QLineEdit()
        self.passwordEntry.setObjectName("passwordEntry")
        self.passwordEntry.setPlaceholderText("password")
        self.passwordEntry.setEchoMode(QLineEdit.EchoMode.Password) 
        self.passwordWidgetLayout.addWidget(self.passwordEntry)
        

        self.databaseWidget = QWidget()
        self.box_layout.addWidget(self.databaseWidget)
        self.databaseWidgetLayout = QHBoxLayout(self.databaseWidget)
        self.databaseWidgetLayout.addWidget(QLabel("Database:"),alignment=Qt.AlignmentFlag.AlignHCenter)
        
        self.databaseEntry = QLineEdit()
        self.databaseEntry.setObjectName("databaseEntry")
        self.databaseEntry.setPlaceholderText("database")
        self.databaseWidgetLayout.addWidget(self.databaseEntry)

        self.databaseWidgetLayout.addWidget(QLabel("Table:"),alignment=Qt.AlignmentFlag.AlignHCenter)
        
        self.tableEntry = QLineEdit()
        self.tableEntry.setObjectName("tableEntry")
        self.tableEntry.setPlaceholderText("table")
        self.tableEntry.setText("inventory")
        self.databaseWidgetLayout.addWidget(self.tableEntry)




        self.connectButton = QPushButton(text="Connect")
        self.box_layout.addWidget(self.connectButton,alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter)

        self.setStyleSheet("""
        QWidget#login_box{
            background-color: #000212;
            border-radius: 15px;
            border: 1px solid #496297;
        }
        #hostWidget{
            margin:0px;
            padding:0px;
            width:300px;
        }
        QLineEdit{
            height:40px;
            width:350px;
            background-color:#0B152A;
            border-radius: 15px;
            border: 1px solid #496297;
            padding:5px;
            font-size:20px;
            color:#D3F2FF;
        }
        #portEntry{
            width:65px;
        }
        QLabel{
            margin:0px;
            padding:0px;
            color:#D3F2FF;
            font-size:20px;
        }
        #titleLabel{
            margin:10px;
        }
        QLabel#titleLabel{
            font-size:36px;
            font-weight:bold;
        }
        QPushButton{
            width: 480px;
            height:50px;
            margin:10px;
            background-color:#91B1F1;
            border-radius: 15px;
            border: 1px solid #496297;
            color:#D3F2FF;
            font-size:24px;
            
        }
        QPushButton:pressed{
            background-color:#496297;
        }
        QPushButton:hover{
            background-color:#0B152A;
        }
        """)
        self.fillWithPrevious()

    def fillWithPrevious(self):
        if os.path.exists("./creds.json"):
            with open("./creds.json","r") as f:
                data = json.load(f)
            self.addressEntry.setText(data.get("address","localhost"))
            self.portEntry.setText(data.get("port","3306"))
            self.userEntry.setText(data.get("user",""))
            self.passwordEntry.setText(data.get("password",""))
            self.databaseEntry.setText(data.get("database",""))
            self.tableEntry.setText(data.get("table","inventory"))
