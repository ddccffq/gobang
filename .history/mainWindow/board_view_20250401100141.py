# coding:utf-8
from PyQt5.QtCore import Qt, QRect, QPoint, QSize
from PyQt5.QtGui import QIcon, QFont, QPainter, QPen, QBrush, QColor, QPaintEvent
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QApplication, QSizePolicy
import sys

from qfluentwidgets import FluentIcon as FIF, PushButton, ComboBox, isDarkTheme
from qframelesswindow import FramelessWindow


class GoBoardWidget(QWidget):
    """15x15的五子棋棋盘组件"""
    
    # 棋盘样式 - 背景颜色
    BOARD_STYLES = {
        "经典木色": {"background": QColor("#E8B473"), "line": QColor("#000000")},
        "淡雅青色": {"background": QColor("#B5D8CC"), "line": QColor("#000000")},
        "复古黄褐": {"background": QColor("#D4B483"), "line": QColor("#000000")},
        "冷酷灰色": {"background": QColor("#CCCCCC"), "line": QColor("#000000")},
        "暗黑模式": {"background": QColor("#2D2D2D"), "line": QColor("#FFFFFF")}
    }
    
    def __init__(self, parent=None, style_index=0):
        super().__init__(parent)
        
        # 棋盘属性
        self.board_size = 15  # 15x15的棋盘
        self.cell_size = 30   # 每个格子的大小
        self.padding = 20     # 边距
        self.stone_size = 28  # 棋子大小
        
        # 获取样式名称列表
        style_names = list(self.BOARD_STYLES.keys())
        # 确保style_index在有效范围内
        self.current_style = style_names[min(style_index, len(style_names)-1)]
        
        # 棋盘数据 - 0表示空，1表示黑棋，2表示白棋
        self.board_data = [[0 for _ in range(self.board_size)] for _ in range(self.board_size)]
        
        # 设置组件大小
        board_width = self.board_size * self.cell_size + 2 * self.padding
        self.setMinimumSize(board_width, board_width)
        self.setMaximumSize(board_width, board_width)
        
        # 当前轮到谁下棋 - 1表示黑棋，2表示白棋
        self.current_player = 1
        
        # 设置组件接受鼠标点击
        self.setMouseTracking(True)
    
    def set_style(self, style_index):
        """设置棋盘风格"""
        style_names = list(self.BOARD_STYLES.keys())
        if 0 <= style_index < len(style_names):
            self.current_style = style_names[style_index]
            self.update()  # 重绘棋盘
            return True
        return False
    
    def get_style_names(self):
        """获取所有棋盘风格名称"""
        return list(self.BOARD_STYLES.keys())
    
    def reset_game(self):
        """重置游戏状态"""
        self.board_data = [[0 for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.current_player = 1  # 黑棋先行
        self.update()
    
    def paintEvent(self, event: QPaintEvent):
        """绘制棋盘和棋子"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)  # 抗锯齿
        
        # 获取当前风格
        style = self.BOARD_STYLES[self.current_style]
        
        # 绘制棋盘背景
        painter.fillRect(
            QRect(0, 0, self.width(), self.height()),
            QBrush(style["background"])
        )
        
        # 设置线条颜色
        painter.setPen(QPen(style["line"], 1))
        
        # 绘制横线和竖线
        for i in range(self.board_size):
            # 横线
            painter.drawLine(
                self.padding, self.padding + i * self.cell_size,
                self.padding + (self.board_size - 1) * self.cell_size, self.padding + i * self.cell_size
            )
            # 竖线
            painter.drawLine(
                self.padding + i * self.cell_size, self.padding,
                self.padding + i * self.cell_size, self.padding + (self.board_size - 1) * self.cell_size
            )
        
        # 绘制天元和星位
        star_points = [(3, 3), (3, 11), (7, 7), (11, 3), (11, 11)]
        for x, y in star_points:
            painter.setBrush(QBrush(style["line"]))
            painter.drawEllipse(
                self.padding + x * self.cell_size - 3,
                self.padding + y * self.cell_size - 3,
                6, 6
            )
        
        # 绘制棋子
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.board_data[row][col] != 0:
                    # 计算棋子位置
                    x = self.padding + col * self.cell_size - self.stone_size // 2
                    y = self.padding + row * self.cell_size - self.stone_size // 2
                    
                    # 设置棋子颜色 - 1是黑棋，2是白棋
                    if self.board_data[row][col] == 1:
                        painter.setBrush(QBrush(Qt.black))
                    else:
                        painter.setBrush(QBrush(Qt.white))
                    
                    # 绘制棋子边框
                    painter.setPen(QPen(Qt.black if self.board_data[row][col] == 2 else Qt.gray, 1))
                    
                    # 绘制棋子
                    painter.drawEllipse(x, y, self.stone_size, self.stone_size)
    
    def mousePressEvent(self, event):
        """处理鼠标点击事件，放置棋子"""
        if event.button() == Qt.LeftButton:
            # 计算点击的格子坐标
            col = round((event.x() - self.padding) / self.cell_size)
            row = round((event.y() - self.padding) / self.cell_size)
            
            # 检查坐标是否有效
            if 0 <= row < self.board_size and 0 <= col < self.board_size:
                # 检查该位置是否已有棋子
                if self.board_data[row][col] == 0:
                    # 放置当前玩家的棋子
                    self.board_data[row][col] = self.current_player
                    
                    # 切换玩家
                    self.current_player = 3 - self.current_player  # 在1和2之间切换
                    
                    # 重绘棋盘
                    self.update()


class BoardWidget(QWidget):
    """五子棋游戏组件，可嵌入到应用界面中"""
    
    def __init__(self, parent=None, style_index=0):
        super().__init__(parent)
        
        # 创建主布局
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 创建标题标签
        self.title_label = QLabel("五子棋游戏")
        self.title_label.setAlignment(Qt.AlignCenter)
        title_font = self.title_label.font()
        title_font.setPointSize(24)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        
        # 创建操作区域布局
        self.controls_layout = QHBoxLayout()
        
        # 创建棋盘风格选择下拉框
        self.style_label = QLabel("棋盘风格：")
        self.style_combo = ComboBox(self)
        
        # 创建棋盘实例
        self.board = GoBoardWidget(self, style_index)
        
        # 填充风格选择下拉框
        self.style_combo.addItems(self.board.get_style_names())
        self.style_combo.setCurrentIndex(style_index)
        self.style_combo.currentIndexChanged.connect(self.change_board_style)
        
        # 将标签和下拉框添加到操作区域
        self.controls_layout.addWidget(self.style_label)
        self.controls_layout.addWidget(self.style_combo)
        self.controls_layout.addStretch(1)
        
        # 玩家信息标签
        self.player_info = QLabel("当前玩家：黑棋")
        self.player_info.setAlignment(Qt.AlignCenter)
        info_font = self.player_info.font()
        info_font.setPointSize(14)
        self.player_info.setFont(info_font)
        
        # 创建按钮布局
        self.button_layout = QHBoxLayout()
        self.start_button = PushButton("开始对局")
        self.restart_button = PushButton("重新开始")
        self.button_layout.addStretch(1)
        self.button_layout.addWidget(self.start_button)
        self.button_layout.addSpacing(20)
        self.button_layout.addWidget(self.restart_button)
        self.button_layout.addStretch(1)
        
        # 添加组件到主布局
        self.main_layout.addWidget(self.title_label)
        self.main_layout.addSpacing(10)
        self.main_layout.addLayout(self.controls_layout)
        self.main_layout.addWidget(self.player_info)
        self.main_layout.addWidget(self.board, 0, Qt.AlignCenter)
        self.main_layout.addSpacing(10)
        self.main_layout.addLayout(self.button_layout)
        
        # 设置对象名称，用于导航
        self.setObjectName('App-Interface')
        
        # 连接按钮事件
        self.start_button.clicked.connect(self.onStartGame)
        self.restart_button.clicked.connect(self.onRestartGame)
        
        # 更新玩家信息的定时器
        self.board.update()
    
    def change_board_style(self, index):
        """更改棋盘风格"""
        self.board.set_style(index)
    
    def update_player_info(self):
        """更新当前玩家信息"""
        player_text = "当前玩家：黑棋" if self.board.current_player == 1 else "当前玩家：白棋"
        self.player_info.setText(player_text)
    
    def onStartGame(self):
        """开始游戏"""
        self.board.reset_game()
        self.update_player_info()
    
    def onRestartGame(self):
        """重新开始游戏"""
        self.board.reset_game()
        self.update_player_info()


class BoardWindow(FramelessWindow):
    """五子棋游戏窗口"""
    
    def __init__(self, parent=None, style_index=0):
        super().__init__(parent)
        
        # 设置窗口标题和图标
        self.setWindowTitle("五子棋游戏")
        self.setWindowIcon(FIF.GAME.icon())
        
        # 设置窗口大小
        self.resize(600, 700)
        
        # 创建主窗口部件
        self.central_widget = QWidget(self)
        
        # 创建主布局
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 创建棋盘组件
        self.board_widget = BoardWidget(self, style_index)
        
        # 创建关闭按钮
        self.button_layout = QHBoxLayout()
        self.close_button = PushButton("关闭窗口")
        self.close_button.clicked.connect(self.close)
        self.button_layout.addStretch(1)
        self.button_layout.addWidget(self.close_button)
        self.button_layout.addStretch(1)
        
        # 添加组件到主布局
        self.main_layout.addWidget(self.board_widget)
        self.main_layout.addLayout(self.button_layout)
        
        # 设置窗口的内容部件
        self.setLayout(QVBoxLayout(self))
        self.layout().setContentsMargins(0, 48, 0, 0)  # 为标题栏留出空间
        self.layout().addWidget(self.central_widget)


if __name__ == "__main__":
    # 测试代码
    app = QApplication(sys.argv)
    window = BoardWindow()
    window.show()
    sys.exit(app.exec_())
