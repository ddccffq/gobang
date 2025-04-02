# coding:utf-8
import os
# �޸�Ϊ���Ե���
from mainWindow.config import cfg, HELP_URL, FEEDBACK_URL, AUTHOR, VERSION, YEAR
from qfluentwidgets import (SettingCardGroup, SwitchSettingCard, 
                            OptionsSettingCard, PushSettingCard,
                            ScrollArea, ComboBoxSettingCard, ExpandLayout, 
                            Theme, InfoBar, InfoBarPosition, setTheme, isDarkTheme)
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtCore import Qt, pyqtSignal, QUrl
from PyQt5.QtGui import QDesktopServices, QPalette, QColor
from PyQt5.QtWidgets import QWidget, QLabel, QFileDialog, QApplication

# �޸�Ϊ���Ե���
from mainWindow.game_history_manager import GameHistoryManager


class SettingInterface(ScrollArea):
    """ ���ý��� """

    minimizeToTrayChanged = pyqtSignal(bool)
    historyDirChanged = pyqtSignal(str)  # ��ʷĿ¼�ı��ź�

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)

        # ��ʼ����ʷ��¼������
        self.history_manager = GameHistoryManager()

        # ���ñ�ǩ
        self.settingLabel = QLabel("����", self)
        self.settingLabel.setObjectName("interfaceTitle")

        # ��Ϸ������
        self.gameSettingsGroup = SettingCardGroup("��Ϸ����", self.scrollWidget)
        self.historyDirCard = PushSettingCard(
            "ѡ���ļ���",
            FIF.FOLDER,
            "��ʷ��¼����·��",
            self.history_manager.history_dir,
            self.gameSettingsGroup
        )

        # ���Ի���
        self.personalGroup = SettingCardGroup("���Ի�", self.scrollWidget)
        self.themeCard = OptionsSettingCard(
            cfg.themeMode,
            FIF.BRUSH,
            "Ӧ������",
            "�������Ӧ�����",
            texts=[
                "ǳɫ", "��ɫ", "����ϵͳ����"
            ],
            parent=self.personalGroup
        )
        self.languageCard = ComboBoxSettingCard(
            cfg.language,
            FIF.LANGUAGE,
            "����",
            "ѡ�������ʹ�õ�����",
            texts=["��������", "���w����", "English", "����ϵͳ����"],
            parent=self.personalGroup
        )

        # �������
        self.mainPanelGroup = SettingCardGroup("�����", self.scrollWidget)
        self.minimizeToTrayCard = SwitchSettingCard(
            FIF.MINIMIZE,
            "�رպ���С��������",
            "Ӧ�ý��ں�̨��������",
            configItem=cfg.minimizeToTray,
            parent=self.mainPanelGroup
        )

        self.__initWidget()

    def __initWidget(self):
        self.resize(1000, 800)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 120, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)

        # ��ʼ����ʽ��
        self.__setQss()

        # ��ʼ������
        self.__initLayout()
        self.__connectSignalToSlot()

    def __initLayout(self):
        self.settingLabel.move(60, 63)

        # ��ӿ�Ƭ����
        self.gameSettingsGroup.addSettingCard(self.historyDirCard)

        self.personalGroup.addSettingCard(self.themeCard)
        self.personalGroup.addSettingCard(self.languageCard)

        self.mainPanelGroup.addSettingCard(self.minimizeToTrayCard)

        # ������ÿ�Ƭ�鵽����
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(60, 10, 60, 0)
        self.expandLayout.addWidget(self.gameSettingsGroup)
        self.expandLayout.addWidget(self.personalGroup)
        self.expandLayout.addWidget(self.mainPanelGroup)

    def __setQss(self):
        """ ������ʽ�� """
        self.scrollWidget.setObjectName('scrollWidget')
        # ��ʽ���������ڼ̳У��˴����ٵ�������

    def __showRestartTooltip(self):
        """ ��ʾ������ʾ """
        InfoBar.warning(
            '',
            '���ý�����������Ч',
            parent=self.window()
        )

    def __onThemeChanged(self, theme: Theme):
        """ ���������� """
        # ����qfluentwidgets������
        setTheme(theme)
        
        # ȫ��Ӧ������
        app = QApplication.instance()
        palette = app.palette()
        if theme == Theme.DARK:
            palette.setColor(QPalette.Window, QColor(32, 32, 32))
            palette.setColor(QPalette.WindowText, Qt.white)
            palette.setColor(QPalette.Base, QColor(42, 42, 42))
            palette.setColor(QPalette.Text, Qt.white)
            palette.setColor(QPalette.Button, QColor(52, 52, 52))
            palette.setColor(QPalette.ButtonText, Qt.white)
        else:
            palette.setColor(QPalette.Window, Qt.white)
            palette.setColor(QPalette.WindowText, Qt.black)
            palette.setColor(QPalette.Base, Qt.white)
            palette.setColor(QPalette.Text, Qt.black)
            palette.setColor(QPalette.Button, Qt.white)
            palette.setColor(QPalette.ButtonText, Qt.black)
        app.setPalette(palette)

    def __onHistoryDirClicked(self):
        """��ʷ��¼Ŀ¼��Ƭ����¼�"""
        directory = QFileDialog.getExistingDirectory(
            self, "ѡ����ʷ��¼����·��", 
            self.history_manager.history_dir,
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        
        if not directory:
            return
            
        # ���Դ���Ŀ¼����������
        try:
            os.makedirs(directory, exist_ok=True)
            self.history_manager.set_history_dir(directory)
            self.history_manager.save_settings()
            self.historyDirCard.setContent(directory)
            
            # �����ź�
            self.historyDirChanged.emit(directory)
            
            InfoBar.success(
                title='�����Ѹ���',
                content="��ʷ��¼����·���Ѹ���",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
        except Exception as e:
            InfoBar.error(
                title='·������',
                content=f"�޷�����Ŀ¼: {str(e)}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )

    def __connectSignalToSlot(self):
        """ �����źźͲ� """
        cfg.appRestartSig.connect(self.__showRestartTooltip)
        cfg.themeChanged.connect(self.__onThemeChanged)

        # ��ʷ��¼Ŀ¼
        self.historyDirCard.clicked.connect(self.__onHistoryDirClicked)

        # �����
        self.minimizeToTrayCard.checkedChanged.connect(
            self.minimizeToTrayChanged)
