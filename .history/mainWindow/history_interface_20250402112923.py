# coding:utf-8
from PyQt5.QtCore import Qt, QSize, QTimer, QFileSystemWatcher, QDate, QEasingCurve, QPropertyAnimation, QRect
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, 
                            QListWidgetItem, QMessageBox, QFileDialog, QGridLayout, 
                            QCheckBox, QFrame, QSizePolicy, QSpacerItem, QButtonGroup)
from PyQt5.QtGui import QFont, QIcon, QColor, QPainter, QPainterPath, QPen

import os
import json
import datetime

from qfluentwidgets import (PushButton, SearchLineEdit, InfoBar, InfoBarPosition, 
                           FluentIcon as FIF, isDarkTheme, ZhDatePicker, CardWidget,
                           ToggleButton, SmoothScrollArea, IconWidget, TransparentToolButton,
                           TitleLabel, SubtitleLabel, CaptionLabel, StrongBodyLabel, BodyLabel)
from mainWindow.board_view import BoardWindow
from mainWindow.game_history_manager import GameHistoryManager


class RoundedCardWidget(CardWidget):
    """圆角卡片小部件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setBorderRadius(10)
        self.setShadowEnabled(True)
        

class HistoryListItem(QWidget):
    """历史记录列表项"""
    
    def __init__(self, title, date, player1, player2, winner, is_favorite=False, parent=None):
        super().__init__(parent)
        self.setFixedHeight(90)  # 增加高度
        
        # 创建布局
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(12, 10, 12, 10)
        self.layout.setSpacing(15)  # 增加间距
        
        # 创建收藏图标
        self.favorite_button = TransparentToolButton(self)
        self.favorite_button.setFixedSize(30, 30)
        self.favorite_button.setObjectName("favoriteButton")
        self.is_favorite = is_favorite
        self.update_favorite_status(is_favorite)
        
        # 创建图标（棋盘）
        self.icon_label = IconWidget(FIF.GAME, self)
        self.icon_label.setFixedSize(48, 48)  # 增大图标
        
        # 创建中央信息区域
        self.info_widget = QWidget()
        self.info_layout = QVBoxLayout(self.info_widget)
        self.info_layout.setContentsMargins(0, 0, 0, 0)
        self.info_layout.setSpacing(4)
        
        # 创建标题
        self.title_label = StrongBodyLabel(title, self)
        title_font = self.title_label.font()
        title_font.setPointSize(12)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        
        # 创建玩家信息
        self.players_label = BodyLabel(f"{player1} vs {player2}", self)
        
        # 日期标签
        self.date_label = CaptionLabel(date, self)
        
        # 添加到信息布局
        self.info_layout.addWidget(self.title_label)
        self.info_layout.addWidget(self.players_label)
        self.info_layout.addWidget(self.date_label)
        
        # 创建胜者标签和背景
        self.winner_widget = QWidget()
        self.winner_widget.setFixedWidth(100)
        self.winner_layout = QVBoxLayout(self.winner_widget)
        self.winner_layout.setContentsMargins(0, 0, 0, 0)
        self.winner_layout.setAlignment(Qt.AlignCenter)
        
        winner_text = f"胜者: {winner}" if winner else "未结束"
        self.winner_label = BodyLabel(winner_text, self)
        self.winner_label.setAlignment(Qt.AlignCenter)
        
        # 创建状态指示器
        self.status_indicator = QFrame(self)
        self.status_indicator.setFixedSize(80, 5)
        self.status_indicator.setObjectName("statusIndicator")
        
        # 根据胜者设置不同颜色
        if winner:
            if winner == player1:  # 黑棋胜
                self.status_indicator.setStyleSheet("background-color: #3a7ebf;")
            else:  # 白棋胜
                self.status_indicator.setStyleSheet("background-color: #d64242;")
        else:  # 未完成
            self.status_indicator.setStyleSheet("background-color: #909090;")
        
        # 添加到胜者布局
        self.winner_layout.addWidget(self.winner_label)
        self.winner_layout.addWidget(self.status_indicator, 0, Qt.AlignCenter)
        
        # 添加所有元素到主布局
        self.layout.addWidget(self.favorite_button, 0, Qt.AlignTop)
        self.layout.addWidget(self.icon_label)
        self.layout.addWidget(self.info_widget, 1)  # 给info_widget分配更多空间
        self.layout.addWidget(self.winner_widget, 0, Qt.AlignRight | Qt.AlignVCenter)
    
    def update_favorite_status(self, is_favorite):
        """更新收藏状态图标"""
        self.is_favorite = is_favorite
        self.favorite_button.setIcon(FIF.STAR_EMPHASIS if is_favorite else FIF.STAR)
        self.favorite_button.setToolTip("已收藏" if is_favorite else "点击收藏")
    
    def enterEvent(self, event):
        """鼠标进入事件"""
        self.setProperty("hovered", True)
        self.setStyle(self.style())
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """鼠标离开事件"""
        self.setProperty("hovered", False)
        self.setStyle(self.style())
        super().leaveEvent(event)


class FilterPanel(RoundedCardWidget):
    """过滤面板组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 15, 20, 15)
        self.layout.setSpacing(10)
        
        # 标题和折叠按钮
        self.header_layout = QHBoxLayout()
        self.header_layout.setContentsMargins(0, 0, 0, 0)
        
        self.title_label = SubtitleLabel("高级筛选", self)
        self.collapse_button = TransparentToolButton(self)
        self.collapse_button.setIcon(FIF.CHEVRON_DOWN)
        self.collapse_button.setFixedSize(32, 32)
        self.collapse_button.clicked.connect(self.toggle_collapse)
        
        self.header_layout.addWidget(self.title_label)
        self.header_layout.addStretch(1)
        self.header_layout.addWidget(self.collapse_button)
        
        # 添加标题到主布局
        self.layout.addLayout(self.header_layout)
        
        # 创建内容区域
        self.content_widget = QWidget(self)
        self.content_layout = QGridLayout(self.content_widget)
        self.content_layout.setContentsMargins(5, 5, 5, 5)
        self.content_layout.setSpacing(15)
        
        # 添加内容区域到主布局
        self.layout.addWidget(self.content_widget)
        
        # 创建日期选择区域
        self.date_label = SubtitleLabel("日期范围:", self)
        
        # 创建日期选择器容器
        self.date_picker_widget = QWidget(self)
        self.date_picker_layout = QHBoxLayout(self.date_picker_widget)
        self.date_picker_layout.setContentsMargins(0, 0, 0, 0)
        self.date_picker_layout.setSpacing(10)
        
        # 创建从日期选择器
        self.date_from_label = BodyLabel("从:", self)
        self.date_from_picker = ZhDatePicker(self)
        self.date_from_picker.setDate(QDate.currentDate().addMonths(-1))
        
        # 创建至日期选择器
        self.date_to_label = BodyLabel("至:", self)
        self.date_to_picker = ZhDatePicker(self)
        self.date_to_picker.setDate(QDate.currentDate())
        
        # 添加到日期选择器布局
        self.date_picker_layout.addWidget(self.date_from_label)
        self.date_picker_layout.addWidget(self.date_from_picker, 1)
        self.date_picker_layout.addWidget(self.date_to_label)
        self.date_picker_layout.addWidget(self.date_to_picker, 1)
        
        # 创建选项区域
        self.options_widget = QWidget(self)
        self.options_layout = QHBoxLayout(self.options_widget)
        self.options_layout.setContentsMargins(0, 0, 0, 0)
        self.options_layout.setSpacing(20)
        
        # 日期过滤启用选项
        self.date_filter_checkbox = QCheckBox("启用日期筛选", self)
        self.date_filter_checkbox.setObjectName("filterCheckBox")
        
        # 仅显示收藏对局
        self.favorites_only_checkbox = QCheckBox("仅显示收藏", self)
        self.favorites_only_checkbox.setObjectName("filterCheckBox")
        
        # 只显示完成的对局
        self.completed_only_checkbox = QCheckBox("只显示已完成对局", self)
        self.completed_only_checkbox.setObjectName("filterCheckBox")
        
        # 添加到选项布局
        self.options_layout.addWidget(self.date_filter_checkbox)
        self.options_layout.addWidget(self.favorites_only_checkbox)
        self.options_layout.addWidget(self.completed_only_checkbox)
        self.options_layout.addStretch(1)
        
        # 添加控件到网格布局
        self.content_layout.addWidget(self.date_label, 0, 0)
        self.content_layout.addWidget(self.date_picker_widget, 1, 0, 1, 2)
        self.content_layout.addWidget(self.options_widget, 2, 0, 1, 2)
        
        # 设置是否折叠
        self._is_collapsed = False
        
        # 初始高度
        self._expanded_height = None
    
    def toggle_collapse(self):
        """切换折叠状态"""
        self._is_collapsed = not self._is_collapsed
        
        # 记录原始高度
        if self._expanded_height is None:
            self._expanded_height = self.height()
        
        # 更新按钮图标
        self.collapse_button.setIcon(FIF.CHEVRON_RIGHT if self._is_collapsed else FIF.CHEVRON_DOWN)
        
        # 显示/隐藏内容
        self.content_widget.setVisible(not self._is_collapsed)
        
        # 执行高度动画
        target_height = 50 if self._is_collapsed else self._expanded_height
        animation = QPropertyAnimation(self, b"minimumHeight")
        animation.setDuration(200)
        animation.setStartValue(self.height())
        animation.setEndValue(target_height)
        animation.setEasingCurve(QEasingCurve.InOutCubic)
        animation.start(QPropertyAnimation.DeleteWhenStopped)


class HistoryInterface(SmoothScrollArea):
    """历史对局界面"""
    
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("History-Interface")
        
        # 设置历史记录保存目录 - 使用与GameHistoryManager相同的目录
        self.history_manager = GameHistoryManager()
        self.history_dir = self.history_manager.history_dir
        
        # 创建内容小部件和布局
        self.scroll_widget = QWidget(self)
        self.setWidget(self.scroll_widget)
        self.setWidgetResizable(True)
        
        # 创建主布局
        self.main_layout = QVBoxLayout(self.scroll_widget)
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        self.main_layout.setSpacing(20)
        
        # 创建标题区域
        self.setup_header()
        
        # 创建过滤面板
        self.setup_filter_panel()
        
        # 创建操作按钮区域
        self.setup_action_buttons()
        
        # 创建历史记录列表区域
        self.setup_history_list()
        
        # 设置文件系统监视器，监视历史目录的变化
        self.watcher = QFileSystemWatcher([self.history_dir])
        self.watcher.directoryChanged.connect(self.on_directory_changed)
        
        # 设置定时器，定期检查文件夹
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.load_history)
        self.refresh_timer.start(10000)  # 每10秒检查一次
        
        # 记录上次文件夹状态
        self.last_files = set()
        
        # 初始加载历史记录
        self.load_history()
        
        # 设置样式
        self.update_style()
    
    def setup_header(self):
        """设置标题区域"""
        # 创建标题卡片
        self.header_card = RoundedCardWidget(self)
        header_layout = QVBoxLayout(self.header_card)
        header_layout.setContentsMargins(20, 15, 20, 15)
        header_layout.setSpacing(10)
        
        # 创建标题
        self.title_label = TitleLabel("历史对局", self)
        
        # 创建搜索框
        self.search_edit = SearchLineEdit(self)
        self.search_edit.setPlaceholderText("搜索历史对局...")
        self.search_edit.textChanged.connect(self.filter_history)
        self.search_edit.setFixedWidth(300)
        
        # 创建水平布局放置标题和搜索框
        title_layout = QHBoxLayout()
        title_layout.addWidget(self.title_label)
        title_layout.addStretch(1)
        title_layout.addWidget(self.search_edit)
        
        # 创建状态标签
        self.status_label = BodyLabel("自动监测历史记录文件夹变化", self)
        self.status_label.setObjectName("statusLabel")
        
        # 添加组件到布局
        header_layout.addLayout(title_layout)
        header_layout.addWidget(self.status_label, 0, Qt.AlignRight)
        
        # 添加到主布局
        self.main_layout.addWidget(self.header_card)
    
    def setup_filter_panel(self):
        """设置过滤面板"""
        # 创建过滤面板组件
        self.filter_panel = FilterPanel(self)
        
        # 连接筛选信号
        self.filter_panel.date_filter_checkbox.stateChanged.connect(self.filter_history)
        self.filter_panel.favorites_only_checkbox.stateChanged.connect(self.filter_history)
        self.filter_panel.completed_only_checkbox.stateChanged.connect(self.filter_history)
        self.filter_panel.date_from_picker.dateChanged.connect(self.filter_history)
        self.filter_panel.date_to_picker.dateChanged.connect(self.filter_history)
        
        # 添加到主布局
        self.main_layout.addWidget(self.filter_panel)
    
    def setup_action_buttons(self):
        """设置操作按钮区域"""
        # 创建按钮卡片
        self.buttons_card = RoundedCardWidget(self)
        self.buttons_layout = QHBoxLayout(self.buttons_card)
        self.buttons_layout.setContentsMargins(20, 10, 20, 10)
        self.buttons_layout.setSpacing(15)
        
        # 添加左侧标题
        self.actions_label = SubtitleLabel("操作", self)
        self.buttons_layout.addWidget(self.actions_label)
        self.buttons_layout.addStretch(1)
        
        # 创建操作按钮
        self.load_button = PushButton("加载对局", self, FIF.PLAY)
        self.load_button.setFixedWidth(120)
        self.load_button.clicked.connect(self.load_game)
        
        self.favorite_button = PushButton("收藏/取消", self, FIF.STAR)
        self.favorite_button.setFixedWidth(120)
        self.favorite_button.clicked.connect(self.toggle_favorite)
        
        self.delete_button = PushButton("删除记录", self, FIF.DELETE)
        self.delete_button.setFixedWidth(120)
        self.delete_button.clicked.connect(self.delete_history)
        
        self.refresh_button = PushButton("刷新列表", self, FIF.SYNC)
        self.refresh_button.setFixedWidth(120)
        self.refresh_button.clicked.connect(self.load_history)
        
        # 添加按钮到布局
        self.buttons_layout.addWidget(self.load_button)
        self.buttons_layout.addWidget(self.favorite_button)
        self.buttons_layout.addWidget(self.delete_button)
        self.buttons_layout.addWidget(self.refresh_button)
        
        # 添加到主布局
        self.main_layout.addWidget(self.buttons_card)
    
    def setup_history_list(self):
        """设置历史记录列表区域"""
        # 创建列表卡片
        self.list_card = RoundedCardWidget(self)
        list_layout = QVBoxLayout(self.list_card)
        list_layout.setContentsMargins(15, 15, 15, 15)
        list_layout.setSpacing(10)
        
        # 创建列表标题
        list_header = QHBoxLayout()
        list_title = SubtitleLabel("历史记录列表", self)
        list_counter = BodyLabel("0 条记录", self)
        list_counter.setObjectName("listCounter")
        self.list_counter = list_counter
        
        list_header.addWidget(list_title)
        list_header.addStretch(1)
        list_header.addWidget(list_counter)
        
        # 创建历史记录列表
        self.history_list = QListWidget()
        self.history_list.setObjectName("historyList")
        self.history_list.setSelectionMode(QListWidget.SingleSelection)
        self.history_list.setSpacing(8)
        
        # 添加到列表布局
        list_layout.addLayout(list_header)
        list_layout.addWidget(self.history_list)
        
        # 添加到主布局
        self.main_layout.addWidget(self.list_card, 1)  # 使列表占用剩余空间
    
    def on_directory_changed(self, path):
        """文件夹变化时触发刷新"""
        self.status_label.setText(f"检测到历史记录变化，正在更新... ({datetime.datetime.now().strftime('%H:%M:%S')})")
        self.load_history()
    
    def load_history(self):
        """加载历史对局记录"""
        # 保存当前选中项的文件路径
        selected_path = None
        selected_items = self.history_list.selectedItems()
        if selected_items:
            selected_path = selected_items[0].data(Qt.UserRole)
        
        # 清空列表
        self.history_list.clear()
        
        try:
            # 获取历史记录列表
            history_records = self.history_manager.get_history_list()
            
            # 更新文件状态记录
            current_files = {record['filepath'] for record in history_records}
            
            # 检查是否有变化
            if current_files == self.last_files and not self.history_list.count() == 0:
                # 如果没有变化且列表非空，则不需要重新加载
                self.status_label.setText(f"历史记录已是最新 ({datetime.datetime.now().strftime('%H:%M:%S')})")
                return
            
            # 更新记录
            self.last_files = current_files
            
            if not history_records:
                # 无历史记录时显示提示
                item = QListWidgetItem()
                widget = QLabel("暂无历史对局记录")
                widget.setAlignment(Qt.AlignCenter)
                widget_font = widget.font()
                widget_font.setPointSize(14)
                widget.setFont(widget_font)
                item.setSizeHint(widget.sizeHint())
                self.history_list.addItem(item)
                self.history_list.setItemWidget(item, widget)
                self.status_label.setText(f"暂无历史对局记录 ({datetime.datetime.now().strftime('%H:%M:%S')})")
                self.list_counter.setText("0 条记录")
                return
            
            for record in history_records:
                # 创建列表项
                item = QListWidgetItem()
                file_name = os.path.splitext(record['filename'])[0]
                
                widget = HistoryListItem(
                    title=file_name,
                    date=record['date'],
                    player1=record['player1'],
                    player2=record['player2'], 
                    winner=record['winner'],
                    is_favorite=record['is_favorite']
                )
                
                # 连接收藏按钮点击事件
                widget.favorite_button.clicked.connect(lambda checked, path=record['filepath']: self.toggle_favorite_by_path(path))
                
                item.setSizeHint(widget.sizeHint())
                item.setData(Qt.UserRole, record['filepath'])  # 保存文件路径
                
                self.history_list.addItem(item)
                self.history_list.setItemWidget(item, widget)
                
                # 如果是之前选中的项，重新选中它
                if selected_path and record['filepath'] == selected_path:
                    self.history_list.setCurrentItem(item)
            
            record_count = len(history_records)
            self.list_counter.setText(f"{record_count} 条记录")
            self.status_label.setText(f"已加载 {record_count} 条历史记录 ({datetime.datetime.now().strftime('%H:%M:%S')})")
                
        except Exception as e:
            print(f"加载历史记录失败: {str(e)}")
            self.status_label.setText(f"加载失败: {str(e)}")
            InfoBar.error(
                title='加载失败',
                content=f"加载历史记录失败: {str(e)}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
    
    def filter_history(self):
        """根据搜索文本、日期和收藏状态过滤历史记录"""
        search_text = self.search_edit.text().lower()
        date_filter_enabled = self.filter_panel.date_filter_checkbox.isChecked()
        favorites_only = self.filter_panel.favorites_only_checkbox.isChecked()
        completed_only = self.filter_panel.completed_only_checkbox.isChecked()
        
        # 获取日期范围
        from_date = self.filter_panel.date_from_picker.date.toPyDate()
        to_date = self.filter_panel.date_to_picker.date.toPyDate()
        
        # 将to_date调整为当天结束时间
        import datetime
        to_date = datetime.datetime.combine(to_date, datetime.time.max)
        from_date = datetime.datetime.combine(from_date, datetime.time.min)
        
        visible_count = 0
        for i in range(self.history_list.count()):
            item = self.history_list.item(i)
            widget = self.history_list.itemWidget(item)
            
            # 判断是否为提示标签
            if isinstance(widget, QLabel):
                continue
            
            # 默认显示
            should_show = True
            
            # 检查文本匹配
            if search_text:
                text_match = (search_text in widget.title_label.text().lower() or 
                             search_text in widget.date_label.text().lower() or
                             search_text in widget.players_label.text().lower() or
                             search_text in widget.winner_label.text().lower())
                should_show = should_show and text_match
            
            # 检查日期范围
            if date_filter_enabled:
                try:
                    date_str = widget.date_label.text()
                    record_date = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                    date_match = from_date <= record_date <= to_date
                    should_show = should_show and date_match
                except:
                    # 如果日期解析失败，则不进行日期过滤
                    pass
            
            # 检查收藏状态
            if favorites_only:
                should_show = should_show and widget.is_favorite
            
            # 检查对局是否已完成
            if completed_only:
                winner_text = widget.winner_label.text()
                has_winner = "胜者:" in winner_text and "未结束" not in winner_text
                should_show = should_show and has_winner
            
            item.setHidden(not should_show)
            if should_show:
                visible_count += 1
        
        # 更新筛选后的记录数量
        self.list_counter.setText(f"{visible_count} 条记录")
    
    def toggle_favorite_by_path(self, filepath):
        """根据路径切换对局收藏状态"""
        # 切换收藏状态
        is_favorite = self.history_manager.toggle_favorite(filepath)
        
        # 查找对应的列表项并更新状态
        for i in range(self.history_list.count()):
            item = self.history_list.item(i)
            if item.data(Qt.UserRole) == filepath:
                widget = self.history_list.itemWidget(item)
                widget.update_favorite_status(is_favorite)
                
                # 显示成功消息
                status = "收藏" if is_favorite else "取消收藏"
                InfoBar.success(
                    title=f'已{status}',
                    content=f"已{status}对局: {os.path.basename(filepath)}",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=2000,
                    parent=self
                )
                break
        
        # 重新应用过滤
        self.filter_history()
    
    def load_game(self):
        """加载选中的对局"""
        selected_items = self.history_list.selectedItems()
        if not selected_items:
            InfoBar.warning(
                title='未选择对局',
                content="请先选择一个历史对局",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
            return
        
        file_path = selected_items[0].data(Qt.UserRole)
        
        try:
            # 从文件加载游戏数据
            with open(file_path, 'r', encoding='utf-8') as f:
                game_data = json.load(f)
            
            # 找到主窗口，通过遍历父对象
            main_window = self
            while main_window.parent() is not None:
                main_window = main_window.parent()
            
            # 确保主窗口有switchTo方法和appInterface属性
            if hasattr(main_window, 'switchTo') and hasattr(main_window, 'appInterface'):
                # 切换到游戏界面
                main_window.switchTo(main_window.appInterface)
                
                # 加载游戏数据到棋盘
                if hasattr(main_window.appInterface, 'load_game_data'):
                    main_window.appInterface.load_game_data(game_data)
                    
                    InfoBar.success(
                        title='加载成功',
                        content=f"已加载对局: {os.path.basename(file_path)}",
                        orient=Qt.Horizontal,
                        isClosable=True,
                        position=InfoBarPosition.BOTTOM,
                        duration=3000,
                        parent=main_window.appInterface
                    )
                else:
                    InfoBar.error(
                        title='功能缺失',
                        content="游戏界面不支持加载功能",
                        orient=Qt.Horizontal,
                        isClosable=True,
                        position=InfoBarPosition.TOP,
                        duration=3000,
                        parent=self
                    )
            else:
                InfoBar.error(
                    title='导航失败',
                    content="无法切换到游戏界面",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self
                )
        except Exception as e:
            InfoBar.error(
                title='加载失败',
                content=f"加载对局失败: {str(e)}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
    
    def toggle_favorite(self):
        """切换选中对局的收藏状态"""
        selected_items = self.history_list.selectedItems()
        if not selected_items:
            InfoBar.warning(
                title='未选择对局',
                content="请先选择一个历史对局",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
            return
        
        item = selected_items[0]
        file_path = item.data(Qt.UserRole)
        self.toggle_favorite_by_path(file_path)
        
        # 重新加载列表以更新排序
        self.load_history()
    
    def delete_history(self):
        """删除选中的历史记录"""
        selected_items = self.history_list.selectedItems()
        if not selected_items:
            InfoBar.warning(
                title='未选择记录',
                content="请先选择一个历史记录",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
            return
        
        file_path = selected_items[0].data(Qt.UserRole)
        
        # 确认删除
        reply = QMessageBox.question(
            self, '确认删除', 
            f"确定要删除选中的历史记录吗?\n{os.path.basename(file_path)}",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                os.remove(file_path)
                
                # 文件系统监视器应该会自动触发刷新
                # 但为了确保，手动刷新一次
                self.load_history()
                
                InfoBar.success(
                    title='删除成功',
                    content="已删除选中的历史记录",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self
                )
            except Exception as e:
                InfoBar.error(
                    title='删除失败',
                    content=f"删除历史记录失败: {str(e)}",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self
                )
    
    def update_style(self):
        """更新界面样式以适应主题变化"""
        # 浅色/深色主题样式
        if isDarkTheme():
            style = """
                #historyList {
                    background-color: #2d2d2d;
                    border: 1px solid #3d3d3d;
                    border-radius: 8px;
                }
                #historyList::item {
                    border-bottom: 1px solid #3d3d3d;
                }
                #historyList::item:selected {
                    background-color: #3a3a3a;
                }
                
                #statusLabel, #listCounter {
                    color: #cccccc;
                }
                
                QWidget[hovered="true"] {
                    background-color: #383838;
                }
                
                #favoriteButton {
                    background-color: transparent;
                    border: none;
                }
                
                #filterCheckBox {
                    color: white;
                }
            """
        else:
            style = """
                #historyList {
                    background-color: white;
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                }
                #historyList::item {
                    border-bottom: 1px solid #f0f0f0;
                }
                #historyList::item:selected {
                    background-color: #f5f5f5;
                }
                
                #statusLabel, #listCounter {
                    color: #707070;
                }
                
                QWidget[hovered="true"] {
                    background-color: #f8f8f8;
                }
                
                #favoriteButton {
                    background-color: transparent;
                    border: none;
                }
                
                #filterCheckBox {
                    color: black;
                }
            """
        
        self.setStyleSheet(style)
        
        # 刷新界面
        self.update()
    
    def showEvent(self, event):
        """当界面显示时触发刷新"""
        super().showEvent(event)
        # 每次显示界面时刷新列表
        self.load_history()
