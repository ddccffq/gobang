# coding:utf-8

class GomokuGame:
    """��������Ϸ�߼���"""
    
    def __init__(self, board_size=15):
        """��ʼ����Ϸ
        
        Args:
            board_size: ���̴�С��Ĭ��Ϊ15x15
        """
        self.board_size = board_size
        self.board = [[0 for _ in range(board_size)] for _ in range(board_size)]
        self.current_player = 1  # 1������壬2�������
        self.game_over = False
        self.winner = 0
        self.move_history = []
    
    def place_stone(self, row, col):
        """��������
        
        Args:
            row: �к� (0-based)
            col: �к� (0-based)
            
        Returns:
            bool: �����Ƿ�ɹ�
        """
        # ��������Ƿ���Ч
        if not (0 <= row < self.board_size and 0 <= col < self.board_size):
            return False
        
        # ���λ���Ƿ��ѱ�ռ��
        if self.board[row][col] != 0:
            return False
        
        # �����Ϸ�Ƿ��ѽ���
        if self.game_over:
            return False
        
        # ��������
        self.board[row][col] = self.current_player
        self.move_history.append((row, col, self.current_player))
        
        # ����Ƿ�ʤ��
        if self._check_win(row, col):
            self.game_over = True
            self.winner = self.current_player
        
        # �л����
        self.current_player = 3 - self.current_player  # 1��2��2��1
        
        return True
    
    def _check_win(self, row, col):
        """������һ���Ƿ��ʤ
        
        Args:
            row: ���һ�ֵ��к�
            col: ���һ�ֵ��к�
            
        Returns:
            bool: �Ƿ��ʤ
        """
        player = self.board[row][col]
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        
        for dr, dc in directions:
            count = 1
            
            # ��һ��������
            r, c = row + dr, col + dc
            while 0 <= r < self.board_size and 0 <= c < self.board_size and self.board[r][c] == player:
                count += 1
                r += dr
                c += dc
            
            # ���෴������
            r, c = row - dr, col - dc
            while 0 <= r < self.board_size and 0 <= c < self.board_size and self.board[r][c] == player:
                count += 1
                r -= dr
                c -= dc
            
            # ���������5����������ͬ���ӣ����ʤ
            if count >= 5:
                return True
        
        return False
    
    def reset(self):
        """������Ϸ"""
        self.board = [[0 for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.current_player = 1
        self.game_over = False
        self.winner = 0
        self.move_history = []
