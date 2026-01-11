#Random math functions that might be useful in multiple places

def floorlog2(n: int) -> int:
    """Return floor(log2(n)) for positive integers using Python's bit_length."""
    if n < 1:
        raise ValueError("n must be >= 1")
    return n.bit_length() - 1