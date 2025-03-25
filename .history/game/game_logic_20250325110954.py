# coding:utf-8

class GomokuGame:
    """五子棋游戏逻辑类"""
    
    def __init__(self, board_size=15):
        """初始化游戏
        
        Args:
            board_size: 棋盘大小，默认为15x15
        """
        self.board_size = board_size
        self.board = [[0 for _ in range(board_size)] for _ in range(board_size)]
        self.current_player = 1  # 1代表黑棋，2代表白棋
        self.game_over = False
        self.winner = 0
        self.move_history = []
    
    def place_stone(self, row, col):
        """放置棋子
        
        Args:
            row: 行号 (0-based)
            col: 列号 (0-based)
            
        Returns:
            bool: 放置是否成功
        """
        # 检查坐标是否有效
        if not (0 <= row < self.board_size and 0 <= col < self.board_size):
            return False
        
        # 检查位置是否已被占用
        if self.board[row][col] != 0:
            return False
        
        # 检查游戏是否已结束
        if self.game_over:
            return False
        
        # 放置棋子
        self.board[row][col] = self.current_player
        self.move_history.append((row, col, self.current_player))
        
        # 检查是否胜利
        if self._check_win(row, col):
            self.game_over = True
            self.winner = self.current_player
        
        # 切换玩家
        self.current_player = 3 - self.current_player  # 1变2，2变1
        
        return True
    
    def _check_win(self, row, col):
        """检查最后一手是否获胜
        
        Args:
            row: 最后一手的行号
            col: 最后一手的列号
            
        Returns:
            bool: 是否获胜
        """
        player = self.board[row][col]
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        
        for dr, dc in directions:
            count = 1
            
            # 向一个方向检查
            r, c = row + dr, col + dc
            while 0 <= r < self.board_size and 0 <= c < self.board_size and self.board[r][c] == player:
                count += 1
                r += dr
                c += dc
            
            # 向相反方向检查
            r, c = row - dr, col - dc
            while 0 <= r < self.board_size and 0 <= c < self.board_size and self.board[r][c] == player:
                count += 1
                r -= dr
                c -= dc
            
            # 如果有连续5个或以上相同棋子，则获胜
            if count >= 5:
                return True
        
        return False
    
    def reset(self):
        """重置游戏"""
        self.board = [[0 for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.current_player = 1
        self.game_over = False
        self.winner = 0
        self.move_history = []
