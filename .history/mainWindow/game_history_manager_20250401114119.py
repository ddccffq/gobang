# coding:utf-8
import os
import json
import datetime
import shutil

class GameHistoryManager:
    """��Ϸ��ʷ��¼������"""
    
    def __init__(self):
        # ������ʷ��¼����Ŀ¼
        self.history_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "history")
        os.makedirs(self.history_dir, exist_ok=True)
    
    def save_game(self, game_data, filename=None):
        """������Ϸ����ʷ��¼"""
        # ���AI������Ϣ
        if 'player_info' not in game_data:
            game_data['player_info'] = {
                'player1': '���',  # ���1Ĭ�����������
                'player2': 'AI'     # ���2Ĭ����AI
            }
        
        # ���ʱ���
        if 'timestamp' not in game_data:
            game_data['timestamp'] = datetime.datetime.now().isoformat()
        
        # ����Ĭ���ļ��� (���δ�ṩ)
        if filename is None:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            winner = "��ʤ" if game_data.get('winner') == 1 else "��ʤ" if game_data.get('winner') == 2 else "δ����"
            filename = f"��ս_{timestamp}_{winner}.json"
        
        # ȷ���ļ�·��
        filepath = os.path.join(self.history_dir, filename)
        
        # �����ļ�
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(game_data, f, ensure_ascii=False, indent=2)
            return filepath
        except Exception as e:
            print(f"������ʷ��¼ʧ��: {str(e)}")
            return None
    
    def get_history_list(self):
        """��ȡ������ʷ��¼"""
        history_list = []
        
        # �����ʷĿ¼�Ƿ����
        if not os.path.exists(self.history_dir):
            return history_list
        
        # ��ȡ����json�ļ�
        for filename in os.listdir(self.history_dir):
            if not filename.endswith('.json'):
                continue
            
            filepath = os.path.join(self.history_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # ����������Ϣ
                timestamp = data.get('timestamp', '')
                try:
                    date_obj = datetime.datetime.fromisoformat(timestamp)
                    date_str = date_obj.strftime('%Y-%m-%d %H:%M:%S')
                except (ValueError, TypeError):
                    date_str = "δ֪ʱ��"
                
                # ��ȡ�����Ϣ
                player_info = data.get('player_info', {})
                player1 = player_info.get('player1', '���')
                player2 = player_info.get('player2', 'AI')
                
                # ��ȡʤ����Ϣ
                winner = None
                if data.get('game_over', False):
                    winner_id = data.get('winner', 0)
                    if winner_id == 1:
                        winner = player1
                    elif winner_id == 2:
                        winner = player2
                
                # ��ӵ��б�
                history_list.append({
                    'filename': filename,
                    'filepath': filepath,
                    'date': date_str,
                    'timestamp': timestamp,
                    'player1': player1,
                    'player2': player2,
                    'winner': winner,
                    'game_data': data
                })
                
            except Exception as e:
                print(f"��ȡ��ʷ��¼ {filename} ʧ��: {str(e)}")
        
        # ��ʱ�����������
        history_list.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return history_list
    
    def delete_history(self, filename):
        """ɾ����ʷ��¼"""
        filepath = os.path.join(self.history_dir, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False
    
    def import_history(self, source_path):
        """�����ⲿ��ʷ��¼"""
        try:
            # ��֤�ļ��Ƿ�����Ч����Ϸ����
            with open(source_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # ����Ҫ�ֶ�
            required_fields = ['board_data', 'current_player']
            if not all(field in data for field in required_fields):
                raise ValueError("��Ч�ĶԾ��ļ���ʽ")
            
            # ���AI������Ϣ�����û�У�
            if 'player_info' not in data:
                data['player_info'] = {
                    'player1': '���',
                    'player2': 'AI'
                }
            
            # ���ʱ��������û�У�
            if 'timestamp' not in data:
                data['timestamp'] = datetime.datetime.now().isoformat()
            
            # ����Ŀ���ļ���
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            source_filename = os.path.basename(source_path)
            target_filename = f"����_{timestamp}_{source_filename}"
            target_path = os.path.join(self.history_dir, target_filename)
            
            # �����ļ�
            with open(target_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            return target_path
            
        except Exception as e:
            print(f"������ʷ��¼ʧ��: {str(e)}")
            raise
