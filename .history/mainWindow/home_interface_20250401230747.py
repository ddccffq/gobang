# coding:utf-8
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QWidget, QGroupBox, QFileDialog
from PyQt5.QtGui import QFont

from qfluentwidgets import PushButton, InfoBar, InfoBarPosition, LineEdit

# 导入历史记录管理器
from game_history_manager import GameHistoryManager


class HomeInterface(QWidget):
    """ 主页界面 - 包含程序介绍和设置 """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.mainLayout = QVBoxLayout(self)
        
        # 创建一个标题标签
        self.titleLabel = QLabel("五子棋游戏", self)
        self.titleLabel.setAlignment(Qt.AlignCenter)
        font = self.titleLabel.font()
        font.setPointSize(24)
        font.setBold(True)
        self.titleLabel.setFont(font)
        
        # 创建简介部分
        self.introGroup = QGroupBox("程序简介")
        self.introLayout = QVBoxLayout(self.introGroup)
        
        # 创建游戏介绍标签
        self.introLabel = QLabel(
            "欢迎使用五子棋游戏！\n\n"
            "本程序是一个简单的五子棋游戏实现，具有以下特点：\n"
            "• 简洁直观的用户界面\n"
            "• 支持黑白双方轮流落子\n"
            "• 自动判断胜负\n"
            "• 支持悔棋、重新开始等操作\n"
            "• 游戏自动保存，随时可查看历史记录\n\n"
            "通过左侧导航栏可以进入不同功能界面：\n"
            "• 五子棋游戏：进入游戏对局页面\n"
            "• 历史对局：查看和管理所有历史对局记录\n"
        )
        self.introLabel.setWordWrap(True)
        introFont = self.introLabel.font()
        introFont.setPointSize(11)
        self.introLabel.setFont(introFont)
        
        self.introLayout.addWidget(self.introLabel)
        
        # 创建设置部分
        self.settingsGroup = QGroupBox("游戏设置")
        self.settingsLayout = QVBoxLayout(self.settingsGroup)
        
        # 历史记录保存路径设置
        self.pathSettingLayout = QHBoxLayout()
        self.pathLabel = QLabel("历史记录保存路径:")
        self.pathEdit = LineEdit()
        self.pathEdit.setReadOnly(True)
        self.browseButton = PushButton("浏览...")
        self.browseButton.clicked.connect(self.onBrowseButtonClicked)
        
        self.pathSettingLayout.addWidget(self.pathLabel)
        self.pathSettingLayout.addWidget(self.pathEdit, 1)  # 1表示伸展因子
        self.pathSettingLayout.addWidget(self.browseButton)
        
        # 应用设置按钮
        self.applyButton = PushButton("应用设置")
        self.applyButton.clicked.connect(self.onApplyButtonClicked)
        
        # 恢复默认设置按钮
        self.resetButton = PushButton("恢复默认")
        self.resetButton.clicked.connect(self.onResetButtonClicked)
        
        # 按钮布局
        self.buttonsLayout = QHBoxLayout()
        self.buttonsLayout.addStretch(1)
        self.buttonsLayout.addWidget(self.resetButton)
        self.buttonsLayout.addWidget(self.applyButton)
        
        # 添加到设置布局
        self.settingsLayout.addLayout(self.pathSettingLayout)
        self.settingsLayout.addSpacing(20)
        self.settingsLayout.addLayout(self.buttonsLayout)
        
        # 添加到主布局
        self.mainLayout.addWidget(self.titleLabel)
        self.mainLayout.addSpacing(20)
        self.mainLayout.addWidget(self.introGroup, 1)  # 1表示伸展因子，占用更多空间
        self.mainLayout.addSpacing(20)
        self.mainLayout.addWidget(self.settingsGroup)
        
        # 设置边距和间距
        self.mainLayout.setContentsMargins(40, 40, 40, 40)
        
        # 设置对象名
        self.setObjectName('Home-Interface')
        
        # 初始化历史记录管理器
        self.history_manager = GameHistoryManager()
        
        # 加载当前设置
        self.loadSettings()
    
    def loadSettings(self):
        """加载当前设置"""
        # 显示当前历史记录保存路径
        self.pathEdit.setText(self.history_manager.history_dir)
    
    def onBrowseButtonClicked(self):
        """浏览按钮点击事件"""
        directory = QFileDialog.getExistingDirectory(
            self, "选择历史记录保存路径", 
            self.pathEdit.text(),
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        
        if directory:
            self.pathEdit.setText(directory)
    
    def onApplyButtonClicked(self):
        """应用设置按钮点击事件"""
        new_path = self.pathEdit.text()
        if not os.path.exists(new_path):
            # 尝试创建目录
            try:
                os.makedirs(new_path, exist_ok=True)
            except Exception as e:
                InfoBar.error(
                    title='路径错误',
                    content=f"无法创建目录: {str(e)}",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self
                )
                return
        
        # 更新设置
        self.history_manager.set_history_dir(new_path)
        self.history_manager.save_settings()
        
        InfoBar.success(
            title='设置已更新',
            content="历史记录保存路径已更新",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=3000,
            parent=self
        )
    
    def onResetButtonClicked(self):
        """恢复默认设置按钮点击事件"""
        self.history_manager.reset_to_default()
        self.loadSettings()
        
        InfoBar.info(
            title='已恢复默认设置',
            content="历史记录保存路径已恢复为默认值",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=3000,
            parent=self
        )