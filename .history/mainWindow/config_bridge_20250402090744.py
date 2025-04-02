# coding:utf-8
"""
���ļ�����settings�ļ����е�configģ������Ӧ�ó�����������
"""

import os
import sys

# ���settings�ļ��е�����·��
settings_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "settings")
if settings_path not in sys.path:
    sys.path.append(settings_path)

# ��settings��������
from config import cfg, AUTHOR, VERSION, YEAR, HELP_URL, FEEDBACK_URL, RELEASE_URL

# �Զ������⹦�ܺ�����
# �޸���Ϸ�������
GAME_YEAR = 2023
GAME_AUTHOR = "BUPT AI�γ�������С��"
GAME_VERSION = "1.0.0"
GAME_HELP_URL = "https://bupt.edu.cn"
GAME_FEEDBACK_URL = "https://github.com/your-username/Gomoku"

# ��дȫ������
cfg.themeColor = "��Ϸ����"
