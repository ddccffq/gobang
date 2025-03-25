# coding:utf-8
import sys
import os
from PyQt5.QtCore import Qt, QPoint, QSize, pyqtSignal
from PyQt5.QtGui import QPainter, QBrush, QPen, QColor, QFont, QIcon, QPalette
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QPushButton, QMessageBox,
                           QButtonGroup, QRadioButton, QFrame, QGridLayout)

from qfluentwidgets import (PrimaryPushButton, PushButton, MessageBox, 
                          TextEdit, TitleBar, FluentIcon as FIF,
                          InfoBar, InfoBarPosition)
from qframelesswindow import FramelessWindow

# ������Ϸ�߼�
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "game"))
from game_logic import GomokuGame


class BoardWidget(QWidget):
    """���̿ؼ�"""
    
    # �����ź�
    stone_placed = pyqtSignal(int, int, int)  # ��, ��, ���
    
    def __init__(self, parent=None, board_size=15, cell_size=30):
        super().__init__(parent)
        self.board_size = board_size
        self.cell_size = cell_size
        self.padding = 20  # ���̱�Ե���
        
        # �������̴�С
        board_width = board_size * cell_size + 2 * self.padding
        board_height = board_size * cell_size + 2 * self.padding
        self.setMinimumSize(board_width, board_height)
        
        # ��ʼ������
        self.board_data = [[0 for _ in range(board_size)] for _ in range(board_size)]
        self.hover_pos = None  # �����ͣλ��
        
        # ���ñ���ɫΪ���̵�ɫ
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(210, 180, 140))  # ���̵�ɫ
        self.setPalette(palette)
        
        # ���������٣��Ա������ʾ��ͣЧ��
        self.setMouseTracking(True)
    
    def paintEvent(self, event):
        """�������̺�����"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)  # �����
        
        # �������̸�
        self.draw_board_grid(painter)
        
        # ������Ԫ����λ
        self.draw_star_points(painter)
        
        # ��������
        self.draw_stones(painter)
        
        # ���������ͣЧ��
        if self.hover_pos:
            self.draw_hover_effect(painter)
    
    def draw_board_grid(self, painter):
        """�������̸���"""
        grid_pen = QPen(QColor(0, 0, 0), 1)
        painter.setPen(grid_pen)
        
        # ���ƺ��ߺ�����
        for i in range(self.board_size):
            # ����
            start_x = self.padding
            start_y = self.padding + i * self.cell_size
            end_x = self.padding + (self.board_size - 1) * self.cell_size
            end_y = start_y
            painter.drawLine(start_x, start_y, end_x, end_y)
            
            # ����
            start_x = self.padding + i * self.cell_size
            start_y = self.padding
            end_x = start_x
            end_y = self.padding + (self.board_size - 1) * self.cell_size
            painter.drawLine(start_x, start_y, end_x, end_y)
    
    def draw_star_points(self, painter):
        """������Ԫ����λ"""
        star_brush = QBrush(QColor(0, 0, 0))
        painter.setBrush(star_brush)
        
        # ��Ԫ(��������)
        center = self.board_size // 2
        center_x = self.padding + center * self.cell_size
        center_y = self.padding + center * self.cell_size
        painter.drawEllipse(QPoint(center_x, center_y), 3, 3)
        
        # ��λ(�������̴�Сȷ��)
        if self.board_size >= 15:  # ��׼19·��15·����
            star_positions = [3, self.board_size - 4]  # ����λ��
            for x in star_positions:
                for y in star_positions:
                    # �Ľ���λ
                    pos_x = self.padding + x * self.cell_size
                    pos_y = self.padding + y * self.cell_size
                    painter.drawEllipse(QPoint(pos_x, pos_y), 3, 3)
                
                # ������λ
                pos_x = self.padding + x * self.cell_size
                pos_y = self.padding + center * self.cell_size
                painter.drawEllipse(QPoint(pos_x, pos_y), 3, 3)
                
                pos_x = self.padding + center * self.cell_size
                pos_y = self.padding + x * self.cell_size
                painter.drawEllipse(QPoint(pos_x, pos_y), 3, 3)
    
    def draw_stones(self, painter):
        """��������"""
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.board_data[row][col] != 0:
                    x = self.padding + col * self.cell_size
                    y = self.padding + row * self.cell_size
                    
                    if self.board_data[row][col] == 1:  # ����
                        painter.setBrush(QBrush(QColor(0, 0, 0)))
                    else:  # ����
                        painter.setBrush(QBrush(QColor(255, 255, 255)))
                    
                    # ��������
                    painter.setPen(QPen(QColor(0, 0, 0), 1))
                    painter.drawEllipse(QPoint(x, y), self.cell_size // 2 - 2, self.cell_size // 2 - 2)
    
    def draw_hover_effect(self, painter):
        """���������ͣЧ��"""
        row, col = self.hover_pos
        x = self.padding + col * self.cell_size
        y = self.padding + row * self.cell_size
        
        # ֻ�ڿ�λ����ʾ��ͣЧ��
        if 0 <= row < self.board_size and 0 <= col < self.board_size and self.board_data[row][col] == 0:
            # ��͸��Ч��
            painter.setOpacity(0.5)
            color = QColor(0, 0, 0) if self.current_player == 1 else QColor(255, 255, 255)
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(QColor(0, 0, 0), 1))
            painter.drawEllipse(QPoint(x, y), self.cell_size // 2 - 2, self.cell_size // 2 - 2)
            painter.setOpacity(1.0)
    
    def mouseMoveEvent(self, event):
        """��������ƶ��¼������ڸ�����ͣλ��"""
        # ����������ڵ����̸�λ��
        pos = event.pos()
        col = round((pos.x() - self.padding) / self.cell_size)
        row = round((pos.y() - self.padding) / self.cell_size)
        
        # ���λ���Ƿ������̷�Χ��
        if 0 <= row < self.board_size and 0 <= col < self.board_size:
            self.hover_pos = (row, col)
            self.update()  # ���»���
    
    def mousePressEvent(self, event):
        """����������¼�"""
        if event.button() == Qt.LeftButton and self.hover_pos:
            row, col = self.hover_pos
            # ���λ���Ƿ������̷�Χ����Ϊ��
            if (0 <= row < self.board_size and 0 <= col < self.board_size and 
                self.board_data[row][col] == 0):
                # ���ͷ��������ź�
                self.stone_placed.emit(row, col, self.current_player)
    
    def update_board(self, board_data, current_player):
        """�����������ݺ͵�ǰ���"""
        self.board_data = board_data
        self.current_player = current_player
        self.update()  # ���»���


class BoardWindow(FramelessWindow):
    """��������Ϸ����"""
    
    def __init__(self, parent=None, style_index=0):
        super().__init__(parent)
        
        # ���ô��ڱ����ͼ��
        self.setWindowTitle("��������Ϸ")
        # Ĭ��ͼ�꣬Ҳ��ʹ����Ŀ�Դ�ͼ��
        self.setWindowIcon(FIF.GAME.icon())
        
        # ���ô��ڴ�С
        self.resize(800, 600)
        
        # ���������ڲ���
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        
        # ����������
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)
        
        # �����ϲ���Ϣ��
        self.info_bar = QWidget()
        self.info_layout = QHBoxLayout(self.info_bar)
        
        # �����Ϣ
        self.player_info = QLabel("��ǰ���: ����")
        self.player_info.setFont(QFont("Arial", 12, QFont.Bold))
        
        # ��Ϸ״̬
        self.game_status = QLabel("��Ϸ������")
        self.game_status.setFont(QFont("Arial", 12))
        
        # ����Ϣ��ӵ�����
        self.info_layout.addWidget(self.player_info)
        self.info_layout.addStretch(1)
        self.info_layout.addWidget(self.game_status)
        
        # �����в���Ϸ����
        self.game_area = QWidget()
        self.game_layout = QHBoxLayout(self.game_area)
        
        # �������̿ؼ�
        self.board_widget = BoardWidget(self, board_size=15, cell_size=32)
        
        # �����Ҳ�������
        self.control_panel = QWidget()
        self.control_layout = QVBoxLayout(self.control_panel)
        
        # ��ӿ��ư�ť
        self.restart_btn = PrimaryPushButton("���¿�ʼ")
        self.restart_btn.clicked.connect(self.restart_game)
        
        self.undo_btn = PushButton("����")
        self.undo_btn.clicked.connect(self.undo_move)
        
        self.settings_btn = PushButton("����")
        self.settings_btn.clicked.connect(self.show_settings)
        
        self.exit_btn = PushButton("�˳���Ϸ")
        self.exit_btn.clicked.connect(self.close)
        
        # ����ť��ӵ��������
        self.control_layout.addWidget(self.restart_btn)
        self.control_layout.addWidget(self.undo_btn)
        self.control_layout.addWidget(self.settings_btn)
        self.control_layout.addStretch(1)
        self.control_layout.addWidget(self.exit_btn)
        
        # �����̺Ϳ��������ӵ���Ϸ����
        self.game_layout.addWidget(self.board_widget, 4)  # ����Ϊ4
        self.game_layout.addWidget(self.control_panel, 1)  # ����Ϊ1
        
        # �����ײ�״̬��
        self.status_bar = QLabel("��Ϸ��׼���������ڷ�����")
        self.status_bar.setAlignment(Qt.AlignCenter)
        
        # ����������ӵ�������
        self.main_layout.addWidget(self.info_bar)
        self.main_layout.addWidget(self.game_area, 1)  # ����Ϸ����ռ����Ҫ�ռ�
        self.main_layout.addWidget(self.status_bar)
        
        # ��ʼ����Ϸ�߼�
        self.game = GomokuGame(board_size=15)
        
        # �������̵�stone_placed�ź�
        self.board_widget.stone_placed.connect(self.on_stone_placed)
        
        # ��������״̬
        self.board_widget.current_player = self.game.current_player
        
        # Ӧ��ѡ������̷��
        self.apply_style(style_index)
    
    def apply_style(self, style_index):
        """Ӧ�����̷��"""
        # ���Ի���style_index���ز�ͬ����ʽ
        styles = [
            {"board_color": QColor(210, 180, 140), "line_color": QColor(0, 0, 0)},  # Ĭ��ľɫ
            {"board_color": QColor(240, 217, 181), "line_color": QColor(80, 80, 80)},  # ǳľɫ
            {"board_color": QColor(60, 120, 60), "line_color": QColor(0, 0, 0)}  # ��ɫ
        ]
        
        # ȷ��style_index����Ч��Χ��
        if 0 <= style_index < len(styles):
            style = styles[style_index]
            
            # Ӧ����ʽ������
            palette = self.board_widget.palette()
            palette.setColor(QPalette.Window, style["board_color"])
            self.board_widget.setPalette(palette)
            
            # ����״̬
            self.status_bar.setText(f"��Ӧ�����̷�� {style_index+1}����Ϸ��׼���������ڷ�����")
            
            # �ػ�����
            self.board_widget.update()
        
    def on_stone_placed(self, row, col, player):
        """�������ӷ����¼�"""
        if self.game.place_stone(row, col):
            # ����������ʾ
            self.board_widget.update_board(self.game.board, self.game.current_player)
            
            # ������Ϸ״̬��Ϣ
            player_name = "����" if self.game.current_player == 1 else "����"
            self.player_info.setText(f"��ǰ���: {player_name}")
            
            # ����״̬��
            last_move = self.game.move_history[-1] if self.game.move_history else None
            if last_move:
                last_row, last_col, last_player = last_move
                last_player_name = "����" if last_player == 1 else "����"
                self.status_bar.setText(f"�������: {last_player_name} �� ({last_row+1}, {last_col+1})")
            
            # �����Ϸ�Ƿ����
            if self.game.game_over:
                winner = "����" if self.game.winner == 1 else "����"
                self.game_status.setText(f"��Ϸ����, {winner}ʤ")
                
                # ��ʾ��Ϸ�����Ի���
                self.show_game_over_dialog(winner)
    
    def restart_game(self):
        """���¿�ʼ��Ϸ"""
        self.game.reset()
        self.board_widget.update_board(self.game.board, self.game.current_player)
        
        # ���½�����Ϣ
        self.player_info.setText("��ǰ���: ����")
        self.game_status.setText("��Ϸ������")
        self.status_bar.setText("��Ϸ�����¿�ʼ���ڷ�����")
    
    def undo_move(self):
        """�������"""
        if not self.game.move_history:
            InfoBar.warning(
                title="�޷�����",
                content="û�п��Գ����Ĳ���",
                parent=self,
                position=InfoBarPosition.TOP
            )
            return
            
        # �Ƴ����һ��
        self.game.move_history.pop()
        
        # �ؽ�����
        self.game.board = [[0 for _ in range(self.game.board_size)] for _ in range(self.game.board_size)]
        self.game.game_over = False
        self.game.winner = 0
        
        # ���û����ʷ��¼����ô��������
        if not self.game.move_history:
            self.game.current_player = 1
        else:
            # ����Ӧ��������ʷ�ƶ�
            for row, col, player in self.game.move_history:
                self.game.board[row][col] = player
            
            # ��һ����������һ�ֵ���ҵĶ���
            _, _, last_player = self.game.move_history[-1]
            self.game.current_player = 3 - last_player  # 1��2��2��1
        
        # ����������ʾ
        self.board_widget.update_board(self.game.board, self.game.current_player)
        
        # ���½�����Ϣ
        player_name = "����" if self.game.current_player == 1 else "����"
        self.player_info.setText(f"��ǰ���: {player_name}")
        self.game_status.setText("��Ϸ������")
        
        # ����״̬��
        if self.game.move_history:
            last_row, last_col, last_player = self.game.move_history[-1]
            last_player_name = "����" if last_player == 1 else "����"
            self.status_bar.setText(f"����ɹ�, �������: {last_player_name} �� ({last_row+1}, {last_col+1})")
        else:
            self.status_bar.setText("����ɹ�, �ڷ�����")
    
    def show_settings(self):
        """��ʾ���öԻ���"""
        # �������ʵ�ִ����öԻ�����߼�
        InfoBar.success(
            title="����",
            content="��Ϸ���ù�����δʵ��",
            parent=self,
            position=InfoBarPosition.TOP
        )
    
    def show_game_over_dialog(self, winner):
        """��ʾ��Ϸ�����Ի���"""
        msg_box = MessageBox(
            "��Ϸ����",
            f"��ϲ {winner} ��ʤ��\n�Ƿ����¿�ʼ��Ϸ��",
            self
        )
        msg_box.yesButton.setText("���¿�ʼ")
        msg_box.cancelButton.setText("�ر�")
        
        if msg_box.exec():
            self.restart_game()


if __name__ == "__main__":
    # ���Դ���
    app = QApplication(sys.argv)
    window = BoardWindow()
    window.show()
    sys.exit(app.exec_())
