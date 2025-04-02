# coding:utf-8
import sys
import os
import signal

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication

# ������������
from mainWindow.main_window import Window

# ȫ�ֱ��������ڴ洢Ӧ��ʵ��
app = None

def safe_exit():
    """��ȫ�˳�����"""
    print("\n�������ڰ�ȫ�˳�...")
    if app:
        app.quit()

def signal_handler(sig, frame):
    """�����ж��źţ�Ctrl+C��"""
    print("\n������յ��ж��źţ�����Qt�¼�ѭ���а�ȫ�˳�...")
    # ʹ�õ��μ�ʱ�������߳���ִ���˳�����
    if app:
        QTimer.singleShot(0, safe_exit)

if __name__ == '__main__':
    # ע���źŴ�����
    signal.signal(signal.SIGINT, signal_handler)
    
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    # ����Ӧ��ʵ�������浽ȫ�ֱ���
    app = QApplication(sys.argv)
    w = Window()
    w.show()
    
    # ����һ����ʱ�����źŵĶ��������¼�ѭ������
    signal_timer = QTimer()
    signal_timer.setInterval(500)
    signal_timer.timeout.connect(lambda: None)  # �պ����������źŴ���
    signal_timer.start()
    
    # ȷ�����˳�ǰ������Դ
    app.aboutToQuit.connect(signal_timer.stop)
    
    sys.exit(app.exec_())
