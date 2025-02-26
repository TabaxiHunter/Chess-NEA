from pieces import Pawn, Knight, Bishop, Rook, Queen, King
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

    def in_check(self, colour):
        """Returns True if the king of the given colour is in check."""
        king = None
        for piece in self.pieces:
            if isinstance(piece, King) and piece.colour == colour:
                king = piece
                break

        if not king:
            return False # Shouldn't happen, but just in case

        # Check if any opponent's piece can attack the king
        for piece in self.pieces:
            if piece.colour != colour:
                # Avoid recursion by not asking the King for its own moves
                if isinstance(piece, King):
                    # Manually check if the opponent king is adjacent (Kings cannot attack each other directly)
                    x, y = king.coords
                    px, py = piece.coords
                    if abs(x - px) <= 1 and abs(y - py) <= 1:
                        return True
                    continue  # Skip further processing for opponent's King

                if king.coords in piece.get_moves(self):
                    return True # King is in check

        return False
    
    def is_checkmate(self, colour):
        """Returns True if the given colour is in checkmate."""
        if not self.in_check(colour):
            return False  # Not checkmate if king is not in check

        # Check if any move can get the player out of check
        for piece in self.pieces:
            if piece.colour == colour:
                for move in piece.get_moves(self):
                    # Simulate move
                    original_position = piece.coords
                    captured_piece = self.get_piece_at(move[0], move[1])

                    piece.move(move[0], move[1])
                    if captured_piece:
                        self.pieces.remove(captured_piece)

                    in_check = self.in_check(colour)

                    # Undo the move
                    piece.move(original_position[0], original_position[1])
                    if captured_piece:
                        self.pieces.append(captured_piece)

                    if not in_check:
                        return False  # The player can escape check

        return True  # No escape moves → Checkmate
    
    def is_stalemate(self, colour):
        """Returns True if the game is in stalemate (no legal moves but not in check)."""
        if self.in_check(colour):
            return False # It's check, not stalemate

        # Check if there are any legal moves left
        for piece in self.pieces:
            if piece.colour == colour:
                for move in piece.get_moves(self):
                    # Simulate move
                    original_position = piece.coords
                    captured_piece = self.get_piece_at(move[0], move[1])

                    piece.move(move[0], move[1])
                    if captured_piece:
                        self.pieces.remove(captured_piece)

                    in_check = self.in_check(colour)

                    # Undo the move
                    piece.move(original_position[0], original_position[1])
                    if captured_piece:
                        self.pieces.append(captured_piece)

                    if not in_check:
                        return False  # The player has at least one move

        return True # No legal moves left → Stalemate

    def make_move(self, start, end):
        """Updates the board with the move and stores it in history"""
        piece = self.get_piece_at(start[0], start[1])
        is_legal = end in piece.get_moves(self)

        if piece and is_legal:
            captured_piece = self.get_piece_at(end[0], end[1])

            if captured_piece:
                self.pieces.remove(captured_piece)

            self.history.append((start, end, piece, captured_piece, None))
            piece.move(end[0], end[1])

            # Attempt to promote the piece if it's a pawn
            if isinstance(piece, Pawn):
                self.promote(piece, start, end, captured_piece)

            # Handle castling
            if isinstance(piece, King) and abs(start[0] - end[0]) == 2:
                self.perform_castling(piece, start, end)

    def perform_castling(self, king, start, end):
        """Moves the rook accordingly when castling."""
        y = start[1]

        if end[0] == 6:  # Kingside
            rook = self.get_piece_at(7, y)
            if rook:
                rook.move(5, y)

        elif end[0] == 2:  # Queenside
            rook = self.get_piece_at(0, y)
            if rook:
                rook.move(3, y)

    def undo_castling(self, king, start, end):
        """Moves the rook back to its original position when undoing castling."""
        y = start[1]

        if end[0] == 6:  # Kingside castling
            rook = self.get_piece_at(5, y)
            if rook:
                rook.move(7, y)  # Move rook back to original position

        elif end[0] == 2:  # Queenside castling
            rook = self.get_piece_at(3, y)
            if rook:
                rook.move(0, y)  # Move rook back to original position

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

        # Undo castling
        if isinstance(piece, King) and abs(start[0] - end[0]) == 2:
            self.undo_castling(piece, start, end)

        # Revert the piece position
        piece.move(start[0], start[1])

        # Restore captured piece
        if captured_piece:
            self.pieces.append(captured_piece)
            captured_piece.move(end[0], end[1])

        
