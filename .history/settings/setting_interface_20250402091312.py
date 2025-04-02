# coding:utf-8
import os
from config import cfg, HELP_URL, FEEDBACK_URL, AUTHOR, VERSION, YEAR
from qfluentwidgets import (SettingCardGroup, SwitchSettingCard, FolderListSettingCard,
                            OptionsSettingCard, RangeSettingCard, PushSettingCard,
                            ColorSettingCard, HyperlinkCard, PrimaryPushSettingCard, ScrollArea,
                            ComboBoxSettingCard, ExpandLayout, Theme, InfoBar, CustomColorSettingCard,
                            setTheme, setThemeColor, isDarkTheme)
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtCore import Qt, pyqtSignal, QUrl, QStandardPaths
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QWidget, QLabel, QFontDialog, QFileDialog

# 添加导入历史记录管理器
from game_history_manager import GameHistoryManager


class SettingInterface(ScrollArea):
    """ 设置界面 """

    checkUpdateSig = pyqtSignal()
    musicFoldersChanged = pyqtSignal(list)
    acrylicEnableChanged = pyqtSignal(bool)
    downloadFolderChanged = pyqtSignal(str)
    minimizeToTrayChanged = pyqtSignal(bool)
    historyDirChanged = pyqtSignal(str)  # 添加历史目录改变信号

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)

        # 初始化历史记录管理器
        self.history_manager = GameHistoryManager()

        # 设置标签
        self.settingLabel = QLabel(self.tr("Settings"), self)

        # 游戏设置组
        self.gameSettingsGroup = SettingCardGroup(self.tr("Game Settings"), self.scrollWidget)
        self.historyDirCard = PushSettingCard(
            self.tr("Choose folder"),
            FIF.FOLDER,
            self.tr("History record save path"),
            self.history_manager.history_dir,
            self.gameSettingsGroup
        )

        # music folders
        self.musicInThisPCGroup = SettingCardGroup(
            self.tr("Music on this PC"), self.scrollWidget)
        self.musicFolderCard = FolderListSettingCard(
            cfg.musicFolders,
            self.tr("Local music library"),
            directory=QStandardPaths.writableLocation(QStandardPaths.MusicLocation),
            parent=self.musicInThisPCGroup
        )
        self.downloadFolderCard = PushSettingCard(
            self.tr('Choose folder'),
            FIF.DOWNLOAD,
            self.tr("Download directory"),
            cfg.get(cfg.downloadFolder),
            self.musicInThisPCGroup
        )

        # 个性化组
        self.personalGroup = SettingCardGroup(self.tr('Personalization'), self.scrollWidget)
        self.enableAcrylicCard = SwitchSettingCard(
            FIF.TRANSPARENT,
            self.tr("Use Acrylic effect"),
            self.tr("Acrylic effect has better visual experience, but it may cause the window to become stuck"),
            configItem=cfg.enableAcrylicBackground,
            parent=self.personalGroup
        )
        self.themeCard = OptionsSettingCard(
            cfg.themeMode,
            FIF.BRUSH,
            self.tr('Application theme'),
            self.tr("Change the appearance of your application"),
            texts=[
                self.tr('Light'), self.tr('Dark'),
                self.tr('Use system setting')
            ],
            parent=self.personalGroup
        )
        self.themeColorCard = CustomColorSettingCard(
            cfg.themeColor,
            FIF.PALETTE,
            self.tr('Theme color'),
            self.tr('Change the theme color of you application'),
            self.personalGroup
        )
        self.zoomCard = OptionsSettingCard(
            cfg.dpiScale,
            FIF.ZOOM,
            self.tr("Interface zoom"),
            self.tr("Change the size of widgets and fonts"),
            texts=[
                "100%", "125%", "150%", "175%", "200%",
                self.tr("Use system setting")
            ],
            parent=self.personalGroup
        )
        self.languageCard = ComboBoxSettingCard(
            cfg.language,
            FIF.LANGUAGE,
            self.tr('Language'),
            self.tr('Set your preferred language for UI'),
            texts=['简体中文', '繁體中文', 'English', self.tr('Use system setting')],
            parent=self.personalGroup
        )

        # online music
        self.onlineMusicGroup = SettingCardGroup(self.tr('Online Music'), self.scrollWidget)
        self.onlinePageSizeCard = RangeSettingCard(
            cfg.onlinePageSize,
            FIF.SEARCH,
            self.tr("Number of online music displayed on each page"),
            parent=self.onlineMusicGroup
        )
        self.onlineMusicQualityCard = OptionsSettingCard(
            cfg.onlineSongQuality,
            FIF.MUSIC,
            self.tr('Online music quality'),
            texts=[
                self.tr('Standard quality'), self.tr('High quality'),
                self.tr('Super quality'), self.tr('Lossless quality')
            ],
            parent=self.onlineMusicGroup
        )
        self.onlineMvQualityCard = OptionsSettingCard(
            cfg.onlineMvQuality,
            FIF.VIDEO,
            self.tr('Online MV quality'),
            texts=[
                self.tr('Full HD'), self.tr('HD'),
                self.tr('SD'), self.tr('LD')
            ],
            parent=self.onlineMusicGroup
        )

        # desktop lyric
        self.deskLyricGroup = SettingCardGroup(self.tr('Desktop Lyric'), self.scrollWidget)
        self.deskLyricFontCard = PushSettingCard(
            self.tr('Choose font'),
            FIF.FONT,
            self.tr('Font'),
            parent=self.deskLyricGroup
        )
        self.deskLyricHighlightColorCard = ColorSettingCard(
            cfg.deskLyricHighlightColor,
            FIF.PALETTE,
            self.tr('Foreground color'),
            parent=self.deskLyricGroup
        )
        self.deskLyricStrokeColorCard = ColorSettingCard(
            cfg.deskLyricStrokeColor,
            FIF.PENCIL_INK,
            self.tr('Stroke color'),
            parent=self.deskLyricGroup
        )
        self.deskLyricStrokeSizeCard = RangeSettingCard(
            cfg.deskLyricStrokeSize,
            FIF.HIGHTLIGHT,
            self.tr('Stroke size'),
            parent=self.deskLyricGroup
        )
        self.deskLyricAlignmentCard = OptionsSettingCard(
            cfg.deskLyricAlignment,
            FIF.ALIGNMENT,
            self.tr('Alignment'),
            texts=[
                self.tr('Center aligned'), self.tr('Left aligned'),
                self.tr('Right aligned')
            ],
            parent=self.deskLyricGroup
        )

        # main panel
        self.mainPanelGroup = SettingCardGroup(self.tr('Main Panel'), self.scrollWidget)
        self.minimizeToTrayCard = SwitchSettingCard(
            FIF.MINIMIZE,
            self.tr('Minimize to tray after closing'),
            self.tr('PyQt-Fluent-Widgets will continue to run in the background'),
            configItem=cfg.minimizeToTray,
            parent=self.mainPanelGroup
        )

        # update software
        self.updateSoftwareGroup = SettingCardGroup(self.tr("Software update"), self.scrollWidget)
        self.updateOnStartUpCard = SwitchSettingCard(
            FIF.UPDATE,
            self.tr('Check for updates when the application starts'),
            self.tr('The new version will be more stable and have more features'),
            configItem=cfg.checkUpdateAtStartUp,
            parent=self.updateSoftwareGroup
        )

        # application
        self.aboutGroup = SettingCardGroup(self.tr('About'), self.scrollWidget)
        self.helpCard = HyperlinkCard(
            HELP_URL,
            self.tr('Open help page'),
            FIF.HELP,
            self.tr('Help'),
            self.tr('Discover new features and learn useful tips about PyQt-Fluent-Widgets'),
            self.aboutGroup
        )
        self.feedbackCard = PrimaryPushSettingCard(
            self.tr('Provide feedback'),
            FIF.FEEDBACK,
            self.tr('Provide feedback'),
            self.tr('Help us improve PyQt-Fluent-Widgets by providing feedback'),
            self.aboutGroup
        )
        self.aboutCard = PrimaryPushSettingCard(
            self.tr('Check update'),
            FIF.INFO,
            self.tr('About'),
            '© ' + self.tr('Copyright') + f" {YEAR}, {AUTHOR}. " +
            self.tr('Version') + f" {VERSION}",
            self.aboutGroup
        )

        self.__initWidget()

    def __initWidget(self):
        self.resize(1000, 800)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 120, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)

        # initialize style sheet
        self.__setQss()

        # initialize layout
        self.__initLayout()
        self.__connectSignalToSlot()

    def __initLayout(self):
        self.settingLabel.move(60, 63)

        # add cards to group
        self.gameSettingsGroup.addSettingCard(self.historyDirCard)

        self.musicInThisPCGroup.addSettingCard(self.musicFolderCard)
        self.musicInThisPCGroup.addSettingCard(self.downloadFolderCard)

        self.personalGroup.addSettingCard(self.enableAcrylicCard)
        self.personalGroup.addSettingCard(self.themeCard)
        self.personalGroup.addSettingCard(self.themeColorCard)
        self.personalGroup.addSettingCard(self.zoomCard)
        self.personalGroup.addSettingCard(self.languageCard)

        self.onlineMusicGroup.addSettingCard(self.onlinePageSizeCard)
        self.onlineMusicGroup.addSettingCard(self.onlineMusicQualityCard)
        self.onlineMusicGroup.addSettingCard(self.onlineMvQualityCard)

        self.deskLyricGroup.addSettingCard(self.deskLyricFontCard)
        self.deskLyricGroup.addSettingCard(self.deskLyricHighlightColorCard)
        self.deskLyricGroup.addSettingCard(self.deskLyricStrokeColorCard)
        self.deskLyricGroup.addSettingCard(self.deskLyricStrokeSizeCard)
        self.deskLyricGroup.addSettingCard(self.deskLyricAlignmentCard)

        self.updateSoftwareGroup.addSettingCard(self.updateOnStartUpCard)

        self.mainPanelGroup.addSettingCard(self.minimizeToTrayCard)

        self.aboutGroup.addSettingCard(self.helpCard)
        self.aboutGroup.addSettingCard(self.feedbackCard)
        self.aboutGroup.addSettingCard(self.aboutCard)

        # add setting card group to layout
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(60, 10, 60, 0)
        self.expandLayout.addWidget(self.gameSettingsGroup)
        self.expandLayout.addWidget(self.musicInThisPCGroup)
        self.expandLayout.addWidget(self.personalGroup)
        self.expandLayout.addWidget(self.onlineMusicGroup)
        self.expandLayout.addWidget(self.deskLyricGroup)
        self.expandLayout.addWidget(self.mainPanelGroup)
        self.expandLayout.addWidget(self.updateSoftwareGroup)
        self.expandLayout.addWidget(self.aboutGroup)

    def __setQss(self):
        """ set style sheet """
        self.scrollWidget.setObjectName('scrollWidget')
        self.settingLabel.setObjectName('settingLabel')

        theme = 'dark' if isDarkTheme() else 'light'
        
        # 获取当前文件的目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 使用绝对路径加载样式表
        qss_path = os.path.join(current_dir, f'resource/qss/{theme}/setting_interface.qss')
        
        # 检查文件是否存在
        if os.path.exists(qss_path):
            with open(qss_path, encoding='utf-8') as f:
                self.setStyleSheet(f.read())
        else:
            # 文件不存在时，尝试使用备用路径
            alternate_paths = [
                os.path.join(current_dir, f'resource/qss/{theme}/setting_interface.qss'),
                os.path.join(os.path.dirname(os.path.dirname(current_dir)), f'settings/resource/qss/{theme}/setting_interface.qss'),
                os.path.join(os.path.dirname(current_dir), f'resource/qss/{theme}/setting_interface.qss')
            ]
            
            for path in alternate_paths:
                if os.path.exists(path):
                    with open(path, encoding='utf-8') as f:
                        self.setStyleSheet(f.read())
                    break
            else:
                print(f"警告: 样式表文件未找到，使用内联样式")
                # 设置一个基本的内联样式
                self.setStyleSheet("""
                    #settingLabel {
                        font: 33px 'Microsoft YaHei Light';
                        background-color: transparent;
                    }
                """)

    def __showRestartTooltip(self):
        """ show restart tooltip """
        InfoBar.warning(
            '',
            self.tr('Configuration takes effect after restart'),
            parent=self.window()
        )

    def __onDeskLyricFontCardClicked(self):
        """ desktop lyric font button clicked slot """
        font, isOk = QFontDialog.getFont(
            cfg.desktopLyricFont, self.window(), self.tr("Choose font"))
        if isOk:
            cfg.desktopLyricFont = font

    def __onDownloadFolderCardClicked(self):
        """ download folder card clicked slot """
        folder = QFileDialog.getExistingDirectory(
            self, self.tr("Choose folder"), "./")
        if not folder or cfg.get(cfg.downloadFolder) == folder:
            return

        cfg.set(cfg.downloadFolder, folder)
        self.downloadFolderCard.setContent(folder)

    def __onThemeChanged(self, theme: Theme):
        """ theme changed slot """
        # change the theme of qfluentwidgets
        setTheme(theme)

        # chang the theme of setting interface
        self.__setQss()

    def __onHistoryDirClicked(self):
        """历史记录目录卡片点击事件"""
        directory = QFileDialog.getExistingDirectory(
            self, self.tr("Choose history record save path"), 
            self.history_manager.history_dir,
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        
        if not directory:
            return
            
        # 尝试创建目录并更新设置
        try:
            os.makedirs(directory, exist_ok=True)
            self.history_manager.set_history_dir(directory)
            self.history_manager.save_settings()
            self.historyDirCard.setContent(directory)
            
            # 发出信号
            self.historyDirChanged.emit(directory)
            
            InfoBar.success(
                title=self.tr('Settings updated'),
                content=self.tr("History record save path updated"),
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBar.Position.TOP,
                duration=3000,
                parent=self
            )
        except Exception as e:
            InfoBar.error(
                title=self.tr('Path error'),
                content=self.tr(f"Unable to set directory: {str(e)}"),
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBar.Position.TOP,
                duration=3000,
                parent=self
            )

    def __connectSignalToSlot(self):
        """ connect signal to slot """
        cfg.appRestartSig.connect(self.__showRestartTooltip)
        cfg.themeChanged.connect(self.__onThemeChanged)

        # music in the pc
        self.musicFolderCard.folderChanged.connect(
            self.musicFoldersChanged)
        self.downloadFolderCard.clicked.connect(
            self.__onDownloadFolderCardClicked)

        # personalization
        self.enableAcrylicCard.checkedChanged.connect(
            self.acrylicEnableChanged)
        self.themeColorCard.colorChanged.connect(setThemeColor)

        # 历史记录目录
        self.historyDirCard.clicked.connect(self.__onHistoryDirClicked)

        # playing interface
        self.deskLyricFontCard.clicked.connect(self.__onDeskLyricFontCardClicked)

        # main panel
        self.minimizeToTrayCard.checkedChanged.connect(
            self.minimizeToTrayChanged)

        # about
        self.aboutCard.clicked.connect(self.checkUpdateSig)
        self.feedbackCard.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(FEEDBACK_URL)))
