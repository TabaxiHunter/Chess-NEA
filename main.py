import tkinter as tk

from pieces import *
from utils import clamp

STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR" # FEN notation for the starting position of chess

class Board(tk.Canvas):
    def __init__(self, square_size, board_size):
        self.square_size = square_size
        self.board_size = board_size

        self.canvas_width = self.square_size * self.board_size
        self.canvas_height = self.square_size * self.board_size

        tk.Canvas.__init__(self, width=self.canvas_width, height=self.canvas_height) # Inherit from Canvas

        self.pieces = []
        self.selected_piece = None

        self.draw_board()
        self.setup_pieces(STARTING_FEN)

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

    def fen_to_coords(self, fen):
        """Convert a FEN string to a dictionary of piece coordinates"""
        ranks = fen.split()[0].split("/") # Extract the board representation
        piece_positions = {}
    
        for rank_idx, rank in enumerate(ranks):
            file_idx = 0
            for char in rank:
                if char.isdigit():
                    file_idx += int(char) # Empty squares
                else:
                    position = (file_idx, rank_idx) # Convert to (x, y) coordinates with (0,0) at the top left
                    if char in piece_positions:
                        piece_positions[char].append(position)
                    else:
                        piece_positions[char] = [position]
                    file_idx += 1
        
        return piece_positions

    def setup_pieces(self, fen):
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

        piece_types = {
            "r": Rook,
            "n": Knight,
            "b": Bishop,
            "q": Queen,
            "k": King,
            "p": Pawn
        }

        piece_coords = self.fen_to_coords(fen)

        for piece_char in piece_coords:
            for position in piece_coords[piece_char]:
                file, rank = position

                colour = "WHITE" if piece_char.isupper() else "BLACK"
                image = piece_images[piece_char]

                piece_type = piece_char.lower()
                piece_class = piece_types[piece_type]

                piece = piece_class(file, rank, colour, image)

                self.add_piece(piece)

    def add_piece(self, piece):
        """Add a chess piece to the board represented by an image"""
        x, y  = piece.coords

        piece.piece_image = self.create_image(
            x * self.square_size + self.square_size // 2,
            y * self.square_size + self.square_size // 2,
            image=piece.image,
            tag="piece"
        )

        self.pieces.append(piece)

    def on_click(self, event):
        """Handle clicking on a piece to start dragging"""
        x = event.x // self.square_size
        y = event.y // self.square_size

        for piece in self.pieces:
            if piece.coords == (x, y):
                self.selected_piece = piece
                self.offset_x = event.x - piece.coords[0] * self.square_size
                self.offset_y = event.y - piece.coords[1] * self.square_size
                break

        if self.selected_piece:
            # Highlight all the possible moves a player can make
            for (x, y) in self.selected_piece.get_moves(self.pieces):
                x1 = x * self.square_size
                y1 = y * self.square_size
                x2 = (x + 1) * self.square_size
                y2 = (y + 1) * self.square_size

                if (x + y) % 2 == 0:
                    colour = "#de3d4b"
                else:
                    colour = "#b0272f"

                self.create_rectangle(x1, y1, x2, y2, fill=colour, width=0, tag="highlight")

            self.tag_raise("piece") # So pieces are visible above the highlight
            
    def on_drag(self, event):
        """Drag the selected piece"""
        x = clamp(event.x, 0, self.canvas_width)
        y = clamp(event.y, 0, self.canvas_height)

        if self.selected_piece:
            self.coords(self.selected_piece.piece_image, x, y)

    def on_drop(self, event):
        """Drop the piece on a square"""
        if self.selected_piece:
            new_x = event.x // self.square_size
            new_y = event.y // self.square_size

            if (new_x, new_y) in self.selected_piece.get_moves(self.pieces):
                self.coords(
                    self.selected_piece.piece_image, 
                    new_x * self.square_size + self.square_size // 2,
                    new_y * self.square_size + self.square_size // 2
                )

                # Update the piece's logical position
                self.selected_piece.coords = (new_x, new_y)
                self.selected_piece.has_moved = True

                print(self.selected_piece.coords)
                self.selected_piece = None
            else:
                self.coords(
                    self.selected_piece.piece_image, 
                    self.selected_piece.coords[0] * self.square_size + self.square_size // 2,
                    self.selected_piece.coords[1] * self.square_size + self.square_size // 2
                )
                self.selected_piece = None

            self.delete("highlight")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Chess")
    
    root.geometry("854x480")
    root.minsize(854, 480)

    board = Board(square_size=60, board_size=8)
    board.pack(anchor="nw")

    root.mainloop()