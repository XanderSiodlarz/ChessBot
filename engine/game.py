from engine.board import Board
from engine.rules import Rules
from engine.eval import Evaluator
from engine.search import Search
from engine.move import Move
class Game:
    def __init__(self, player_color="w", ai_depth = 4):
        self.board = Board()
        self.rules = Rules(self.board)
        self.evaluator = Evaluator()
        self.search = Search(self.board, self.rules, self.evaluator)
        
        self.player_color = player_color
        self.ai_color = "b" if player_color == "w" else "w"
        self.ai_depth = ai_depth
        
        self.game_over = False
        self.winner = None
        self.game_over_reason = None
        
        self.move_history = []
        
    def is_player_turn(self):
        return self.board.white_to_move == (self.player_color == "w")
    def is_ai_turn(self):
        return not self.is_player_turn()
    def get_legal_moves(self):
        color = "w" if self.board.white_to_move else "b"
        return self.rules.generate_legal_moves(color)
    def is_legal_move(self, move):
        legal_moves = self.get_legal_moves()
        
        for legal_move in legal_moves:
            if (move.start == legal_move.start and move.end == legal_move.end and move.promotion == legal_move.promotion):
                return True
        return False
    def make_player_move(self, start, end, promo=None):
        if self.game_over:
            return False
        if not self.is_player_turn():
            return False
        
        moved_piece = self.board.get_piece(start[0], start[1])
        captured_piece = self.board.get_piece(end[0], end[1])
        move = Move(start, end, moved_piece, captured_piece, promo)
        
        if not self.is_legal_move(move):
            return False
        
        self.board.make_move(move)
        self.move_history.append(move)
        
        self.check_game_state()
        
        return True
    def make_ai_move(self):
        if self.game_over:
            return False
        if not self.is_ai_turn():
            return False
        
        print("AI thinking...")
        best_move = self.search.find_best_move(self.ai_depth)
        
        if best_move is None:
            self.check_game_state()
            return None
        self.board.get_board()
        
        self.board.make_move(best_move)
        print()
        self.board.get_board()
        self.board.get_last_five()

        self.move_history.append(best_move)
        print("AI played move")
        self.check_game_state()
        
        return best_move
    def check_game_state(self):
        color = "w" if self.board.white_to_move else "b"
        legal_moves = self.rules.generate_legal_moves(color)
        if not legal_moves:
            if self.rules.in_check(color):
                self.game_over = True
                self.winner = "b" if color == "w" else "w"
                self.game_over_reason = "checkmate"
            else:
                self.game_over = True
                self.winner = None
                self.game_over_reason = "stalemate"
                
        elif self.board.halfmoves >= 50:
            self.game_over = True
            self.winner = None
            self.game_over_reason = "fifty-move rule"
        
        elif self.is_insufficient_material():
            self.game_over = True
            self.winner = None
            self.game_over_reason = "insufficient material"
    def get_game_status(self):
        if self.game_over:
            if self.winner:
                winner_name = "White" if self.winner == "w" else "Black"
                return f"Game over: {winner_name} wins by {self.game_over_reason}."
            else:
                return f"Game over: Draw by {self.game_over_reason}."
        curr_player = "White" if self.board.white_to_move else "Black"
        color = "w" if self.board.white_to_move else "b"
        if self.rules.in_check(color):
            return f"CHECK -- {curr_player} to move."
        return f"{curr_player} to move."
    def is_insufficient_material(self):
        white_pieces = []
        black_pieces = []
        white_bishops = []
        black_bishops = []
        for r in range(8):
            for c in range(8):
                piece = self.board.get_piece(r,c)
                if piece != "--" and piece[1] != 'K':
                    if piece[0] == 'w':
                        white_pieces.append(piece[1])
                        if piece[1] == 'B':
                            white_bishops.append((r + c) % 2)
                    else:
                        black_pieces.append(piece[1])
                        if piece[1] == 'B':
                            black_bishops.append((r + c) % 2)
        total_pieces = len(white_pieces) + len(black_pieces)
        if total_pieces == 0:
            return True
        if total_pieces == 1:
            if white_pieces == ['N'] or black_pieces == ['N']:
                return True
            if white_pieces == ['B'] or black_pieces == ['B']:
                return True
        if total_pieces == 2:
            if white_pieces == ['B'] and black_pieces == ['B']:
                if white_bishops[0] == black_bishops[0]:
                    return True
        return False
                
    def reset_game(self):
        self.board = Board()
        self.rules = Rules(self.board)
        self.evaluator = Evaluator()
        self.search = Search(self.board, self.rules, self.evaluator)
        
        self.game_over = False
        self.winner = None
        self.game_over_reason = None
        
        self.move_history = []
    def get_current_player(self):
        return "w" if self.board.white_to_move else "b"
    def get_board_fen(self):
        return self.board.to_fen()
    def loard_position(self, fen):
        self.board.load_fen(fen)
        self.rules = Rules(self.board)
        self.evaluator = Evaluator()
        self.search = Search(self.board, self.rules, self.evaluator)
        
        self.game_over = False
        self.winner = None
        self.game_over_reason = None
        
        self.move_history = []
        
        self.check_game_state()