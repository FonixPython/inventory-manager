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
                background-color: transparent;
                color: #f0f6fc;
                gridline-color: transparent;
                font-size: 14px;
                border: none;
                outline: none;
            }
            QTableWidget::item {
                height: 56px;
                background-color: rgba(22, 27, 34, 0.6);
                border: 1px solid rgba(48, 54, 61, 0.4);
                border-left: none;
                border-right: none;
                font-size: 14px;
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: rgba(56, 139, 253, 0.15);
                border: 1px solid rgba(56, 139, 253, 0.3);
            }
            QTableWidget::item:first {
                border-left: 1px solid rgba(48, 54, 61, 0.4);
                border-top-left-radius: 10px;
                border-bottom-left-radius: 10px;
            }
            QTableWidget::item:last {
                border-right: 1px solid rgba(48, 54, 61, 0.4);
                border-top-right-radius: 10px;
                border-bottom-right-radius: 10px;
            }
            QHeaderView::section {
                background-color: rgba(13, 17, 23, 0.8);
                color: #8b949e;
                padding: 12px 8px;
                font-size: 12px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                border: none;
                border-bottom: 1px solid rgba(48, 54, 61, 0.6);
            }
            QHeaderView::section:first {
                border-top-left-radius: 12px;
            }
            QHeaderView::section:last {
                border-top-right-radius: 12px;
            }
            QHeaderView {
                background-color: transparent;
            }
        """)
        
        self.setStyleSheet("""
        QWidget#actionBar {
            background-color: rgba(22, 27, 34, 0.8);
            border-radius: 16px;
            border: 1px solid rgba(48, 54, 61, 0.6);
            padding: 8px;
        }
        #page {
            background-color: #0d1117;
        }
        #searchWidget {
            margin: 0px;
            padding: 0px;
        }
        #searchEntry {
            width: 400px;
        }
        #addEntry {
            width: 200px;
        }
        #addButton {
            width: 140px;
        }
        QLineEdit {
            height: 40px;
            background-color: rgba(13, 17, 23, 0.8);
            border-radius: 10px;
            border: 1px solid rgba(48, 54, 61, 0.6);
            padding: 0 14px;
            margin: 4px;
            font-size: 14px;
            color: #f0f6fc;
        }
        QLineEdit:focus {
            border: 2px solid #58a6ff;
            background-color: rgba(13, 17, 23, 1);
        }
        QLineEdit::placeholder {
            color: #6e7681;
        }
        QLabel {
            margin: 0px;
            padding: 0px;
            color: #8b949e;
            font-size: 14px;
            font-weight: 500;
        }
        QPushButton {
            height: 36px;
            margin: 4px;
            padding: 0 16px;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #21262d, stop:1 #161b22);
            border-radius: 8px;
            border: 1px solid rgba(48, 54, 61, 0.6);
            color: #f0f6fc;
            font-size: 13px;
            font-weight: 500;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #30363d, stop:1 #21262d);
            border-color: rgba(139, 148, 158, 0.4);
        }
        QPushButton:pressed {
            background: #161b22;
        }
        #logoutButton, #refreshButton {
            width: 36px;
            height: 36px;
            background: transparent;
            border: 1px solid rgba(48, 54, 61, 0.6);
            border-radius: 8px;
            padding: 0;
        }
        #logoutButton:hover, #refreshButton:hover {
            background: rgba(48, 54, 61, 0.4);
            border-color: rgba(139, 148, 158, 0.6);
        }
        QScrollBar:vertical {
            background: transparent;
            width: 8px;
            margin: 4px 0 4px 0;
        }
        QScrollBar::handle:vertical {
            background: rgba(139, 148, 158, 0.4);
            border-radius: 4px;
            min-height: 20px;
        }
        QScrollBar::handle:vertical:hover {
            background: rgba(139, 148, 158, 0.6);
        }
        QScrollBar::handle:vertical:pressed {
            background: rgba(139, 148, 158, 0.8);
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
        QPushButton:disabled {
            background: rgba(48, 54, 61, 0.3);
            color: #6e7681;
        }
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
        base_style = """
            height: 28px;
            width: 70px;
            margin: 4px;
            padding: 0 12px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        """
        
        if self.filterState == "all":
            self.inButton.setStyleSheet(f"""
                #inButton{{
                    {base_style}
                    border: 1px solid rgba(35, 134, 54, 0.5);
                    background-color: rgba(35, 134, 54, 0.2);
                    color: #3fb950;
                }}
                #inButton:hover {{
                    background-color: rgba(35, 134, 54, 0.3);
                    border-color: rgba(35, 134, 54, 0.7);
                }}
            """)
            self.outButton.setStyleSheet(f"""
                #outButton{{
                    {base_style}
                    border: 1px solid rgba(248, 81, 73, 0.5);
                    background-color: rgba(248, 81, 73, 0.2);
                    color: #f85149;
                }}
                #outButton:hover {{
                    background-color: rgba(248, 81, 73, 0.3);
                    border-color: rgba(248, 81, 73, 0.7);
                }}
            """)
        if self.filterState == "in":
            self.inButton.setStyleSheet(f"""
                #inButton{{
                    {base_style}
                    border: 1px solid #238636;
                    background-color: #238636;
                    color: #ffffff;
                }}
                #inButton:hover {{
                    background-color: #2ea043;
                    border-color: #2ea043;
                }}
            """)
            self.outButton.setStyleSheet(f"""
                #outButton{{
                    {base_style}
                    border: 1px solid rgba(248, 81, 73, 0.5);
                    background-color: rgba(248, 81, 73, 0.2);
                    color: #f85149;
                }}
                #outButton:hover {{
                    background-color: rgba(248, 81, 73, 0.3);
                    border-color: rgba(248, 81, 73, 0.7);
                }}
            """)
        if self.filterState == "out":
            self.inButton.setStyleSheet(f"""
                #inButton{{
                    {base_style}
                    border: 1px solid rgba(35, 134, 54, 0.5);
                    background-color: rgba(35, 134, 54, 0.2);
                    color: #3fb950;
                }}
                #inButton:hover {{
                    background-color: rgba(35, 134, 54, 0.3);
                    border-color: rgba(35, 134, 54, 0.7);
                }}
            """)
            self.outButton.setStyleSheet(f"""
                #outButton{{
                    {base_style}
                    border: 1px solid #da3633;
                    background-color: #da3633;
                    color: #ffffff;
                }}
                #outButton:hover {{
                    background-color: #f85149;
                    border-color: #f85149;
                }}
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

        self.decisionWidgetLayout.addStretch()
        self.decisionWidgetLayout.addWidget(QLabel("Are you sure?"))

        self.decisionWidget.setStyleSheet("""
        QLabel{
            margin:0px;
            padding:0px;
            color:#D3F2FF;
            font-size:20px;
        }""")

        self.decisionWidgetYesButton = QPushButton(icon=QIcon(resource_path("assets/check.png")))
        self.decisionWidgetLayout.addWidget(self.decisionWidgetYesButton)
        self.decisionWidgetYesButton.setIconSize(QSize(35,35))
        self.decisionWidgetYesButton.setStyleSheet("""
            QPushButton {
                height: 32px;
                width: 32px;
                margin: 2px;
                background-color: rgba(35, 134, 54, 0.2);
                border: 1px solid rgba(35, 134, 54, 0.5);
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: rgba(35, 134, 54, 0.3);
                border-color: rgba(35, 134, 54, 0.7);
            }
        """)
        
        self.decisionWidgetCancelButton = QPushButton(icon=QIcon(resource_path("assets/close.png")))
        self.decisionWidgetLayout.addWidget(self.decisionWidgetCancelButton)
        self.decisionWidgetCancelButton.setIconSize(QSize(35,35))
        self.decisionWidgetCancelButton.clicked.connect(self.cancelAction)
        self.decisionWidgetCancelButton.setStyleSheet("""
            QPushButton {
                height: 32px;
                width: 32px;
                margin: 2px;
                background-color: rgba(248, 81, 73, 0.2);
                border: 1px solid rgba(248, 81, 73, 0.5);
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: rgba(248, 81, 73, 0.3);
                border-color: rgba(248, 81, 73, 0.7);
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
            QPushButton {
                height: 32px;
                width: 32px;
                margin: 2px;
                background-color: rgba(35, 134, 54, 0.2);
                border: 1px solid rgba(35, 134, 54, 0.5);
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: rgba(35, 134, 54, 0.3);
                border-color: rgba(35, 134, 54, 0.7);
            }
        """)
        
        self.typingWidgetCancelButton = QPushButton(icon=QIcon(resource_path("assets/close.png")))
        self.typingWidgetLayout.addWidget(self.typingWidgetCancelButton)
        self.typingWidgetCancelButton.setIconSize(QSize(35,35))
        self.typingWidgetCancelButton.clicked.connect(self.cancelAction)
        self.typingWidgetCancelButton.setStyleSheet("""
            QPushButton {
                height: 32px;
                width: 32px;
                margin: 2px;
                background-color: rgba(248, 81, 73, 0.2);
                border: 1px solid rgba(248, 81, 73, 0.5);
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: rgba(248, 81, 73, 0.3);
                border-color: rgba(248, 81, 73, 0.7);
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
            QPushButton {
                height: 32px;
                padding: 0 16px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1f6feb, stop:1 #1158c7);
                border: none;
                border-radius: 6px;
                color: #ffffff;
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #388bfd, stop:1 #1f6feb);
            }
        """)
        
        self.actionWidgetLayout.addWidget(statusChangeButton,alignment=Qt.AlignmentFlag.AlignRight)
        
        self.editButton = QPushButton(icon=QIcon(resource_path("assets/edit.png")))
        self.editButton.setIconSize(QSize(35,35))
        self.editButton.clicked.connect(self.enterEditMode)
        self.editButton.setStyleSheet("""
            QPushButton {
                width: 32px;
                height: 32px;
                margin: 2px;
                background-color: rgba(139, 148, 158, 0.15);
                border: 1px solid rgba(139, 148, 158, 0.3);
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: rgba(139, 148, 158, 0.25);
                border-color: rgba(139, 148, 158, 0.5);
            }
        """)
        self.actionWidgetLayout.addWidget(self.editButton,alignment=Qt.AlignmentFlag.AlignRight)
        
        self.deleteButton = QPushButton(icon=QIcon(resource_path("assets/delete.png")))
        self.deleteButton.setIconSize(QSize(35,35))
        self.deleteButton.clicked.connect(self.enterDeleteMode)
        self.deleteButton.setStyleSheet("""
            QPushButton {
                width: 32px;
                height: 32px;
                margin: 2px;
                background-color: rgba(248, 81, 73, 0.15);
                border: 1px solid rgba(248, 81, 73, 0.3);
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: rgba(248, 81, 73, 0.25);
                border-color: rgba(248, 81, 73, 0.5);
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
