# coding:utf-8
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QWidget
from PyQt5.QtGui import QFont

from qfluentwidgets import PrimaryPushButton, PushButton, HorizontalFlipView, HorizontalPipsPager


class HomeInterface(QWidget):
    """ ��ҳ���� - �ɶ��Ƶ���ҳ """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.mainLayout = QVBoxLayout(self)
        
        # ����һ�������ǩ
        self.titleLabel = QLabel("��������Ϸ", self)
        self.titleLabel.setAlignment(Qt.AlignCenter)
        font = self.titleLabel.font()
        font.setPointSize(24)
        font.setBold(True)
        self.titleLabel.setFont(font)
        
        # ������Ϸ���ܱ�ǩ
        self.introLabel = QLabel(
            "��ӭ������������Ϸ��\n"
            "��������һ�����˶��ĵĴ�������������Ϸ��ͨ�����ӷ�Ϊ�ڰ���ɫ��\n"
            "��Ϸ����˫�������������Ϸ����Լ������ӣ����γ����������߻�ʤ��"
        )
        self.introLabel.setAlignment(Qt.AlignCenter)
        self.introLabel.setWordWrap(True)
        introFont = self.introLabel.font()
        introFont.setPointSize(12)
        self.introLabel.setFont(introFont)
        
        # �������̷��ѡ������
        self.boardStyleWidget = QWidget()
        self.boardStyleLayout = QVBoxLayout(self.boardStyleWidget)
        
        # ���̷�����
        self.boardStyleTitle = QLabel("ѡ�����̷��")
        boardStyleFont = self.boardStyleTitle.font()
        boardStyleFont.setPointSize(16)
        boardStyleFont.setBold(True)
        self.boardStyleTitle.setFont(boardStyleFont)
        self.boardStyleTitle.setAlignment(Qt.AlignCenter)
        
        # ����FlipView����չʾ���̷��
        self.flipViewWidget = QWidget()
        self.flipViewLayout = QVBoxLayout(self.flipViewWidget)
        
        # ��ʼ��FlipView��Pager
        self.flipView = HorizontalFlipView(self)
        self.pager = HorizontalPipsPager(self)
        
        # ����FlipView������
        self.flipView.setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatio)
        self.flipView.setFixedHeight(200)  # ����һ�����ʵĸ߶�
        
        # ������̷��ͼƬ (����ͼƬ����Щ·��)
        boardStyles = [
            "c:/Users/17657/Desktop/Bupt/�˹�����/������/resource/board_style1.png",
            "c:/Users/17657/Desktop/Bupt/�˹�����/������/resource/board_style2.png",
            "c:/Users/17657/Desktop/Bupt/�˹�����/������/resource/board_style3.png"
        ]
        
        # �������ͼƬ�����·������������ʾ��ʾ
        try:
            self.flipView.addImages(boardStyles)
            self.pager.setPageNumber(self.flipView.count())
            
            # ���ӷ�ҳ�¼�
            self.pager.currentIndexChanged.connect(self.flipView.setCurrentIndex)
            self.flipView.currentIndexChanged.connect(self.pager.setCurrentIndex)
        except Exception as e:
            errorLabel = QLabel(f"�޷��������̷��ͼƬ����ȷ��ͼƬ·����ȷ��\n�����Խ�����ͼƬ������resource�ļ����С�")
            errorLabel.setAlignment(Qt.AlignCenter)
            errorLabel.setWordWrap(True)
            self.flipViewLayout.addWidget(errorLabel)
        
        # ���FlipView��Pager������
        self.flipViewLayout.addWidget(self.flipView, 0, Qt.AlignCenter)
        self.flipViewLayout.addWidget(self.pager, 0, Qt.AlignCenter)
        self.flipViewLayout.setSpacing(10)
        
        # ���ȷ�ϰ�ť
        self.confirmButtonWidget = QWidget()
        self.confirmButtonLayout = QHBoxLayout(self.confirmButtonWidget)
        
        self.confirmButton = PushButton("ȷ��ѡ��", self)
        self.confirmButton.setFixedWidth(150)
        
        self.confirmButtonLayout.addStretch(1)
        self.confirmButtonLayout.addWidget(self.confirmButton)
        self.confirmButtonLayout.addStretch(1)
        
        # �����ѡ�������ӵ�����
        self.boardStyleLayout.addWidget(self.boardStyleTitle)
        self.boardStyleLayout.addWidget(self.flipViewWidget)
        self.boardStyleLayout.addWidget(self.confirmButtonWidget)
        
        # ������ť����
        self.buttonWidget = QWidget()
        self.buttonLayout = QHBoxLayout(self.buttonWidget)
        
        # ��Ӱ�ť����ʼ��Ϸ���鿴��ʷ��
        self.startGameBtn = PrimaryPushButton("��ʼ��Ϸ")
        self.startGameBtn.setFixedWidth(180)
        self.startGameBtn.setFixedHeight(40)
        
        self.historyBtn = PushButton("�鿴��ʷ��¼")
        self.historyBtn.setFixedWidth(180)
        self.historyBtn.setFixedHeight(40)
        
        # ����ť��ӵ�������
        self.buttonLayout.addStretch(1)
        self.buttonLayout.addWidget(self.startGameBtn)
        self.buttonLayout.addSpacing(20)
        self.buttonLayout.addWidget(self.historyBtn)
        self.buttonLayout.addStretch(1)
        
        # ���������Ϸ����
        self.recentGamesWidget = QWidget()
        self.recentGamesLayout = QVBoxLayout(self.recentGamesWidget)
        
        # �����Ϸ����
        self.recentTitle = QLabel("�����Ϸ")
        recentTitleFont = self.recentTitle.font()
        recentTitleFont.setPointSize(16)
        recentTitleFont.setBold(True)
        self.recentTitle.setFont(recentTitleFont)
        self.recentTitle.setAlignment(Qt.AlignCenter)
        
        # �����Ϸ����
        self.recentGamesContent = QWidget()
        self.recentGamesContentLayout = QVBoxLayout(self.recentGamesContent)
        
        # ���һЩʾ���������Ϸ��¼
        recentGames = [
            "����ʤ - С�� vs С�� (2023-11-10 14:30)",
            "����ʤ - С�� vs С�� (2023-11-09 10:00)",
            "����ʤ - ���� vs ���� (2023-11-08 17:10)"
        ]
        
        for game in recentGames:
            gameLabel = QLabel(game)
            gameLabel.setAlignment(Qt.AlignCenter)
            self.recentGamesContentLayout.addWidget(gameLabel)
        
        # �������Ϸ�����������ӵ������Ϸ����
        self.recentGamesLayout.addWidget(self.recentTitle)
        self.recentGamesLayout.addWidget(self.recentGamesContent)
        
        # �������岼��
        self.mainLayout.addWidget(self.titleLabel)
        self.mainLayout.addSpacing(10)
        self.mainLayout.addWidget(self.introLabel)
        self.mainLayout.addSpacing(20)
        self.mainLayout.addWidget(self.boardStyleWidget)  # ������̷��ѡ������
        self.mainLayout.addSpacing(20)
        self.mainLayout.addWidget(self.buttonWidget)
        self.mainLayout.addSpacing(20)
        self.mainLayout.addWidget(self.recentGamesWidget)
        
        # ���ñ߾�ͼ��
        self.mainLayout.setContentsMargins(40, 40, 40, 40)
        
        # ���ö�����
        self.setObjectName('Home-Interface')
        
        # �����źźͲ�
        self.connectSignalsToSlots()
    
    def connectSignalsToSlots(self):
        """�����źźͲ�"""
        # ���Ӱ�ť����¼�
        self.historyBtn.clicked.connect(self.onHistoryBtnClicked)
        self.startGameBtn.clicked.connect(self.onStartGameBtnClicked)
        self.confirmButton.clicked.connect(self.onConfirmButtonClicked)
    
    def onHistoryBtnClicked(self):
        """�鿴��ʷ��¼��ť����¼�"""
        # �л�����ҳ����ʾ��ʷ��¼
        parent = self.parent()
        if parent and hasattr(parent, 'libraryInterface'):
            parent.switchTo(parent.libraryInterface)
    
    def onStartGameBtnClicked(self):
        """��ʼ��Ϸ��ť����¼�"""
        # �л�����Ϸҳ��
        parent = self.parent()
        if parent and hasattr(parent, 'appInterface'):
            parent.switchTo(parent.appInterface)
            
    def onConfirmButtonClicked(self):
        """ȷ�����̷��ѡ��ť����¼�"""
        # ��ȡ��ǰѡ��ķ������
        currentStyleIndex = self.flipView.currentIndex()
        # ������Ա����û���ѡ�񣬻��߽�����������
        print(f"�û�ѡ���˷������: {currentStyleIndex}")