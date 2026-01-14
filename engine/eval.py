class Evaluator:
    def __init__(self):
        self.piece_values = {
            "P": 100,
            "N": 320,
            "B": 320,
            "R": 500,
            "Q": 900,
            "K": 20000
        }
        
        self.pawn_table = [
            [0,  5, 10, 15, 20, 25, 30, 0],
            [5, 10, 15, 20, 25, 30, 35, 5],
            [0, 10, 20, 25, 30, 35, 40, 0],
            [0, 15, 25, 30, 35, 40, 45, 0],
            [5, 20, 30, 35, 40, 45, 50, 5],
            [10,25, 35, 40, 45, 50, 55,10],
            [50,55, 60, 65, 70, 75,80,50],
            [0, 0,   0,   0,   0,   0,   0,   0]
        ]
        
        self.knight_table = [
            [-50,-40,-30,-30,-30,-30,-40,-50],
            [-40,-20,  0,  0,  0,  0,-20,-40],
            [-30,  0, 10, 15, 15, 10,  0,-30],
            [-30,  5, 15, 20, 20, 15,  5,-30],
            [-30,  0, 15, 20, 20, 15,  0,-30],
            [-30,  5, 10, 15, 15, 10,  5,-30],
            [-40,-20,  0,  5,  5,  0,-20,-40],
            [-50,-40,-30,-30,-30,-30,-40,-50]
        ]
        self.bishop_table = [
            [-20,-10,-10,-10,-10,-10,-10,-20],
            [-10,  0,  0,  0,  0,  0,  0,-10],
            [-10,  0,  5, 10, 10,  5,  0,-10],
            [-10,  5,  5, 10, 10,  5,  5,-10],
            [-10,  0, 10, 10, 10, 10,  0,-10],
            [-10, 10, 10, 10, 10, 10, 10,-10],
            [-10,  5,  0,  0,  0,  0,  5,-10],
            [-20,-10,-10,-10,-10,-10,-10,-20]
        ]
        
        self.rook_table = [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [5, 10, 10, 10, 10, 10, 10, 5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [0, 0, 0, 5, 5, 0, 0, 0]
        ]
        self.queen_table = [
            [-20,-10,-10, -5, -5,-10,-10,-20],
            [-10,  0,  0,  0,  0,  0,  0,-10],
            [-10,  0,  5,  5,  5,  5,  0,-10],
            [ -5,  0,  5,  5,  5,  5,  0, -5],
            [  0,  0,  5,  5,  5,  5,  0, -5],
            [-10,  5,  5,  5,  5,  5,  0,-10],
            [-10,  0,  5,  0,  0,  0,  0,-10],
            [-20,-10,-10, -5, -5,-10,-10,-20]
        ]
        
        self.king_table_middlegame = [
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-20,-30,-30,-40,-40,-30,-30,-20],
            [-10,-20,-20,-20,-20,-20,-20,-10],
             [ 20, 20,  0,  0,  0,  0, 20, 20],
             [ 20, 30, 10,  0,  0, 10, 30, 20]
        ]
        self.king_table_endgame = [
            [-50,-40,-30,-20,-20,-30,-40,-50],
            [-30,-20,-10,  0,  0,-10,-20,-30],
            [-30,-10, 20, 30, 30, 20,-10,-30],
            [-30,-10, 30, 40, 40, 30,-10,-30],
            [-30,-10, 30, 40, 40, 30,-10,-30],
            [-30,-10, 20, 30, 30, 20,-10,-30],
            [-30,-30,  0,  0,  0,  0,-30,-30],
            [-50,-40,-30,-20,-20,-30,-40,-50]
        ]

    def evaluate(self, board):
        score = 0

        score += self.evaluate_material_and_position(board)

        return score
    
    def evaluate_material_and_position(self, board):
        score = 0
        piece_count = 0
        for r in range(8):
            for c in range(8):
                piece = board.get_piece(r,c)
                if piece != "--":
                    piece_count += 1
                    piece_type = piece[1]
                    piece_color = piece[0]
                    
                    piece_value = self.piece_values[piece_type]
                    positional_value = self.get_positional_val(piece_type, r, c, piece_color, piece_count)
                    
                    if piece_color == "w":
                        score += piece_value + positional_value
                    else:
                        score -= piece_value + positional_value
        return score
    def get_positional_val(self, pt, r, c, color, pc):
        table_row = r if color == "w" else 7 - r
        
        if pt == 'P':
            return self.pawn_table[table_row][c]
        elif pt == 'N':
            return self.knight_table[table_row][c]
        elif pt == 'B':
            return self.bishop_table[table_row][c]
        elif pt == 'R':
            return self.rook_table[table_row][c]
        elif pt == 'Q':
            return self.queen_table[table_row][c]
        elif pt == 'K':
            if pc >= 16:
                return self.king_table_middlegame[table_row][c]
            else:
                return self.king_table_endgame[table_row][c]
            
        return 0
    