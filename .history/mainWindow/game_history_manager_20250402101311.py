# coding:utf-8
import os
import json
import datetime
import shutil

# 修改为绝对导入
from mainWindow.config import cfg

class GameHistoryManager:
    """游戏历史记录管理器"""
    
    def __init__(self):
        # 设置配置文件路径
        self.config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config")
        os.makedirs(self.config_dir, exist_ok=True)
        
        # 收藏的对局文件路径集合
        self.favorites_file = os.path.join(self.config_dir, "favorites.json")
        self.favorites = self.load_favorites()
        
        # 加载设置
        self.load_settings()
    
    def load_settings(self):
        """加载设置"""
        default_history_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), cfg.get(cfg.historyDir))
        self.history_dir = default_history_dir
        
        # 确保目录存在
        os.makedirs(self.history_dir, exist_ok=True)
        print(f"历史记录保存目录: {self.history_dir}")
    
    def save_settings(self):
        """保存设置"""
        try:
            # 更新cfg里的历史记录目录
            cfg.set(cfg.historyDir, os.path.basename(self.history_dir))
            cfg.save()
            return True
        except Exception as e:
            print(f"保存设置失败: {str(e)}")
            return False
    
    def set_history_dir(self, directory):
        """设置历史记录目录"""
        self.history_dir = directory
        os.makedirs(self.history_dir, exist_ok=True)
    
    def reset_to_default(self):
        """重置为默认设置"""
        self.history_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), cfg.get(cfg.historyDir))
        os.makedirs(self.history_dir, exist_ok=True)
        self.save_settings()
    
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
        
        # 确保目录存在
        os.makedirs(self.history_dir, exist_ok=True)
        
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
    
    def load_favorites(self):
        """加载已收藏的对局列表"""
        if os.path.exists(self.favorites_file):
            try:
                with open(self.favorites_file, 'r', encoding='utf-8') as f:
                    return set(json.load(f))
            except Exception as e:
                print(f"加载收藏列表失败: {str(e)}")
        return set()
    
    def save_favorites(self):
        """保存收藏列表"""
        try:
            with open(self.favorites_file, 'w', encoding='utf-8') as f:
                json.dump(list(self.favorites), f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存收藏列表失败: {str(e)}")
            return False
    
    def toggle_favorite(self, filepath):
        """切换对局的收藏状态"""
        if filepath in self.favorites:
            self.favorites.remove(filepath)
            result = False  # 取消收藏
        else:
            self.favorites.add(filepath)
            result = True  # 添加收藏
        
        self.save_favorites()
        return result
    
    def is_favorite(self, filepath):
        """检查对局是否已收藏"""
        return filepath in self.favorites
    
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
                # 检查文件是否可访问
                if not os.access(filepath, os.R_OK):
                    print(f"无法访问文件: {filepath}")
                    continue
                    
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 解析基本信息
                timestamp = data.get('timestamp', '')
                try:
                    date_obj = datetime.datetime.fromisoformat(timestamp)
                    date_str = date_obj.strftime('%Y-%m-%d %H:%M:%S')
                except (ValueError, TypeError):
                    # 如果没有时间戳或格式不正确，使用文件修改时间
                    date_str = datetime.datetime.fromtimestamp(
                        os.path.getmtime(filepath)
                    ).strftime('%Y-%m-%d %H:%M:%S')
                
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
                    'game_data': data,
                    'modified_time': os.path.getmtime(filepath),  # 添加文件修改时间
                    'is_favorite': filepath in self.favorites  # 添加收藏状态
                })
                
            except Exception as e:
                print(f"读取历史记录 {filename} 失败: {str(e)}")
        
        # 按收藏状态和修改时间排序，收藏的排前面，同样收藏状态下按时间排序
        history_list.sort(key=lambda x: (not x.get('is_favorite'), -x.get('modified_time', 0)))
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
            
            # 生成目标文件名
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            source_filename = os.path.basename(source_path)
            target_filename = f"导入_{timestamp}_{source_filename}"
            target_path = os.path.join(self.history_dir, target_filename)
            
            # 保存文件
            with open(target_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            return target_path
            
        except Exception as e:
            print(f"导入历史记录失败: {str(e)}")
            raise
