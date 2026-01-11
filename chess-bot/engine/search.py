from engine.rules import Rules
from engine.move import Move

class Search:
    def __init__(self, board, rules):
        self.board = board
        self.rules = rules
        self.nodes_searched = 0
        self.positions_evalled = 0
        
        self.piece_values = {
            "P": 1,
            "N": 3,
            "B": 3,
            "R": 5,
            "Q": 9,
            "K": 20000
        }