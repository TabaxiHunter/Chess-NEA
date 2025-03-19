from tables import piece_square_tables

class Engine:
    def __init__(self, depth):
        self.MAX_DEPTH = depth
        self.ALPHA = float("-inf")
        self.BETA = float("inf")

    def get_square_value(self, piece):
        """Retrieve the piece-square value for a given piece"""
        table = piece_square_tables[piece.piece_type]
        x, y = piece.coords

        if piece.colour == 1:
            return table[x][y]
        else:
            return table[7-x][y] # Mirror for Black

    def evaluate_board(self, board, colour):
        if board.is_checkmate(colour):
            return float("-inf")
        
        if board.is_checkmate(-colour):
            return float("inf")

        if board.is_stalemate(colour) or board.is_stalemate(-colour):
            return 0

        score = 0

        for piece in board.pieces:
            square_value = self.get_square_value(piece)

            if piece.colour == 1:
                score = score + piece.get_value() + square_value
            else:
                score = score - piece.get_value() + square_value

        return score * colour

    def negamax(self, board, depth, alpha, beta, colour):
        """Negamax algorithm with alpha-beta pruning"""
        if depth == 0 or board.is_checkmate(colour):
            return self.evaluate_board(board, colour), None

        best_score = float("-inf")
        best_move = None

        sorted_moves = self.sorted_moves(board, colour) # Generate legal moves for the current player
        
        for move in sorted_moves:
            start, end = move
            board.make_move(start, end)

            score, _ = self.negamax(board, depth - 1, -beta, -alpha, -colour)
            score = -score

            board.unmake_move() 

            if score > best_score:
                best_score = score
                best_move = move

            alpha = max(alpha, score)

            # Alpha-beta pruning
            if alpha >= beta:
                break
        
        return best_score, best_move

    def sorted_moves(self, board, colour):
        """Orders moves so captures are considered before other moves"""
        moves = []

        captures = []
        checks = []

        for piece in board.pieces:
            if piece.colour != colour:
                continue # Ignore other player's pieces

            for end in piece.get_legal_moves(board):
                move = (piece.coords, end)

                if board.causes_check(move, -colour):
                    checks.append(move)
                elif board.get_piece_at(end[0], end[1]):
                    captures.append(move)
                else:
                    moves.append(move)

        return checks + captures + moves

    def generate_move(self, board, colour):
        """Finds the best move for the AI"""
        _, move = self.negamax(board, self.MAX_DEPTH, self.ALPHA, self.BETA, colour)

        return move