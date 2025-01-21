class Piece:
    def __init__(self, x, y, colour, image):
        self.coords = (x, y)
        self.colour = colour

        self.image = image # Store a reference to each image to prevent garbage collection
        self.piece_image = None # Store the tkinter canvas image

        self.has_moved = False

    def position_taken(self, position, pieces):
        """Check if a given position is occupied by any piece"""
        for piece in pieces:
            if position == piece.coords:
                return piece

class Pawn(Piece):
    def get_moves(self, pieces):
        """Generate legal moves for a pawn"""
        x, y = self.coords
        moves = []
        direction = -1 if self.colour == "WHITE" else 1 # White moves up, black moves down
        
        # Single step forward
        if 0 <= y + direction < 8:
            if not self.position_taken((x, y + direction), pieces):
                moves.append((x, y + direction))

        # Double step forward
        if not self.has_moved and 0 <= y + 2 * direction < 8:
            if not self.position_taken((x, y + direction), pieces) and not self.position_taken((x, y + 2 * direction), pieces):
                moves.append((x, y + 2 * direction))

        # Capture diagonally left
        if 0 <= x - 1 < 8 and 0 <= y + direction < 8:
            target_pos = (x - 1, y + direction)
            blocking_piece = self.position_taken(target_pos, pieces)

            if blocking_piece and blocking_piece.colour != self.colour:
                moves.append(target_pos)

        # Capture diagonally right
        if 0 <= x + 1 < 8 and 0 <= y + direction < 8:
            target_pos = (x + 1, y + direction)
            blocking_piece = self.position_taken(target_pos, pieces)
            
            if blocking_piece and blocking_piece.colour != self.colour:
                moves.append(target_pos)

        # En Passant Capture
        """for piece in pieces:
            if isinstance(piece, Pawn) and piece.colour != self.colour:
                # The enemy pawn must have just moved two steps
                adjacent = piece.coords[1] - self.coords[1] == 0
                diagonal = abs(piece.coords[0] - self.coords[0]) == 1
                    
                if adjacent and diagonal and not piece.has_moved:
                    moves.append((piece.coords[0], piece.coords[1] + direction))"""

        # Promotion
        # For the sake of simplicity, all promotions will be to queens

        return moves
    
    def get_value(self):
        return 1

class Knight(Piece):
    def get_moves(self, pieces):
        """Generate legal moves for a knight given"""
        x, y = self.coords
        moves = []
        
        directions = [(-2, -1), (-1, -2), (1, -2), (2, -1), (2, 1), (1, 2), (-1, 2), (-2, 1)]
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 8 and 0 <= ny < 8:
                blocking_piece = self.position_taken((nx, ny), pieces)
                if blocking_piece:
                    if blocking_piece.colour != self.colour:
                        moves.append((nx, ny))
                    continue
                moves.append((nx, ny))
        
        return moves
    
    def get_value(self):
        return 3

class Bishop(Piece):
    def get_moves(self, pieces):
        """Generate legal moves for a bishop"""
        x, y = self.coords
        moves = []
        directions = [(-1, -1), (1, -1), (-1, 1), (1, 1)]
    
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            while 0 <= nx < 8 and 0 <= ny < 8:
                blocking_piece = self.position_taken((nx, ny), pieces)
                if blocking_piece:
                    if blocking_piece.colour != self.colour:
                        moves.append((nx, ny))
                    break
                moves.append((nx, ny))

                nx += dx
                ny += dy
    
        return moves
    
    def get_value(self):
        return 3

class Rook(Piece):
    def get_moves(self, pieces):
        """Generate legal moves for a rook"""
        x, y = self.coords
        moves = []
    
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            while 0 <= nx < 8 and 0 <= ny < 8:
                blocking_piece = self.position_taken((nx, ny), pieces)
                if blocking_piece:
                    if blocking_piece.colour != self.colour:
                        moves.append((nx, ny))
                    break
                moves.append((nx, ny))

                nx += dx
                ny += dy
    
        return moves
    
    def get_value(self):
        return 5

class Queen(Piece):
    def get_moves(self, pieces):
        """Generate legal moves for the queen"""

        # The Queen's moves are just a combination of the Bishop and Rook
        rook = Rook(self.coords[0], self.coords[1], self.colour, self.image)
        bishop = Bishop(self.coords[0], self.coords[1], self.colour, self.image)
        
        # To reuse code we can get the moves of both pieces and combine them
        return rook.get_moves(pieces) + bishop.get_moves(pieces)
    
    def get_value(self):
        return 9

class King(Piece):
    def get_moves(self, pieces):
        """Generate legal moves for the king"""
        x, y = self.coords
        moves = []
        
        directions = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 8 and 0 <= ny < 8:
                blocking_piece = self.position_taken((nx, ny), pieces)
                if blocking_piece:
                    if blocking_piece.colour != self.colour:
                        moves.append((nx, ny))
                    continue
                moves.append((nx, ny))
        
        # Castling
        
        return moves
    
    def get_value(self):
        return 100 # The king is invaluable