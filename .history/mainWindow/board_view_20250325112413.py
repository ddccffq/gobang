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

# 导入游戏逻辑
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "game"))
from game_logic import GomokuGame


class BoardWidget(QWidget):
    """棋盘控件"""
    
    # 定义信号
    stone_placed = pyqtSignal(int, int, int)  # 行, 列, 玩家
    
    def __init__(self, parent=None, board_size=15, cell_size=30):
        super().__init__(parent)
        self.board_size = board_size
        self.cell_size = cell_size
        self.padding = 20  # 棋盘边缘填充
        
        # 设置棋盘大小
        board_width = board_size * cell_size + 2 * self.padding
        board_height = board_size * cell_size + 2 * self.padding
        self.setMinimumSize(board_width, board_height)
        
        # 初始化数据
        self.board_data = [[0 for _ in range(board_size)] for _ in range(board_size)]
        self.hover_pos = None  # 鼠标悬停位置
        
        # 设置背景色为棋盘底色
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(210, 180, 140))  # 棋盘底色
        self.setPalette(palette)
        
        # 启用鼠标跟踪，以便可以显示悬停效果
        self.setMouseTracking(True)
    
    def paintEvent(self, event):
        """绘制棋盘和棋子"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)  # 抗锯齿
        
        # 绘制棋盘格
        self.draw_board_grid(painter)
        
        # 绘制天元和星位
        self.draw_star_points(painter)
        
        # 绘制棋子
        self.draw_stones(painter)
        
        # 绘制鼠标悬停效果
        if self.hover_pos:
            self.draw_hover_effect(painter)
    
    def draw_board_grid(self, painter):
        """绘制棋盘格线"""
        grid_pen = QPen(QColor(0, 0, 0), 1)
        painter.setPen(grid_pen)
        
        # 绘制横线和竖线
        for i in range(self.board_size):
            # 横线
            start_x = self.padding
            start_y = self.padding + i * self.cell_size
            end_x = self.padding + (self.board_size - 1) * self.cell_size
            end_y = start_y
            painter.drawLine(start_x, start_y, end_x, end_y)
            
            # 竖线
            start_x = self.padding + i * self.cell_size
            start_y = self.padding
            end_x = start_x
            end_y = self.padding + (self.board_size - 1) * self.cell_size
            painter.drawLine(start_x, start_y, end_x, end_y)
    
    def draw_star_points(self, painter):
        """绘制天元和星位"""
        star_brush = QBrush(QColor(0, 0, 0))
        painter.setBrush(star_brush)
        
        # 天元(棋盘中心)
        center = self.board_size // 2
        center_x = self.padding + center * self.cell_size
        center_y = self.padding + center * self.cell_size
        painter.drawEllipse(QPoint(center_x, center_y), 3, 3)
        
        # 星位(根据棋盘大小确定)
        if self.board_size >= 15:  # 标准19路或15路棋盘
            star_positions = [3, self.board_size - 4]  # 边星位置
            for x in star_positions:
                for y in star_positions:
                    # 四角星位
                    pos_x = self.padding + x * self.cell_size
                    pos_y = self.padding + y * self.cell_size
                    painter.drawEllipse(QPoint(pos_x, pos_y), 3, 3)
                
                # 边中星位
                pos_x = self.padding + x * self.cell_size
                pos_y = self.padding + center * self.cell_size
                painter.drawEllipse(QPoint(pos_x, pos_y), 3, 3)
                
                pos_x = self.padding + center * self.cell_size
                pos_y = self.padding + x * self.cell_size
                painter.drawEllipse(QPoint(pos_x, pos_y), 3, 3)
    
    def draw_stones(self, painter):
        """绘制棋子"""
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.board_data[row][col] != 0:
                    x = self.padding + col * self.cell_size
                    y = self.padding + row * self.cell_size
                    
                    if self.board_data[row][col] == 1:  # 黑棋
                        painter.setBrush(QBrush(QColor(0, 0, 0)))
                    else:  # 白棋
                        painter.setBrush(QBrush(QColor(255, 255, 255)))
                    
                    # 棋子轮廓
                    painter.setPen(QPen(QColor(0, 0, 0), 1))
                    painter.drawEllipse(QPoint(x, y), self.cell_size // 2 - 2, self.cell_size // 2 - 2)
    
    def draw_hover_effect(self, painter):
        """绘制鼠标悬停效果"""
        row, col = self.hover_pos
        x = self.padding + col * self.cell_size
        y = self.padding + row * self.cell_size
        
        # 只在空位置显示悬停效果
        if 0 <= row < self.board_size and 0 <= col < self.board_size and self.board_data[row][col] == 0:
            # 半透明效果
            painter.setOpacity(0.5)
            color = QColor(0, 0, 0) if self.current_player == 1 else QColor(255, 255, 255)
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(QColor(0, 0, 0), 1))
            painter.drawEllipse(QPoint(x, y), self.cell_size // 2 - 2, self.cell_size // 2 - 2)
            painter.setOpacity(1.0)
    
    def mouseMoveEvent(self, event):
        """处理鼠标移动事件，用于更新悬停位置"""
        # 计算鼠标所在的棋盘格位置
        pos = event.pos()
        col = round((pos.x() - self.padding) / self.cell_size)
        row = round((pos.y() - self.padding) / self.cell_size)
        
        # 检查位置是否在棋盘范围内
        if 0 <= row < self.board_size and 0 <= col < self.board_size:
            self.hover_pos = (row, col)
            self.update()  # 更新绘制
    
    def mousePressEvent(self, event):
        """处理鼠标点击事件"""
        if event.button() == Qt.LeftButton and self.hover_pos:
            row, col = self.hover_pos
            # 检查位置是否在棋盘范围内且为空
            if (0 <= row < self.board_size and 0 <= col < self.board_size and 
                self.board_data[row][col] == 0):
                # 发送放置棋子信号
                self.stone_placed.emit(row, col, self.current_player)
    
    def update_board(self, board_data, current_player):
        """更新棋盘数据和当前玩家"""
        self.board_data = board_data
        self.current_player = current_player
        self.update()  # 更新绘制


class BoardWindow(FramelessWindow):
    """五子棋游戏窗口"""
    
    def __init__(self, parent=None, style_index=0):
        super().__init__(parent)
        
        # 设置窗口标题和图标
        self.setWindowTitle("五子棋游戏")
        # 默认图标，也可使用项目自带图标
        self.setWindowIcon(FIF.GAME.icon())
        
        # 设置窗口大小
        self.resize(800, 600)
        
        # 创建主窗口部件
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        
        # 创建主布局
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)
        
        # 创建上部信息栏
        self.info_bar = QWidget()
        self.info_layout = QHBoxLayout(self.info_bar)
        
        # 玩家信息
        self.player_info = QLabel("当前玩家: 黑棋")
        self.player_info.setFont(QFont("Arial", 12, QFont.Bold))
        
        # 游戏状态
        self.game_status = QLabel("游戏进行中")
        self.game_status.setFont(QFont("Arial", 12))
        
        # 将信息添加到布局
        self.info_layout.addWidget(self.player_info)
        self.info_layout.addStretch(1)
        self.info_layout.addWidget(self.game_status)
        
        # 创建中部游戏区域
        self.game_area = QWidget()
        self.game_layout = QHBoxLayout(self.game_area)
        
        # 创建棋盘控件
        self.board_widget = BoardWidget(self, board_size=15, cell_size=32)
        
        # 创建右侧控制面板
        self.control_panel = QWidget()
        self.control_layout = QVBoxLayout(self.control_panel)
        
        # 添加控制按钮
        self.restart_btn = PrimaryPushButton("重新开始")
        self.restart_btn.clicked.connect(self.restart_game)
        
        self.undo_btn = PushButton("悔棋")
        self.undo_btn.clicked.connect(self.undo_move)
        
        self.settings_btn = PushButton("设置")
        self.settings_btn.clicked.connect(self.show_settings)
        
        self.exit_btn = PushButton("退出游戏")
        self.exit_btn.clicked.connect(self.close)
        
        # 将按钮添加到控制面板
        self.control_layout.addWidget(self.restart_btn)
        self.control_layout.addWidget(self.undo_btn)
        self.control_layout.addWidget(self.settings_btn)
        self.control_layout.addStretch(1)
        self.control_layout.addWidget(self.exit_btn)
        
        # 将棋盘和控制面板添加到游戏区域
        self.game_layout.addWidget(self.board_widget, 4)  # 比例为4
        self.game_layout.addWidget(self.control_panel, 1)  # 比例为1
        
        # 创建底部状态栏
        self.status_bar = QLabel("游戏已准备就绪，黑方先行")
        self.status_bar.setAlignment(Qt.AlignCenter)
        
        # 将各部分添加到主布局
        self.main_layout.addWidget(self.info_bar)
        self.main_layout.addWidget(self.game_area, 1)  # 让游戏区域占据主要空间
        self.main_layout.addWidget(self.status_bar)
        
        # 初始化游戏逻辑
        self.game = GomokuGame(board_size=15)
        
        # 连接棋盘的stone_placed信号
        self.board_widget.stone_placed.connect(self.on_stone_placed)
        
        # 更新棋盘状态
        self.board_widget.current_player = self.game.current_player
        
        # 应用选择的棋盘风格
        self.apply_style(style_index)
    
    def apply_style(self, style_index):
        """应用棋盘风格"""
        # 可以基于style_index加载不同的样式
        styles = [
            {"board_color": QColor(210, 180, 140), "line_color": QColor(0, 0, 0)},  # 默认木色
            {"board_color": QColor(240, 217, 181), "line_color": QColor(80, 80, 80)},  # 浅木色
            {"board_color": QColor(60, 120, 60), "line_color": QColor(0, 0, 0)}  # 绿色
        ]
        
        # 确保style_index在有效范围内
        if 0 <= style_index < len(styles):
            style = styles[style_index]
            
            # 应用样式到棋盘
            palette = self.board_widget.palette()
            palette.setColor(QPalette.Window, style["board_color"])
            self.board_widget.setPalette(palette)
            
            # 更新状态
            self.status_bar.setText(f"已应用棋盘风格 {style_index+1}，游戏已准备就绪，黑方先行")
            
            # 重绘棋盘
            self.board_widget.update()
        
    def on_stone_placed(self, row, col, player):
        """处理棋子放置事件"""
        if self.game.place_stone(row, col):
            # 更新棋盘显示
            self.board_widget.update_board(self.game.board, self.game.current_player)
            
            # 更新游戏状态信息
            player_name = "黑棋" if self.game.current_player == 1 else "白棋"
            self.player_info.setText(f"当前玩家: {player_name}")
            
            # 更新状态栏
            last_move = self.game.move_history[-1] if self.game.move_history else None
            if last_move:
                last_row, last_col, last_player = last_move
                last_player_name = "黑棋" if last_player == 1 else "白棋"
                self.status_bar.setText(f"最后落子: {last_player_name} 在 ({last_row+1}, {last_col+1})")
            
            # 检查游戏是否结束
            if self.game.game_over:
                winner = "黑棋" if self.game.winner == 1 else "白棋"
                self.game_status.setText(f"游戏结束, {winner}胜")
                
                # 显示游戏结束对话框
                self.show_game_over_dialog(winner)
    
    def restart_game(self):
        """重新开始游戏"""
        self.game.reset()
        self.board_widget.update_board(self.game.board, self.game.current_player)
        
        # 更新界面信息
        self.player_info.setText("当前玩家: 黑棋")
        self.game_status.setText("游戏进行中")
        self.status_bar.setText("游戏已重新开始，黑方先行")
    
    def undo_move(self):
        """悔棋操作"""
        if not self.game.move_history:
            InfoBar.warning(
                title="无法悔棋",
                content="没有可以撤销的操作",
                parent=self,
                position=InfoBarPosition.TOP
            )
            return
            
        # 移除最后一步
        self.game.move_history.pop()
        
        # 重建棋盘
        self.game.board = [[0 for _ in range(self.game.board_size)] for _ in range(self.game.board_size)]
        self.game.game_over = False
        self.game.winner = 0
        
        # 如果没有历史记录，那么黑棋先行
        if not self.game.move_history:
            self.game.current_player = 1
        else:
            # 重新应用所有历史移动
            for row, col, player in self.game.move_history:
                self.game.board[row][col] = player
            
            # 下一个玩家是最后一手的玩家的对手
            _, _, last_player = self.game.move_history[-1]
            self.game.current_player = 3 - last_player  # 1变2，2变1
        
        # 更新棋盘显示
        self.board_widget.update_board(self.game.board, self.game.current_player)
        
        # 更新界面信息
        player_name = "黑棋" if self.game.current_player == 1 else "白棋"
        self.player_info.setText(f"当前玩家: {player_name}")
        self.game_status.setText("游戏进行中")
        
        # 更新状态栏
        if self.game.move_history:
            last_row, last_col, last_player = self.game.move_history[-1]
            last_player_name = "黑棋" if last_player == 1 else "白棋"
            self.status_bar.setText(f"悔棋成功, 最后落子: {last_player_name} 在 ({last_row+1}, {last_col+1})")
        else:
            self.status_bar.setText("悔棋成功, 黑方先行")
    
    def show_settings(self):
        """显示设置对话框"""
        # 这里可以实现打开设置对话框的逻辑
        InfoBar.success(
            title="设置",
            content="游戏设置功能尚未实现",
            parent=self,
            position=InfoBarPosition.TOP
        )
    
    def show_game_over_dialog(self, winner):
        """显示游戏结束对话框"""
        msg_box = MessageBox(
            "游戏结束",
            f"恭喜 {winner} 获胜！\n是否重新开始游戏？",
            self
        )
        msg_box.yesButton.setText("重新开始")
        msg_box.cancelButton.setText("关闭")
        
        if msg_box.exec():
            self.restart_game()


if __name__ == "__main__":
    # 测试代码
    app = QApplication(sys.argv)
    window = BoardWindow()
    window.show()
    sys.exit(app.exec_())
