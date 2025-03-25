# coding:utf-8
from PyQt5.QtCore import Qt, pyqtSignal, QEasingCurve
from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QFrame, QWidget, QTableWidgetItem, QSizePolicy, QHeaderView

from qfluentwidgets import PopUpAniStackedWidget, TableWidget


class Widget(QWidget):
    """ ����ͨ�ý��� """

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.label = QLabel(text, self)
        self.label.setAlignment(Qt.AlignCenter)
        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.addWidget(self.label, 1, Qt.AlignCenter)
        self.setObjectName(text.replace(' ', '-'))


class AppInterface(QWidget):
    """ Ӧ�ý��� - ���������ͼ��������ʾ��������ʷ��¼ """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.hBoxLayout = QHBoxLayout(self)
        self.tableView = TableWidget(self)

        # ���ñ��߿�
        self.tableView.setBorderVisible(True)
        self.tableView.setBorderRadius(8)
        self.tableView.setWordWrap(False)

        # ���ñ������
        self.setupTable()
        
        # ��ȫ�����߾�ʹ���������Χ
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout.addWidget(self.tableView)
        
        # �ñ��������п��ÿռ�
        self.tableView.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # ���ö����������ڵ���
        self.setObjectName('Application-Interface')
    
    def setupTable(self):
        """ ���ñ������Ϊ��������ʷ��¼ """
        # ����4�У���ţ�ʱ�䣬ʤ��������Ծ�
        self.tableView.setColumnCount(4)
        
        # ʾ����ʷ����
        gameHistory = [
            ['1', '2023-11-01 15:30', '����ʤ', '���壺С�� vs ���壺С��'],
            ['2', '2023-11-02 10:15', '����ʤ', '���壺С�� vs ���壺С��'],
            ['3', '2023-11-03 14:20', '����ʤ', '���壺С�� vs ���壺С��'],
            ['4', '2023-11-04 16:45', '����ʤ', '���壺���� vs ���壺����'],
            ['5', '2023-11-05 09:30', '����', '���壺���� vs ���壺����'],
            ['6', '2023-11-06 11:20', '����ʤ', '���壺��һ vs ���壺�¶�'],
            ['7', '2023-11-07 13:40', '����ʤ', '���壺���� vs ���壺����'],
            ['8', '2023-11-08 17:10', '����ʤ', '���壺���� vs ���壺����'],
            ['9', '2023-11-09 10:00', '����ʤ', '���壺С�� vs ���壺С��'],
            ['10', '2023-11-10 14:30', '����ʤ', '���壺С�� vs ���壺С��'],
        ]
        
        # �����㹻������
        self.tableView.setRowCount(len(gameHistory))
        
        # �����
        for i, game in enumerate(gameHistory):
            for j in range(4):
                item = QTableWidgetItem(game[j])
                # ʹ��ź�ʱ���о��ж���
                if j <= 1:
                    item.setTextAlignment(Qt.AlignCenter)
                self.tableView.setItem(i, j, item)
        
        # ���ñ�ͷ
        self.tableView.verticalHeader().hide()
        self.tableView.setHorizontalHeaderLabels(['���', 'ʱ��', 'ʤ��', '����Ծ�'])
        
        # ��ȡ����ˮƽ��ͷ
        header = self.tableView.horizontalHeader()
        
        # �����п� - ��������н�խ������Ծ��нϿ�
        self.tableView.setColumnWidth(0, 60)   # ����п�
        self.tableView.setColumnWidth(1, 150)  # ʱ���п�
        self.tableView.setColumnWidth(2, 100)  # ʤ���п�
        
        # �̶�ǰ���еĿ�ȣ��������û�����
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # ����й̶�
        header.setSectionResizeMode(1, QHeaderView.Fixed)  # ʱ���й̶�
        header.setSectionResizeMode(2, QHeaderView.Fixed)  # ʤ���й̶�
        
        # �������һ���Զ���չ�����ʣ��ռ�
        header.setSectionResizeMode(3, QHeaderView.Stretch)  # ����Ծ�������Ӧʣ����

        # ���ñ���ѡ������
        self.tableView.setSelectionBehavior(TableWidget.SelectRows)


class StackedWidget(QFrame):
    """ �ѵ�ʽ������� """

    currentChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.hBoxLayout = QHBoxLayout(self)
        self.view = PopUpAniStackedWidget(self)

        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout.addWidget(self.view)

        self.view.currentChanged.connect(self.currentChanged)

    def addWidget(self, widget):
        """ add widget to view """
        self.view.addWidget(widget)

    def widget(self, index: int):
        return self.view.widget(index)

    def setCurrentWidget(self, widget, popOut=False):
        if not popOut:
            self.view.setCurrentWidget(widget, duration=300)
        else:
            self.view.setCurrentWidget(
                widget, True, False, 200, QEasingCurve.InQuad)

    def setCurrentIndex(self, index, popOut=False):
        self.setCurrentWidget(self.view.widget(index), popOut)
