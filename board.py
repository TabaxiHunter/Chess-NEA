from pieces import *
from utils import fen_to_coords

class Board:
    def __init__(self):
        self.pieces = []
        self.history = [] # Stack to store move history

        # FEN notation for the starting position of chess
        self.setup_pieces("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")
    
    def create_piece(self, piece_character, coords):
        piece_types = {
            "r": Rook,
            "n": Knight,
            "b": Bishop,
            "q": Queen,
            "k": King,
            "p": Pawn
        }

        colour = 1 if piece_character.isupper() else -1
        file, rank = coords

        piece_type = piece_character.lower()
        piece_class = piece_types[piece_type]

        piece = piece_class(file, rank, colour, piece_type)
        self.pieces.append(piece)

        return piece

    def setup_pieces(self, fen):
        """Set up the pieces in their starting positions"""
        piece_coords = fen_to_coords(fen)

        for piece_character in piece_coords:
            for position in piece_coords[piece_character]:
                self.create_piece(piece_character, position)

    def get_piece_at(self, x, y):
        """Returns the piece at a given (x, y) coordinate"""
        for piece in self.pieces:
            if piece.coords[0] == x and piece.coords[1] == y:
                return piece
            
        return None
    
    def promote(self, piece, start, end, captured_piece):
        # Promote Pawn to Queen automatically if possible
        # A possible improvement could be to let the player pick which piece they want to promote to
        white_promote = piece.colour == 1 and piece.coords[1] == 0
        black_promote = piece.colour == -1 and piece.coords[1] == 7

        if white_promote or black_promote:
            # Remove the Pawn and replace with a Queen at the same position
            self.pieces.remove(piece)
            piece_type = "Q" if piece.colour == 1 else "q"
            promoted_piece = self.create_piece(piece_type, piece.coords)

            # Update the move history to track promotion
            self.history[-1] = (start, end, piece, captured_piece, promoted_piece)

    def make_move(self, start, end):
        """Updates the board with the move and stores it in history"""
        piece = self.get_piece_at(start[0], start[1])
        is_legal = end in piece.get_moves(self.pieces)

        if piece and is_legal:
            captured_piece = self.get_piece_at(end[0], end[1])

            if captured_piece:
                self.pieces.remove(captured_piece)

            self.history.append((start, end, piece, captured_piece, None))
            piece.move(end[0], end[1])

        # Attempt to promote the piece if it's a pawn
        if isinstance(piece, Pawn):
            self.promote(piece, start, end, captured_piece)

    def unmake_move(self):
        """Reverts the last move"""
        if not self.history:
            return
        
        start, end, piece, captured_piece, promoted_piece = self.history.pop()

        # If the move was a promotion, remove the queen and restore the pawn
        if promoted_piece:
            old_pawn = self.get_piece_at(end[0], end[1])
            if old_pawn:
                self.pieces.remove(old_pawn)
            self.pieces.append(piece)

        piece.move(start[0], start[1]) # Revert the piece position

        # Restore captured piece
        if captured_piece:
            self.pieces.append(captured_piece)
            captured_piece.move(end[0], end[1])
