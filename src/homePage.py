from PyQt6.QtWidgets import QApplication, QMainWindow,QLineEdit, QWidget,QLabel, QPushButton,QHBoxLayout,QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIntValidator

from db import Database


class HomePage(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.layout = QVBoxLayout(self)
        self.setObjectName("page")

        self.filterState = "all"

        self.actionBar = QWidget()
        self.actionBar.setObjectName("actionBar")
        self.layout.addWidget(self.actionBar,alignment=Qt.AlignmentFlag.AlignTop)
        self.actionBarLayout = QVBoxLayout(self.actionBar)
        self.actionBarLayout.setContentsMargins(0, 0, 0, 0)

        # Search section

        self.searchWidget = QWidget()
        self.searchWidgetLayout = QHBoxLayout(self.searchWidget)
        self.searchWidgetLayout.setContentsMargins(5, 5, 5, 0)
        self.actionBarLayout.addWidget(self.searchWidget)

        self.searchEntry = QLineEdit()
        self.searchEntry.setObjectName("searchEntry")
        self.searchEntry.setPlaceholderText("Search inventory")
        self.searchWidgetLayout.addWidget(self.searchEntry)

        self.searchButton = QPushButton("Search")
        self.searchButton.setObjectName("searchButton")
        self.searchWidgetLayout.addWidget(self.searchButton)


        # Second row

        self.actionWidget = QWidget()
        self.actionBarLayout.addWidget(self.actionWidget)
        self.actionWidgetLayout = QHBoxLayout(self.actionWidget)
        self.actionWidgetLayout.setContentsMargins(0, 0, 0, 5)


        # Filter section

        self.filterWidget = QWidget()
        self.actionWidgetLayout.addWidget(self.filterWidget,alignment=Qt.AlignmentFlag.AlignLeft)
        self.filterWidgetLayout = QHBoxLayout(self.filterWidget)
        self.filterWidgetLayout.setContentsMargins(20, 0, 0, 0)
        self.filterWidgetLayout.addWidget(QLabel("Filter:"))
        self.inButton = QPushButton("In")
        self.inButton.setObjectName("inButton")
        self.inButton.clicked.connect(self.inButtonClick)
        self.filterWidgetLayout.addWidget(self.inButton)
        self.outButton = QPushButton("Out")
        self.outButton.setObjectName("outButton")
        self.outButton.clicked.connect(self.outButtonClick)
        self.filterWidgetLayout.addWidget(self.outButton)

        # Add new item

        self.addButton = QPushButton("Add new item")
        self.addButton.setContentsMargins(0, 0, 0, 0)
        self.addButton.setObjectName("addButton")
        self.actionWidgetLayout.addWidget(self.addButton,alignment=Qt.AlignmentFlag.AlignRight)


        self.dataTable = QTableWidget()
        self.dataTable.setShowGrid(False)
        self.dataTable.setAlternatingRowColors(False)
        self.dataTable.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.dataTable.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.dataTable.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.dataTable.verticalHeader().setVisible(False)
        self.dataTable.setColumnCount(4)
        self.dataTable.setHorizontalHeaderLabels(["#","Name","Status","Actions"])
        header = self.dataTable.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.layout.addWidget(self.dataTable)

        self.dataTable.setStyleSheet("""
            QTableWidget {
                background-color: #000212;
                color: #D3F2FF;
                gridline-color: #444;
                font-size: 14px;
                border-radius:15px;
            }
            QTableWidget::item{
                height:60px;
                margin-bottom:5px;
                border-radius:0px;
                border: 1px solid #496297;
                background-color:#0B152A;
                border-left: none;
                border-right: none;
                font-size:24px;
            }
            QTableWidget::item:first {
                border-left: 1px solid #496297;
                border-top-left-radius: 15px;
                border-bottom-left-radius: 15px;
            }
            QTableWidget::item:last {
                border-right: 1px solid #496297;
                border-top-right-radius: 15px;
                border-bottom-right-radius: 15px;
            }
            QHeaderView::section{
                background-color: #000212;
                color: #D3F2FF;
                padding: 6px;
                font-size:24px;
                font-weight: bold;
                border-radius:15px;
            }
            QHeaderView{
                background-color: #000212;
                border-radius:15px;
                border: 1px solid #496297;
                margin-bottom:5px;
            }
        """)
        
        self.setStyleSheet("""
        QWidget#actionBar{
            background-color: #000212;
            border-radius: 15px;
            border: 1px solid #496297;
            padding: 0px
        }
        #page{
            background-color:#030A1E;
        }
        #searchWidget{
            margin:0px;
            padding:0px;
            width:300px;
        }
        #addButton{
            width:200px;
        }
        QLineEdit{
            height:40px;
            background-color:#0B152A;
            border-radius: 15px;
            border: 1px solid #496297;
            padding:5px;
            margin:5px;
            font-size:20px;
            color:#D3F2FF;
        }
        QLabel{
            margin:0px;
            padding:0px;
            color:#D3F2FF;
            font-size:20px;
        }
        QPushButton{
            height:40px;
            margin:5px;
            padding:5px;
            background-color:#91B1F1;
            border-radius: 15px;
            border: 1px solid #496297;
            color:#D3F2FF;
            font-size:24px;
        }
        #searchButton{width:100px;}
        QPushButton:disabled{background-color:#a6b8dc;}
        QPushButton:hover{background-color:#0B152A;}
        """)
        self.upadteFilters()
        self.addItem(0)
        self.addItem(1)
        self.addItem(2)
        self.addItem(3)
        self.addItem(4)
        self.addItem(5)
        self.addItem(6)





    def inButtonClick(self):
        if self.filterState in ["all","out"]:self.filterState = "in"
        else: self.filterState="all"
        self.upadteFilters()
    def outButtonClick(self):
        if self.filterState in ["all","in"]:self.filterState = "out"
        else: self.filterState="all"
        self.upadteFilters()

    def addItem(self,row):
        self.dataTable.insertRow(row)
        self.dataTable.setItem(row, 0, QTableWidgetItem(f"{row}"))
        self.dataTable.setItem(row, 1, QTableWidgetItem("Lenovo PUNOSZ"))
        self.dataTable.setItem(row, 2, QTableWidgetItem("Lent to Zétény Botyánszki on 2025.12.01"))

        for row in range(self.dataTable.rowCount()):
            self.dataTable.setRowHeight(row, 50)  # increase height for padding feel

    def upadteFilters(self):
        if self.filterState == "all":
            self.inButton.setStyleSheet("""
                #inButton{
                    height:30px;
                    width:100px;
                    margin:5px;
                    padding:5px;
                    border: 1px solid #09D71A;
                    background-color:#2D7316;
                    border-radius: 15px;
                    font-size:24px;
                }""")
            self.outButton.setStyleSheet("""
                #outButton{
                    height:30px;
                    width:100px;
                    margin:5px;
                    padding:5px;
                    border: 1px solid #D70909;
                    background-color:#731616;
                    border-radius: 15px;
                    font-size:24px;
                }
            """)
        if self.filterState == "in":
            self.inButton.setStyleSheet("""
                #inButton{
                    height:30px;
                    width:100px;
                    margin:5px;
                    padding:5px;
                    border: 1px solid #09D71A;
                    background-color:#09D71A;
                    border-radius: 15px;
                    font-size:24px;
                }""")
            self.outButton.setStyleSheet("""
                #outButton{
                    height:30px;
                    width:100px;
                    margin:5px;
                    padding:5px;
                    border: 1px solid #D70909;
                    background-color:#731616;
                    border-radius: 15px;
                    font-size:24px;
                }
            """)
        if self.filterState == "out":
            self.inButton.setStyleSheet("""
                #inButton{
                    height:30px;
                    width:100px;
                    margin:5px;
                    padding:5px;
                    border: 1px solid #09D71A;
                    background-color:#2D7316;
                    border-radius: 15px;
                    font-size:24px;
                }""")
            self.outButton.setStyleSheet("""
                #outButton{
                    height:30px;
                    width:100px;
                    margin:5px;
                    padding:5px;
                    border: 1px solid #D70909;
                    background-color:#D70909;
                    border-radius: 15px;
                    font-size:24px;
                }
            """)
