import tkinter as tk
import threading

from board import Board
from engine import Engine

from pieces import *
from utils import clamp

class Chess:
    def __init__(self, root, square_size, board_size):
        self.square_size = square_size
        self.board_size = board_size

        self.root = root
        self.root.geometry("854x480")
        self.root.minsize(854, 480)

        self.images = []
        self.selected_piece = None
        self.current_turn = 1 # White starts

        self.board = Board()
        self.engine = Engine(depth=2)

        self.setup_ui()

    def setup_ui(self):
        self.canvas_width = self.square_size * self.board_size
        self.canvas_height = self.square_size * self.board_size

        self.canvas = tk.Canvas(self.root, width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack(anchor="nw")

        self.undo_button = tk.Button(self.root, text="Undo Move", command=self.undo_move)
        self.undo_button.pack()

        self.game_button = tk.Button(self.root, text="New Game", command=self.reset_game)
        self.game_button.pack()

        self.update_graphics()

    def reset_game(self):
        self.board = Board()
        self.update_graphics()

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

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=colour, width=0)
        
        # Bind events so player can move pieces
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_drop)

    def draw_pieces(self):
        white_pieces = {
            "r": tk.PhotoImage(file="ChessPieces/wR.png"),
            "n": tk.PhotoImage(file="ChessPieces/wN.png"),
            "b": tk.PhotoImage(file="ChessPieces/wB.png"),
            "q": tk.PhotoImage(file="ChessPieces/wQ.png"),
            "k": tk.PhotoImage(file="ChessPieces/wK.png"),
            "p": tk.PhotoImage(file="ChessPieces/wP.png")
        }

        black_pieces = {
            "r": tk.PhotoImage(file="ChessPieces/bR.png"),
            "n": tk.PhotoImage(file="ChessPieces/bN.png"),
            "b": tk.PhotoImage(file="ChessPieces/bB.png"),
            "q": tk.PhotoImage(file="ChessPieces/bQ.png"),
            "k": tk.PhotoImage(file="ChessPieces/bK.png"),
            "p": tk.PhotoImage(file="ChessPieces/bP.png")
        }

        for piece in self.board.pieces:
            if piece.colour == 1:
                image = white_pieces[piece.piece_type]
            else:
                image = black_pieces[piece.piece_type]

            piece.piece_image = self.canvas.create_image(
                piece.coords[0] * self.square_size + self.square_size // 2,
                piece.coords[1] * self.square_size + self.square_size // 2,
                image=image,
                tag="piece"
            )

            # Keep a reference to the image to prevent garbage collection
            self.images.append(image)

    def on_click(self, event):
        """Handle clicking on a piece to start dragging"""
        x = event.x // self.square_size
        y = event.y // self.square_size

        for piece in self.board.pieces:
            if piece.coords == (x, y) and self.current_turn == 1 and piece.colour == 1:
                self.selected_piece = piece
                self.offset_x = event.x - piece.coords[0] * self.square_size
                self.offset_y = event.y - piece.coords[1] * self.square_size
                break

        if self.selected_piece:
            # Highlight all the possible moves a player can make
            for (x, y) in self.selected_piece.get_moves(self.board):
                x1 = x * self.square_size
                y1 = y * self.square_size
                x2 = (x + 1) * self.square_size
                y2 = (y + 1) * self.square_size

                if (x + y) % 2 == 0:
                    colour = "#de3d4b"
                else:
                    colour = "#b0272f"

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=colour, width=0, tag="highlight")

            self.canvas.tag_raise("piece") # So pieces are visible above the highlight
            
    def on_drag(self, event):
        """Drag the selected piece"""
        x = clamp(event.x, 0, self.canvas_width)
        y = clamp(event.y, 0, self.canvas_height)

        if self.selected_piece:
            self.canvas.coords(self.selected_piece.piece_image, x, y)

    def on_drop(self, event):
        """Drop the piece on a square"""
        if self.selected_piece:
            new_x = event.x // self.square_size
            new_y = event.y // self.square_size
            new_coords = (new_x, new_y)

            if new_coords in self.selected_piece.get_moves(self.board):
                # The player has selected a valid move, so play it
                self.board.make_move(self.selected_piece.coords, new_coords)
                self.update_graphics()

                self.selected_piece = None
                self.current_turn = -1 # Black

                # AI turn
                thread = threading.Thread(target=self.ai_turn, daemon=True)
                thread.start()
            else:
                # Otherwise, the attempted move is invalid so don't update position
                self.selected_piece = None
                self.update_graphics()

    def ai_done(self):
        self.current_turn = 1 # Switch back to player's turn
        self.update_graphics()

    def ai_turn(self):
        best_move = self.engine.generate_move(self.board, -1)
        _, start, end = best_move

        self.board.make_move(start, end)
        self.root.after(0, self.ai_done)

    def update_graphics(self):
        """Updates the graphics based on the board state"""
        self.canvas.delete("piece") # Remove all the old piece images
        self.canvas.delete("highlight")

        self.draw_board()
        self.draw_pieces()

    def undo_move(self):
        """Undoes the last move"""
        self.board.unmake_move()
        self.board.unmake_move()
        self.update_graphics()

if __name__ == "__main__":
    root = tk.Tk()
    app = Chess(root, square_size=60, board_size=8)

    root.mainloop()