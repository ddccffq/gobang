# coding:utf-8
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QWidget, QFrame, QGridLayout
from PyQt5.QtGui import QFont, QPainter, QPen, QBrush, QColor

from qfluentwidgets import PushButton, RadioButton, ComboBox, RoundMenu, FluentIcon as FIF

class GameInterface(QWidget):
    """ ��Ϸ���� - ��������Ϸ������ """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.mainLayout = QHBoxLayout(self)
        
        # ��Ϸ���� - ���
        self.gameArea = QFrame(self)
        self.gameArea.setFrameShape(QFrame.StyledPanel)
        self.gameAreaLayout = QVBoxLayout(self.gameArea)
        
        # ����
        self.boardWidget = ChessBoardWidget(self)
        self.boardWidget.setSizePolicy(QWidget.Policy.Expanding, QWidget.Policy.Expanding)
        
        # ��Ϸ��Ϣ
        self.gameInfoWidget = QWidget(self)
        self.gameInfoLayout = QHBoxLayout(self.gameInfoWidget)
        
        self.currentPlayerLabel = QLabel("��ǰ: ����", self)
        self.currentPlayerLabel.setFont(QFont("΢���ź�", 12, QFont.Bold))
        
        self.timeLimitLabel = QLabel("ʣ��ʱ��: 30��", self)
        self.timeLimitLabel.setFont(QFont("΢���ź�", 12))
        
        self.gameInfoLayout.addWidget(self.currentPlayerLabel)
        self.gameInfoLayout.addStretch(1)
        self.gameInfoLayout.addWidget(self.timeLimitLabel)
        
        # �������ӵ���Ϸ���򲼾�
        self.gameAreaLayout.addWidget(self.boardWidget)
        self.gameAreaLayout.addWidget(self.gameInfoWidget)
        
        # �������� - �Ҳ�
        self.controlArea = QFrame(self)
        self.controlArea.setFrameShape(QFrame.StyledPanel)
        self.controlArea.setFixedWidth(200)
        self.controlAreaLayout = QVBoxLayout(self.controlArea)
        
        # ��Ϸ����
        self.gameControlLabel = QLabel("��Ϸ����", self)
        self.gameControlLabel.setFont(QFont("΢���ź�", 14, QFont.Bold))
        self.gameControlLabel.setAlignment(Qt.AlignCenter)
        
        # ��ť
        self.startButton = PushButton("��ʼ��Ϸ", self)
        self.restartButton = PushButton("���¿�ʼ", self)
        self.undoButton = PushButton("����", self)
        self.surrenderButton = PushButton("����", self)
        
        # ��Ϸ����
        self.settingsLabel = QLabel("��Ϸ����", self)
        self.settingsLabel.setFont(QFont("΢���ź�", 14, QFont.Bold))
        self.settingsLabel.setAlignment(Qt.AlignCenter)
        
        # ����ѡ��
        self.opponentWidget = QWidget(self)
        self.opponentLayout = QVBoxLayout(self.opponentWidget)
        
        self.opponentLabel = QLabel("ѡ�����:", self)
        self.opponentLabel.setFont(QFont("΢���ź�", 12))
        
        self.humanRadio = RadioButton("�������", self)
        self.aiRadio = RadioButton("AI ����", self)
        self.humanRadio.setChecked(True)
        
        self.opponentLayout.addWidget(self.opponentLabel)
        self.opponentLayout.addWidget(self.humanRadio)
        self.opponentLayout.addWidget(self.aiRadio)
        
        # AI �Ѷ�ѡ��
        self.difficultyWidget = QWidget(self)
        self.difficultyLayout = QVBoxLayout(self.difficultyWidget)
        
        self.difficultyLabel = QLabel("AI �Ѷ�:", self)
        self.difficultyLabel.setFont(QFont("΢���ź�", 12))
        
        self.difficultyCombo = ComboBox(self)
        self.difficultyCombo.addItems(["��", "�е�", "����"])
        self.difficultyCombo.setCurrentIndex(1)  # Ĭ���е��Ѷ�
        
        self.difficultyLayout.addWidget(self.difficultyLabel)
        self.difficultyLayout.addWidget(self.difficultyCombo)
        
        # �����������ӵ��������򲼾�
        self.controlAreaLayout.addWidget(self.gameControlLabel)
        self.controlAreaLayout.addWidget(self.startButton)
        self.controlAreaLayout.addWidget(self.restartButton)
        self.controlAreaLayout.addWidget(self.undoButton)
        self.controlAreaLayout.addWidget(self.surrenderButton)
        self.controlAreaLayout.addSpacing(20)
        self.controlAreaLayout.addWidget(self.settingsLabel)
        self.controlAreaLayout.addWidget(self.opponentWidget)
        self.controlAreaLayout.addWidget(self.difficultyWidget)
        self.controlAreaLayout.addStretch(1)
        
        # ��������Ҫ������ӵ�������
        self.mainLayout.addWidget(self.gameArea, 1)
        self.mainLayout.addWidget(self.controlArea)
        
        # ���ü��
        self.mainLayout.setContentsMargins(10, 10, 10, 10)
        self.mainLayout.setSpacing(10)
        
        # ���ö�����
        self.setObjectName('Game-Interface')
        
        # �����źźͲ�
        self.connectSignalsToSlots()
        
        # ��ʼ������
        self.updateDifficultyVisibility()
    
    def connectSignalsToSlots(self):
        """�����źźͲ�"""
        self.aiRadio.toggled.connect(self.updateDifficultyVisibility)
        self.humanRadio.toggled.connect(self.updateDifficultyVisibility)
        
        self.startButton.clicked.connect(self.onStartButtonClicked)
        self.restartButton.clicked.connect(self.onRestartButtonClicked)
        self.undoButton.clicked.connect(self.onUndoButtonClicked)
        self.surrenderButton.clicked.connect(self.onSurrenderButtonClicked)
    
    def updateDifficultyVisibility(self):
        """���ݶ���ѡ������Ѷ�ѡ��Ŀɼ���"""
        self.difficultyWidget.setVisible(self.aiRadio.isChecked())
    
    def onStartButtonClicked(self):
        """��ʼ��Ϸ��ť����¼�"""
        print("��ʼ��Ϸ")
        # ������ʵ����Ϸ��ʼ�߼�
    
    def onRestartButtonClicked(self):
        """���¿�ʼ��ť����¼�"""
        print("���¿�ʼ��Ϸ")
        # ������ʵ�����¿�ʼ��Ϸ�߼�
    
    def onUndoButtonClicked(self):
        """���尴ť����¼�"""
        print("����")
        # ������ʵ�ֻ����߼�
    
    def onSurrenderButtonClicked(self):
        """���䰴ť����¼�"""
        print("����")
        # ������ʵ�������߼�

class ChessBoardWidget(QWidget):
    """���̿ؼ�"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 400)
        self.boardSize = 15  # 15��15������
        self.board = [[0 for _ in range(self.boardSize)] for _ in range(self.boardSize)]
        self.currentPlayer = 1  # 1��ʾ���壬2��ʾ����
        self.gameStarted = False
        
    def paintEvent(self, event):
        """�������̺�����"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # �������̸��Ӵ�С
        cellSize = min(self.width(), self.height()) / (self.boardSize + 1)
        margin = cellSize
        
        # �������̱���
        painter.fillRect(self.rect(), QColor(240, 217, 181))  # ľɫ����
        
        # ����������
        pen = QPen(QColor(0, 0, 0))
        pen.setWidth(1)
        painter.setPen(pen)
        
        for i in range(self.boardSize):
            # ����
            painter.drawLine(
                margin, margin + i * cellSize,
                margin + (self.boardSize - 1) * cellSize, margin + i * cellSize
            )
            # ����
            painter.drawLine(
                margin + i * cellSize, margin,
                margin + i * cellSize, margin + (self.boardSize - 1) * cellSize
            )
        
        # �����������ĺ���λ
        starPoints = [(3, 3), (3, 11), (7, 7), (11, 3), (11, 11)]
        pen.setWidth(3)
        painter.setPen(pen)
        
        for x, y in starPoints:
            painter.drawPoint(margin + x * cellSize, margin + y * cellSize)
        
        # ��������
        for i in range(self.boardSize):
            for j in range(self.boardSize):
                if self.board[i][j] == 1:  # ����
                    painter.setBrush(QBrush(QColor(0, 0, 0)))
                    painter.drawEllipse(
                        margin + i * cellSize - cellSize * 0.4,
                        margin + j * cellSize - cellSize * 0.4,
                        cellSize * 0.8, cellSize * 0.8
                    )
                elif self.board[i][j] == 2:  # ����
                    painter.setBrush(QBrush(QColor(255, 255, 255)))
                    painter.drawEllipse(
                        margin + i * cellSize - cellSize * 0.4,
                        margin + j * cellSize - cellSize * 0.4,
                        cellSize * 0.8, cellSize * 0.8
                    )
    
    def mousePressEvent(self, event):
        """����������¼�"""
        if not self.gameStarted:
            return
            
        # �������̸��Ӵ�С
        cellSize = min(self.width(), self.height()) / (self.boardSize + 1)
        margin = cellSize
        
        # ��������λ�ö�Ӧ����������
        x = round((event.x() - margin) / cellSize)
        y = round((event.y() - margin) / cellSize)
        
        # ����Ƿ�����Ч��Χ��
        if 0 <= x < self.boardSize and 0 <= y < self.boardSize and self.board[x][y] == 0:
            # ��������
            self.board[x][y] = self.currentPlayer
            
            # �л����
            self.currentPlayer = 3 - self.currentPlayer  # 1��2��2��1
            
            # ����������ʾ
            self.update()
            
            # ֪ͨ��������µ�ǰ�����Ϣ
            if self.parent() and hasattr(self.parent(), 'currentPlayerLabel'):
                playerText = "����" if self.currentPlayer == 1 else "����"
                self.parent().currentPlayerLabel.setText(f"��ǰ: {playerText}")
            
            # TODO: �����Ϸ�Ƿ������ʤ��������
