# coding:utf-8
from PyQt5.QtCore import Qt, QSize, QTimer, QFileSystemWatcher
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QPushButton, QMessageBox, QFileDialog
from PyQt5.QtGui import QFont, QIcon
import os
import json
import datetime

from qfluentwidgets import PushButton, SearchLineEdit, InfoBar, InfoBarPosition, FluentIcon as FIF
from board_view import BoardWindow


class HistoryListItem(QWidget):
    """历史记录列表项"""
    
    def __init__(self, title, date, player1, player2, winner, parent=None):
        super().__init__(parent)
        self.setFixedHeight(70)
        
        # 创建布局
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(10, 5, 10, 5)
        
        # 创建图标（棋盘）
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(40, 40)
        self.icon_label.setPixmap(FIF.GAME.icon().pixmap(QSize(32, 32)))
        
        # 创建标题和日期标签
        self.title_label = QLabel(title)
        title_font = self.title_label.font()
        title_font.setPointSize(12)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        
        # 创建玩家信息
        self.players_label = QLabel(f"{player1} vs {player2}")
        players_font = self.players_label.font()
        players_font.setPointSize(10)
        self.players_label.setFont(players_font)
        
        # 日期标签
        self.date_label = QLabel(date)
        date_font = self.date_label.font()
        date_font.setPointSize(9)
        self.date_label.setFont(date_font)
        
        # 创建胜者标签
        winner_text = f"胜者: {winner}" if winner else "未结束"
        self.winner_label = QLabel(winner_text)
        winner_font = self.winner_label.font()
        winner_font.setPointSize(10)
        self.winner_label.setFont(winner_font)
        
        # 创建一个垂直布局放置标题、玩家和日期
        self.info_layout = QVBoxLayout()
        self.info_layout.addWidget(self.title_label)
        self.info_layout.addWidget(self.players_label)
        self.info_layout.addWidget(self.date_label)
        
        # 添加所有元素到主布局
        self.layout.addWidget(self.icon_label)
        self.layout.addLayout(self.info_layout, 1)  # 给info_layout分配更多空间
        self.layout.addWidget(self.winner_label)


class HistoryInterface(QWidget):
    """历史对局界面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("History-Interface")
        
        # 设置历史记录保存目录 - 使用与GameHistoryManager相同的目录
        from game_history_manager import GameHistoryManager
        self.history_manager = GameHistoryManager()
        self.history_dir = self.history_manager.history_dir
        
        # 创建主布局
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        self.main_layout.setSpacing(15)
        
        # 创建标题
        self.title_label = QLabel("历史对局")
        self.title_label.setAlignment(Qt.AlignCenter)
        title_font = self.title_label.font()
        title_font.setPointSize(24)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        
        # 创建搜索栏和按钮区域
        self.search_layout = QHBoxLayout()
        self.search_edit = SearchLineEdit(self)
        self.search_edit.setPlaceholderText("搜索历史对局...")
        self.search_edit.setFixedWidth(300)
        self.search_edit.textChanged.connect(self.filter_history)
        
        self.search_layout.addWidget(self.search_edit)
        self.search_layout.addStretch(1)
        
        self.load_button = PushButton("加载对局")
        self.load_button.setFixedWidth(120)
        self.load_button.clicked.connect(self.load_game)
        
        self.delete_button = PushButton("删除记录")
        self.delete_button.setFixedWidth(120)
        self.delete_button.clicked.connect(self.delete_history)
        
        self.refresh_button = PushButton("刷新列表")
        self.refresh_button.setFixedWidth(120)
        self.refresh_button.clicked.connect(self.load_history)
        
        self.search_layout.addWidget(self.load_button)
        self.search_layout.addWidget(self.delete_button)
        self.search_layout.addWidget(self.refresh_button)
        
        # 创建历史记录列表和状态标签
        self.status_label = QLabel("自动监测历史记录文件夹变化")
        self.status_label.setAlignment(Qt.AlignCenter)
        
        self.history_list = QListWidget()
        self.history_list.setSelectionMode(QListWidget.SingleSelection)
        self.history_list.setSpacing(5)
        
        # 添加组件到主布局
        self.main_layout.addWidget(self.title_label)
        self.main_layout.addLayout(self.search_layout)
        self.main_layout.addWidget(self.status_label)
        self.main_layout.addWidget(self.history_list)
        
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
    
    def on_directory_changed(self, path):
        """文件夹变化时触发刷新"""
        self.status_label.setText(f"检测到历史记录变化，正在更新... ({datetime.datetime.now().strftime('%H:%M:%S')})")
        self.load_history()
    
    def load_history(self):
        """加载历史对局记录"""
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
                    winner=record['winner']
                )
                
                item.setSizeHint(widget.sizeHint())
                item.setData(Qt.UserRole, record['filepath'])  # 保存文件路径
                
                self.history_list.addItem(item)
                self.history_list.setItemWidget(item, widget)
            
            self.status_label.setText(f"已加载 {len(history_records)} 条历史记录 ({datetime.datetime.now().strftime('%H:%M:%S')})")
                
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
    
    def filter_history(self, text):
        """根据搜索文本过滤历史记录"""
        search_text = text.lower()
        for i in range(self.history_list.count()):
            item = self.history_list.item(i)
            widget = self.history_list.itemWidget(item)
            
            # 判断是否为提示标签
            if isinstance(widget, QLabel):
                continue
                
            # 检查标题、日期、玩家信息是否包含搜索文本
            if (search_text in widget.title_label.text().lower() or 
                search_text in widget.date_label.text().lower() or
                search_text in widget.players_label.text().lower() or
                search_text in widget.winner_label.text().lower()):
                item.setHidden(False)
            else:
                item.setHidden(True)
    
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
                        position=InfoBarPosition.TOP,
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
    
    def import_game(self):
        """从文件导入对局"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "导入对局", "", "JSON文件 (*.json)"
        )
        
        if not file_path:
            return
        
        try:
            # 检查文件是否为有效的棋局JSON
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 检查必要的字段
            required_fields = ['board_data', 'current_player', 'game_started']
            if not all(field in data for field in required_fields):
                raise ValueError("无效的对局文件格式")
            
            # 复制文件到历史目录
            file_name = os.path.basename(file_path)
            if os.path.exists(os.path.join(self.history_dir, file_name)):
                # 如果文件已存在，添加时间戳前缀
                timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S_")
                file_name = timestamp + file_name
            
            import shutil
            shutil.copy2(file_path, os.path.join(self.history_dir, file_name))
            
            # 重新加载历史记录
            self.load_history()
            
            InfoBar.success(
                title='导入成功',
                content=f"已导入对局: {file_name}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
        except Exception as e:
            InfoBar.error(
                title='导入失败',
                content=f"导入对局失败: {str(e)}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
    
    def showEvent(self, event):
        """当界面显示时触发刷新"""
        super().showEvent(event)
        # 每次显示界面时刷新列表
        self.load_history()
