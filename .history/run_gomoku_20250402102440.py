# coding:utf-8
import sys
import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

# 导入主窗口类
from mainWindow.main_window import Window

if __name__ == '__main__':
    # 配置高DPI支持
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    # 创建应用实例
    app = QApplication(sys.argv)
    
    # 创建并显示主窗口
    w = Window()
    w.show()
    
    # 启动事件循环并返回退出代码
    sys.exit(app.exec_())
