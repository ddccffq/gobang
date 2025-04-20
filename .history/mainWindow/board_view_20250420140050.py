# coding:utf-8
from PyQt5.QtCore import Qt, QRect, QPoint, QSize
from PyQt5.QtGui import QIcon, QFont, QPainter, QPen, QBrush, QColor, QPaintEvent
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QApplication, QSizePolicy, QFrame, QFileDialog, QMessageBox, QScrollArea
import sys
import os
import json
import datetime

from qfluentwidgets import FluentIcon as FIF, PushButton, ComboBox, isDarkTheme, InfoBar, InfoBarPosition
from qframelesswindow import FramelessWindow

# 修改导入历史记录管理器
from mainWindow.game_history_manager import GameHistoryManager


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
        
        # 添加禁手位置列表
        self.forbidden_positions = []
        
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
    
    def reset_game(self, start_immediately=True):
        """重置游戏状态"""
        self.board_data = [[0 for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.current_player = 1  # 黑棋先行
        self.game_started = start_immediately  # 根据参数决定游戏是否立即开始
        self.move_history = []  # 清空历史记录
        self.game_over = False  # 游戏未结束
        self.winner = 0  # 无胜者
        
        # 清空禁手位置
        self.forbidden_positions = []
        
        # 如果开始是黑棋回合，检测禁手
        if start_immediately and self.current_player == 1:
            self.update_forbidden_positions()
            
        self.update()
    
    def update_forbidden_positions(self):
        """更新所有禁手位置"""
        self.forbidden_positions = []
        # 只在黑棋回合且游戏进行中检测禁手
        if self.current_player != 1 or not self.game_started or self.game_over:
            return
            
        # 检查所有空位
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.board_data[row][col] == 0:  # 空位
                    if self.is_forbidden_move(row, col):
                        self.forbidden_positions.append((row, col))
    
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
            
        # 如果悔棋后是黑棋回合，更新禁手位置
        if self.current_player == 1:
            self.update_forbidden_positions()
            
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
        # 获取当前时间戳
        timestamp = datetime.datetime.now().isoformat()
        
        game_data = {
            "board_data": self.board_data,
            "current_player": self.current_player,
            "game_started": self.game_started,
            "game_over": self.game_over,
            "move_history": self.move_history,
            "winner": self.winner,
            "timestamp": timestamp,  # 添加时间戳
            "style_index": list(self.BOARD_STYLES.keys()).index(self.current_style),  # 添加棋盘风格索引
            "player_info": {
                "player1": "玩家",  # 玩家1是人类
                "player2": "AI"     # 玩家2是AI
            }
        }
        
        # 导入历史记录管理器
        from mainWindow.game_history_manager import GameHistoryManager
        history_manager = GameHistoryManager()
        
        if filename is None:
            # 生成默认文件名
            winner_str = "黑胜" if self.winner == 1 else "白胜" if self.winner == 2 else "未结束"
            default_filename = f"对战_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{winner_str}.json"
            return default_filename, game_data
        
        # 保存到指定文件
        try:
            saved_path = history_manager.save_game(game_data, os.path.basename(filename))
            if saved_path:
                return saved_path, game_data
            return None, game_data
        except Exception as e:
            print(f"保存游戏失败: {str(e)}")
            return None, game_data
    
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
                        text_color = Qt.white  # 黑棋上使用白色文字
                    else:
                        painter.setBrush(QBrush(Qt.white))
                        text_color = Qt.black  # 白棋上使用黑色文字
                    
                    # 绘制棋子边框，使用同样的线宽参数
                    painter.setPen(QPen(Qt.black if self.board_data[row][col] == 2 else Qt.gray, line_width))
                    
                    # 绘制棋子
                    painter.drawEllipse(x, y, int(stone_size), int(stone_size))
                    
                    # 查找该棋子的序号
                    move_number = self.find_move_number(row, col)
                    if move_number > 0:
                        # 设置序号文本字体和颜色
                        number_font = painter.font()
                        number_font.setPointSize(int(stone_size / 3))  # 字体大小约为棋子大小的1/3
                        number_font.setBold(True)
                        painter.setFont(number_font)
                        painter.setPen(QPen(text_color))
                        
                        # 绘制序号文本
                        number_rect = QRect(
                            x, y, int(stone_size), int(stone_size)
                        )  # 修复: 添加缺失的右括号
                        painter.drawText(number_rect, Qt.AlignCenter, str(move_number))
        
        # 绘制禁手标记（如果有）
        if self.current_player == 1 and self.game_started and not self.game_over:
            for row, col in self.forbidden_positions:
                # 计算禁手标记位置
                x = int(padding_x + col * cell_size)
                y = int(padding_y + row * cell_size)
                
                # 设置禁手标记样式 - 红色粗线
                mark_size = int(cell_size * 0.4)  # 标记大小为格子大小的40%
                mark_pen = QPen(QColor(255, 0, 0), line_width * 1.5)
                painter.setPen(mark_pen)
                
                # 绘制X形标记
                painter.drawLine(
                    x - mark_size, y - mark_size,
                    x + mark_size, y + mark_size
                )
                painter.drawLine(
                    x + mark_size, y - mark_size,
                    x - mark_size, y + mark_size
                )
        
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
    
    def find_move_number(self, row, col):
        """查找指定位置棋子的序号"""
        for i, move in enumerate(self.move_history):
            if move[0] == row and move[1] == col:
                return i + 1  # 序号从1开始
        return 0  # 如果没找到（棋盘被直接设置而不是通过下棋），返回0

    def is_forbidden_move(self, row, col):
        """完整的黑棋禁手检测
        包括：三三禁手、四四禁手、长连禁手"""
        # 先在棋盘上模拟落子以便后续检测
        self.board_data[row][col] = 1  # 假设是黑子
        
        # 长连禁手(已经实现) - 连子超过5个
        longConnect = self.check_long_connect(row, col)
        
        # 三三禁手 - 检查是否形成两个以上的活三
        threeThree = self.check_three_three(row, col)
        
        # 四四禁手 - 检查是否形成两个以上的活四
        fourFour = self.check_four_four(row, col)
        
        # 恢复棋盘状态
        self.board_data[row][col] = 0
        
        return longConnect or threeThree or fourFour
    
    def check_long_connect(self, row, col):
        """检查长连禁手 - 超过5个连子"""
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]  # 横、竖、正斜、反斜四个方向
        
        for dx, dy in directions:
            count = 1  # 当前落子点计为1
            
            # 沿着正方向检查连子
            for step in range(1, 6):
                x, y = row + dx * step, col + dy * step
                if 0 <= x < self.board_size and 0 <= y < self.board_size and self.board_data[x][y] == 1:
                    count += 1
                else:
                    break
                    
            # 沿着反方向检查连子
            for step in range(1, 6):
                x, y = row - dx * step, col - dy * step
                if 0 <= x < self.board_size and 0 <= y < self.board_size and self.board_data[x][y] == 1:
                    count += 1
                else:
                    break
                    
            # 超过5个连子属于长连禁手
            if count > 5:
                return True
                
        return False
    
    def check_three_three(self, row, col):
        """检查三三禁手 - 同时形成两个以上的活三"""
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        active_threes = 0
        
        for dx, dy in directions:
            # 检查这个方向是否形成活三
            if self.is_active_three(row, col, dx, dy):
                active_threes += 1
                
        # 两个及以上活三形成三三禁手
        return active_threes >= 2
    
    def is_active_three(self, row, col, dx, dy):
        """检查指定方向上是否形成活三"""
        # 活三的定义：XXX_ 或 _XXX 或 X_XX 或 XX_X，两端都是空格
        
        # 获取当前方向上的连续模式
        pattern = self.get_line_pattern(row, col, dx, dy)
        
        # 检查是否为活三模式
        active_three_patterns = [
            '...111..',  # _XXX_
            '..1.11..',  # _X_XX_
            '..11.1..',  # _XX_X_
        ]
        
        for p in active_three_patterns:
            if p in pattern:
                return True
                
        return False
    
    def check_four_four(self, row, col):
        """检查四四禁手 - 同时形成两个以上的活四"""
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        active_fours = 0
        
        for dx, dy in directions:
            # 检查这个方向是否形成活四
            if self.is_active_four(row, col, dx, dy):
                active_fours += 1
                
        # 两个及以上活四形成四四禁手
        return active_fours >= 2
    
    def is_active_four(self, row, col, dx, dy):
        """检查指定方向上是否形成活四"""
        # 活四的定义：XXXX_ 或 _XXXX 或 X_XXX 或 XX_XX 或 XXX_X，一端是空格
        
        # 获取当前方向上的连续模式
        pattern = self.get_line_pattern(row, col, dx, dy)
        
        # 检查是否为活四模式
        active_four_patterns = [
            '..1111.',  # _XXXX
            '.1111..',  # XXXX_
            '.1.111.',  # X_XXX
            '.11.11.',  # XX_XX
            '.111.1.',  # XXX_X
        ]
        
        for p in active_four_patterns:
            if p in pattern:
                return True
                
        return False
    
    def get_line_pattern(self, row, col, dx, dy):
        """获取指定方向上的棋子模式，用于禁手检测
        使用 '0' 表示空位，'1' 表示黑子，'2' 表示白子，'.' 表示棋盘外区域"""不是默认显示选中项
        pattern = []
        
        # 向两边各延伸5格，共11格
        for step in range(-5, 6):self.style_combo.addItems(self.board.get_style_names())
            x, y = row + dx * step, col + dy * stepe_combo.setCurrentIndex(style_index)
            if 0 <= x < self.board_size and 0 <= y < self.board_size:onnect(self.change_board_style)
                pattern.append(str(self.board_data[x][y]))
            else:
                pattern.append('.')  # 表示棋盘外elf)
                (self)
        return ''.join(pattern)
self.side_combo.setPlaceholderText("选择执棋方")

class BoardWidget(QWidget):
    """五子棋游戏组件，可嵌入到应用界面中"""
    def __init__(self, parent=None, style_index=0):
        super().__init__(parent)d.connect(self.on_side_changed)
        # 设置自身尺寸策略为扩展
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)ntrols_layout.addWidget(self.style_label)
        # 创建主布局 - 改为水平布局，左侧放棋盘，右侧放控制面板idget(self.style_combo)
        self.main_layout = QHBoxLayout(self)abel)
        self.main_layout.setContentsMargins(20, 20, 20, 20)bo)
        self.main_layout.setSpacing(20)  # 增加间距self.controls_layout.addStretch(1)
        # 创建左侧容器，用于保持棋盘居中
        self.left_container = QWidget()
        self.left_layout = QVBoxLayout(self.left_container)
        self.left_layout.setContentsMargins(0, 0, 0, 0).HLine)
        # 创建棋盘实例dow(QFrame.Sunken)
        self.board = GoBoardWidget(self, style_index)
        # 左侧容器采用扩展策略，允许随窗口放大
        self.left_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)黑棋")
        # 将棋盘添加到左侧容器，完全填充nfo.setAlignment(Qt.AlignCenter)
        self.left_layout.addWidget(self.board, 1)  # 移除了Qt.AlignCenter参数，让棋盘完全填充容器nfo.font()
        # 创建右侧控制面板(16)
        self.right_panel = QWidget()ont(info_font)
        self.right_layout = QVBoxLayout(self.right_panel)
        self.right_layout.setContentsMargins(10, 10, 10, 10)Label(
        self.right_layout.setSpacing(15)
        # 设置右侧面板的宽度策略，使其不随窗口拉伸   "1. 点击「开始对局」按钮开始游戏\n"
        self.right_panel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.right_panel.setFixedWidth(300)  # 略微减小右侧面板宽度
        # 创建标题标签点击「悔棋」可撤销最后一步\n"
        self.title_label = QLabel("五子棋游戏")
        self.title_label.setAlignment(Qt.AlignCenter)
        title_font = self.title_label.font()
        title_font.setPointSize(24)
        title_font.setBold(True)e_instructions.setAlignment(Qt.AlignLeft)
        self.title_label.setFont(title_font)
        # 创建操作区域布局 # 改为垂直布局
        self.controls_layout = QHBoxLayout()
        # 创建棋盘风格选择下拉框self.undo_button = PushButton("悔棋")
        self.style_label = QLabel("棋盘风格：")game_button = PushButton("结束游戏")
        self.style_combo = ComboBox(self)
        # 填充风格选择下拉框40)
        self.style_combo.addItems(self.board.get_style_names())
        self.style_combo.setCurrentIndex(style_index)ht(40)
        self.style_combo.currentIndexChanged.connect(self.change_board_style)
        # 按钮添加到布局
        # 增加执棋方选择_layout.addWidget(self.start_button)
        self.side_label = QLabel("执棋方：", self)
        self.side_combo = ComboBox(self)f.undo_button)
        self.side_combo.addItems(["玩家执黑", "玩家执白"])
        self.side_combo.setCurrentIndex(0)button)
        self.player_side = "black"
        self.side_combo.currentIndexChanged.connect(self.on_side_changed)
        
        self.controls_layout.addWidget(self.style_label)
        self.controls_layout.addWidget(self.style_combo)
        self.controls_layout.addWidget(self.side_label)
        self.controls_layout.addWidget(self.side_combo)self.right_layout.addWidget(self.player_info)
        self.controls_layout.addStretch(1)ing(20)
        
        # 创建分隔线
        self.separator = QFrame()self.right_layout.addLayout(self.button_layout)  # 添加按钮布局
        self.separator.setFrameShape(QFrame.HLine)yout.addStretch(1)  # 添加伸缩器使组件靠上对齐
        self.separator.setFrameShadow(QFrame.Sunken)
        右侧面板添加到主布局，增加棋盘比例
        # 玩家信息标签棋盘区域更多的比例
        self.player_info = QLabel("当前玩家：黑棋")# 右侧面板不拉伸
        self.player_info.setAlignment(Qt.AlignCenter)
        info_font = self.player_info.font()航
        info_font.setPointSize(16)nterface')
        self.player_info.setFont(info_font)# 连接按钮事件
        # 创建游戏说明_button.clicked.connect(self.onStartGame)    
        self.game_instructions = QLabel(t(self.onUndoMove)
            "游戏说明：\n"    self.end_game_button.clicked.connect(self.onEndGame)
            "1. 点击「开始对局」按钮开始游戏\n"
            "2. 黑棋先行，双方轮流下棋\n"player_info()
            "3. 先连成五子一线者获胜\n"
            "4. 点击「悔棋」可撤销最后一步\n"    # 设置初始游戏状态
            "5. 点击「结束游戏」可结束当前游戏\n"se
            "6. 游戏会自动保存到历史记录"
        )
        self.game_instructions.setWordWrap(True)
        self.game_instructions.setAlignment(Qt.AlignLeft)self.board.set_style(index)    
        # 创建按钮布局
        self.button_layout = QVBoxLayout()  # 改为垂直布局
        self.start_button = PushButton("开始对局")
        self.undo_button = PushButton("悔棋")player_side = "black" if index == 0 else "white"
        self.end_game_button = PushButton("结束游戏")
        # 设置按钮尺寸
        self.start_button.setFixedHeight(40)
        self.undo_button.setFixedHeight(40)nt_player == 1:
        self.end_game_button.setFixedHeight(40)        self.board.update_forbidden_positions()
        
        # 按钮添加到布局.forbidden_positions = []  # 白棋回合清空禁手
        self.button_layout.addWidget(self.start_button)
        self.button_layout.addSpacing(10)
        self.button_layout.addWidget(self.undo_button)board.update()
        self.button_layout.addSpacing(10)
        self.button_layout.addWidget(self.end_game_button)
            """更新当前玩家信息"""
        # 添加组件到右侧布局_over:
        self.right_layout.addWidget(self.title_label)游戏结束！胜者：黑棋" if self.board.winner == 1 else "游戏结束！胜者：白棋"
        self.right_layout.addSpacing(10)
        self.right_layout.addLayout(self.controls_layout)    player_text = "当前玩家：黑棋" if self.board.current_player == 1 else "当前玩家：白棋"
        self.right_layout.addWidget(self.separator).setText(player_text)
        self.right_layout.addWidget(self.player_info)
        self.right_layout.addSpacing(20)
        self.right_layout.addWidget(self.game_instructions)
        self.right_layout.addSpacing(20)
        self.right_layout.addLayout(self.button_layout)  # 添加按钮布局
        self.right_layout.addStretch(1)  # 添加伸缩器使组件靠上对齐
        ark_mode:
        # 将棋盘容器和右侧面板添加到主布局，增加棋盘比例换到暗黑模式
        self.main_layout.addWidget(self.left_container, 3)  # 给棋盘区域更多的比例tyle_names()):
        self.main_layout.addWidget(self.right_panel, 0)  # 右侧面板不拉伸
        
        # 设置对象名称，用于导航
        self.setObjectName('App-Interface')
        # 连接按钮事件
        self.start_button.clicked.connect(self.onStartGame)     white;")
        self.undo_button.clicked.connect(self.onUndoMove)
        self.end_game_button.clicked.connect(self.onEndGame)self.game_instructions.setStyleSheet("color: white;")
        # 初始化时更新玩家信息_label.setStyleSheet("color: white;")
        self.update_player_info()
        
        # 设置初始游戏状态
        self.board.game_started = Falseex(0)  # 经典木色
        
    def change_board_style(self, index):恢复默认文本颜色
        """更改棋盘风格"""er_info.setStyleSheet("")
        self.board.set_style(index)            self.style_label.setStyleSheet("")
    ructions.setStyleSheet("")
    def on_side_changed(self, index):itle_label.setStyleSheet("")
        """更改执棋方"""
        self.player_side = "black" if index == 0 else "white"
        self.board.current_player = 1 if index == 0 else 2
        
        # 如果是黑棋回合，检测禁手rtGame(self):
        if self.board.current_player == 1:
            self.board.update_forbidden_positions().board.reset_game(start_immediately=True)  # 游戏立即开始
        else:
            self.board.forbidden_positions = []  # 白棋回合清空禁手
            
        self.update_player_info():
        self.board.update()ayer = 1
        
    def update_player_info(self):手，检测并显示禁手
        """更新当前玩家信息"""rrent_player == 1:
        if self.board.game_over:ate_forbidden_positions()
            player_text = "游戏结束！胜者：黑棋" if self.board.winner == 1 else "游戏结束！胜者：白棋"
        else:
            player_text = "当前玩家：黑棋" if self.board.current_player == 1 else "当前玩家：白棋"
        self.player_info.setText(player_text)
    
    def updateStyle(self):始',
        """更新界面样式以适应主题变化"""   content="黑棋先行，请点击棋盘落子",
        dark_mode = isDarkTheme()        orient=Qt.Horizontal,
        ue,
        # 可能需要根据主题调整棋盘样式tion=InfoBarPosition.TOP,
        if dark_mode:000,
            # 将棋盘风格切换到暗黑模式
            for i, style_name in enumerate(self.board.get_style_names()):
                if style_name == "暗黑模式":
                    self.style_combo.setCurrentIndex(i)
                    break
            
            # 更新文本颜色d.winner > 0:
            self.player_info.setStyleSheet("color: white;")
            self.style_label.setStyleSheet("color: white;")',
            self.game_instructions.setStyleSheet("color: white;")   content="游戏已经结束，不能悔棋",
            self.title_label.setStyleSheet("color: white;")ient=Qt.Horizontal,
        else:    isClosable=True,
            # 如果当前是暗黑模式，切换到经典木色sition.TOP,
            if self.board.current_style == "暗黑模式":
                self.style_combo.setCurrentIndex(0)  # 经典木色lf
            
            # 恢复默认文本颜色
            self.player_info.setStyleSheet("")
            self.style_label.setStyleSheet("")):
            self.game_instructions.setStyleSheet("")
            self.title_label.setStyleSheet("")
        ',
        # 刷新界面   content="已撤销最后一步",
        self.update()   orient=Qt.Horizontal,
    rue,
    def onStartGame(self):BarPosition.TOP,
        """开始游戏"""
        self.board.reset_game(start_immediately=True)  # 游戏立即开始
        # 根据选择设置先手
        if self.player_side == "white":
            self.board.current_player = 2
        else:',
            self.board.current_player = 1   content="没有可撤销的步骤",
                        orient=Qt.Horizontal,
        # 如果是黑棋先手，检测并显示禁手le=True,
        if self.board.current_player == 1:InfoBarPosition.TOP,
            self.board.update_forbidden_positions()
            
        self.update_player_info()
        
        # 显示提示信息
        InfoBar.success(
            title='游戏已开始',
            content="黑棋先行，请点击棋盘落子",
            orient=Qt.Horizontal,',
            isClosable=True,   content="游戏尚未开始",
            position=InfoBarPosition.TOP,ient=Qt.Horizontal,
            duration=3000,        isClosable=True,
            parent=selfPosition.TOP,
        ),
    
    def onUndoMove(self):
        """悔棋"""return
        # 检查是否因投降而结束游戏
        if self.board.game_over and self.board.winner > 0:r:
            InfoBar.warning(
                title='无法悔棋',rt_immediately=False)
                content="游戏已经结束，不能悔棋",nfo()
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,戏',
                duration=3000,   content="棋盘已清空，请点击「开始对局」按钮",
                parent=selfient=Qt.Horizontal,
            )        isClosable=True,
            returnInfoBarPosition.TOP,
            
        if self.board.undo_move():
            self.update_player_info()
            InfoBar.info(
                title='悔棋成功',
                content="已撤销最后一步",
                orient=Qt.Horizontal,in self.board.board_data):
                isClosable=True, 只有在棋盘上有棋子时才询问是否保存
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )geBox.Discard | QMessageBox.Cancel, 
        else:
            InfoBar.warning(
                title='悔棋失败',geBox.Cancel:
                content="没有可撤销的步骤",
                orient=Qt.Horizontal,sageBox.Save:
                isClosable=True,)  # 用户选择保存
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self 棋盘上没有棋子，只需确认是否结束
            )n(
    
    def onEndGame(self):        "确定要结束当前游戏吗？",
        """结束游戏并准备重新开始"""MessageBox.Yes | QMessageBox.No, 
        if not self.board.game_started:
            InfoBar.warning(
                title='无法结束',ox.No:
                content="游戏尚未开始",        return  # 用户取消操作
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,self.board.game_over = True
                duration=3000,ner = 0  # 没有胜者
                parent=self
            )
            return# 根据是否保存显示不同提示
        保存" if (reply == QMessageBox.Save) else ""
        if self.board.game_over:
            # 如果游戏已经结束，直接重置棋盘
            self.board.reset_game(start_immediately=False)rt_immediately=False)
            self.update_player_info()nfo()
            
            InfoBar.info(
                title='准备新游戏',束',
                content="棋盘已清空，请点击「开始对局」按钮",   content=f"游戏已结束{save_msg}，棋盘已清空，请点击「开始对局」按钮开始新游戏",
                orient=Qt.Horizontal,        orient=Qt.Horizontal,
                isClosable=True,True,
                position=InfoBarPosition.TOP,Position.TOP,
                duration=3000,
                parent=self
            )
            return
        
        # 询问是否结束游戏并提供保存选项"""内部方法：保存游戏到历史记录"""
        if any(any(row) for row in self.board.board_data):.game_started:
            # 只有在棋盘上有棋子时才询问是否保存
            reply = QMessageBox.question(
                self, '结束游戏', 戏数据
                "确定要结束当前游戏吗？",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel, 
                QMessageBox.Save# 导入历史记录管理器获取保存目录
            )indow.game_history_manager import GameHistoryManager
            if reply == QMessageBox.Cancel:meHistoryManager()
                return  # 用户取消操作
            elif reply == QMessageBox.Save:_manager.history_dir, os.path.basename(filename))
                self.saveGame()  # 用户选择保存ame(save_path)
            # 如果选择Discard，则不保存直接结束
        else:
            # 棋盘上没有棋子，只需确认是否结束
            reply = QMessageBox.question(',
                self, '结束游戏',    content=f"游戏已自动保存到历史记录",
                "确定要结束当前游戏吗？",Qt.Horizontal,
                QMessageBox.Yes | QMessageBox.No, osable=True,
                QMessageBox.Yes            position=InfoBarPosition.TOP,
            )
            if reply == QMessageBox.No:lf
                return  # 用户取消操作)
        rue
        # 先通知游戏结束
        self.board.game_over = True
        self.board.winner = 0  # 没有胜者ta(self, game_data):
        self.update_player_info()
        
        # 根据是否保存显示不同提示
        save_msg = "并保存" if (reply == QMessageBox.Save) else ""
        
        # 立即重置棋盘，准备新游戏
        self.board.reset_game(start_immediately=False)self.board.current_player = game_data['current_player']
        self.update_player_info()
        
        InfoBar.info(self.board.game_started = game_data['game_started']
            title='游戏已结束',rd.game_over = game_data['game_over']
            content=f"游戏已结束{save_msg}，棋盘已清空，请点击「开始对局」按钮开始新游戏",'winner']
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,self.board.move_history = game_data['move_history']
            duration=3000,
            parent=self
        )if 'style_index' in game_data:
    lf.style_combo.setCurrentIndex(game_data['style_index'])
    def saveGame(self):style(game_data['style_index'])
        """内部方法：保存游戏到历史记录"""
        if not self.board.game_started:
            return False
            
        # 获取默认文件名和游戏数据
        filename, game_data = self.board.save_game()
        
        # 导入历史记录管理器获取保存目录
        from mainWindow.game_history_manager import GameHistoryManager
        history_manager = GameHistoryManager()
        # 直接保存到默认路径错误',
        save_path = os.path.join(history_manager.history_dir, os.path.basename(filename))   content=f"加载游戏数据失败: {str(e)}",
        result, _ = self.board.save_game(save_path)t.Horizontal,
                        isClosable=True,
        if result:                position=InfoBarPosition.TOP,
            InfoBar.success(
                title='自动保存',arent=self
                content=f"游戏已自动保存到历史记录",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self子棋游戏窗口"""
            )lf, parent=None, style_index=0):
            return True
        return False
    
    def load_game_data(self, game_data):wIcon(FIF.GAME.icon())
        """从历史记录加载游戏数据"""
        try:口
            # 设置棋盘数据
            self.board.board_data = game_data['board_data']
            elf.resize(1000, 800)  # 从900x700增加到1000x800
            # 设置当前玩家# 设置窗口在屏幕中央显示
            self.board.current_player = game_data['current_player']QApplication.desktop().availableGeometry()
            
            # 设置游戏状态    (screen.width() - self.width()) // 2,
            self.board.game_started = game_data['game_started']ght() - self.height()) // 2
            self.board.game_over = game_data['game_over']
            self.board.winner = game_data['winner']
            # 创建主窗口部件
            # 设置棋步历史
            self.board.move_history = game_data['move_history']
            # 创建棋盘组件并设置尺寸策略
            # 设置棋盘风格n_layout = QVBoxLayout(self.central_widget)
            if 'style_index' in game_data:s(10, 10, 10, 10)  # 减小边距，为棋盘留更多空间
                self.style_combo.setCurrentIndex(game_data['style_index'])
                self.board.set_style(game_data['style_index'])dex)
            xpanding, QSizePolicy.Expanding)
            # 更新玩家信息显示
            self.update_player_info()
            self.button_layout = QHBoxLayout()
            # 重绘棋盘ton = PushButton("关闭窗口")
            self.board.update()
            return True
        except Exception as e:self.button_layout.addStretch(1)
            print(f"加载游戏数据失败: {str(e)}")_layout.addWidget(self.close_button)
            InfoBar.error(
                title='数据加载错误',
                content=f"加载游戏数据失败: {str(e)}",, 1)  # 添加拉伸因子，确保棋盘占据所有可用空间
                orient=Qt.Horizontal,    self.main_layout.addLayout(self.button_layout, 0)  # 按钮布局不拉伸
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,t(self))
                parent=selfntentsMargins(0, 48, 0, 0)  # 为标题栏留出空间
            )elf.central_widget)
            return False    
    def closeEvent(self, event):

class BoardWindow(FramelessWindow):int("游戏窗口正在关闭，清理资源...")
    """五子棋游戏窗口"""
    def __init__(self, parent=None, style_index=0):(event)
        super().__init__(parent)
        # 设置窗口标题和图标
        self.setWindowTitle("五子棋游戏")if __name__ == "__main__":






















































    sys.exit(app.exec_())    window.show()    window = BoardWindow()    app = QApplication(sys.argv)    # 测试代码if __name__ == "__main__":        super().closeEvent(event)        # 这里可以添加任何需要的资源清理代码        print("游戏窗口正在关闭，清理资源...")        """窗口关闭时的清理工作"""    def closeEvent(self, event):            self.layout().addWidget(self.central_widget)        self.layout().setContentsMargins(0, 48, 0, 0)  # 为标题栏留出空间        self.setLayout(QVBoxLayout(self))        # 设置窗口的内容部件                self.main_layout.addLayout(self.button_layout, 0)  # 按钮布局不拉伸        self.main_layout.addWidget(self.board_widget, 1)  # 添加拉伸因子，确保棋盘占据所有可用空间        # 添加到布局时设置拉伸因子                self.button_layout.addWidget(self.close_button)        self.button_layout.addStretch(1)        self.close_button.clicked.connect(self.close)        self.close_button.setFixedWidth(150)  # 设置固定宽度        self.close_button = PushButton("关闭窗口")        self.button_layout = QHBoxLayout()        # 创建关闭按钮                self.board_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)        self.board_widget = BoardWidget(self, style_index)                self.main_layout.setContentsMargins(10, 10, 10, 10)  # 减小边距，为棋盘留更多空间        self.main_layout = QVBoxLayout(self.central_widget)        # 创建棋盘组件并设置尺寸策略                self.central_widget = QWidget(self)        # 创建主窗口部件                )            (screen.height() - self.height()) // 2            (screen.width() - self.width()) // 2,        self.move(        screen = QApplication.desktop().availableGeometry()        # 设置窗口在屏幕中央显示        self.resize(1000, 800)  # 从900x700增加到1000x800        # 设置窗口大小，增加宽度以适应新布局        self.setWindowFlags(Qt.Window)        # 设置窗口为独立窗口                self.setWindowIcon(FIF.GAME.icon())    # 测试代码
    app = QApplication(sys.argv)
    window = BoardWindow()
    window.show()
    sys.exit(app.exec_())
