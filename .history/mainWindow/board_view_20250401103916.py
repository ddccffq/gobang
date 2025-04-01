# coding:utf-8
from PyQt5.QtCore import Qt, QRect, QPoint, QSize
from PyQt5.QtGui import QIcon, QFont, QPainter, QPen, QBrush, QColor, QPaintEvent
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QApplication, QSizePolicy, QFrame
import sys

from qfluentwidgets import FluentIcon as FIF, PushButton, ComboBox, isDarkTheme, InfoBar, InfoBarPosition
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
        self.base_cell_size = 40  # 基础格子大小，实际大小会根据组件尺寸自动计算
        self.base_padding = 25  # 基础边距，实际边距会根据组件尺寸自动计算
        self.base_stone_size = 36  # 基础棋子大小，实际大小会根据组件尺寸自动计算
        
        # 获取样式名称列表
        style_names = list(self.BOARD_STYLES.keys())
        # 确保style_index在有效范围内
        self.current_style = style_names[min(style_index, len(style_names)-1)]
        
        # 棋盘数据 - 0表示空，1表示黑棋，2表示白棋
        self.board_data = [[0 for _ in range(self.board_size)] for _ in range(self.board_size)]
        
        # 设置组件最小大小
        min_board_width = self.board_size * self.base_cell_size + 2 * self.base_padding
        self.setMinimumSize(min_board_width, min_board_width)
        
        # 设置大小策略为扩展，允许组件随窗口调整而放大
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # 当前轮到谁下棋 - 1表示黑棋，2表示白棋
        self.current_player = 1
        
        # 游戏状态标志 - 只有游戏开始后才能下棋
        self.game_started = False
        
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
        self.game_started = True  # 游戏已开始
        self.update()
    
    def paintEvent(self, event: QPaintEvent):
        """绘制棋盘和棋子"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)  # 抗锯齿
        
        # 计算当前实际的格子大小和边距
        # 使用较小的维度确保棋盘是正方形的
        size = min(self.width(), self.height())
        cell_size = (size - 2 * self.base_padding) / self.board_size
        padding = (size - cell_size * self.board_size) / 2
        stone_size = cell_size * 0.9  # 棋子大小为格子大小的90%
        
        # 获取当前风格
        style = self.BOARD_STYLES[self.current_style]
        
        # 绘制棋盘背景
        painter.fillRect(QRect(0, 0, self.width(), self.height()), QBrush(style["background"]))
        
        # 设置线条颜色
        painter.setPen(QPen(style["line"], max(1, int(cell_size / 20))))  # 线宽根据格子大小调整
        
        # 绘制横线和竖线
        for i in range(self.board_size):
            # 横线
            painter.drawLine(
                int(padding), int(padding + i * cell_size),
                int(padding + (self.board_size - 1) * cell_size), int(padding + i * cell_size)
            )
            # 竖线
            painter.drawLine(
                int(padding + i * cell_size), int(padding),
                int(padding + i * cell_size), int(padding + (self.board_size - 1) * cell_size)
            )
        
        # 绘制天元和星位
        star_points = [(3, 3), (3, 11), (7, 7), (11, 3), (11, 11)]
        star_size = max(4, int(cell_size / 10))  # 星位点大小根据格子大小调整
        
        for x, y in star_points:
            painter.setBrush(QBrush(style["line"]))
            painter.drawEllipse(
                int(padding + x * cell_size - star_size / 2),
                int(padding + y * cell_size - star_size / 2),
                star_size, star_size
            )
        
        # 绘制棋子
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.board_data[row][col] != 0:
                    # 计算棋子位置
                    x = int(padding + col * cell_size - stone_size / 2)
                    y = int(padding + row * cell_size - stone_size / 2)
                    
                    # 设置棋子颜色 - 1是黑棋，2是白棋
                    if self.board_data[row][col] == 1:
                        painter.setBrush(QBrush(Qt.black))
                    else:
                        painter.setBrush(QBrush(Qt.white))
                    
                    # 绘制棋子边框
                    painter.setPen(QPen(Qt.black if self.board_data[row][col] == 2 else Qt.gray, max(1, int(cell_size / 20))))
                    
                    # 绘制棋子
                    painter.drawEllipse(x, y, int(stone_size), int(stone_size))
        
        # 如果游戏未开始，绘制提示
        if not self.game_started:
            font = painter.font()
            font.setPointSize(int(14 * cell_size / self.base_cell_size))  # 字体大小根据棋盘大小调整
            font.setBold(True)
            painter.setFont(font)
            painter.setPen(QPen(QColor(255, 0, 0, 180)))
            
            # 创建半透明背景
            rect = QRect(
                int(self.width() / 4),
                int(self.height() / 2 - size / 20),
                int(self.width() / 2),
                int(size / 10)
            )
            painter.fillRect(rect, QBrush(QColor(0, 0, 0, 120)))
            
            painter.drawText(rect, Qt.AlignCenter, "请点击「开始对局」按钮")
    
    def mousePressEvent(self, event):
        """处理鼠标点击事件，放置棋子"""
        # 如果游戏未开始，忽略点击
        if not self.game_started:
            return
            
        if event.button() == Qt.LeftButton:
            # 计算当前实际的格子大小和边距
            size = min(self.width(), self.height())
            cell_size = (size - 2 * self.base_padding) / self.board_size
            padding = (size - cell_size * self.board_size) / 2
            
            # 计算点击的格子坐标
            col = round((event.x() - padding) / cell_size)
            row = round((event.y() - padding) / cell_size)
            
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
                    
                    # 通知父组件更新玩家信息
                    parent = self.parent()
                    if parent and hasattr(parent, 'update_player_info'):
                        parent.update_player_info()


class BoardWidget(QWidget):
    """五子棋游戏组件，可嵌入到应用界面中"""
    
    def __init__(self, parent=None, style_index=0):
        super().__init__(parent)
        
        # 创建主布局 - 改为水平布局，左侧放棋盘，右侧放控制面板
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)  # 增加间距
        
        # 创建左侧容器，用于保持棋盘居中
        self.left_container = QWidget()
        self.left_layout = QVBoxLayout(self.left_container)
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建棋盘实例
        self.board = GoBoardWidget(self, style_index)
        
        # 左侧容器采用扩展策略，允许随窗口放大
        self.left_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # 将棋盘添加到左侧容器，使用Qt.AlignCenter但允许扩展
        self.left_layout.addWidget(self.board, 1, Qt.AlignCenter)
        
        # 创建右侧控制面板
        self.right_panel = QWidget()
        self.right_layout = QVBoxLayout(self.right_panel)
        self.right_layout.setContentsMargins(10, 10, 10, 10)
        self.right_layout.setSpacing(15)
        
        # 设置右侧面板的固定宽度，防止过度拉伸
        self.right_panel.setFixedWidth(300)
        
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
        
        # 填充风格选择下拉框
        self.style_combo.addItems(self.board.get_style_names())
        self.style_combo.setCurrentIndex(style_index)
        self.style_combo.currentIndexChanged.connect(self.change_board_style)
        
        # 将标签和下拉框添加到操作区域
        self.controls_layout.addWidget(self.style_label)
        self.controls_layout.addWidget(self.style_combo)
        self.controls_layout.addStretch(1)
        
        # 创建分隔线
        self.separator = QFrame()
        self.separator.setFrameShape(QFrame.HLine)
        self.separator.setFrameShadow(QFrame.Sunken)
        
        # 玩家信息标签
        self.player_info = QLabel("当前玩家：黑棋")
        self.player_info.setAlignment(Qt.AlignCenter)
        info_font = self.player_info.font()
        info_font.setPointSize(16)
        self.player_info.setFont(info_font)
        
        # 创建游戏说明
        self.game_instructions = QLabel(
            "游戏说明：\n"
            "1. 点击「开始对局」按钮开始游戏\n"
            "2. 黑棋先行，双方轮流下棋\n"
            "3. 先连成五子一线者获胜\n"
            "4. 点击「重新开始」可随时重置游戏"
        )
        self.game_instructions.setWordWrap(True)
        self.game_instructions.setAlignment(Qt.AlignLeft)
        
        # 创建按钮布局
        self.button_layout = QVBoxLayout()  # 改为垂直布局
        self.start_button = PushButton("开始对局")
        self.restart_button = PushButton("重新开始")
        
        # 设置按钮尺寸
        self.start_button.setFixedHeight(40)
        self.restart_button.setFixedHeight(40)
        
        # 按钮添加到布局
        self.button_layout.addWidget(self.start_button)
        self.button_layout.addSpacing(10)
        self.button_layout.addWidget(self.restart_button)
        
        # 添加组件到右侧布局
        self.right_layout.addWidget(self.title_label)
        self.right_layout.addSpacing(10)
        self.right_layout.addLayout(self.controls_layout)
        self.right_layout.addWidget(self.separator)
        self.right_layout.addWidget(self.player_info)
        self.right_layout.addSpacing(20)
        self.right_layout.addWidget(self.game_instructions)
        self.right_layout.addSpacing(20)
        self.right_layout.addLayout(self.button_layout)
        self.right_layout.addStretch(1)  # 添加伸缩器使组件靠上对齐
        
        # 将棋盘容器和右侧面板添加到主布局，并添加两侧伸缩项
        self.main_layout.addStretch(1)
        self.main_layout.addWidget(self.left_container, 1)  # 给左侧容器一个拉伸因子1
        self.main_layout.addWidget(self.right_panel, 0)  # 右侧面板不拉伸
        self.main_layout.addStretch(1)
        
        # 设置对象名称，用于导航
        self.setObjectName('App-Interface')
        
        # 连接按钮事件
        self.start_button.clicked.connect(self.onStartGame)
        self.restart_button.clicked.connect(self.onRestartGame)
        
        # 初始化时更新玩家信息
        self.update_player_info()
        
        # 设置初始游戏状态
        self.board.game_started = False
    
    def change_board_style(self, index):
        """更改棋盘风格"""
        self.board.set_style(index)
    
    def update_player_info(self):
        """更新当前玩家信息"""
        player_text = "当前玩家：黑棋" if self.board.current_player == 1 else "当前玩家：白棋"
        self.player_info.setText(player_text)
    
    def onStartGame(self):
        """开始游戏"""
        self.board.reset_game()  # 这个方法内部会设置game_started为True
        self.update_player_info()
        
        # 显示提示信息
        InfoBar.success(
            title='游戏已开始',
            content="黑棋先行，请点击棋盘落子",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=3000,
            parent=self
        )
    
    def onRestartGame(self):
        """重新开始游戏"""
        self.board.reset_game()
        self.update_player_info()
        
        # 显示提示信息
        InfoBar.info(
            title='游戏已重置',
            content="棋盘已清空，黑棋先行",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=3000,
            parent=self
        )


class BoardWindow(FramelessWindow):
    """五子棋游戏窗口"""
    
    def __init__(self, parent=None, style_index=0):
        super().__init__(parent)
        
        # 设置窗口标题和图标
        self.setWindowTitle("五子棋游戏")
        self.setWindowIcon(FIF.GAME.icon())
        
        # 设置窗口为独立窗口
        self.setWindowFlags(Qt.Window)
        
        # 设置窗口大小，增加宽度以适应新布局
        self.resize(900, 700)
        
        # 设置窗口在屏幕中央显示
        screen = QApplication.desktop().availableGeometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )
        
        # 创建主窗口部件
        self.central_widget = QWidget(self)
        
        # 创建主布局
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 创建棋盘组件
        self.board_widget = BoardWidget(self, style_index)
        
        # 创建关闭按钮布局，并添加伸缩项让内容居中
        self.button_layout = QHBoxLayout()
        self.close_button = PushButton("关闭窗口")
        self.close_button.setFixedWidth(150)  # 设置固定宽度
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
    
    def closeEvent(self, event):
        """窗口关闭时的清理工作"""
        print("游戏窗口正在关闭，清理资源...")
        # 这里可以添加任何需要的资源清理代码
        super().closeEvent(event)


if __name__ == "__main__":
    # 测试代码
    app = QApplication(sys.argv)
    window = BoardWindow()
    window.show()
    sys.exit(app.exec_())
