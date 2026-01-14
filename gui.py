import pygame
import sys
from engine.game import Game

class ChessGUI:
    """
    Pygame-based graphical interface for chess.
    Handles rendering, mouse input, and user interaction.
    """
    
    def __init__(self, width=800, height=800):
        """
        Initialize the chess GUI.
        
        Args:
            width: Window width in pixels
            height: Window height in pixels
        """
        pygame.init()
        
        # Window setup
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Chess Game")
        
        # Board dimensions
        self.square_size = width // 8
        
        # Colors
        self.light_square = (240, 217, 181)
        self.dark_square = (181, 136, 99)
        self.highlight_color = (186, 202, 68, 100)  # Semi-transparent yellow
        self.move_indicator = (130, 151, 105)
        self.check_color = (255, 0, 0, 100)
        
        # Game state
        self.game = Game(player_color="w", ai_depth=4)
        self.selected_square = None
        self.legal_moves_for_selected = []
        
        # Font for text
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Simple piece representation (Unicode characters)
        self.piece_symbols = {
            'wP': 'P', 'wN': 'N', 'wB': 'B', 'wR': 'R', 'wQ': 'Q', 'wK': 'K',
            'bP': 'p', 'bN': 'n', 'bB': 'b', 'bR': 'r', 'bQ': 'q', 'bK': 'k'
        }
        
        # Piece font (larger for pieces)
        self.piece_font = pygame.font.Font(None, 80)
        
        # Clock
        self.clock = pygame.time.Clock()
        self.fps = 60
    
    def get_square_from_mouse(self, pos):
        """
        Convert mouse position to board coordinates.
        
        Args:
            pos: tuple (x, y) - mouse position
        
        Returns:
            tuple (row, col) or None if outside board
        """
        x, y = pos
        col = x // self.square_size
        row = y // self.square_size
        
        if 0 <= row < 8 and 0 <= col < 8:
            return (row, col)
        return None
    
    def draw_board(self):
        """Draw the chess board (alternating squares)"""
        for row in range(8):
            for col in range(8):
                # Determine square color
                color = self.light_square if (row + col) % 2 == 0 else self.dark_square
                
                # Draw square
                rect = pygame.Rect(
                    col * self.square_size,
                    row * self.square_size,
                    self.square_size,
                    self.square_size
                )
                pygame.draw.rect(self.screen, color, rect)
    
    def draw_coordinates(self):
        """Draw rank and file labels (a-h, 1-8)"""
        # Files (a-h)
        for col in range(8):
            label = chr(ord('a') + col)
            text = self.small_font.render(label, True, (100, 100, 100))
            x = col * self.square_size + self.square_size - 20
            y = self.height - 20
            self.screen.blit(text, (x, y))
        
        # Ranks (1-8)
        for row in range(8):
            label = str(8 - row)
            text = self.small_font.render(label, True, (100, 100, 100))
            x = 5
            y = row * self.square_size + 5
            self.screen.blit(text, (x, y))
    
    def draw_pieces(self):
        """Draw all pieces on the board"""
        for row in range(8):
            for col in range(8):
                piece = self.game.board.get_piece(row, col)
                
                if piece != "--":
                    symbol = self.piece_symbols.get(piece, "?")
                    piece_text = self.piece_font.render(symbol, True, (0, 0, 0))
                    
                    # Center the piece in the square
                    text_rect = piece_text.get_rect()
                    text_rect.center = (
                        col * self.square_size + self.square_size // 2,
                        row * self.square_size + self.square_size // 2
                    )
                    
                    self.screen.blit(piece_text, text_rect)
    
    def highlight_selected_square(self):
        """Highlight the currently selected square"""
        if self.selected_square:
            row, col = self.selected_square
            s = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
            s.fill(self.highlight_color)
            self.screen.blit(s, (col * self.square_size, row * self.square_size))
    
    def highlight_legal_moves(self):
        """Show dots on squares where selected piece can move"""
        for move in self.legal_moves_for_selected:
            row, col = move.end
            
            # Draw a circle in the center of legal move squares
            center_x = col * self.square_size + self.square_size // 2
            center_y = row * self.square_size + self.square_size // 2
            
            # Different indicator for captures
            if move.is_capture():
                # Draw ring for captures
                pygame.draw.circle(self.screen, self.move_indicator, (center_x, center_y), 
                                 self.square_size // 3, 5)
            else:
                # Draw filled circle for regular moves
                pygame.draw.circle(self.screen, self.move_indicator, (center_x, center_y), 
                                 self.square_size // 6)
    
    def highlight_check(self):
        """Highlight the king if in check"""
        color = "w" if self.game.board.white_to_move else "b"
        if self.game.rules.in_check(color):
            king_pos = self.game.board.find_king(color)
            if king_pos:
                row, col = king_pos
                s = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
                s.fill(self.check_color)
                self.screen.blit(s, (col * self.square_size, row * self.square_size))
    
    def draw_status(self):
        """Draw game status text at the bottom"""
        status_text = self.game.get_game_status()
        text = self.font.render(status_text, True, (255, 255, 255))
        
        # Black background for text
        text_rect = text.get_rect()
        text_rect.center = (self.width // 2, self.height - 50)
        bg_rect = text_rect.inflate(20, 10)
        pygame.draw.rect(self.screen, (0, 0, 0), bg_rect)
        
        self.screen.blit(text, text_rect)
    
    def handle_click(self, pos):
        """
        Handle mouse click on the board.
        
        Args:
            pos: tuple (x, y) - mouse position
        """
        if self.game.game_over:
            return
        
        if not self.game.is_player_turn():
            return
        
        square = self.get_square_from_mouse(pos)
        if not square:
            return
        
        row, col = square
        
        # If no piece selected, select piece
        if self.selected_square is None:
            piece = self.game.board.get_piece(row, col)
            
            # Can only select your own pieces
            if piece != "--" and piece[0] == self.game.player_color:
                self.selected_square = (row, col)
                
                # Get legal moves for this piece
                all_legal_moves = self.game.get_legal_moves()
                self.legal_moves_for_selected = [
                    move for move in all_legal_moves 
                    if move.start == self.selected_square
                ]
        
        # If piece already selected, try to move it
        else:
            # Check if clicking on a legal move
            target_move = None
            for move in self.legal_moves_for_selected:
                if move.end == (row, col):
                    target_move = move
                    break
            
            if target_move:
                # Check for pawn promotion
                promotion = None
                piece = self.game.board.get_piece(self.selected_square[0], self.selected_square[1])
                if piece[1] == 'P' and (row == 0 or row == 7):
                    # Simple auto-promotion to Queen
                    # In a full GUI, you'd show a dialog to choose
                    promotion = 'Q'
                
                # Make the move
                success = self.game.make_player_move(
                    self.selected_square, 
                    (row, col),
                    promotion
                )
                
                if success:
                    print(f"Player moved: {self.selected_square} to {(row, col)}")
            
            # Deselect
            self.selected_square = None
            self.legal_moves_for_selected = []
    
    def handle_ai_move(self):
        """Let the AI make its move"""
        if self.game.is_ai_turn() and not self.game.game_over:
            # Add a small delay so player can see the position
            pygame.time.wait(500)
            self.game.make_ai_move()
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        self.handle_click(event.pos)
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        # Reset game
                        self.game.reset_game()
                        self.selected_square = None
                        self.legal_moves_for_selected = []
                    
                    elif event.key == pygame.K_u:
                        # Undo last move
                        self.game.undo_last_move()
                        self.selected_square = None
                        self.legal_moves_for_selected = []
            
            # AI move (if it's AI's turn)
            self.handle_ai_move()
            
            # Drawing
            self.draw_board()
            self.highlight_check()
            self.highlight_selected_square()
            self.highlight_legal_moves()
            self.draw_pieces()
            self.draw_coordinates()
            self.draw_status()
            
            # Update display
            pygame.display.flip()
            self.clock.tick(self.fps)
        
        pygame.quit()
        sys.exit()


def main():
    """Entry point for the chess game"""
    gui = ChessGUI()
    gui.run()


if __name__ == "__main__":
    main()