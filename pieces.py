class Piece:
    def __init__(self, x, y, colour, piece_type):
        self.coords = (x, y)
        self.colour = colour # 1 for white, -1 for black

        self.piece_type = piece_type # Single character e.g. "p" for Pawn
        self.piece_image = None

    def move(self, new_x, new_y):
        """Move the piece to a new location"""
        self.coords = (new_x, new_y)
            
    def has_moved(self, board):
        """Returns True if the piece has moved at least once"""
        history = board.history

        for move in history:
            if self == move[2]:
                return True

        return False
    
    def get_legal_moves(self, board):
        """Returns only moves that do not leave the king in check"""
        legal_moves = []
        for end in self.get_moves(board):
            if not board.causes_check((self.coords, end), self.colour):
                legal_moves.append(end)

        return legal_moves

class Pawn(Piece):
    def get_moves(self, board):
        """Generate legal moves for a pawn"""
        x, y = self.coords
        direction = -self.colour # White moves up, black moves down

        moves = []
        
        # Single step forward
        if 0 <= y + direction < 8:
            if not board.get_piece_at(x, y + direction):
                moves.append((x, y + direction))

        # Double step forward
        if not self.has_moved(board) and 0 <= y + 2 * direction < 8:
            if not board.get_piece_at(x, y + direction) and not board.get_piece_at(x, y + 2 * direction):
                moves.append((x, y + 2 * direction))

        # Capture diagonally left
        if 0 <= x - 1 < 8 and 0 <= y + direction < 8:
            target_pos = (x - 1, y + direction)
            blocking_piece = board.get_piece_at(x-1, y+direction)

            if blocking_piece and blocking_piece.colour != self.colour:
                moves.append(target_pos)

        # Capture diagonally right
        if 0 <= x + 1 < 8 and 0 <= y + direction < 8:
            target_pos = (x + 1, y + direction)
            blocking_piece = board.get_piece_at(x+1, y+direction)
            
            if blocking_piece and blocking_piece.colour != self.colour:
                moves.append(target_pos)

        return moves
    
    def get_value(self):
        return 100

class Knight(Piece):
    def get_moves(self, board):
        """Generate legal moves for a knight given"""
        x, y = self.coords
        moves = []
        
        directions = [(-2, -1), (-1, -2), (1, -2), (2, -1), (2, 1), (1, 2), (-1, 2), (-2, 1)]
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 8 and 0 <= ny < 8:
                blocking_piece = board.get_piece_at(nx, ny)
                if blocking_piece:
                    if blocking_piece.colour != self.colour:
                        moves.append((nx, ny))
                    continue
                moves.append((nx, ny))
        
        return moves
    
    def get_value(self):
        return 300

class Bishop(Piece):
    def get_moves(self, board):
        """Generate legal moves for a bishop"""
        x, y = self.coords
        moves = []
        directions = [(-1, -1), (1, -1), (-1, 1), (1, 1)]
    
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            while 0 <= nx < 8 and 0 <= ny < 8:
                blocking_piece = board.get_piece_at(nx, ny)
                if blocking_piece:
                    if blocking_piece.colour != self.colour:
                        moves.append((nx, ny))
                    break
                moves.append((nx, ny))

                nx += dx
                ny += dy
    
        return moves
    
    def get_value(self):
        return 300

class Rook(Piece):
    def get_moves(self, board):
        """Generate legal moves for a rook"""
        x, y = self.coords
        moves = []
    
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            while 0 <= nx < 8 and 0 <= ny < 8:
                blocking_piece = board.get_piece_at(nx, ny)
                if blocking_piece:
                    if blocking_piece.colour != self.colour:
                        moves.append((nx, ny))
                    break
                moves.append((nx, ny))

                nx += dx
                ny += dy
    
        return moves
    
    def get_value(self):
        return 500

class Queen(Piece):
    def get_moves(self, board):
        """Generate legal moves for the queen"""

        # The Queen's moves are just a combination of the Bishop and Rook
        rook = Rook(self.coords[0], self.coords[1], self.colour, self.piece_type)
        bishop = Bishop(self.coords[0], self.coords[1], self.colour, self.piece_type)
        
        # To reuse code we can get the moves of both pieces and combine them
        return rook.get_moves(board) + bishop.get_moves(board)
    
    def get_value(self):
        return 900

class King(Piece):
    def get_moves(self, board):
        """Generate legal moves for the king"""
        x, y = self.coords
        moves = []
        
        directions = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 8 and 0 <= ny < 8:
                blocking_piece = board.get_piece_at(nx, ny)
                if blocking_piece:
                    if blocking_piece.colour != self.colour :
                        moves.append((nx, ny))
                    continue
                moves.append((nx, ny))
        
        # Castling
        if not self.has_moved(board) and not board.in_check(self.colour):
            moves += self.get_castling_moves(board)
        
        return moves
    
    def get_castling_moves(self, board):
        """Checks and returns valid castling moves"""
        x, y = self.coords
        castling_moves = []

        # Check Rook positions (Kingside and Queenside)
        rooks = [(7, y), (0, y)]

        for rook_x, rook_y in rooks:
            rook = board.get_piece_at(rook_x, rook_y)
            if rook and rook.piece_type == "r" and not rook.has_moved(board):
                if self.clear_path((x, y), (rook_x, rook_y), board):
                    if rook_x == 7: # Kingside
                        castling_moves.append((x + 2, y))
                    else: # Queenside
                        castling_moves.append((x - 2, y))

        return castling_moves
    
    def clear_path(self, start, end, board):
        """Returns True if there are no pieces between start and end"""
        x1, y1 = start
        x2, y2 = end
        
        step = 1 if x1 < x2 else -1

        for x in range(x1 + step, x2, step):
            if board.get_piece_at(x, y1):
                return False

        return True
    
    def get_value(self):
        return 10000000 # The king is invaluable