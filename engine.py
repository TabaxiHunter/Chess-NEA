import random

class Engine:
    def evaluate_board(self, pieces):
        pass

    def generate_move(self, colour, pieces):
        legal_moves = []
        
        for piece in pieces:
            if piece.colour == colour:
                moves = piece.get_moves(pieces)

                for move in moves:
                    legal_moves.append((piece, move))

        return random.choice(legal_moves)