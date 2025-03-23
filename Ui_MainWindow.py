# Form implementation generated from reading ui file 'c:\Users\17657\Desktop\Bupt\人工智能\五子棋\Ui_MainWindow.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets
from Ui_Panel import Ui_Form as Ui_Panel
from Ui_History import Ui_Form as Ui_History


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(881, 618)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.pushButton = QtWidgets.QPushButton(parent=self.centralwidget)
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout.addWidget(self.pushButton)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.pushButton_2 = QtWidgets.QPushButton(parent=self.centralwidget)
        self.pushButton_2.setObjectName("pushButton_2")
        self.verticalLayout.addWidget(self.pushButton_2)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)
        self.listWidget = QtWidgets.QListWidget(parent=self.centralwidget)
        self.listWidget.setObjectName("listWidget")
        self.gridLayout.addWidget(self.listWidget, 0, 1, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 881, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.panel = QtWidgets.QWidget(parent=self.centralwidget)
        self.panel_ui = Ui_Panel()
        self.panel_ui.setupUi(self.panel)
        self.gridLayout.addWidget(self.panel, 0, 1, 1, 1)

        self.history = QtWidgets.QWidget(parent=self.centralwidget)
        self.history_ui = Ui_History()
        self.history_ui.setupUi(self.history)
        self.history.hide()
        self.gridLayout.addWidget(self.history, 0, 1, 1, 1)

        self.pushButton.clicked.connect(self.show_panel)
        self.pushButton_2.clicked.connect(self.show_history)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def show_panel(self):
        self.history.hide()
        self.panel.show()

    def show_history(self):
        self.panel.hide()
        self.history.show()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton.setText(_translate("MainWindow", "开始"))
        self.pushButton_2.setText(_translate("MainWindow", "历史"))
