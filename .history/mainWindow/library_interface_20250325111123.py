# coding:utf-8
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QWidget, QTableWidgetItem, QSizePolicy, QHeaderView

from qfluentwidgets import TableWidget


class LibraryInterface(QWidget):
    """ ����� - ���������ͼ��������ʾ��������ʷ��¼ """

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
        self.setObjectName('Library-Interface')
    
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