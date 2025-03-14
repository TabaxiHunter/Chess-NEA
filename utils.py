def clamp(n, min, max):
    """Keep numbers within a valid range"""
    if n < min: 
        return min
    elif n > max: 
        return max
    else:
        return n
    
def fen_to_coords(fen):
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

def move_to_pgn(move):
    start, end, piece, captured_piece, promoted_piece = move

    def coord_to_chess(coord):
        """Convert (row, col) to chess notation."""
        row, col = coord
        return chr(col + ord('a')) + str(8 - row)

    start_notation = coord_to_chess(start)
    end_notation = coord_to_chess(end)

    pgn_move = ""

    if piece.piece_type == "p":
        if captured_piece:
            pgn_move += start_notation[0]  # Include file of pawn if capturing
    else:
        pgn_move += piece.piece_type

    # Capture notation
    if captured_piece:
        pgn_move += "x"

    # Add destination square
    pgn_move += end_notation

    # Handle promotion
    if promoted_piece:
        pgn_move += "=" + promoted_piece

    return pgn_move

def format_seconds(seconds):
    minutes = seconds // 60
    remaining_seconds = seconds % 60

    return f"{minutes:02}:{remaining_seconds:02}"