# coding:utf-8
import sys
import signal
import platform

from PyQt5.QtCore import Qt, QTimer, QSocketNotifier
from PyQt5.QtWidgets import QApplication

from main_window import Window  # 更新import语句，使用新的文件名

# 全局变量，用于存储应用实例
app = None

# 创建一个更安全的信号处理机制
def setup_interrupt_handling():
    """设置更安全的中断处理机制"""
    global app
    
    # 平台特定处理
    if platform.system() == 'Windows':
        # Windows平台: 简单地忽略SIGINT，依赖应用程序的原生退出机制
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        return
    
    # Unix/Linux/Mac平台: 使用QSocketNotifier进行高级信号处理
    # 创建管道并安装信号处理器
    try:
        # 尝试导入Unix特定模块
        import os
        
        # 创建一个管道
        r, w = os.pipe()
        
        # 定义信号处理器，将信号写入管道
        def signal_handler(signum, frame):
            # 只是写入一个字节到管道中
            os.write(w, b'x')
            
        # 安装SIGINT处理器
        signal.signal(signal.SIGINT, signal_handler)
        
        # 创建QSocketNotifier监听管道
        sn = QSocketNotifier(r, QSocketNotifier.Read)
        sn.activated.connect(lambda: handle_sigint(sn, r))
        
    except ImportError:
        # 如果导入失败，退回到默认行为
        print("注意: 无法设置高级信号处理，退回到默认行为")

def handle_sigint(sn, pipe):
    """处理从管道接收到的SIGINT信号"""
    global app
    
    # 禁用QSocketNotifier以避免重复调用
    sn.setEnabled(False)
    
    # 从管道读取并清空数据
    import os
    os.read(pipe, 1)
    
    # 提示用户
    print("\n接收到中断信号，程序即将退出...")
    
    # 安全退出应用程序
    if app is not None:
        app.quit()
    
    # 重新启用notifier以处理后续信号
    sn.setEnabled(True)

if __name__ == '__main__':
    # 创建Qt应用
    app = QApplication(sys.argv)
    
    # 设置信号处理，确保适当处理Ctrl+C
    setup_interrupt_handling()
    
    # 设置高DPI支持
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    # 创建并显示主窗口
    w = Window()
    w.show()
    
    # 启动应用的事件循环
    sys.exit(app.exec_())
