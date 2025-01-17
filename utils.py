def clamp(n, min, max):
    """Keep numbers within a valid range"""
    if n < min: 
        return min
    elif n > max: 
        return max
    else: 
        return n