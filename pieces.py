class Piece:
    def __init__(self, x, y, colour, image):
        self.coords = (x, y)
        self.colour = colour
        self.image = image

class Pawn(Piece):
    def get_moves(self):
        return
    
    def get_value(self):
        return 1

class Knight(Piece):
    def get_moves(self):
        return 
    
    def get_value(self):
        return 3

class Bishop(Piece):
    def get_moves(self):
        return 
    
    def get_value(self):
        return 3

class Rook(Piece):
    def get_moves(self):
        return 
    
    def get_value(self):
        return 5

class Queen(Piece):
    def get_moves(self):
        return
    
    def get_value(self):
        return 9

class King(Piece):
    def get_moves(self):
        return
    
    def get_value(self):
        return 100 # The king is invaluable