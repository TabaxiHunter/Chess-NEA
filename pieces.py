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
                return True
        return False

class Pawn(Piece):
    def get_moves(self, pieces):
        """Generate legal moves for a pawn given its position"""
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
        
        return moves
    
    def get_value(self):
        return 1

class Knight(Piece):
    def get_moves(self, pieces):
        """Generate legal moves for a knight given its position"""
        x, y = self.coords
        moves = []
        
        directions = [(-2, -1), (-1, -2), (1, -2), (2, -1), (2, 1), (1, 2), (-1, 2), (-2, 1)]
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 8 and 0 <= ny < 8: # Ensure within board limits
                # Check if the position is occupied
                occupied_piece = None
                for piece in pieces:
                    if piece.coords == (nx, ny):
                        occupied_piece = piece
                        break
                
                # The knight can move if the square is empty or occupied by an opponent
                if occupied_piece is None or occupied_piece.colour != self.colour:
                    moves.append((nx, ny))
        
        return moves
    
    def get_value(self):
        return 3

class Bishop(Piece):
    def get_moves(self, pieces):
        """Generate legal moves for a bishop given its position"""
        x, y = self.coords
        moves = []
        directions = [(-1, -1), (1, -1), (-1, 1), (1, 1)]
    
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            while 0 <= nx < 8 and 0 <= ny < 8:
                # If the position is occupied by an opponent's piece, add the move and stop
                if self.position_taken((nx, ny), pieces):
                    if (nx, ny) != (x, y):  # If occupied by a piece, stop at the first piece (enemy or friendly)
                        break
                moves.append((nx, ny))  # Add the valid move
                if (nx, ny) != (x, y) and self.position_taken((nx, ny), pieces):
                    break  # Stop if the position is occupied
                nx += dx
                ny += dy
    
        return moves
    
    def get_value(self):
        return 3

class Rook(Piece):
    def get_moves(self, pieces):
        x, y = self.coords
        moves = []
    
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            while 0 <= nx < 8 and 0 <= ny < 8:
                if self.position_taken((nx, ny), pieces): # Check if the position is occupied
                    if (nx, ny) != (x, y): # If occupied, stop at the first piece (enemy or friendly)
                        break
                moves.append((nx, ny))  # Add the valid move
                if (nx, ny) != (x, y) and self.position_taken((nx, ny), pieces):
                    break # Stop at the first occupied position
                nx += dx
                ny += dy
    
        return moves
    
    def get_value(self):
        return 5

class Queen(Piece):
    def get_moves(self, pieces):
        rook = Rook(self.coords[0], self.coords[1], self.colour, self.image) # Create a rook at the queen's position
        bishop = Bishop(self.coords[0], self.coords[1], self.colour, self.image) # Create a bishop at the queen's position
        
        # Combine the moves from both rook and bishop
        return rook.get_moves(pieces) + bishop.get_moves(pieces)
    
    def get_value(self):
        return 9

class King(Piece):
    def get_moves(self, pieces):
        x, y = self.coords
        moves = []
        
        directions = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 8 and 0 <= ny < 8:
                # Check if the position is occupied
                occupied_piece = None
                for piece in pieces:
                    if piece.coords == (nx, ny):
                        occupied_piece = piece
                        break

                # The king can move if the square is empty or occupied by an opponent
                if occupied_piece is None or occupied_piece.colour != self.colour:
                    moves.append((nx, ny))
        
        return moves
    
    def get_value(self):
        return 100 # The king is invaluable