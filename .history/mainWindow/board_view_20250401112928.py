# coding:utf-8
from PyQt5.QtCore import Qt, QRect, QPoint, QSize
from PyQt5.QtGui import QIcon, QFont, QPainter, QPen, QBrush, QColor, QPaintEvent
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QApplication, QSizePolicy, QFrame, QFileDialog
import sys
import os
import json
import datetime

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
        
        # 棋盘属性 - 增加基础尺寸
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
        
        # 棋步记录
        self.move_history = []
        
        # 设置组件最小大小
        min_board_width = self.board_size * self.base_cell_size + 2 * self.base_padding
        self.setMinimumSize(min_board_width, min_board_width)
        
        # 设置大小策略为扩展，允许组件随窗口调整而放大
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # 当前轮到谁下棋 - 1表示黑棋，2表示白棋
        self.current_player = 1
        
        # 游戏状态标志 - 只有游戏开始后才能下棋
        self.game_started = False
        self.game_over = False
        self.winner = 0  # 0表示无胜者，1表示黑棋胜，2表示白棋胜
        
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
        self.move_history = []  # 清空历史记录
        self.game_over = False  # 游戏未结束
        self.winner = 0  # 无胜者
        self.update()
    
    def undo_move(self):
        """悔棋 - 撤销最后一步"""
        # 如果历史记录为空，或者游戏已通过投降结束，不允许悔棋
        if not self.move_history or (self.game_over and self.winner > 0):
            return False
        
        # 获取最后一步
        last_move = self.move_history.pop()
        
        # 清除该位置的棋子
        self.board_data[last_move[0]][last_move[1]] = 0
        
        # 切换回前一个玩家
        self.current_player = 3 - self.current_player
        
        # 如果游戏已结束且不是因为投降，恢复为未结束状态
        if self.game_over and self.winner == 0:
            self.game_over = False
            
        self.update()
        return True
    
    def surrender(self):
        """投降操作"""
        if self.game_started and not self.game_over:
            self.game_over = True
            self.winner = 3 - self.current_player  # 对方获胜
            self.update()
            return True
        return False
    
    def save_game(self, filename=None):
        """保存游戏状态"""
        game_data = {
            "board_data": self.board_data,
            "current_player": self.current_player,
            "game_started": self.game_started,
            "game_over": self.game_over,
            "move_history": self.move_history,
            "winner": self.winner
        }
        
        if filename is None:
            default_filename = f"gomoku_game_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            return default_filename, game_data
        
        # 保存到文件
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(game_data, f, indent=2)
            
        return filename, game_data
    
    def paintEvent(self, event: QPaintEvent):
        """绘制棋盘和棋子"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)  # 抗锯齿
        
        # 计算当前实际的格子大小和边距
        # 使用较小的维度确保棋盘是正方形的
        size = min(self.width(), self.height())
        
        # 计算实际可用空间
        available_space = size - 2 * self.base_padding
        
        # 计算格子大小，确保能够整除
        cell_size = available_space / (self.board_size - 1)  # 修改：减1确保边缘线贴合
        
        # 计算实际棋盘的边距 - 居中对齐
        padding_x = (self.width() - (self.board_size - 1) * cell_size) / 2
        padding_y = (self.height() - (self.board_size - 1) * cell_size) / 2
        
        # 计算棋子大小
        stone_size = cell_size * 0.9  # 棋子大小为格子大小的90%
        
        # 获取当前风格
        style = self.BOARD_STYLES[self.current_style]
        
        # 绘制棋盘背景
        painter.fillRect(QRect(0, 0, self.width(), self.height()), QBrush(style["background"]))
        
        # 设置线条颜色和宽度
        line_width = max(1, int(cell_size / 15))
        painter.setPen(QPen(style["line"], line_width))
        
        # 绘制网格线 - 修改绘制方式确保线条贴合边界
        # 在每个循环中计算具体坐标，而不是使用公式
        
        # 绘制横线
        for i in range(self.board_size):
            y = int(padding_y + i * cell_size)
            # 横线从最左边到最右边
            painter.drawLine(
                int(padding_x), y,
                int(padding_x + (self.board_size - 1) * cell_size), y
            )
        
        # 绘制竖线
        for i in range(self.board_size):
            x = int(padding_x + i * cell_size)
            # 竖线从最上边到最下边
            painter.drawLine(
                x, int(padding_y),
                x, int(padding_y + (self.board_size - 1) * cell_size)
            )
        
        # 绘制天元和星位
        star_points = [(3, 3), (3, 11), (7, 7), (11, 3), (11, 11)]
        star_size = max(4, int(cell_size / 8))  # 星位点大小随格子大小缩放
        
        for x, y in star_points:
            painter.setBrush(QBrush(style["line"]))
            painter.drawEllipse(
                int(padding_x + x * cell_size - star_size / 2),
                int(padding_y + y * cell_size - star_size / 2),
                star_size, star_size
            )
        
        # 绘制棋子
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.board_data[row][col] != 0:
                    # 计算棋子位置 - 使用padding_x和padding_y
                    x = int(padding_x + col * cell_size - stone_size / 2)
                    y = int(padding_y + row * cell_size - stone_size / 2)
                    
                    # 设置棋子颜色 - 1是黑棋，2是白棋
                    if self.board_data[row][col] == 1:
                        painter.setBrush(QBrush(Qt.black))
                    else:
                        painter.setBrush(QBrush(Qt.white))
                    
                    # 绘制棋子边框，使用同样的线宽参数
                    painter.setPen(QPen(Qt.black if self.board_data[row][col] == 2 else Qt.gray, line_width))
                    
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
        # 如果游戏未开始或已结束，忽略点击
        if not self.game_started or self.game_over:
            return
            
        if event.button() == Qt.LeftButton:
            # 计算当前实际的格子大小和边距
            size = min(self.width(), self.height())
            available_space = size - 2 * self.base_padding
            cell_size = available_space / (self.board_size - 1)  # 与绘制时保持一致
            
            # 计算实际棋盘的边距 - 居中对齐
            padding_x = (self.width() - (self.board_size - 1) * cell_size) / 2
            padding_y = (self.height() - (self.board_size - 1) * cell_size) / 2
            
            # 计算点击的格子坐标
            col = round((event.x() - padding_x) / cell_size)
            row = round((event.y() - padding_y) / cell_size)
            
            # 检查坐标是否有效
            if 0 <= row < self.board_size and 0 <= col < self.board_size:
                # 检查该位置是否已有棋子
                if self.board_data[row][col] == 0:
                    # 放置当前玩家的棋子
                    self.board_data[row][col] = self.current_player
                    
                    # 记录棋步
                    self.move_history.append((row, col))
                    
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
        
        # 设置自身尺寸策略为扩展
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
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
        
        # 将棋盘添加到左侧容器，完全填充
        self.left_layout.addWidget(self.board, 1)  # 移除了Qt.AlignCenter参数，让棋盘完全填充容器
        
        # 创建右侧控制面板
        self.right_panel = QWidget()
        self.right_layout = QVBoxLayout(self.right_panel)
        self.right_layout.setContentsMargins(10, 10, 10, 10)
        self.right_layout.setSpacing(15)
        
        # 设置右侧面板的宽度策略，使其不随窗口拉伸
        self.right_panel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.right_panel.setFixedWidth(300)  # 略微减小右侧面板宽度
        
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
            "4. 点击「重新开始」可随时重置游戏\n"
            "5. 点击「悔棋」可撤销最后一步\n"
            "6. 点击「投降」可认输结束游戏\n"
            "7. 点击「保存」可保存当前游戏状态"
        )
        self.game_instructions.setWordWrap(True)
        self.game_instructions.setAlignment(Qt.AlignLeft)
        
        # 创建按钮布局
        self.button_layout = QVBoxLayout()  # 改为垂直布局
        self.start_button = PushButton("开始对局")
        self.restart_button = PushButton("重新开始")
        self.undo_button = PushButton("悔棋")
        self.surrender_button = PushButton("投降")
        self.save_button = PushButton("保存")
        
        # 设置按钮尺寸
        self.start_button.setFixedHeight(40)
        self.restart_button.setFixedHeight(40)
        self.undo_button.setFixedHeight(40)
        self.surrender_button.setFixedHeight(40)
        self.save_button.setFixedHeight(40)
        
        # 按钮添加到布局
        self.button_layout.addWidget(self.start_button)
        self.button_layout.addSpacing(10)
        self.button_layout.addWidget(self.restart_button)
        self.button_layout.addSpacing(10)
        self.button_layout.addWidget(self.undo_button)
        self.button_layout.addSpacing(10)
        self.button_layout.addWidget(self.surrender_button)
        self.button_layout.addSpacing(10)
        self.button_layout.addWidget(self.save_button)
        
        # 添加组件到右侧布局
        self.right_layout.addWidget(self.title_label)
        self.right_layout.addSpacing(10)
        self.right_layout.addLayout(self.controls_layout)
        self.right_layout.addWidget(self.separator)
        self.right_layout.addWidget(self.player_info)
        self.right_layout.addSpacing(20)
        self.right_layout.addWidget(self.game_instructions)
        self.right_layout.addSpacing(20)
        self.right_layout.addLayout(self.button_layout)  # 添加按钮布局
        self.right_layout.addStretch(1)  # 添加伸缩器使组件靠上对齐
        
        # 将棋盘容器和右侧面板添加到主布局，增加棋盘比例
        self.main_layout.addWidget(self.left_container, 3)  # 给棋盘区域更多的比例
        self.main_layout.addWidget(self.right_panel, 0)  # 右侧面板不拉伸
        
        # 设置对象名称，用于导航
        self.setObjectName('App-Interface')
        
        # 连接按钮事件
        self.start_button.clicked.connect(self.onStartGame)
        self.restart_button.clicked.connect(self.onRestartGame)
        self.undo_button.clicked.connect(self.onUndoMove)
        self.surrender_button.clicked.connect(self.onSurrender)
        self.save_button.clicked.connect(self.onSaveGame)
        
        # 初始化时更新玩家信息
        self.update_player_info()
        
        # 设置初始游戏状态
        self.board.game_started = False
    
    def change_board_style(self, index):
        """更改棋盘风格"""
        self.board.set_style(index)
    
    def update_player_info(self):
        """更新当前玩家信息"""
        if self.board.game_over:
            player_text = "游戏结束！胜者：黑棋" if self.board.winner == 1 else "游戏结束！胜者：白棋"
        else:
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
    
    def onUndoMove(self):
        """悔棋"""
        # 检查是否因投降而结束游戏
        if self.board.game_over and self.board.winner > 0:
            InfoBar.warning(
                title='无法悔棋',
                content="游戏已经结束，不能悔棋",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
            return
            
        if self.board.undo_move():
            self.update_player_info()
            InfoBar.info(
                title='悔棋成功',
                content="已撤销最后一步",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
        else:
            InfoBar.warning(
                title='悔棋失败',
                content="没有可撤销的步骤",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
    
    def onSurrender(self):
        """投降"""
        if self.board.surrender():
            self.update_player_info()
            InfoBar.info(
                title='投降成功',
                content="游戏结束，胜者为对方",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
        else:
            InfoBar.warning(
                title='投降失败',
                content="当前无法投降",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
    
    def onSaveGame(self):
        """保存游戏"""
        filename, game_data = self.board.save_game()
        save_path, _ = QFileDialog.getSaveFileName(self, "保存游戏", filename, "JSON文件 (*.json)")
        if save_path:
            self.board.save_game(save_path)
            InfoBar.success(
                title='保存成功',
                content=f"游戏已保存到 {save_path}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
        else:
            InfoBar.warning(
                title='保存失败',
                content="未选择保存路径",
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
        self.resize(1000, 800)  # 从900x700增加到1000x800
        
        # 设置窗口在屏幕中央显示
        screen = QApplication.desktop().availableGeometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )
        
        # 创建主窗口部件
        self.central_widget = QWidget(self)
        
        # 创建棋盘组件并设置尺寸策略
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)  # 减小边距，为棋盘留更多空间
        
        self.board_widget = BoardWidget(self, style_index)
        self.board_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # 创建关闭按钮
        self.button_layout = QHBoxLayout()
        self.close_button = PushButton("关闭窗口")
        self.close_button.setFixedWidth(150)  # 设置固定宽度
        self.close_button.clicked.connect(self.close)
        self.button_layout.addStretch(1)
        self.button_layout.addWidget(self.close_button)
        
        # 添加到布局时设置拉伸因子
        self.main_layout.addWidget(self.board_widget, 1)  # 添加拉伸因子，确保棋盘占据所有可用空间
        self.main_layout.addLayout(self.button_layout, 0)  # 按钮布局不拉伸
        
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