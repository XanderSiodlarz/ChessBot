class Move:
    def __init__(self, start_pos, end_pos, moved_piece, piece_captured="--", promotion=None):
        self.start = start_pos
        self.end = end_pos
        self.moved_piece = moved_piece
        self.piece_captured = piece_captured
        self.promotion = promotion
    def is_capture(self):
        return self.piece_captured != "--"
    
    def is_promotion(self):
        return self.promotion is not None

    def is_castling(self, piece:str) -> bool:
        return (
            piece[1] == "K" and
            abs(self.start[1] - self.end[1]) == 2
        )
    
    def __str__(self):
        return f"{self.start} to {self.end}, captured: {self.piece_captured}, promotion: {self.promotion}"