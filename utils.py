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