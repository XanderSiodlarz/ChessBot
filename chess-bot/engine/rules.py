from engine.move import Move
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
    #move generation - overall legalmoves
    def generate_legal_moves(self, color: str):
        pseudo_legal_moves = self.generate_pseudo_legal_moves(color)
        legal_moves = []
        
        for move in pseudo_legal_moves:
            self.board.make_move(move)
            if not self.in_check(color):
                legal_moves.append(move)
            self.board.undo_move()
        return legal_moves
    #move generation - overall moves
    def generate_pseudo_legal_moves(self, color: str):
        moves = []
        for r in range(8):
            for c in range(8):
                piece = self.board.get_piece(r, c)
                if piece[0] != color[0]:
                    continue
                piece_type = piece[1]
                
                if piece_type == "P":
                    moves.extend(self._generate_pawn_moves(r, c, color))
                elif piece_type == "N":
                    moves.extend(self._generate_knight_moves(r, c, color))
                elif piece_type == "B":
                    moves.extend(self._generate_sliding_moves(r, c, color, self.bishop_directions))
                elif piece_type == "R":
                    moves.extend(self._generate_sliding_moves(r, c, color, self.rook_directions))
                elif piece_type == "Q":
                    moves.extend(self._generate_sliding_moves(r, c, color, self.queen_directions))
                elif piece_type == "K":
                    moves.extend(self._generate_king_moves(r, c, color))
        return moves
    #move generation - piece specific
    def _generate_pawn_moves(self, r, c, color) -> list:
        moves = []
        piece = self.board.get_piece(r, c)
        dir = -1 if color == "w" else 1
        start_row = 6 if color == "w" else 1
        prom_row = 0 if color == "w" else 7
        
        new_r = r + dir
        #generate normal advancement
        if 0 <= new_r < 8:
            if self.board.get_piece(new_r, c) == "--":
                if new_r == prom_row:
                    for prom_piece in ["Q", "R", "N", "B"]:
                        moves.append(Move((r,c), (new_r,c), piece, promotion=prom_piece))
                else:
                    moves.append(Move((r,c), (new_r, c), piece))
                #generate starting double move
                if r == start_row and self.board.get_piece(new_r + dir, c) == "--":
                    moves.append(Move((r,c), (new_r + dir, c), piece))
            #generate capture to the left
            if c - 1 >= 0:
                target_piece = self.board.get_piece(new_r, c-1)
                if target_piece[0] != color[0] and target_piece[0] != "-":
                    if new_r == prom_row:
                        for prom_piece in ["Q", "R", "N", "B"]:
                            moves.append(Move((r,c), (new_r,c-1), piece, piece_captured=target_piece, promotion=prom_piece))
                    else:
                        moves.append(Move((r,c), (new_r, c-1), piece, piece_captured=target_piece))
            #generate capture to the right
            if c + 1 < 8:
                target_piece = self.board.get_piece(new_r, c+1)
                if target_piece[0] != color[0] and target_piece[0] != "-":
                    if new_r == prom_row:
                        for prom_piece in ["Q", "R", "N", "B"]:
                            moves.append(Move((r,c), (new_r,c+1), piece, piece_captured=target_piece, promotion=prom_piece))
                    else:
                        moves.append(Move((r,c), (new_r, c+1), piece, piece_captured=target_piece))
            #generate en passant
            for dc in [-1, 1]:
                if self.board.en_passant_square == (new_r, c + dc):
                    captured_pawn = "bP" if color == "w" else "wP"
                    moves.append(Move((r,c), (new_r, c + dc), piece, piece_captured=captured_pawn))
        return moves
    def _generate_knight_moves(self, r, c, color) -> list:
        moves = []
        piece = self.board.get_piece(r, c)
        for dr, dc in self.knight_moves:
            new_r, new_c = r + dr, c + dc
            if 0 <= new_r < 8 and 0 <= new_c < 8:
                target_piece = self.board.get_piece(new_r, new_c)
                if target_piece[0] != color[0]:
                    moves.append(Move((r,c), (new_r, new_c), piece, piece_captured=target_piece))
        return moves
    def _generate_sliding_moves(self, r, c, color, dir) -> list:
        moves = []
        piece = self.board.get_piece(r,c)
        for dr, dc in dir:
            new_r, new_c = r + dr, c + dc
            while 0 <= new_r < 8 and 0 <= new_c < 8:
                target_piece = self.board.get_piece(new_r, new_c)
                if target_piece == "--":
                    moves.append(Move((r,c), (new_r, new_c), piece))
                else:
                    if target_piece[0] != color[0]:
                        moves.append(Move((r,c), (new_r, new_c), piece, piece_captured=target_piece))
                        break
                new_r += dr
                new_c += dc
        return moves
    def _generate_king_moves(self, r, c, color) -> list:
        moves = []
        piece = self.board.get_piece(r, c)
        for dr, dc in self.king_moves:
            new_r, new_c = r + dr, c + dc
            if 0 <= new_r < 8 and 0 <= new_c < 8:
                target_piece = self.board.get_piece(new_r, new_c)
                if target_piece[0] != color[0]:
                    moves.append(Move((r,c), (new_r, new_c), piece, piece_captured=target_piece))
        if not self.in_check(color):
            if self.can_castle(color, "K"):
                king_end_col = 6
                moves.append(Move((r,c), (r, king_end_col), piece))
            if self.can_castle(color, "Q"):
                king_end_col = 2
                moves.append(Move((r,c), (r, king_end_col), piece))
        return moves
    def is_checkmate(self, color:str) -> bool:
        if not self.in_check(color):
            return False
        legal_moves = self.generate_legal_moves(color)
        if len(legal_moves) == 0:
            return True
    def is_stalemate(self, color:str) -> bool:
        if not self.in_check(color):
            legal_moves = self.generate_legal_moves(color)
            if len(legal_moves) == 0:
                return True
        return False
    def is_draw(self, color:str):
        if self.is_stalemate(color):
            return True
        if self.board.halfmove_clock >= 50:
            return True
        return False