# 将mainWindow目录标记为Python包
from qfluentwidgets import FluentIcon as FIF

# 打印所有非私有属性
for attr in dir(FIF):
    if not attr.startswith('_'):
        print(attr)