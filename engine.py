import copy

class Engine:
    def __init__(self, depth):
        self.MAX_DEPTH = depth
        self.ALPHA = float("-inf")
        self.BETA = float("inf")

    def evaluate_board(self, pieces):
        score = 0

        for piece in pieces:
            if piece.colour == 1:
                score = score + piece.get_value()
            else:
                score = score - piece.get_value()

        return score

    def negamax(self, board, depth, alpha, beta, colour):
        """Negamax algorithm with alpha-beta pruning"""
        if depth == 0:
            return colour * self.evaluate_board(board.pieces)

        best_score = float("-inf")
        best_move = None

        # Generate moves for all pieces of the current colour
        legal_moves = self.get_all_moves(board, colour)

        for move in legal_moves:
            _, start, end = move

            board.make_move(start, end)

            # Recursively call Negamax with the opposite color
            score = -self.negamax(board, depth - 1, -beta, -alpha, -colour)
            board.unmake_move()

            # Update the best move and score
            if score > best_score:
                best_score = score
                best_move = move

            alpha = max(alpha, score)

            if alpha >= beta:
                break # Alpha-beta pruning

        if depth == self.MAX_DEPTH:
            return best_move # Return best move at root level
        
        return best_score

    def get_all_moves(self, board, colour):
        """Generates all legal moves for the given colour using each piece's get_moves()"""
        all_moves = []
        for piece in board.pieces:
            if piece.colour == colour:
                for move in piece.get_moves(board.pieces):
                    all_moves.append((piece, piece.coords, move))

        return all_moves

    def generate_move(self, board, colour):
        """Finds the best move for the AI"""
        best_move = self.negamax(board, self.MAX_DEPTH, self.ALPHA, self.BETA, colour)

        return best_move