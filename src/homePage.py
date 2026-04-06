from PyQt6.QtWidgets import (QApplication, QMainWindow,QLineEdit,
                             QWidget,QLabel, QPushButton,QHBoxLayout,
                             QVBoxLayout, QTableWidget, QTableWidgetItem,
                              QHeaderView, QAbstractItemView, QDialog,
                              QDialogButtonBox, QInputDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIntValidator, QFont

from db import Database,check_mysql_connection
import os
import json
import datetime


class HomePage(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.layout = QVBoxLayout(self)
        self.setObjectName("page")
        self.connectToSaved()
        self.filterState = "all"
        self.addState = False


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
        self.searchWidgetLayout.addWidget(self.searchEntry,alignment=Qt.AlignmentFlag.AlignHCenter)
        self.searchEntry.textChanged.connect(self.refresh_display)


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
        self.addButton.clicked.connect(self.addItemButtonClick)

        self.addEntry = QLineEdit()
        self.addEntry.setObjectName("addEntry")
        self.addEntry.setPlaceholderText("Item name")
        self.actionWidgetLayout.addWidget(self.addEntry,alignment=Qt.AlignmentFlag.AlignRight)
        self.addEntry.setContentsMargins(0, 0, 0, 0)
        self.addEntry.setVisible(False)
        self.addEntry.returnPressed.connect(self.addEntryEnter)
        self.addEntry.editingFinished.connect(self.addEntryFocusOut)


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
        #searchEntry{
            width:550px;
        }
        #addEntry{
            width:200px;
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
        QScrollBar:vertical {
            background: transparent;
            width: 10px;
            margin: 4px 0 4px 0;
        }
        QScrollBar::handle:vertical {
            background: #91B1F1;
            border-radius: 5px;
            min-height: 20px;
        }
        QScrollBar::handle:vertical:hover {
            background: rgba(120, 120, 120, 0.8);
        }
        QScrollBar::handle:vertical:pressed {
            background: rgba(90, 90, 90, 1);
        }
        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {
            height: 0;
            background: none;
        }
        QScrollBar::add-page:vertical,
        QScrollBar::sub-page:vertical {
            background: none;
        }
        #searchButton{width:100px;}
        QPushButton:disabled{background-color:#a6b8dc;}
        QPushButton:hover{background-color:#0B152A;}
        """)
        self.upadteFilters()
        self.refresh_display()
        # self.database.add_item("3m VGA kábel akasztáshoz")
    def connectToSaved(self):
        if not os.path.exists("./creds.json"): raise OSError("No credentials!")
        try:
            with open("./creds.json","r") as f:data = json.load(f)
        except Exception as e:
            raise e
        result = check_mysql_connection(host=data.get("address",None),
                                        port=data.get("port",None),
                                        user=data.get("user",None),
                                        password=data.get("password",None),
                                        database=data.get("database",None)
                                        )
        if not result == "Success":
            raise result
        self.database = Database(db_host=data.get("address",None),db_port=data.get("port",None),db_user=data.get("user",None),db_password=data.get("password",None),db=data.get("database",None),table=data.get("table",None))
    
    def addItemButtonClick(self):
        if self.addState == False:
            self.addEntry.setVisible(True)
            self.addButton.setVisible(False)
            self.addState = True

    def addEntryEnter(self):
        self.addEntry.setVisible(False)
        self.addButton.setVisible(True)
        self.addState = False
        if self.addEntry.text() != "":
            self.database.add_item(self.addEntry.text()) 
        self.addEntry.clear()
        self.refresh_display()

    def addEntryFocusOut(self):
        self.addEntry.setVisible(False)
        self.addButton.setVisible(True)
        self.addEntry.clear()

    def refresh_display(self):
        results = self.database.get_items(search_query=None if self.searchEntry.text() == "" else self.searchEntry.text(),filter=None if self.filterState == "all" else self.filterState.upper())
        self.dataTable.setRowCount(0)
        for i in results:
            self.addItem(i[0],i[1],f"{"Lent to" if i[4] == 0 else "Here"} {"" if i[2] is None else str(i[2])+" on "+ i[3].strftime("%Y %m %d")}",i[4])
        for row in range(self.dataTable.rowCount()):
            self.dataTable.setRowHeight(row, 80)

    def inButtonClick(self):
        if self.filterState in ["all","out"]:self.filterState = "in"
        else: self.filterState="all"
        self.upadteFilters()

    def outButtonClick(self):
        if self.filterState in ["all","in"]:self.filterState = "out"
        else: self.filterState="all"
        self.upadteFilters()

    def addItem(self,id,name,status_text, status):
        row = self.dataTable.rowCount()
        self.dataTable.insertRow(row)
        self.dataTable.setItem(row, 0, QTableWidgetItem(f"{id}"))
        self.dataTable.setItem(row, 1, QTableWidgetItem(name))
        self.dataTable.setItem(row, 2, QTableWidgetItem(status_text))

        itemWidget = QWidget()
        itemWidgetLayout = QHBoxLayout(itemWidget)
        
        itemWidgetLayout.addStretch()

        if status:statusChangeButton = QPushButton("Lend")
        else:statusChangeButton = QPushButton("Got Back")

        statusChangeButton.setStyleSheet("""
            QPushButton{
                height: 40px;
                padding: 5px;
            }
        """)

        itemWidgetLayout.addWidget(statusChangeButton,alignment=Qt.AlignmentFlag.AlignRight)
        
        editButton = QPushButton("E")
        editButton.setStyleSheet("""
            QPushButton{
                width: 35px;
                height: 40px;
                margin:0px;
            }
        """)
        itemWidgetLayout.addWidget(editButton,alignment=Qt.AlignmentFlag.AlignRight)
        
        deleteButton = QPushButton("X")
        deleteButton.clicked.connect(lambda:self.deleteAction(id))
        deleteButton.setStyleSheet("""
            QPushButton{
                height: 40px;
                width: 35px;
                margin:0px;
            }
        """)
        itemWidgetLayout.addWidget(deleteButton,alignment=Qt.AlignmentFlag.AlignRight)


        self.dataTable.setCellWidget(row, 3, itemWidget)

    def deleteAction(self,dbId):
        dialog = ConfirmationDialog()
        if dialog.exec():
            self.database.delete_item(dbId)
            self.refresh_display()


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
        self.refresh_display()


class ConfirmationDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Are you sure?")
        QBtn = (
            QDialogButtonBox.StandardButton.Yes | QDialogButtonBox.StandardButton.Cancel
        )

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.setStyleSheet("""
        QDialog{
            background-color:#030A1E
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
        QPushButton:hover{background-color:#0B152A;}
        """)

        layout = QVBoxLayout()
        message = QLabel("Are you sure?")
        layout.addWidget(message)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)
