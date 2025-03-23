import tkinter as tk
import threading

from board import Board
from engine import Engine
from utils import clamp, move_to_pgn, format_seconds
from tkinter import messagebox

class Game:
    def __init__(self, root, square_size, board_size):
        self.square_size = square_size
        self.board_size = board_size

        self.root = root
        self.root.geometry("854x480")
        self.root.minsize(854, 480)
        self.root.title("Chess AI")
        self.root.resizable(False, False) # Window size cannot be changed
        self.jobs = []

        self.difficulty = 2
        self.time = 300

        self.load_images()
        self.setup_ui()
        self.start_game()

    def setup_ui(self):
        self.canvas_width = self.square_size * self.board_size
        self.canvas_height = self.square_size * self.board_size

        self.canvas = tk.Canvas(self.root, width=self.canvas_width, height=self.canvas_height)
        self.canvas.place(x=0,y=0)

        # Bind events so player can move pieces
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_drop)

        self.timer = tk.Label(self.root, text="", borderwidth=2, relief="solid", height=2, width=8, font=("Arial", 25), bg="white")
        self.timer.place(x=490, y=2)

        self.move_list = tk.Listbox(self.root, height=15, width=14, relief="solid", borderwidth=2, font=("Arial", 14))
        self.move_list.bindtags((self.move_list, self.root, tk.ALL)) # So that moves cannot be selected
        self.move_list.place(x=489, y=115)

        tk.Label(self.root, text="Move History", borderwidth=2, relief="solid", height=1, width=14, font=("Arial", 14), bg="grey").place(x=489, y=90)
        tk.Label(self.root, text="Difficulty", borderwidth=2, relief="solid", height=1, width=14, font=("Arial", 14), bg="grey").place(x=670, y=2)

        tk.Button(self.root, text="Beginner", borderwidth=2, relief="solid", height=1, width=13, font=("Arial", 14), bg="white",
            command=lambda: self.update_difficulty(1)
        ).place(x=674, y=32)

        tk.Button(self.root, text="Intermediate", borderwidth=2, relief="solid", height=1, width=13, font=("Arial", 14), bg="white",
            command=lambda: self.update_difficulty(2)
        ).place(x=674, y=72)

        tk.Button(self.root, text="Advanced", borderwidth=2, relief="solid", height=1, width=13, font=("Arial", 14), bg="white",
            command=lambda: self.update_difficulty(3)
        ).place(x=674, y=112)

        tk.Label(self.root, text="Time Controls", borderwidth=2, relief="solid", height=1, width=14, font=("Arial", 14), bg="grey").place(x=670, y=152)

        tk.Button(self.root, text="Bullet", borderwidth=2, relief="solid", height=1, width=13, font=("Arial", 14), bg="white",
            command=lambda: self.update_time(60)
        ).place(x=674, y=182)

        tk.Button(self.root, text="Blitz", borderwidth=2, relief="solid", height=1, width=13, font=("Arial", 14), bg="white",
            command=lambda: self.update_time(5*60)
        ).place(x=674, y=222)

        tk.Button(self.root, text="Classical", borderwidth=2, relief="solid", height=1, width=13, font=("Arial", 14), bg="white",
            command=lambda: self.update_time(60*60)
        ).place(x=674, y=262)

        tk.Button(self.root, text="Start Game", borderwidth=2, relief="solid", height=2, width=13, font=("Arial", 14), bg="grey",
            command=lambda: self.start_game()
        ).place(x=674, y=352)

    def update_difficulty(self, difficulty):
        self.difficulty = difficulty

    def update_time(self, time):
        self.time = time

    def start_game(self):
        self.images = []
        self.selected_piece = None
        self.current_turn = 1 # White starts

        self.board = Board()
        self.engine = Engine(depth=self.difficulty)

        self.start_time = self.time
        self.time_left = self.start_time

        for job in self.jobs:
            self.root.after_cancel(job)

        self.move_list.delete(0, tk.END)

        # Start timer
        self.timer.configure(text=format_seconds(self.time_left))
        self.jobs.append(self.root.after(1000, self.start_timer))

        self.update_graphics()

    def start_timer(self):
        # Timer only counts down during the player's turn
        if self.current_turn == 1:
            self.time_left -= 1
            self.timer.configure(text=format_seconds(self.time_left))

        if self.time_left > 0:
            self.jobs.append(self.root.after(1000, self.start_timer))
        else:
            self.end_game()
            messagebox.showinfo(parent=self.root, title="Game over!", message="You ran out of time")

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

        # Show the AI's previous move move
        history = self.board.history

        if len(history) == 0:
            return
        
        last_move = history[-1]
        piece = last_move[2]

        if piece.colour == 1:
            return

        coords = last_move[0], last_move[1]

        for coord in coords:
            x, y = coord

            if (x + y) % 2 == 0:
                colour = "#CDD26A"
            else:
                colour = "#aba23a"

            x1 = x * self.square_size
            y1 = y * self.square_size
            x2 = (x + 1) * self.square_size
            y2 = (y + 1) * self.square_size

            self.canvas.create_rectangle(x1, y1, x2, y2, fill=colour, width=0)

    def load_images(self):
        self.white_pieces = {
            "r": tk.PhotoImage(file="ChessPieces/wR.png"),
            "n": tk.PhotoImage(file="ChessPieces/wN.png"),
            "b": tk.PhotoImage(file="ChessPieces/wB.png"),
            "q": tk.PhotoImage(file="ChessPieces/wQ.png"),
            "k": tk.PhotoImage(file="ChessPieces/wK.png"),
            "p": tk.PhotoImage(file="ChessPieces/wP.png")
        }

        self.black_pieces = {
            "r": tk.PhotoImage(file="ChessPieces/bR.png"),
            "n": tk.PhotoImage(file="ChessPieces/bN.png"),
            "b": tk.PhotoImage(file="ChessPieces/bB.png"),
            "q": tk.PhotoImage(file="ChessPieces/bQ.png"),
            "k": tk.PhotoImage(file="ChessPieces/bK.png"),
            "p": tk.PhotoImage(file="ChessPieces/bP.png")
        }

    def draw_pieces(self):
        for piece in self.board.pieces:
            if piece.colour == 1:
                image = self.white_pieces[piece.piece_type]
            else:
                image = self.black_pieces[piece.piece_type]

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
            for (x, y) in self.selected_piece.get_legal_moves(self.board):
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
            self.canvas.tag_raise(self.selected_piece.piece_image)
            
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

            if new_coords in self.selected_piece.get_legal_moves(self.board):
                # The player has selected a valid move, so play it
                move = self.board.make_move(self.selected_piece.coords, new_coords)

                self.move_list.insert(tk.END, f"{self.move_list.index(tk.END)+1}. {move_to_pgn(move)}")
                self.move_list.yview(tk.END)

                self.update_graphics()
                self.is_game_over() # Check for checkmate or stalemate

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
        # Check for checkmate or stalemate
        self.is_game_over()

        self.current_turn = 1 # Switch back to player's turn
        self.update_graphics()

    def ai_turn(self):
        best_move = self.engine.generate_move(self.board, -1)

        if best_move:
            start, end = best_move

            move = self.board.make_move(start, end)
            last_move = self.move_list.get(tk.END)

            self.move_list.delete(tk.END)
            self.move_list.insert(tk.END, f"{last_move} {move_to_pgn(move)}")
            self.move_list.yview(tk.END)

            self.root.after(0, self.ai_done)

    def end_game(self):
        self.update_graphics()

        # Rebind canvas events so player can't interact with board anymore
        self.canvas.bind("<Button-1>", "")
        self.canvas.bind("<B1-Motion>", "")
        self.canvas.bind("<ButtonRelease-1>", "")

        for job in self.jobs:
            self.root.after_cancel(job)

    def is_game_over(self):
        colour = "White" if self.current_turn == 1 else "Black"

        if self.board.is_checkmate(-self.current_turn):
            self.end_game()
            messagebox.showinfo(parent=self.root, title="Checkmate!", message=f"{colour} wins")

        elif self.board.is_stalemate(-self.current_turn):
            self.end_game()
            messagebox.showinfo(parent=self.root, title="Stalemate!", message="It's a draw")

    def update_graphics(self):
        """Updates the graphics based on the board state"""
        self.canvas.delete("piece") # Remove all the old piece images
        self.canvas.delete("highlight")

        self.draw_board()
        self.draw_pieces()

if __name__ == "__main__":
    root = tk.Tk()
    app = Game(root, square_size=60, board_size=8)

    root.mainloop()