# coding:utf-8
import os
import json
import datetime
import shutil

class GameHistoryManager:
    """游戏历史记录管理器"""
    
    def __init__(self):
        # 设置历史记录保存目录 - 使用新创建的文件夹
        self.history_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "game_history")
        os.makedirs(self.history_dir, exist_ok=True)
        print(f"历史记录保存目录: {self.history_dir}")
    
    def save_game(self, game_data, filename=None):
        """保存游戏到历史记录"""
        # 添加AI对手信息
        if 'player_info' not in game_data:
            game_data['player_info'] = {
                'player1': '玩家',  # 玩家1默认是人类玩家
                'player2': 'AI'     # 玩家2默认是AI
            }
        
        # 添加时间戳
        if 'timestamp' not in game_data:
            game_data['timestamp'] = datetime.datetime.now().isoformat()
        
        # 生成默认文件名 (如果未提供)
        if filename is None:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            winner = "黑胜" if game_data.get('winner') == 1 else "白胜" if game_data.get('winner') == 2 else "未结束"
            filename = f"对战_{timestamp}_{winner}.json"
        
        # 确保文件路径
        filepath = os.path.join(self.history_dir, filename)
        
        # 保存文件
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(game_data, f, ensure_ascii=False, indent=2)
            return filepath
        except Exception as e:
            print(f"保存历史记录失败: {str(e)}")
            return None
    
    def get_history_list(self):
        """获取所有历史记录"""
        history_list = []
        
        # 检查历史目录是否存在
        if not os.path.exists(self.history_dir):
            return history_list
        
        # 获取所有json文件
        for filename in os.listdir(self.history_dir):
            if not filename.endswith('.json'):
                continue
            
            filepath = os.path.join(self.history_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 解析基本信息
                timestamp = data.get('timestamp', '')
                try:
                    date_obj = datetime.datetime.fromisoformat(timestamp)
                    date_str = date_obj.strftime('%Y-%m-%d %H:%M:%S')
                except (ValueError, TypeError):
                    date_str = "未知时间"
                
                # 获取玩家信息
                player_info = data.get('player_info', {})
                player1 = player_info.get('player1', '玩家')
                player2 = player_info.get('player2', 'AI')
                
                # 获取胜者信息
                winner = None
                if data.get('game_over', False):
                    winner_id = data.get('winner', 0)
                    if winner_id == 1:
                        winner = player1
                    elif winner_id == 2:
                        winner = player2
                
                # 添加到列表
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
                print(f"读取历史记录 {filename} 失败: {str(e)}")
        
        # 按时间戳倒序排序
        history_list.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return history_list
    
    def delete_history(self, filename):
        """删除历史记录"""
        filepath = os.path.join(self.history_dir, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False
    
    def import_history(self, source_path):
        """导入外部历史记录"""
        try:
            # 验证文件是否是有效的游戏数据
            with open(source_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # 检查必要字段
            required_fields = ['board_data', 'current_player']
            if not all(field in data for field in required_fields):
                raise ValueError("无效的对局文件格式")
            
            # 添加AI对手信息（如果没有）
            if 'player_info' not in data:
                data['player_info'] = {
                    'player1': '玩家',
                    'player2': 'AI'
                }
            
            # 添加时间戳（如果没有）
            if 'timestamp' not in data:
                data['timestamp'] = datetime.datetime.now().isoformat()
            
            # 获取对局的胜负情况
            winner_str = "黑胜" if data.get('winner') == 1 else "白胜" if data.get('winner') == 2 else "未结束"
            
            # 生成与保存对局相同格式的文件名
            current_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            target_filename = f"对战_{current_time}_{winner_str}.json"
            target_path = os.path.join(self.history_dir, target_filename)
            
            # 保存文件
            with open(target_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            return target_path
            
        except Exception as e:
            print(f"导入历史记录失败: {str(e)}")
            raise
