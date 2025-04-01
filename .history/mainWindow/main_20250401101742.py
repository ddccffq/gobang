# coding:utf-8
import sys
import signal

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from main_window import Window  # 更新import语句，使用新的文件名


def signal_handler(sig, frame):
    """处理中断信号（Ctrl+C）"""
    print("\n程序接收到中断信号，正在安全退出...")
    QApplication.quit()
    sys.exit(0)


if __name__ == '__main__':
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    w = Window()
    w.show()
    
    # 允许Python解释器定期处理信号，即便在Qt事件循环中
    timer = Qt.QTimer()
    timer.start(500)  # 每500ms检查一次信号
    timer.timeout.connect(lambda: None)  # 空函数，只是为了让Qt事件循环醒来
    
    sys.exit(app.exec_())
