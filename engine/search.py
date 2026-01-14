from engine.rules import Rules
from engine.move import Move
from engine.eval import Evaluator

class Search:
    def __init__(self, board, rules, evaluator=None):
        self.board = board
        self.rules = rules
        self.nodes_searched = 0
        self.positions_evalled = 0

        self.evaluator = evaluator if evaluator else Evaluator()

        self.piece_values = {
            "P": 1,
            "N": 3,
            "B": 3,
            "R": 5,
            "Q": 9,
            "K": 20000
        }
    def find_best_move(self, depth):
        self.nodes_searched = 0
        self.positions_evalled = 0
        
        color = "w" if self.board.white_to_move else "b"
        legal_moves = self.rules.generate_legal_moves(color)
        
        if not legal_moves:
            return None
        
        best_move = None
        best_score = float('-inf')
        a = float('-inf')
        b = float('inf')
        for move in self.order_moves(legal_moves):
            self.board.make_move(move)
            score = -self.alpha_beta(depth-1, a, b, False)
            self.board.undo_move()
            
            if score > best_score:
                best_score = score
                best_move = move
            a = max(a, score)
        print(f"Searched {self.nodes_searched} nodes, evaluated {self.positions_evalled} positions")
        print(f"Best move: {best_move} with score: {best_score}")
        
        return best_move
    def alpha_beta(self, depth, a, b, maximizing):
        self.nodes_searched += 1
        
        if depth == 0:
            self.positions_evalled += 1
            return self.evaluator.evaluate(self.board)
        color = "w" if self.board.white_to_move else "b"
        legal_moves = self.rules.generate_legal_moves(color)
        
        if not legal_moves:
            if self.rules.in_check(color):
                return -20000 + depth
            else:
                return 0
            
        if maximizing:
            max_score = float('-inf')
            for move in self.order_moves(legal_moves):
                self.board.make_move(move)
                score = self.alpha_beta(depth - 1, b, a, False)
                
                self.board.undo_move()
                
                max_score = max(max_score, score)
                a = max(a, score)
                if b <= a:
                    break
            return max_score
        else:
            min_score = float('inf')
            for move in self.order_moves(legal_moves):
                self.board.make_move(move)
                score = self.alpha_beta(depth - 1, a, b, True)
                
                self.board.undo_move()
                
                min_score = min(min_score, score)
                b = min(b, score)
                if b <= a:
                    break
            return min_score
    def order_moves(self, moves):
        def move_priority(move):
            r = Rules(self.board)
            score = 0

            # Additional priority for forks and pins
            if r.is_square_forking(self.board, move):
                score += 3000
                counter += 1
            if r.is_square_pinning(self.board, move):
                score += 3000
                counter += 1
            if move.is_capture():
                
                target_value = self.evaluator.piece_values.get(move.piece_captured[1], 0)
                attacker_value = self.evaluator.piece_values.get(move.moved_piece[1], 0)
                score += 10000 + target_value - attacker_value
            if move.is_promotion():
                promotion_value = self.evaluator.piece_values.get(move.promotion, 0)
                score += 5000 + promotion_value

            return score
        return sorted(moves, key=move_priority, reverse=True)
    