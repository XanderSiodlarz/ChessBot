from engine.move import Move
from engine.rules import Rules
class Board:
    def __init__(self, fen=None):
        if fen:
            self.load_fen(fen)
        else:
            self._init_start_position()
    def _init_start_position(self):
        #Standard chess starting position
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        ]
        #White always goes first
        self.white_to_move = True

        self.en_passant_square = None
        #Castle can occur from both colors and sides if king/rook is unmoved
        #All castling positions start out true(No pieces have moved)
        self.castle_rights = {
            "wK": True,
            "wQ": True,
            "bK": True,
            "bQ": True
        }
        #50 halfmoves equals draw
        self.halfmoves = 0
        
        self.fullmoves = 1
        #Used for search and undoing moves
        self.move_stack = []
    def to_fen(self) -> str:
        fen_rows = []
        for row in self.board:
            empty_count = 0
            fen_row = ""
            for piece in row:
                if piece == "--":
                    empty_count += 1
                else:
                    if empty_count > 0:
                        fen_row += str(empty_count)
                        empty_count = 0
                    color = piece[0]
                    p = piece[1]
                    fen_row += p.upper() if color == "w" else p.lower()
            if empty_count > 0:
                fen_row += str(empty_count)
            fen_rows.append(fen_row)
        board_part = "/".join(fen_rows)
        active_color = 'w' if self.white_to_move else 'b'
        castling_part = ''.join([k for k, v in self.castle_rights.items() if v])
        if castling_part == '':
            castling_part = '-'
        en_passant_part = self.en_passant_square if self.en_passant_square else '-'
        fen = f"{board_part} {active_color} {castling_part} {en_passant_part} {self.halfmoves} {self.fullmoves}"
        return fen
    def load_fen(self, fen: str):
        parts = fen.split()
        board_part = parts[0]
        rows = board_part.split('/')
        self.board = []
        for row in rows:
            board_row = []
            for char in row:
                if char.isdigit():
                    board_row.extend(['--'] * int(char))
                else:
                    color = 'w' if char.isupper() else 'b'
                    piece = char.upper()
                    self.board_row.append(color + piece)
            self.board.append(board_row)
        self.white_to_move = (parts[1] == 'w')
        self.castle_rights = parts[2]
        self.en_passant_square = parts[3] if parts[3] != '-' else None
        self.halfmoves = int(parts[4])
        self.fullmoves = int(parts[5])
    def current_board(self):
        return self.board
    def copy(self):
        new_board = Board()
        new_board.board = [row[:] for row in self.board]
        new_board.white_to_move = self.white_to_move
        new_board.en_passant_square = self.en_passant_square
        new_board.castle_rights = self.castle_rights.copy()
        new_board.halfmove_clock = self.halfmove_clock
        new_board.fullmoves = self.fullmoves
        new_board.move_stack = self.move_stack[:]
        return new_board
    def get_piece(self, row, col) -> str:
        if 0 <= row < 8 and 0 <= col < 8:
            return self.board[row][col]
        else:
            return ValueError("Row and Column must be between 0 and 7 inclusive.")
    def set_piece(self, row, col, piece: str):
        if 0 <= row < 8 and 0 <= col < 8:
            self.board[row][col] = piece
        else:
            return ValueError("Row and Column must be between 0 and 7 inclusive.")
    def find_king(self, color:str) -> tuple:
        king = "wK" if color == "w" else "bK"
        #Kings typically won't move far from starting until end game
        if king == "wK":
            for r in range(8, -1, -1):
                for c in range(8, -1, -1):
                    if self.board[r][c] == king:
                        return (r, c)
        else:
            for r in range(8):
                for c in range(8):
                    if self.board[r][c] == king:
                        return (r, c)
        return None
    #Use Move class
    def make_move(self, move: Move):
        state = (
            move, 
            move.moved_piece,
            move.piece_captured,
            self.castle_rights.copy(),
            self.en_passant_square,
            self.halfmove_clock,   
            self.fullmoves
        )
        self.move_stack.append(state)
        
        piece = move.moved_piece
        
        if move.is_castling(piece):
            color = piece[0]
            if move.end[1] == 6:
                self.board[move.start[0]][7] = "--"
                self.board[move.end[0]][5] = color + "R"
            elif move.end[1] == 2:
                self.board[move.start[0]][0] = "--"
                self.board[move.end[0]][3] = color + "R"

        self.board[move.start[0]][move.start[1]] = "--"
        self.board[move.end[0]][move.end[1]] = piece

        if move.promotion:
            self.board[move.end[0]][move.end[1]] = piece[0] + move.promotion

        #Update castle rights
        if piece[1] == "K":
            if piece[0] == "w":
                self.castle_rights["wK"] = False
                self.castle_rights["wQ"] = False
            else:
                self.castle_rights["bK"] = False
                self.castle_rights["bQ"] = False
        elif piece[1] == "R":
            if piece[0] == "w":
                if move.start == (7, 0):
                    self.castle_rights["wQ"] = False
                elif move.start == (7, 7):
                    self.castle_rights["wK"] = False
            else:
                if move.start == (0, 0):
                    self.castle_rights["bQ"] = False
                elif move.start == (0, 7):
                    self.castle_rights["bK"] = False
        
        if piece[1] == "P" or move.piece_captured != "--":
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1
            
        if not self.white_to_move:
            self.fullmoves += 1 
        
        self.white_to_move = not self.white_to_move
    def undo_move(self):
        if not self.move_stack:
            return 
        state = self.move_stack.pop()
        move, moved_piece, captured_piece, castling_rights, en_passant_square, halfmove_clock, fullmoves = state
        self.board[move.start[0]][move.start[1]] = moved_piece
        self.board[move.end[0]][move.end[1]] = captured_piece
        self.castle_rights = castling_rights
        self.en_passant_square = en_passant_square
        self.halfmove_clock = halfmove_clock
        self.fullmoves = fullmoves
        
        self.white_to_move = not self.white_to_move
    #Use Rules class