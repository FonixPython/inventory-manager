from PyQt6.QtWidgets import (QApplication, QMainWindow,QLineEdit,
                             QWidget,QLabel, QPushButton,QHBoxLayout,
                             QVBoxLayout, QTableWidget, QTableWidgetItem,
                              QHeaderView, QAbstractItemView, QDialog,
                              QDialogButtonBox, QInputDialog, QStackedWidget)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIntValidator, QFont, QIcon

from db import Database,check_mysql_connection
import os
import json
import datetime
import sys

def resource_path(relative_path):
    try:base_path = sys._MEIPASS
    except AttributeError:base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class HomePage(QWidget):
    def __init__(self,logoutFunction, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.logoutFunction = logoutFunction
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

        self.searchWidgetLayout.addStretch()

        self.refreshButton = QPushButton(icon=QIcon(resource_path("assets/refresh.png")))
        self.refreshButton.clicked.connect(self.refresh_display)
        self.refreshButton.setIconSize(QSize(35,35))
        self.refreshButton.setObjectName("refreshButton")
        self.searchWidgetLayout.addWidget(self.refreshButton, alignment=Qt.AlignmentFlag.AlignRight)
        
        self.logoutButton = QPushButton(icon=QIcon(resource_path("assets/logout.png")))
        self.logoutButton.clicked.connect(self.logOutAction)
        self.logoutButton.setIconSize(QSize(35,35))
        self.logoutButton.setObjectName("logoutButton")
        self.searchWidgetLayout.addWidget(self.logoutButton, alignment=Qt.AlignmentFlag.AlignRight)


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
        self.dataTable.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.dataTable.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.dataTable.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.dataTable.verticalHeader().setVisible(False)
        self.dataTable.setColumnCount(4)
        self.dataTable.setHorizontalHeaderLabels(["#","Name","Status","Actions"])
        header = self.dataTable.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.dataTable.setColumnWidth(0,40)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.dataTable.setColumnWidth(3,400)

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
        #logoutButton{
            width:40px;
            height:40px;
            background-color:#0B152A;
        }
        #logoutButton:hover{
            background-color:#030A1E;
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
        if self.database == None:
            self.connectToSaved()
        results = self.database.get_items(search_query=None if self.searchEntry.text() == "" else self.searchEntry.text(),filter=None if self.filterState == "all" else self.filterState.upper())
        self.dataTable.setRowCount(0)
        for i in results:
            self.addItem(i)
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

    def addItem(self,i):
        row = self.dataTable.rowCount()
        statusText = f"{"Lent to" if i[4] == 0 else "Here"} {"" if i[2] is None else str(i[2])+" on "+ i[3].strftime("%Y %m %d")}"
        self.dataTable.insertRow(row)
        idItem = QTableWidgetItem(f"{i[0]}")
        idItem.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dataTable.setItem(row, 0, idItem)
        nameItem = QTableWidgetItem(i[1])
        nameItem.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dataTable.setItem(row, 1, nameItem)
        statusItem = QTableWidgetItem(statusText)
        statusItem.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dataTable.setItem(row, 2, statusItem)

        self.dataTable.setCellWidget(row, 3, ItemActionWidget(itemId=i[0],itemStatus=i[4],itemName=i[1],refreshAction=self.refresh_display,databasePointer=self.database))
        
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

    def logOutAction(self):
        if self.database:
            self.database.conn.close()
            self.database = None
        self.logoutFunction()

class ItemActionWidget(QStackedWidget):
    def __init__(self,itemId,itemStatus,itemName,refreshAction,databasePointer):
        super().__init__()
        self.itemId = itemId
        self.itemStatus = itemStatus
        self.itemName = itemName
        self.refreshAction = refreshAction
        self.databasePointer = databasePointer

        # Decision widget section

        self.decisionWidget = QWidget()
        self.decisionWidgetLayout = QHBoxLayout(self.decisionWidget)
        self.addWidget(self.decisionWidget)

        self.decisionWidgetYesButton = QPushButton(icon=QIcon(resource_path("assets/check.png")))
        self.decisionWidgetLayout.addWidget(self.decisionWidgetYesButton)
        self.decisionWidgetYesButton.setIconSize(QSize(35,35))
        self.decisionWidgetYesButton.setStyleSheet("""
            QPushButton{
                height: 40px;
                margin:0px;
            }
        """)
        
        self.decisionWidgetCancelButton = QPushButton(icon=QIcon(resource_path("assets/close.png")))
        self.decisionWidgetLayout.addWidget(self.decisionWidgetCancelButton)
        self.decisionWidgetCancelButton.setIconSize(QSize(35,35))
        self.decisionWidgetCancelButton.clicked.connect(self.cancelAction)
        self.decisionWidgetCancelButton.setStyleSheet("""
            QPushButton{
                height: 40px;
                margin:0px;
            }
        """)

        self.addWidget(self.decisionWidget)


        # Typing widget section
        self.typingWidget = QWidget()
        self.typingWidgetLayout = QHBoxLayout(self.typingWidget)
        
        self.typingWidgetEntry = QLineEdit()
        self.typingWidgetLayout.addWidget(self.typingWidgetEntry)

        self.typingWidgetYesButton = QPushButton(icon=QIcon(resource_path("assets/check.png")))
        self.typingWidgetLayout.addWidget(self.typingWidgetYesButton)
        self.typingWidgetYesButton.setIconSize(QSize(35,35))
        self.typingWidgetYesButton.setStyleSheet("""
            QPushButton{
                height: 40px;
                width: 35px;
                margin:0px;
            }
        """)
        
        self.typingWidgetCancelButton = QPushButton(icon=QIcon(resource_path("assets/close.png")))
        self.typingWidgetLayout.addWidget(self.typingWidgetCancelButton)
        self.typingWidgetCancelButton.setIconSize(QSize(35,35))
        self.typingWidgetCancelButton.clicked.connect(self.cancelAction)
        self.typingWidgetCancelButton.setStyleSheet("""
            QPushButton{
                height: 40px;
                width: 35px;
                margin:0px;
            }
        """)

        self.addWidget(self.typingWidget)


        # Action choosing widget section

        self.actionWidget = QWidget()
        self.actionWidgetLayout = QHBoxLayout(self.actionWidget)
        self.actionWidgetLayout.addStretch()

        if itemStatus:
            statusChangeButton = QPushButton("Lend")
            statusChangeButton.clicked.connect(self.enterLendMode)
        else:
            statusChangeButton = QPushButton("Got Back")
            statusChangeButton.clicked.connect(self.enterGotBackMode)
        statusChangeButton.setStyleSheet("""
            QPushButton{
                height: 40px;
                padding: 5px;
            }
        """)
        
        self.actionWidgetLayout.addWidget(statusChangeButton,alignment=Qt.AlignmentFlag.AlignRight)
        
        self.editButton = QPushButton(icon=QIcon(resource_path("assets/edit.png")))
        self.editButton.setIconSize(QSize(35,35))
        self.editButton.clicked.connect(self.enterEditMode)
        self.editButton.setStyleSheet("""
            QPushButton{
                width: 35px;
                height: 40px;
                margin:0px;
            }
        """)
        self.actionWidgetLayout.addWidget(self.editButton,alignment=Qt.AlignmentFlag.AlignRight)
        
        self.deleteButton = QPushButton(icon=QIcon(resource_path("assets/delete.png")))
        self.deleteButton.setIconSize(QSize(35,35))
        self.deleteButton.clicked.connect(self.enterDeleteMode)
        self.deleteButton.setStyleSheet("""
            QPushButton{
                height: 40px;
                width: 35px;
                margin:0px;
            }
        """)
        self.actionWidgetLayout.addWidget(self.deleteButton,alignment=Qt.AlignmentFlag.AlignRight)
        self.addWidget(self.actionWidget)
        # Default page

        self.setCurrentIndex(2)
    
    def enterDeleteMode(self):
        self.setCurrentIndex(0)
        self.decisionWidgetYesButton.clicked.connect(self.deleteItem)
    
    def deleteItem(self):
        self.databasePointer.delete_item(self.itemId)
        self.refreshAction()
    
    def enterLendMode(self):
        self.setCurrentIndex(1)
        self.typingWidgetEntry.setText("")
        self.typingWidgetEntry.setPlaceholderText("Who is it being lent to?")
        self.typingWidgetEntry.setFocus()
        self.typingWidgetEntry.editingFinished.connect(self.lendItem)
        self.typingWidgetYesButton.clicked.connect(self.lendItem)
    
    def lendItem(self):
        if self.typingWidgetEntry.text() != "":
            self.databasePointer.lend(self.itemId,self.typingWidgetEntry.text())
            self.refreshAction()
        else: self.cancelAction()
    def enterEditMode(self):
        self.setCurrentIndex(1)
        self.typingWidgetEntry.setPlaceholderText("Type new item name")
        self.typingWidgetEntry.setText(self.itemName)
        self.typingWidgetEntry.setFocus()
        self.typingWidgetEntry.editingFinished.connect(self.saveNewName)
        self.typingWidgetYesButton.clicked.connect(self.saveNewName)

    def saveNewName(self):
        if self.typingWidgetEntry.text() != "":
            self.databasePointer.edit_item(self.itemId,self.typingWidgetEntry.text())
            self.refreshAction()

    def enterGotBackMode(self):
        self.setCurrentIndex(0)
        self.decisionWidgetYesButton.clicked.connect(self.gotBack)

    def gotBack(self):
        self.databasePointer.got_back(self.itemId)
        self.refreshAction()
        
    def cancelAction(self):
        self.setCurrentIndex(2)
