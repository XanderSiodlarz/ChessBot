class Rules:
    def __init__(self, board):
        self.board = board
        
        self.knight_moves = [
            (-2, -1), (-2, 1), (2, -1), (2, 1),
            (-1, -2), (-1, 2), (1, -2), (1, 2)
        ]
        
        self.king_moves = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 1), (1, -1), 
            (1, 0), (1, 1)
        ]
        
        self.bishop_directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        self.rook_directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        self.queen_directions = self.bishop_directions + self.rook_directions
    
    #board:array, square:tuple, attacking_color:str
    def is_square_attacked(self, board, square, attacking_color):
        for r in range(8):
            for c in range(8):
                piece = board.get_piece(r,c)
                if piece[0] != attacking_color[0] or piece[0] == "-":
                    continue
                if piece[1] == "P":
                    direction = -1 if attacking_color == "w" else 1
                    if r + direction == square[0]:
                        if c - 1 == square[1] or c + 1 == square[1]:
                            return True
                elif piece[1] == "N":
                    for dr, dc in self.knight_moves:
                        if (r+dr, c+dc) == square:
                            return True
                elif piece[1] in ["B", "Q", "R"]:
                        direction = []
                        if piece[1] in ["B", "Q"]:
                            direction += self.bishop_directions
                        if piece[1] in ["R", "Q"]:
                            direction += self.rook_directions
                        for dr, dc in direction:
                            nr, nc = r + dr, c + dc
                            while 0 <= nr < 8 and 0 <= nc < 8:
                                target_piece = board.get_piece(nr, nc)
                                if (nr, nc) == square:
                                    return True
                                if target_piece != "--":
                                    break
                                nr += dr
                                nc += dc
                elif piece[1] == "K":
                    for dr, dc in self.king_moves:
                        if (r+dr, c+dc) == square:
                            return True
        return False
    def in_check(self, color:str) -> bool:
        king_pos = self.board.find_king(color)
        if not king_pos:
            return False
        attacking_color = "b" if color == "w" else "w"
        return self.is_square_attacked(self.board, king_pos, attacking_color)
    def can_castle(self, color, side):
        if color == "w":
            row = 7
            castle_key = "w" + side
        else:
            row = 0
            castle_key = "b" + side
        
        if not self.board.castle_rights[castle_key]:
            return False
        
        if self.in_check(color):
            return False
        
        attacking_color = "b" if color == "w" else "w"
        
        if side == "K": 
            if (self.board.get_piece(row, 5) != "--" or 
                self.board.get_piece(row, 6) != "--"):
                return False
            if (self.is_square_attacked(self.board, (row, 5), attacking_color) or
                self.is_square_attacked(self.board, (row, 6), attacking_color)):
                return False
            return True
        
        else:
            if (self.board.get_piece(row, 1) != "--" or 
                self.board.get_piece(row, 2) != "--" or
                self.board.get_piece(row, 3) != "--"):
                return False
            if (self.is_square_attacked(self.board, (row, 2), attacking_color) or
                self.is_square_attacked(self.board, (row, 3), attacking_color)):
                return False
            return True