# coding:utf-8
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QPushButton, QMessageBox, QFileDialog
from PyQt5.QtGui import QFont, QIcon
import os
import json
import datetime

from qfluentwidgets import PushButton, SearchLineEdit, InfoBar, InfoBarPosition, FluentIcon as FIF
from board_view import BoardWindow


class HistoryListItem(QWidget):
    """��ʷ��¼�б���"""
    
    def __init__(self, title, date, winner, parent=None):
        super().__init__(parent)
        self.setFixedHeight(70)
        
        # ��������
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(10, 5, 10, 5)
        
        # ����ͼ�꣨���̣�
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(40, 40)
        self.icon_label.setPixmap(FIF.GAME.icon().pixmap(QSize(32, 32)))
        
        # ������������ڱ�ǩ
        self.title_label = QLabel(title)
        title_font = self.title_label.font()
        title_font.setPointSize(12)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        
        self.date_label = QLabel(date)
        date_font = self.date_label.font()
        date_font.setPointSize(9)
        self.date_label.setFont(date_font)
        
        # ����ʤ�߱�ǩ
        self.winner_label = QLabel(f"ʤ��: {winner}" if winner else "δ����")
        winner_font = self.winner_label.font()
        winner_font.setPointSize(10)
        self.winner_label.setFont(winner_font)
        
        # ����һ����ֱ���ַ��ñ��������
        self.info_layout = QVBoxLayout()
        self.info_layout.addWidget(self.title_label)
        self.info_layout.addWidget(self.date_label)
        
        # �������Ԫ�ص�������
        self.layout.addWidget(self.icon_label)
        self.layout.addLayout(self.info_layout, 1)  # ��info_layout�������ռ�
        self.layout.addWidget(self.winner_label)


class HistoryInterface(QWidget):
    """��ʷ�Ծֽ���"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("History-Interface")
        
        # ������ʷ��¼����Ŀ¼
        self.history_dir = os.path.join(os.path.expanduser("~"), "Gomoku", "history")
        os.makedirs(self.history_dir, exist_ok=True)
        
        # ����������
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        self.main_layout.setSpacing(15)
        
        # ��������
        self.title_label = QLabel("��ʷ�Ծ�")
        self.title_label.setAlignment(Qt.AlignCenter)
        title_font = self.title_label.font()
        title_font.setPointSize(24)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        
        # �����������Ͱ�ť����
        self.search_layout = QHBoxLayout()
        self.search_edit = SearchLineEdit(self)
        self.search_edit.setPlaceholderText("������ʷ�Ծ�...")
        self.search_edit.setFixedWidth(300)
        self.search_edit.textChanged.connect(self.filter_history)
        
        self.search_layout.addWidget(self.search_edit)
        self.search_layout.addStretch(1)
        
        self.load_button = PushButton("���ضԾ�")
        self.load_button.setFixedWidth(120)
        self.load_button.clicked.connect(self.load_game)
        
        self.delete_button = PushButton("ɾ����¼")
        self.delete_button.setFixedWidth(120)
        self.delete_button.clicked.connect(self.delete_history)
        
        self.import_button = PushButton("����Ծ�")
        self.import_button.setFixedWidth(120)
        self.import_button.clicked.connect(self.import_game)
        
        self.search_layout.addWidget(self.load_button)
        self.search_layout.addWidget(self.delete_button)
        self.search_layout.addWidget(self.import_button)
        
        # ������ʷ��¼�б�
        self.history_list = QListWidget()
        self.history_list.setSelectionMode(QListWidget.SingleSelection)
        self.history_list.setSpacing(5)
        
        # ��������������
        self.main_layout.addWidget(self.title_label)
        self.main_layout.addLayout(self.search_layout)
        self.main_layout.addWidget(self.history_list)
        
        # ������ʷ��¼
        self.load_history()
    
    def load_history(self):
        """������ʷ�Ծּ�¼"""
        self.history_list.clear()
        
        try:
            # ��ȡ��ʷĿ¼�µ�����json�ļ�
            files = [f for f in os.listdir(self.history_dir) if f.endswith('.json')]
            files.sort(key=lambda x: os.path.getmtime(os.path.join(self.history_dir, x)), reverse=True)
            
            if not files:
                # ����ʷ��¼ʱ��ʾ��ʾ
                item = QListWidgetItem()
                widget = QLabel("������ʷ�Ծּ�¼")
                widget.setAlignment(Qt.AlignCenter)
                widget_font = widget.font()
                widget_font.setPointSize(14)
                widget.setFont(widget_font)
                item.setSizeHint(widget.sizeHint())
                self.history_list.addItem(item)
                self.history_list.setItemWidget(item, widget)
                return
            
            for file in files:
                try:
                    with open(os.path.join(self.history_dir, file), 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # �����ļ���������
                    file_name = os.path.splitext(file)[0]
                    timestamp = data.get('timestamp', '')
                    
                    # ���Խ���ʱ���
                    try:
                        if timestamp:
                            dt = datetime.datetime.fromisoformat(timestamp)
                            date_str = dt.strftime("%Y-%m-%d %H:%M:%S")
                        else:
                            date_str = "δ֪ʱ��"
                    except (ValueError, TypeError):
                        date_str = "δ֪ʱ��"
                    
                    # ��ȡʤ����Ϣ
                    winner = "��"
                    if data.get('game_over', False):
                        winner_id = data.get('winner', 0)
                        if winner_id == 1:
                            winner = "����"
                        elif winner_id == 2:
                            winner = "����"
                    else:
                        winner = "δ����"
                    
                    # �����б���
                    item = QListWidgetItem()
                    widget = HistoryListItem(file_name, date_str, winner)
                    item.setSizeHint(widget.sizeHint())
                    item.setData(Qt.UserRole, os.path.join(self.history_dir, file))  # �����ļ�·��
                    
                    self.history_list.addItem(item)
                    self.history_list.setItemWidget(item, widget)
                    
                except Exception as e:
                    print(f"���ؼ�¼�ļ�ʧ��: {file}, ����: {str(e)}")
                    
        except Exception as e:
            print(f"������ʷ��¼ʧ��: {str(e)}")
            InfoBar.error(
                title='����ʧ��',
                content=f"������ʷ��¼ʧ��: {str(e)}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
    
    def filter_history(self, text):
        """���������ı�������ʷ��¼"""
        for i in range(self.history_list.count()):
            item = self.history_list.item(i)
            widget = self.history_list.itemWidget(item)
            
            # �ж��Ƿ�Ϊ��ʾ��ǩ
            if isinstance(widget, QLabel):
                continue
                
            # �������Ƿ���������ı�
            if text.lower() in widget.title_label.text().lower() or text.lower() in widget.date_label.text().lower():
                item.setHidden(False)
            else:
                item.setHidden(True)
    
    def load_game(self):
        """����ѡ�еĶԾ�"""
        selected_items = self.history_list.selectedItems()
        if not selected_items:
            InfoBar.warning(
                title='δѡ��Ծ�',
                content="����ѡ��һ����ʷ�Ծ�",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
            return
        
        file_path = selected_items[0].data(Qt.UserRole)
        
        try:
            # ����Ϸ���ڲ�������Ϸ
            window = BoardWindow(self)
            # TODO: ʵ�ּ����ѱ������ֹ���
            window.show()
            
            InfoBar.success(
                title='���سɹ�',
                content=f"�Ѽ��ضԾ�: {os.path.basename(file_path)}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
        except Exception as e:
            InfoBar.error(
                title='����ʧ��',
                content=f"���ضԾ�ʧ��: {str(e)}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
    
    def delete_history(self):
        """ɾ��ѡ�е���ʷ��¼"""
        selected_items = self.history_list.selectedItems()
        if not selected_items:
            InfoBar.warning(
                title='δѡ���¼',
                content="����ѡ��һ����ʷ��¼",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
            return
        
        file_path = selected_items[0].data(Qt.UserRole)
        
        # ȷ��ɾ��
        reply = QMessageBox.question(
            self, 'ȷ��ɾ��', 
            f"ȷ��Ҫɾ��ѡ�е���ʷ��¼��?\n{os.path.basename(file_path)}",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                os.remove(file_path)
                
                # ���¼�����ʷ��¼
                self.load_history()
                
                InfoBar.success(
                    title='ɾ���ɹ�',
                    content="��ɾ��ѡ�е���ʷ��¼",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self
                )
            except Exception as e:
                InfoBar.error(
                    title='ɾ��ʧ��',
                    content=f"ɾ����ʷ��¼ʧ��: {str(e)}",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self
                )
    
    def import_game(self):
        """���ļ�����Ծ�"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "����Ծ�", "", "JSON�ļ� (*.json)"
        )
        
        if not file_path:
            return
        
        try:
            # ����ļ��Ƿ�Ϊ��Ч�����JSON
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # ����Ҫ���ֶ�
            required_fields = ['board_data', 'current_player', 'game_started']
            if not all(field in data for field in required_fields):
                raise ValueError("��Ч�ĶԾ��ļ���ʽ")
            
            # �����ļ�����ʷĿ¼
            file_name = os.path.basename(file_path)
            if os.path.exists(os.path.join(self.history_dir, file_name)):
                # ����ļ��Ѵ��ڣ����ʱ���ǰ׺
                timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S_")
                file_name = timestamp + file_name
            
            import shutil
            shutil.copy2(file_path, os.path.join(self.history_dir, file_name))
            
            # ���¼�����ʷ��¼
            self.load_history()
            
            InfoBar.success(
                title='����ɹ�',
                content=f"�ѵ���Ծ�: {file_name}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
        except Exception as e:
            InfoBar.error(
                title='����ʧ��',
                content=f"����Ծ�ʧ��: {str(e)}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
