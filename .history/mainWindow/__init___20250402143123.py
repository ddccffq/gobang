# ��mainWindowĿ¼���ΪPython��
from qfluentwidgets import FluentIcon as FIF

# ��ӡ���з�˽������
for attr in dir(FIF):
    if not attr.startswith('_'):
        print(attr)