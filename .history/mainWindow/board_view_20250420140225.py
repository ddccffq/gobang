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
        """黑棋超连（连>5）禁手检测"""
        for dx, dy in [(1,0), (0,1), (1,1), (1,-1)]:
            c = 1  # 当前位置算作一个棋子
            # 向一个方向查找连续黑棋ow][col] = 1  # 假设是黑子
            for step in range(1, 6):
                x, y = row + dx * step, col + dy * step
                if 0 <= x < self.board_size and 0 <= y < self.board_size and self.board_data[x][y] == 1:
                    c += 1
                else:形成两个以上的活三
                    break.check_three_three(row, col)
            # 向相反方向查找连续黑棋
            for step in range(1, 6):
                x, y = row - dx * step, col - dy * step
                if 0 <= x < self.board_size and 0 <= y < self.board_size and self.board_data[x][y] == 1:
                    c += 1
                else:ta[row][col] = 0
                    break
            # 如果总连子数超过5，则为禁手r threeThree or fourFour
            if c > 5:
                return Trueself, row, col):
        return False超过5个连子"""
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]  # 横、竖、正斜、反斜四个方向
    def mousePressEvent(self, event):
        """处理鼠标点击事件，放置棋子"""tions:
        if not self.game_started or self.game_over:
            return
        if event.button() != Qt.LeftButton:
            returnep in range(1, 6):
                x, y = row + dx * step, col + dy * step
        # 计算格子大小和边距0 <= x < self.board_size and 0 <= y < self.board_size and self.board_data[x][y] == 1:
        size = min(self.width(), self.height())
        available = size - 2 * self.base_padding
        cell_size = available / (self.board_size - 1)
        padding_x = (self.width() - (self.board_size - 1) * cell_size) / 2
        padding_y = (self.height() - (self.board_size - 1) * cell_size) / 2
            for step in range(1, 6):
        # 计算落子行列x, y = row - dx * step, col - dy * step
        col = round((event.x() - padding_x) / cell_size) self.board_size and self.board_data[x][y] == 1:
        row = round((event.y() - padding_y) / cell_size)
        if not (0 <= row < self.board_size and 0 <= col < self.board_size):
            return  break
        if self.board_data[row][col] != 0:
            return连子属于长连禁手
            if count > 5:
        # 黑棋禁手检测（超连>5） True
        if self.current_player == 1 and self.is_forbidden_move(row, col):
            InfoBar.warning(
                title='禁手',
                content='黑棋超连（>5）禁手，不允许落子',
                orient=Qt.Horizontal,
                isClosable=True,, 1), (1, 1), (1, -1)]
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=selftions:
            ) 检查这个方向是否形成活三
            returnf.is_active_three(row, col, dx, dy):
                active_threes += 1
        # 放置棋子并记录
        self.board_data[row][col] = self.current_player
        self.move_history.append((row, col))
        
        # 检查胜负ive_three(self, row, col, dx, dy):
        if self.check_win(row, col):
            self.game_over = True# 活三的定义：XXX_ 或 _XXX 或 X_XX 或 XX_X，两端都是空格
            self.winner = self.current_player
            
            # 显示胜利消息col, dx, dy)
            winner_text = "黑棋" if self.current_player == 1 else "白棋"
            InfoBar.success(
                title=f'{winner_text}胜利!',active_three_patterns = [
                content=f"{winner_text}已经获胜！您可以悔棋或开始新游戏。",',  # _XXX_
                orient=Qt.Horizontal,            '..1.11..',  # _X_XX_
                isClosable=True,.',  # _XX_X_
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )            if p in pattern:
                            return True
            # 更新界面
            self.update()
            
            # 通知父组件更新玩家信息w, col):
            parent = self.parent()时形成两个以上的活四"""
            if parent and hasattr(parent, 'update_player_info'):
                parent.update_player_info()
                
            return
        
        # 切换玩家tive_four(row, col, dx, dy):
        self.current_player = 3 - self.current_player
        
        # 如果轮到黑棋，更新禁手位置
        if self.current_player == 1:ctive_fours >= 2
            self.update_forbidden_positions()
        else: row, col, dx, dy):
            self.forbidden_positions = []  # 白棋回合清空禁手标记
        XXXX 或 X_XXX 或 XX_XX 或 XXX_X，一端是空格
        self.update()
连续模式
        # 更新父组件的玩家信息ern(row, col, dx, dy)
        parent = self.parent()
        if parent and hasattr(parent, 'update_player_info'):
            parent.update_player_info()
    X
    def check_win(self, row, col):
        """检查当前玩家是否获胜"""
        player = self.board_data[row][col].11.',  # XX_XX
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]  # 横、竖、斜、反斜四个方向
        
        for dx, dy in directions:
            count = 1  # 当前落子点计为1ns:
            
            # 沿着正方向检查连子
            for step in range(1, 5):  # 最多检查4步，加上当前位置刚好5子
                x, y = row + dx * step, col + dy * step
                if 0 <= x < self.board_size and 0 <= y < self.board_size and self.board_data[x][y] == player:
                    count += 1x, dy):
                else:
                    break，'1' 表示黑子，'2' 表示白子，'.' 表示棋盘外区域"""不是默认显示选中项
                    
            # 沿着反方向检查连子
            for step in range(1, 5):
                x, y = row - dx * step, col - dy * stepfor step in range(-5, 6):self.style_combo.addItems(self.board.get_style_names())
                if 0 <= x < self.board_size and 0 <= y < self.board_size and self.board_data[x][y] == player:= row + dx * step, col + dy * stepe_combo.setCurrentIndex(style_index)
                    count += 1<= y < self.board_size:onnect(self.change_board_style)
                else:board_data[x][y]))
                    break
                    盘外elf)
            # 正好5子连线则获胜，超过5子对白棋也算获胜，对黑棋则是禁手
            if count == 5 or (count > 5 and player == 2):
                return Truee_combo.setPlaceholderText("选择执棋方")
                
        return False


class BoardWidget(QWidget):self.on_side_changed)
    """五子棋游戏组件，可嵌入到应用界面中"""# 设置自身尺寸策略为扩展
    def __init__(self, parent=None, style_index=0):tSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)ntrols_layout.addWidget(self.style_label)
        super().__init__(parent)放控制面板idget(self.style_combo)
        # 设置自身尺寸策略为扩展
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)20, 20)bo)
        # 创建主布局 - 改为水平布局，左侧放棋盘，右侧放控制面板self.main_layout.setSpacing(20)  # 增加间距self.controls_layout.addStretch(1)
        self.main_layout = QHBoxLayout(self)，用于保持棋盘居中
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)  # 增加间距ainer)
        # 创建左侧容器，用于保持棋盘居中(0, 0, 0, 0).HLine)
        self.left_container = QWidget()
        self.left_layout = QVBoxLayout(self.left_container)yle_index)
        self.left_layout.setContentsMargins(0, 0, 0, 0)扩展策略，允许随窗口放大
        # 创建棋盘实例y(QSizePolicy.Expanding, QSizePolicy.Expanding)黑棋")
        self.board = GoBoardWidget(self, style_index)完全填充nfo.setAlignment(Qt.AlignCenter)
        # 左侧容器采用扩展策略，允许随窗口放大t(self.board, 1)  # 移除了Qt.AlignCenter参数，让棋盘完全填充容器nfo.font()
        self.left_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # 将棋盘添加到左侧容器，完全填充idget()ont(info_font)
        self.left_layout.addWidget(self.board, 1)  # 移除了Qt.AlignCenter参数，让棋盘完全填充容器xLayout(self.right_panel)
        # 创建右侧控制面板ntsMargins(10, 10, 10, 10)Label(
        self.right_panel = QWidget()Spacing(15)
        self.right_layout = QVBoxLayout(self.right_panel) 设置右侧面板的宽度策略，使其不随窗口拉伸   "1. 点击「开始对局」按钮开始游戏\n"
        self.right_layout.setContentsMargins(10, 10, 10, 10)cy.Fixed, QSizePolicy.Preferred)
        self.right_layout.setSpacing(15)
        # 设置右侧面板的宽度策略，使其不随窗口拉伸点击「悔棋」可撤销最后一步\n"
        self.right_panel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.right_panel.setFixedWidth(300)  # 略微减小右侧面板宽度Center)
        # 创建标题标签)
        self.title_label = QLabel("五子棋游戏")
        self.title_label.setAlignment(Qt.AlignCenter)nt.setBold(True)e_instructions.setAlignment(Qt.AlignLeft)
        title_font = self.title_label.font()
        title_font.setPointSize(24)
        title_font.setBold(True)
        self.title_label.setFont(title_font)# 创建棋盘风格选择下拉框self.undo_button = PushButton("悔棋")
        # 创建操作区域布局e_label = QLabel("棋盘风格：")game_button = PushButton("结束游戏")
        self.controls_layout = QHBoxLayout()
        # 创建棋盘风格选择下拉框
        self.style_label = QLabel("棋盘风格：")_names())
        self.style_combo = ComboBox(self)style_index)ht(40)
        # 填充风格选择下拉框change_board_style)
        self.style_combo.addItems(self.board.get_style_names())# 按钮添加到布局
        self.style_combo.setCurrentIndex(style_index)ayout.addWidget(self.start_button)
        self.style_combo.currentIndexChanged.connect(self.change_board_style)
        f.undo_button)
        # 增加执棋方选择
        self.side_label = QLabel("执棋方：", self)
        self.side_combo = ComboBox(self)
        self.side_combo.addItems(["玩家执黑", "玩家执白"])ged.connect(self.on_side_changed)
        self.side_combo.setCurrentIndex(0)
        self.player_side = "black"elf.style_label)
        self.side_combo.currentIndexChanged.connect(self.on_side_changed)
        
        self.controls_layout.addWidget(self.style_label)self.controls_layout.addWidget(self.side_combo)self.right_layout.addWidget(self.player_info)
        self.controls_layout.addWidget(self.style_combo)tretch(1)ing(20)
        self.controls_layout.addWidget(self.side_label)
        self.controls_layout.addWidget(self.side_combo)
        self.controls_layout.addStretch(1)self.separator = QFrame()self.right_layout.addLayout(self.button_layout)  # 添加按钮布局
        r.setFrameShape(QFrame.HLine)yout.addStretch(1)  # 添加伸缩器使组件靠上对齐
        # 创建分隔线e.Sunken)
        self.separator = QFrame()布局，增加棋盘比例
        self.separator.setFrameShape(QFrame.HLine)
        self.separator.setFrameShadow(QFrame.Sunken)
        
        # 玩家信息标签self.player_info.font()航
        self.player_info = QLabel("当前玩家：黑棋"))nterface')
        self.player_info.setAlignment(Qt.AlignCenter)self.player_info.setFont(info_font)# 连接按钮事件
        info_font = self.player_info.font()utton.clicked.connect(self.onStartGame)    
        info_font.setPointSize(16)(t(self.onUndoMove)
        self.player_info.setFont(info_font)        "游戏说明：\n"    self.end_game_button.clicked.connect(self.onEndGame)
        # 创建游戏说明
        self.game_instructions = QLabel(，双方轮流下棋\n"player_info()
            "游戏说明：\n"
            "1. 点击「开始对局」按钮开始游戏\n"        "4. 点击「悔棋」可撤销最后一步\n"    # 设置初始游戏状态
            "2. 黑棋先行，双方轮流下棋\n"
            "3. 先连成五子一线者获胜\n"自动保存到历史记录"
            "4. 点击「悔棋」可撤销最后一步\n"
            "5. 点击「结束游戏」可结束当前游戏\n"
            "6. 游戏会自动保存到历史记录"self.game_instructions.setAlignment(Qt.AlignLeft)self.board.set_style(index)    
        )
        self.game_instructions.setWordWrap(True)  # 改为垂直布局
        self.game_instructions.setAlignment(Qt.AlignLeft)
        # 创建按钮布局undo_button = PushButton("悔棋")player_side = "black" if index == 0 else "white"
        self.button_layout = QVBoxLayout()  # 改为垂直布局
        self.start_button = PushButton("开始对局")按钮尺寸
        self.undo_button = PushButton("悔棋")dHeight(40)
        self.end_game_button = PushButton("结束游戏")tFixedHeight(40)nt_player == 1:
        # 设置按钮尺寸    self.end_game_button.setFixedHeight(40)        self.board.update_forbidden_positions()
        self.start_button.setFixedHeight(40)
        self.undo_button.setFixedHeight(40)idden_positions = []  # 白棋回合清空禁手
        self.end_game_button.setFixedHeight(40)dget(self.start_button)
        
        # 按钮添加到布局button_layout.addWidget(self.undo_button)board.update()
        self.button_layout.addWidget(self.start_button)
        self.button_layout.addSpacing(10)_game_button)
        self.button_layout.addWidget(self.undo_button)        """更新当前玩家信息"""
        self.button_layout.addSpacing(10)
        self.button_layout.addWidget(self.end_game_button)ddWidget(self.title_label)游戏结束！胜者：黑棋" if self.board.winner == 1 else "游戏结束！胜者：白棋"
        ing(10)
        # 添加组件到右侧布局self.right_layout.addLayout(self.controls_layout)    player_text = "当前玩家：黑棋" if self.board.current_player == 1 else "当前玩家：白棋"
        self.right_layout.addWidget(self.title_label)t.addWidget(self.separator).setText(player_text)
        self.right_layout.addSpacing(10)yout.addWidget(self.player_info)
        self.right_layout.addLayout(self.controls_layout)addSpacing(20)
        self.right_layout.addWidget(self.separator)
        self.right_layout.addWidget(self.player_info)
        self.right_layout.addSpacing(20)  # 添加按钮布局
        self.right_layout.addWidget(self.game_instructions).addStretch(1)  # 添加伸缩器使组件靠上对齐
        self.right_layout.addSpacing(20)mode:
        self.right_layout.addLayout(self.button_layout)  # 添加按钮布局添加到主布局，增加棋盘比例换到暗黑模式
        self.right_layout.addStretch(1)  # 添加伸缩器使组件靠上对齐 # 给棋盘区域更多的比例tyle_names()):
        右侧面板不拉伸
        # 将棋盘容器和右侧面板添加到主布局，增加棋盘比例
        self.main_layout.addWidget(self.left_container, 3)  # 给棋盘区域更多的比例
        self.main_layout.addWidget(self.right_panel, 0)  # 右侧面板不拉伸setObjectName('App-Interface')
        
        # 设置对象名称，用于导航tartGame)     white;")
        self.setObjectName('App-Interface')
        # 连接按钮事件.end_game_button.clicked.connect(self.onEndGame)self.game_instructions.setStyleSheet("color: white;")
        self.start_button.clicked.connect(self.onStartGame)    abel.setStyleSheet("color: white;")
        self.undo_button.clicked.connect(self.onUndoMove)
        self.end_game_button.clicked.connect(self.onEndGame)
        # 初始化时更新玩家信息
        self.update_player_info()# 经典木色
        
        # 设置初始游戏状态_board_style(self, index):恢复默认文本颜色
        self.board.game_started = Falser_info.setStyleSheet("")
        self.board.set_style(index)            self.style_label.setStyleSheet("")
    def change_board_style(self, index):("")
        """更改棋盘风格"""anged(self, index):itle_label.setStyleSheet("")
        self.board.set_style(index)    
    r_side = "black" if index == 0 else "white"
    def on_side_changed(self, index):f index == 0 else 2
        """更改执棋方"""
        self.player_side = "black" if index == 0 else "white"黑棋回合，检测禁手rtGame(self):
        self.board.current_player = 1 if index == 0 else 2:
        self.board.update_forbidden_positions().board.reset_game(start_immediately=True)  # 游戏立即开始
        # 如果是黑棋回合，检测禁手
        if self.board.current_player == 1: = []  # 白棋回合清空禁手
            self.board.update_forbidden_positions()
        else:.update_player_info():
            self.board.forbidden_positions = []  # 白棋回合清空禁手 1
            
        self.update_player_info()layer_info(self):手，检测并显示禁手
        self.board.update()ent_player == 1:
    _over:ate_forbidden_positions()
    def update_player_info(self):黑棋" if self.board.winner == 1 else "游戏结束！胜者：白棋"
        """更新当前玩家信息"""
        if self.board.game_over:前玩家：黑棋" if self.board.current_player == 1 else "当前玩家：白棋"
            player_text = "游戏结束！胜者：黑棋" if self.board.winner == 1 else "游戏结束！胜者：白棋"ext)
        else:
            player_text = "当前玩家：黑棋" if self.board.current_player == 1 else "当前玩家：白棋"f):始',
        self.player_info.setText(player_text)""更新界面样式以适应主题变化"""   content="黑棋先行，请点击棋盘落子",
        dark_mode = isDarkTheme()        orient=Qt.Horizontal,
    def updateStyle(self):
        """更新界面样式以适应主题变化"""主题调整棋盘样式tion=InfoBarPosition.TOP,
        dark_mode = isDarkTheme()00,
        
        # 可能需要根据主题调整棋盘样式e in enumerate(self.board.get_style_names()):
        if dark_mode: == "暗黑模式":
            # 将棋盘风格切换到暗黑模式etCurrentIndex(i)
            for i, style_name in enumerate(self.board.get_style_names()):
                if style_name == "暗黑模式":
                    self.style_combo.setCurrentIndex(i)
                    breaketStyleSheet("color: white;")
            l.setStyleSheet("color: white;")',
            # 更新文本颜色elf.game_instructions.setStyleSheet("color: white;")   content="游戏已经结束，不能悔棋",
            self.player_info.setStyleSheet("color: white;")itle_label.setStyleSheet("color: white;")ient=Qt.Horizontal,
            self.style_label.setStyleSheet("color: white;"):    isClosable=True,
            self.game_instructions.setStyleSheet("color: white;")ion.TOP,
            self.title_label.setStyleSheet("color: white;")le == "暗黑模式":
        else:e_combo.setCurrentIndex(0)  # 经典木色lf
            # 如果当前是暗黑模式，切换到经典木色
            if self.board.current_style == "暗黑模式":
                self.style_combo.setCurrentIndex(0)  # 经典木色Sheet("")
            StyleSheet("")):
            # 恢复默认文本颜色eet("")
            self.player_info.setStyleSheet("")etStyleSheet("")
            self.style_label.setStyleSheet("")
            self.game_instructions.setStyleSheet("")面   content="已撤销最后一步",
            self.title_label.setStyleSheet("")update()   orient=Qt.Horizontal,
        
        # 刷新界面Position.TOP,
        self.update()
    mmediately=True)  # 游戏立即开始
    def onStartGame(self):
        """开始游戏"""
        self.board.reset_game(start_immediately=True)  # 游戏立即开始_player = 2
        # 根据选择设置先手
        if self.player_side == "white":elf.board.current_player = 1   content="没有可撤销的步骤",
            self.board.current_player = 2                    orient=Qt.Horizontal,
        else:手le=True,
            self.board.current_player = 1rent_player == 1:InfoBarPosition.TOP,
            _positions()
        # 如果是黑棋先手，检测并显示禁手
        if self.board.current_player == 1:fo()
            self.board.update_forbidden_positions()
            
        self.update_player_info()
        
        # 显示提示信息盘落子",
        InfoBar.success(ontal,',
            title='游戏已开始',sClosable=True,   content="游戏尚未开始",
            content="黑棋先行，请点击棋盘落子",on=InfoBarPosition.TOP,ient=Qt.Horizontal,
            orient=Qt.Horizontal,    duration=3000,        isClosable=True,
            isClosable=True,TOP,
            position=InfoBarPosition.TOP,
            duration=3000,
            parent=self
        )棋"""return
    
    def onUndoMove(self):r and self.board.winner > 0:r:
        """悔棋"""
        # 检查是否因投降而结束游戏iately=False)
        if self.board.game_over and self.board.winner > 0:不能悔棋",nfo()
            InfoBar.warning(
                title='无法悔棋',e,
                content="游戏已经结束，不能悔棋",foBarPosition.TOP,戏',
                orient=Qt.Horizontal,   duration=3000,   content="棋盘已清空，请点击「开始对局」按钮",
                isClosable=True,rent=selfient=Qt.Horizontal,
                position=InfoBarPosition.TOP,    )        isClosable=True,
                duration=3000,Position.TOP,
                parent=self
            )():
            return
            
        if self.board.undo_move():
            self.update_player_info()
            InfoBar.info(ntal,in self.board.board_data):
                title='悔棋成功',   isClosable=True, 只有在棋盘上有棋子时才询问是否保存
                content="已撤销最后一步",P,
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,Cancel, 
                duration=3000,
                parent=selfnfoBar.warning(
            )eBox.Cancel:
        else:
            InfoBar.warning(zontal,sageBox.Save:
                title='悔棋失败',e,)  # 用户选择保存
                content="没有可撤销的步骤",
                orient=Qt.Horizontal,
                isClosable=True,   parent=self 棋盘上没有棋子，只需确认是否结束
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=selfonEndGame(self):        "确定要结束当前游戏吗？",
            )备重新开始"""MessageBox.Yes | QMessageBox.No, 
    ted:
    def onEndGame(self):
        """结束游戏并准备重新开始"""o:
        if not self.board.game_started:        content="游戏尚未开始",        return  # 用户取消操作
            InfoBar.warning(=Qt.Horizontal,
                title='无法结束',
                content="游戏尚未开始",        position=InfoBarPosition.TOP,self.board.game_over = True
                orient=Qt.Horizontal,on=3000,ner = 0  # 没有胜者
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,    return# 根据是否保存显示不同提示
                parent=self == QMessageBox.Save) else ""
            )_over:
            return
        (start_immediately=False)rt_immediately=False)
        if self.board.game_over:er_info()nfo()
            # 如果游戏已经结束，直接重置棋盘
            self.board.reset_game(start_immediately=False)
            self.update_player_info()准备新游戏',束',
                   content="棋盘已清空，请点击「开始对局」按钮",   content=f"游戏已结束{save_msg}，棋盘已清空，请点击「开始对局」按钮开始新游戏",
            InfoBar.info(            orient=Qt.Horizontal,        orient=Qt.Horizontal,
                title='准备新游戏',ble=True,True,
                content="棋盘已清空，请点击「开始对局」按钮",oBarPosition.TOP,Position.TOP,
                orient=Qt.Horizontal,
                isClosable=True,elf
                position=InfoBarPosition.TOP,)
                duration=3000,
                parent=self
            )# 询问是否结束游戏并提供保存选项"""内部方法：保存游戏到历史记录"""
            returnor row in self.board.board_data):.game_started:
        
        # 询问是否结束游戏并提供保存选项
        if any(any(row) for row in self.board.board_data):f, '结束游戏', 戏数据
            # 只有在棋盘上有棋子时才询问是否保存
            reply = QMessageBox.question(ard | QMessageBox.Cancel, 
                self, '结束游戏',         QMessageBox.Save# 导入历史记录管理器获取保存目录
                "确定要结束当前游戏吗？",.game_history_manager import GameHistoryManager
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel, sageBox.Cancel:meHistoryManager()
                QMessageBox.Save消操作
            )ve:_manager.history_dir, os.path.basename(filename))
            if reply == QMessageBox.Cancel:选择保存ame(save_path)
                return  # 用户取消操作结束
            elif reply == QMessageBox.Save:
                self.saveGame()  # 用户选择保存
            # 如果选择Discard，则不保存直接结束eBox.question(',
        else:   self, '结束游戏',    content=f"游戏已自动保存到历史记录",
            # 棋盘上没有棋子，只需确认是否结束前游戏吗？",Qt.Horizontal,
            reply = QMessageBox.question(sageBox.Yes | QMessageBox.No, osable=True,
                self, '结束游戏',             QMessageBox.Yes            position=InfoBarPosition.TOP,
                "确定要结束当前游戏吗？",
                QMessageBox.Yes | QMessageBox.No, MessageBox.No:lf
                QMessageBox.Yes    return  # 用户取消操作)
            )
            if reply == QMessageBox.No:
                return  # 用户取消操作.board.game_over = True
        inner = 0  # 没有胜者ta(self, game_data):
        # 先通知游戏结束
        self.board.game_over = True
        self.board.winner = 0  # 没有胜者提示
        self.update_player_info()
        
        # 根据是否保存显示不同提示
        save_msg = "并保存" if (reply == QMessageBox.Save) else "".board.reset_game(start_immediately=False)self.board.current_player = game_data['current_player']
        player_info()
        # 立即重置棋盘，准备新游戏
        self.board.reset_game(start_immediately=False)Bar.info(self.board.game_started = game_data['game_started']
        self.update_player_info()戏已结束',rd.game_over = game_data['game_over']
        空，请点击「开始对局」按钮开始新游戏",'winner']
        InfoBar.info(
            title='游戏已结束',
            content=f"游戏已结束{save_msg}，棋盘已清空，请点击「开始对局」按钮开始新游戏",position=InfoBarPosition.TOP,self.board.move_history = game_data['move_history']
            orient=Qt.Horizontal,000,
            isClosable=True,
            position=InfoBarPosition.TOP,'style_index' in game_data:
            duration=3000,.setCurrentIndex(game_data['style_index'])
            parent=selfme_data['style_index'])
        )记录"""
    _started:
    def saveGame(self):
        """内部方法：保存游戏到历史记录"""
        if not self.board.game_started:
            return Falsegame()
            
        # 获取默认文件名和游戏数据
        filename, game_data = self.board.save_game()import GameHistoryManager
        HistoryManager()
        # 导入历史记录管理器获取保存目录
        from mainWindow.game_history_manager import GameHistoryManagerpath = os.path.join(history_manager.history_dir, os.path.basename(filename))   content=f"加载游戏数据失败: {str(e)}",
        history_manager = GameHistoryManager().board.save_game(save_path)t.Horizontal,
        # 直接保存到默认路径                        isClosable=True,
        save_path = os.path.join(history_manager.history_dir, os.path.basename(filename))        if result:                position=InfoBarPosition.TOP,
        result, _ = self.board.save_game(save_path)
        itle='自动保存',arent=self
        if result:
            InfoBar.success(ntal,
                title='自动保存',losable=True,
                content=f"游戏已自动保存到历史记录",tion.TOP,
                orient=Qt.Horizontal,
                isClosable=True,        parent=self子棋游戏窗口"""
                position=InfoBarPosition.TOP,rent=None, style_index=0):
                duration=3000,
                parent=self
            )
            return Truea(self, game_data):wIcon(FIF.GAME.icon())
        return False
    
    def load_game_data(self, game_data):
        """从历史记录加载游戏数据"""rd_data']
        try:   elf.resize(1000, 800)  # 从900x700增加到1000x800
            # 设置棋盘数据    # 设置当前玩家# 设置窗口在屏幕中央显示
            self.board.board_data = game_data['board_data']board.current_player = game_data['current_player']QApplication.desktop().availableGeometry()
            
            # 设置当前玩家    # 设置游戏状态    (screen.width() - self.width()) // 2,
            self.board.current_player = game_data['current_player']game_started = game_data['game_started']ght() - self.height()) // 2
            
            # 设置游戏状态
            self.board.game_started = game_data['game_started']    # 创建主窗口部件
            self.board.game_over = game_data['game_over']
            self.board.winner = game_data['winner']
                # 创建棋盘组件并设置尺寸策略
            # 设置棋步历史棋盘风格n_layout = QVBoxLayout(self.central_widget)
            self.board.move_history = game_data['move_history']s(10, 10, 10, 10)  # 减小边距，为棋盘留更多空间
            ex(game_data['style_index'])
            # 设置棋盘风格index'])dex)
            if 'style_index' in game_data:
                self.style_combo.setCurrentIndex(game_data['style_index'])
                self.board.set_style(game_data['style_index'])
                self.button_layout = QHBoxLayout()
            # 更新玩家信息显示= PushButton("关闭窗口")
            self.update_player_info()
            
            # 重绘棋盘except Exception as e:self.button_layout.addStretch(1)
            self.board.update()"加载游戏数据失败: {str(e)}")_layout.addWidget(self.close_button)
            return True
        except Exception as e:
            print(f"加载游戏数据失败: {str(e)}")# 添加拉伸因子，确保棋盘占据所有可用空间
            InfoBar.error(            orient=Qt.Horizontal,    self.main_layout.addLayout(self.button_layout, 0)  # 按钮布局不拉伸
                title='数据加载错误',
                content=f"加载游戏数据失败: {str(e)}",=InfoBarPosition.TOP,
                orient=Qt.Horizontal,elf))
                isClosable=True,ntentsMargins(0, 48, 0, 0)  # 为标题栏留出空间
                position=InfoBarPosition.TOP,
                duration=3000,            return False    
                parent=self    def closeEvent(self, event):
            )
            return FalsedWindow(FramelessWindow):int("游戏窗口正在关闭，清理资源...")

ent=None, style_index=0):(event)
class BoardWindow(FramelessWindow):_init__(parent)
    """五子棋游戏窗口"""
    def __init__(self, parent=None, style_index=0):        self.setWindowTitle("五子棋游戏")if __name__ == "__main__":

























































    sys.exit(app.exec_())    window.show()    window = BoardWindow()    app = QApplication(sys.argv)    # 测试代码if __name__ == "__main__":        super().closeEvent(event)        # 这里可以添加任何需要的资源清理代码        print("游戏窗口正在关闭，清理资源...")        """窗口关闭时的清理工作"""    def closeEvent(self, event):            self.layout().addWidget(self.central_widget)        self.layout().setContentsMargins(0, 48, 0, 0)  # 为标题栏留出空间        self.setLayout(QVBoxLayout(self))        # 设置窗口的内容部件                self.main_layout.addLayout(self.button_layout, 0)  # 按钮布局不拉伸        self.main_layout.addWidget(self.board_widget, 1)  # 添加拉伸因子，确保棋盘占据所有可用空间        # 添加到布局时设置拉伸因子                self.button_layout.addWidget(self.close_button)        self.button_layout.addStretch(1)        self.close_button.clicked.connect(self.close)        self.close_button.setFixedWidth(150)  # 设置固定宽度        self.close_button = PushButton("关闭窗口")        self.button_layout = QHBoxLayout()        # 创建关闭按钮                self.board_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)        self.board_widget = BoardWidget(self, style_index)                self.main_layout.setContentsMargins(10, 10, 10, 10)  # 减小边距，为棋盘留更多空间        self.main_layout = QVBoxLayout(self.central_widget)        # 创建棋盘组件并设置尺寸策略                self.central_widget = QWidget(self)        # 创建主窗口部件                )            (screen.height() - self.height()) // 2            (screen.width() - self.width()) // 2,        self.move(        screen = QApplication.desktop().availableGeometry()        # 设置窗口在屏幕中央显示        self.resize(1000, 800)  # 从900x700增加到1000x800        # 设置窗口大小，增加宽度以适应新布局        self.setWindowFlags(Qt.Window)        # 设置窗口为独立窗口                self.setWindowIcon(FIF.GAME.icon())        self.setWindowTitle("五子棋游戏")        # 设置窗口标题和图标        super().__init__(parent)





















































    sys.exit(app.exec_())    window.show()    window = BoardWindow()    app = QApplication(sys.argv)    # 测试代码if __name__ == "__main__":        super().closeEvent(event)        # 这里可以添加任何需要的资源清理代码        print("游戏窗口正在关闭，清理资源...")        """窗口关闭时的清理工作"""    def closeEvent(self, event):            self.layout().addWidget(self.central_widget)        self.layout().setContentsMargins(0, 48, 0, 0)  # 为标题栏留出空间        self.setLayout(QVBoxLayout(self))        # 设置窗口的内容部件                self.main_layout.addLayout(self.button_layout, 0)  # 按钮布局不拉伸        self.main_layout.addWidget(self.board_widget, 1)  # 添加拉伸因子，确保棋盘占据所有可用空间        # 添加到布局时设置拉伸因子                self.button_layout.addWidget(self.close_button)        self.button_layout.addStretch(1)        self.close_button.clicked.connect(self.close)        self.close_button.setFixedWidth(150)  # 设置固定宽度        self.close_button = PushButton("关闭窗口")        self.button_layout = QHBoxLayout()        # 创建关闭按钮                self.board_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)        self.board_widget = BoardWidget(self, style_index)                self.main_layout.setContentsMargins(10, 10, 10, 10)  # 减小边距，为棋盘留更多空间        self.main_layout = QVBoxLayout(self.central_widget)        # 创建棋盘组件并设置尺寸策略                self.central_widget = QWidget(self)        # 创建主窗口部件                )            (screen.height() - self.height()) // 2            (screen.width() - self.width()) // 2,        self.move(        screen = QApplication.desktop().availableGeometry()        # 设置窗口在屏幕中央显示        self.resize(1000, 800)  # 从900x700增加到1000x800        # 设置窗口大小，增加宽度以适应新布局        self.setWindowFlags(Qt.Window)        # 设置窗口为独立窗口                self.setWindowIcon(FIF.GAME.icon())    # 测试代码
    app = QApplication(sys.argv)
    window = BoardWindow()
    window.show()
    sys.exit(app.exec_())
