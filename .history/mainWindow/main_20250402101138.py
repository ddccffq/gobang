# coding:utf-8
import sys
import signal

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication

# 修改为更明确的绝对导入
from mainWindow.main_window import Window


# 全局变量，用于存储应用实例
app = None


def safe_exit():
    """安全退出程序"""
    print("\n程序正在安全退出...")
    if app:
        app.quit()


def signal_handler(sig, frame):
    """处理中断信号（Ctrl+C）"""
    print("\n程序接收到中断信号，将在Qt事件循环中安全退出...")
    # 不直接调用sys.exit()，而是通过事件循环退出应用
    # 使用单次计时器在主线程中执行退出操作
    if app:
        QTimer.singleShot(0, safe_exit)


if __name__ == '__main__':
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    # 创建应用实例并保存到全局变量
    app = QApplication(sys.argv)
    w = Window()
    w.show()
    
    # 修改定时器实现方式，确保在主线程中执行
    # 创建一个定时处理信号的对象，与主事件循环集成
    signal_timer = QTimer()
    signal_timer.setInterval(500)
    signal_timer.timeout.connect(lambda: None)  # 空函数，允许信号处理
    signal_timer.start()
    
    # 确保在退出前清理资源
    app.aboutToQuit.connect(signal_timer.stop)
    
    sys.exit(app.exec_())
