# coding:utf-8
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel

from qfluentwidgets import FluentIcon as FIF, PushButton
from qframelesswindow import FramelessWindow


class BoardWindow(FramelessWindow):
    """五子棋游戏窗口"""
    
    def __init__(self, parent=None, style_index=0):
        super().__init__(parent)
        
        # 设置窗口标题和图标
        self.setWindowTitle("五子棋游戏")
        self.setWindowIcon(FIF.GAME.icon())
        
        # 设置窗口大小
        self.resize(800, 600)
        
        # 创建主窗口部件
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        
        # 创建主布局
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 创建标题标签
        self.title_label = QLabel("五子棋游戏窗口")
        self.title_label.setAlignment(Qt.AlignCenter)
        title_font = self.title_label.font()
        title_font.setPointSize(24)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        
        # 创建内容标签
        self.content_label = QLabel(f"这是一个简单的游戏窗口\n当前选择的棋盘风格: {style_index+1}")
        self.content_label.setAlignment(Qt.AlignCenter)
        content_font = self.content_label.font()
        content_font.setPointSize(14)
        self.content_label.setFont(content_font)
        
        # 创建关闭按钮
        self.button_layout = QHBoxLayout()
        self.close_button = PushButton("关闭窗口")
        self.close_button.clicked.connect(self.close)
        self.button_layout.addStretch(1)
        self.button_layout.addWidget(self.close_button)
        self.button_layout.addStretch(1)
        
        # 添加组件到主布局
        self.main_layout.addWidget(self.title_label)
        self.main_layout.addSpacing(30)
        self.main_layout.addWidget(self.content_label)
        self.main_layout.addSpacing(30)
        self.main_layout.addLayout(self.button_layout)
        self.main_layout.addStretch(1)


if __name__ == "__main__":
    # 测试代码
    app = QApplication(sys.argv)
    window = BoardWindow()
    window.show()
    sys.exit(app.exec_())
