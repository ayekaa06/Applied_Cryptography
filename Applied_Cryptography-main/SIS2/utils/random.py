_random_state = None

def _seed_random():
    """Initialize random state using system time"""
    global _random_state
    import time
    _random_state = int(time.time() * 1000000) % (2**32)

def _pseudo_random(n):
    """Generate pseudo-random bytes using a simple LCG"""
    global _random_state
    if _random_state is None:
        _seed_random()
    
    result = bytearray()
    for _ in range(n):
        # Linear Congruential Generator
        _random_state = (_random_state * 1103515245 + 12345) & 0xFFFFFFFF
        result.append((_random_state >> 16) & 0xFF)
    return bytes(result)

def _urandom(n):
    """Generate random bytes"""
    try:
        os_module = __import__('os')
        return os_module.urandom(n)
    except:
        return _pseudo_random(n)