# coding:utf-8
from enum import Enum

from PyQt5.QtCore import Qt, QLocale
from PyQt5.QtGui import QGuiApplication, QFont
from qfluentwidgets import (qconfig, QConfig, ConfigItem, OptionsConfigItem, BoolValidator,
                            ColorConfigItem, OptionsValidator, RangeConfigItem, RangeValidator,
                            FolderListValidator, EnumSerializer, FolderValidator, ConfigSerializer, 
                            __version__, Theme)


class Language(Enum):
    """ 语言枚举 """
    CHINESE_SIMPLIFIED = QLocale(QLocale.Chinese, QLocale.China)
    CHINESE_TRADITIONAL = QLocale(QLocale.Chinese, QLocale.HongKong)
    ENGLISH = QLocale(QLocale.English)
    AUTO = QLocale()


class LanguageSerializer(ConfigSerializer):
    """ 语言序列化器 """
    def serialize(self, language):
        return language.value.name() if language != Language.AUTO else "Auto"

    def deserialize(self, value: str):
        return Language(QLocale(value)) if value != "Auto" else Language.AUTO


class ThemeSerializer(ConfigSerializer):
    """ 主题序列化器 """
    def serialize(self, theme):
        """将Theme枚举序列化为字符串"""
        if theme == Theme.AUTO:
            return "Auto"
        elif theme == Theme.DARK:
            return "Dark"
        else:
            return "Light"

    def deserialize(self, value: str):
        """将字符串反序列化为Theme枚举"""
        if value == "Auto":
            return Theme.AUTO
        elif value == "Dark":
            return Theme.DARK
        else:
            return Theme.LIGHT


class Config(QConfig):
    """ 应用程序配置 """
    
    # 主窗口
    enableAcrylicBackground = ConfigItem(
        "MainWindow", "EnableAcrylicBackground", False, BoolValidator())
    minimizeToTray = ConfigItem(
        "MainWindow", "MinimizeToTray", True, BoolValidator())
    dpiScale = OptionsConfigItem(
        "MainWindow", "DpiScale", "Auto", OptionsValidator([1, 1.25, 1.5, 1.75, 2, "Auto"]), restart=True)
    language = OptionsConfigItem(
        "MainWindow", "Language", Language.AUTO, OptionsValidator(Language), LanguageSerializer(), restart=True)
    
    # 主题模式 - 使用 Theme 枚举并添加序列化器
    themeMode = OptionsConfigItem(
        "Theme", "ThemeMode", Theme.LIGHT, 
        OptionsValidator([Theme.LIGHT, Theme.DARK, Theme.AUTO]),
        ThemeSerializer()  # 添加序列化器
    )
    
    # 游戏设置
    historyDir = ConfigItem(
        "Game", "HistoryDirectory", "game_history", FolderValidator())
    
    # 软件更新
    checkUpdateAtStartUp = ConfigItem(
        "Update", "CheckUpdateAtStartUp", True, BoolValidator())


# 应用元数据
YEAR = 2023
AUTHOR = "BUPT AI课程五子棋小组"
VERSION = "1.0.0"
HELP_URL = "https://bupt.edu.cn" 
FEEDBACK_URL = "https://github.com/your-username/Gomoku"
RELEASE_URL = "https://github.com/your-username/Gomoku/releases"

# 加载配置
cfg = Config()
qconfig.load('config/config.json', cfg)
