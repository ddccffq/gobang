# coding:utf-8
from enum import Enum

from PyQt5.QtCore import Qt, QLocale
from PyQt5.QtGui import QGuiApplication, QFont
from qfluentwidgets import (qconfig, QConfig, ConfigItem, OptionsConfigItem, BoolValidator,
                            ColorConfigItem, OptionsValidator, RangeConfigItem, RangeValidator,
                            FolderListValidator, EnumSerializer, FolderValidator, ConfigSerializer, __version__)


class Language(Enum):
    """ ����ö�� """
    CHINESE_SIMPLIFIED = QLocale(QLocale.Chinese, QLocale.China)
    CHINESE_TRADITIONAL = QLocale(QLocale.Chinese, QLocale.HongKong)
    ENGLISH = QLocale(QLocale.English)
    AUTO = QLocale()


class LanguageSerializer(ConfigSerializer):
    """ �������л��� """
    def serialize(self, language):
        return language.value.name() if language != Language.AUTO else "Auto"

    def deserialize(self, value: str):
        return Language(QLocale(value)) if value != "Auto" else Language.AUTO


class Config(QConfig):
    """ Ӧ�ó������� """
    
    # ������
    enableAcrylicBackground = ConfigItem(
        "MainWindow", "EnableAcrylicBackground", False, BoolValidator())
    minimizeToTray = ConfigItem(
        "MainWindow", "MinimizeToTray", True, BoolValidator())
    dpiScale = OptionsConfigItem(
        "MainWindow", "DpiScale", "Auto", OptionsValidator([1, 1.25, 1.5, 1.75, 2, "Auto"]), restart=True)
    language = OptionsConfigItem(
        "MainWindow", "Language", Language.AUTO, OptionsValidator(Language), LanguageSerializer(), restart=True)
    
    # ����ģʽ
    themeMode = OptionsConfigItem(
        "Theme", "ThemeMode", "Light", OptionsValidator(["Light", "Dark", "Auto"]))
    
    # ��Ϸ����
    historyDir = ConfigItem(
        "Game", "HistoryDirectory", "game_history", FolderValidator())
    
    # �������
    checkUpdateAtStartUp = ConfigItem(
        "Update", "CheckUpdateAtStartUp", True, BoolValidator())


# Ӧ��Ԫ����
YEAR = 2023
AUTHOR = "BUPT AI�γ�������С��"
VERSION = "1.0.0"
HELP_URL = "https://bupt.edu.cn" 
FEEDBACK_URL = "https://github.com/your-username/Gomoku"
RELEASE_URL = "https://github.com/your-username/Gomoku/releases"

# ��������
cfg = Config()
qconfig.load('config/config.json', cfg)
