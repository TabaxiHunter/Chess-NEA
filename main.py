import tkinter as tk

from pieces import *

def clamp(n, min, max):
    """Keep numbers within a valid range"""
    if n < min: 
        return min
    elif n > max: 
        return max
    else: 
        return n
    
FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR" # FEN notation for the starting position of chess

class Board(tk.Canvas):
    def __init__(self, square_size, board_size):
        self.square_size = square_size
        self.board_size = board_size

        self.canvas_width = self.square_size * self.board_size
        self.canvas_height = self.square_size * self.board_size

        tk.Canvas.__init__(self, width=self.canvas_width, height=self.canvas_height) # Inherit from Canvas

        self.pieces = {}
        self.selected_piece = None
        self.grid = ["." for _ in range(64)]

        self.draw_board()
        self.setup_pieces(FEN)

        # Bind events so player can move pieces
        self.bind("<Button-1>", self.on_click)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<ButtonRelease-1>", self.on_drop)

    def draw_board(self):
        """Draw the chessboard with alternating colours"""
        for row in range(self.board_size):
            for column in range(self.board_size):
                if (row + column) % 2 == 0:
                    colour = "#F0D9B5"
                else:
                    colour = "#B58863"

                x1 = column * self.square_size
                y1 = row * self.square_size
                x2 = (column + 1) * self.square_size
                y2 = (row + 1) * self.square_size

                self.create_rectangle(x1, y1, x2, y2, fill=colour, width=0)

    def setup_pieces(self, fen):
        print(fen)

        row = 0
        column = 0

        print(self.grid)

        for character in fen:
            if character == "/":
                row += 1
                column = 0
            elif character.isdigit():
                row += int(character)
            else:
                colour = "WHITE" if character.isupper() else "BLACK"
                piece_type = character.lower()

                self.grid[row+column] = (colour, piece_type)
                column += 1

        print(self.grid)

        """Set up the pieces in their starting positions"""
        initial_positions = {
            "r1": (0, 0), "n1": (1, 0), "b1": (2, 0), "q1": (3, 0), "k1": (4, 0), "b2": (5, 0), "n2": (6, 0), "r2": (7, 0),
            "p1": (0, 1), "p2": (1, 1), "p3": (2, 1), "p4": (3, 1), "p5": (4, 1), "p6": (5, 1), "p7": (6, 1), "p8": (7, 1),
            "P1": (0, 6), "P2": (1, 6), "P3": (2, 6), "P4": (3, 6), "P5": (4, 6), "P6": (5, 6), "P7": (6, 6), "P8": (7, 6),
            "R1": (0, 7), "N1": (1, 7), "B1": (2, 7), "Q1": (3, 7), "K1": (4, 7), "B2": (5, 7), "N2": (6, 7), "R2": (7, 7),
        }

        piece_images = {
            "r": tk.PhotoImage(file="ChessPieces/bR.png"),
            "n": tk.PhotoImage(file="ChessPieces/bN.png"),
            "b": tk.PhotoImage(file="ChessPieces/bB.png"),
            "q": tk.PhotoImage(file="ChessPieces/bQ.png"),
            "k": tk.PhotoImage(file="ChessPieces/bK.png"),
            "p": tk.PhotoImage(file="ChessPieces/bP.png"),
            "R": tk.PhotoImage(file="ChessPieces/wR.png"),
            "N": tk.PhotoImage(file="ChessPieces/wN.png"),
            "B": tk.PhotoImage(file="ChessPieces/wB.png"),
            "Q": tk.PhotoImage(file="ChessPieces/wQ.png"),
            "K": tk.PhotoImage(file="ChessPieces/wK.png"),
            "P": tk.PhotoImage(file="ChessPieces/wP.png")
        }

        root.images = [] # Store a reference to each image to prevent garbage collection

        for name, position in initial_positions.items():
            x, y = position
            piece_symbol = piece_images.get(name[0])

            self.add_piece(name, x, y, piece_symbol)

    def add_piece(self, name, x, y, image):
        """Add a chess piece to the board represented by an image"""
        root.images.append(image)

        piece_id = self.create_image(
            x * self.square_size + self.square_size // 2,
            y * self.square_size + self.square_size // 2,
            image=image
        )

        self.pieces[piece_id] = (name, x, y)

    def on_click(self, event):
        """Handle clicking on a piece to start dragging"""
        x = event.x // self.square_size
        y = event.y // self.square_size

        for piece_id, (name, px, py) in self.pieces.items():
            if px == x and py == y:
                self.selected_piece = piece_id
                self.offset_x = event.x - px * self.square_size
                self.offset_y = event.y - py * self.square_size
                break

    def on_drag(self, event):
        """Drag the selected piece"""
        x = clamp(event.x, 0, self.canvas_width)
        y = clamp(event.y, 0, self.canvas_height)

        if self.selected_piece:
            self.coords(self.selected_piece, x, y)

    def on_drop(self, event):
        """Drop the piece on a square"""
        # TODO: Validate before allowing piece to move
        if self.selected_piece:
            new_x = event.x // self.square_size
            new_y = event.y // self.square_size

            self.coords(
                self.selected_piece, 
                new_x * self.square_size + self.square_size // 2,
                new_y * self.square_size + self.square_size // 2
            )

            # Update the piece's logical position
            name, old_x, old_y = self.pieces[self.selected_piece]
            self.pieces[self.selected_piece] = (name, new_x, new_y)

            self.selected_piece = None

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Chess")
    #root.iconbitmap("icon.ico") # TODO: Replace this icon
    root.geometry("854x480")
    root.minsize(854, 480)

    board = Board(square_size=60, board_size=8)
    board.pack(anchor="nw")

    root.mainloop()