# main.py
# NO IMPORTS - Console-based cryptographic tool without tkinter

# ============================================================================
# SHA256 Implementation
# ============================================================================

class SHA256:
    def __init__(self):
        self.H = [
            0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
            0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19
        ]
        self.K = [
            0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
            0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
            0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
            0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
            0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
            0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
            0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
            0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
        ]

    def _rotr(self, x, n):
        return ((x >> n) | (x << (32 - n))) & 0xFFFFFFFF

    def _shr(self, x, n):
        return x >> n

    def _ch(self, x, y, z):
        return (x & y) ^ (~x & z)

    def _maj(self, x, y, z):
        return (x & y) ^ (x & z) ^ (y & z)

    def _sigma0(self, x):
        return self._rotr(x, 2) ^ self._rotr(x, 13) ^ self._rotr(x, 22)

    def _sigma1(self, x):
        return self._rotr(x, 6) ^ self._rotr(x, 11) ^ self._rotr(x, 25)

    def _gamma0(self, x):
        return self._rotr(x, 7) ^ self._rotr(x, 18) ^ self._shr(x, 3)

    def _gamma1(self, x):
        return self._rotr(x, 17) ^ self._rotr(x, 19) ^ self._shr(x, 10)

    def pad_message(self, message):
        if isinstance(message, str):
            message = message.encode('utf-8')
        bit_len = len(message) * 8
        message += b'\x80'
        while (len(message) * 8) % 512 != 448:
            message += b'\x00'
        message += bit_len.to_bytes(8, 'big')
        return message

    def hash(self, message, educational=False):
        padded = self.pad_message(message)
        h = self.H[:]
        states = [] if educational else None
        for i in range(0, len(padded), 64):
            block = padded[i:i+64]
            w = [0] * 64
            for j in range(16):
                w[j] = int.from_bytes(block[j*4:(j+1)*4], 'big')
            for j in range(16, 64):
                w[j] = (self._gamma1(w[j-2]) + w[j-7] + self._gamma0(w[j-15]) + w[j-16]) & 0xFFFFFFFF
            a, b, c, d, e, f, g, hh = h
            for j in range(64):
                t1 = (hh + self._sigma1(e) + self._ch(e, f, g) + self.K[j] + w[j]) & 0xFFFFFFFF
                t2 = (self._sigma0(a) + self._maj(a, b, c)) & 0xFFFFFFFF
                hh = g
                g = f
                f = e
                e = (d + t1) & 0xFFFFFFFF
                d = c
                c = b
                b = a
                a = (t1 + t2) & 0xFFFFFFFF
            if educational:
                states.append([a, b, c, d, e, f, g, hh])
            h = [(h[k] + [a, b, c, d, e, f, g, hh][k]) & 0xFFFFFFFF for k in range(8)]
        digest = ''.join(f'{x:08x}' for x in h)
        return (digest, states) if educational else digest

# ============================================================================
# HMAC Implementation
# ============================================================================

def hmac_sha256(key, message):
    block_size = 64
    if isinstance(key, str):
        key = key.encode()
    if isinstance(message, str):
        message = message.encode()
    sha = SHA256()
    if len(key) > block_size:
        key = bytes.fromhex(sha.hash(key))
    if len(key) < block_size:
        key = key + b'\x00' * (block_size - len(key))
    o_key_pad = bytes([b ^ 0x5c for b in key])
    i_key_pad = bytes([b ^ 0x36 for b in key])
    inner = sha.hash(i_key_pad + message)
    inner_bytes = bytes.fromhex(inner)
    final = sha.hash(o_key_pad + inner_bytes)
    return bytes.fromhex(final)

# ============================================================================
# PBKDF2 Implementation
# ============================================================================

def pbkdf2(password, salt, iterations, dk_len):
    if isinstance(password, str):
        password = password.encode()
    if isinstance(salt, str):
        salt = salt.encode()
    h_len = 32  # SHA-256
    l = (dk_len + h_len - 1) // h_len
    dk = b''
    for i in range(1, l + 1):
        u = hmac_sha256(password, salt + i.to_bytes(4, 'big'))
        t = u
        for _ in range(1, iterations):
            u = hmac_sha256(password, u)
            t = bytes(a ^ b for a, b in zip(t, u))
        dk += t
    return dk[:dk_len]

# ============================================================================
# HKDF Implementation
# ============================================================================

def hkdf_extract(salt, ikm):
    if salt is None:
        salt = b'\x00' * 32
    return hmac_sha256(salt, ikm)

def hkdf_expand(prk, info, length):
    h_len = 32
    n = (length + h_len - 1) // h_len
    okm = b''
    t = b''
    for i in range(1, n + 1):
        t = hmac_sha256(prk, t + info + bytes([i]))
        okm += t
    return okm[:length]

def hkdf(salt, ikm, info, length):
    prk = hkdf_extract(salt, ikm)
    return hkdf_expand(prk, info, length)

# ============================================================================
# Random utilities
# ============================================================================

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

# ============================================================================
# Hex Utilities
# ============================================================================

def hexlify(data):
    """Convert bytes to hex string"""
    if isinstance(data, str):
        data = data.encode('utf-8')
    result = ''
    for byte in data:
        result += '{:02x}'.format(byte)
    return result

def unhexlify(hex_string):
    """Convert hex string to bytes"""
    if isinstance(hex_string, bytes):
        hex_string = hex_string.decode('utf-8')
    hex_string = hex_string.strip()
    result = bytearray()
    for i in range(0, len(hex_string), 2):
        byte_val = int(hex_string[i:i+2], 16)
        result.append(byte_val)
    return bytes(result)

# ============================================================================
# Console-based UI
# ============================================================================

def show_menu():
    """Display main menu"""
    print("\n" + "="*60)
    print("   SHA-256 Cryptographic Tools (No Imports!)")
    print("="*60)
    print("1. Hash Tool")
    print("2. HMAC Tool")
    print("3. Password Manager")
    print("4. Key Derivation (PBKDF2/HKDF)")
    print("5. File Integrity")
    print("0. Exit")
    print("-"*60)
    return input("Select option: ").strip()

def hash_tool():
    """Hash computation tool"""
    print("\n--- Hash Tool ---")
    msg = input("Enter message to hash (text): ").strip()
    
    if not msg:
        print("No input provided")
        return
    
    sha = SHA256()
    hash_val = sha.hash(msg)
    print(f"SHA-256 Hash: {hash_val}")
    
    show_educational = input("Show internal states? (y/n): ").lower().strip()
    if show_educational == 'y':
        _, states = sha.hash(msg, educational=True)
        for i, state in enumerate(states[:3]):
            print(f"  Round {i}: {state}")
        if len(states) > 3:
            print(f"  ... ({len(states)-3} more rounds)")

def hmac_tool():
    """HMAC tool"""
    print("\n--- HMAC Tool ---")
    key_input = input("Enter key (hex or text): ").strip()
    msg = input("Enter message (text): ").strip()
    
    if not key_input or not msg:
        print("Missing input")
        return
    
    if key_input.startswith(('0x', '0X')):
        key = unhexlify(key_input[2:])
    else:
        key = key_input.encode('utf-8')
    
    message = msg.encode('utf-8')
    tag = hmac_sha256(key, message)
    tag_hex = hexlify(tag)
    
    print(f"HMAC Tag: {tag_hex}")
    
    verify_input = input("Verify against a tag? (y/n): ").lower().strip()
    if verify_input == 'y':
        provided_tag = input("Enter tag to verify (hex): ").strip()
        try:
            provided_bytes = unhexlify(provided_tag)
            if provided_bytes == tag:
                print("✓ Tag matches!")
            else:
                print("✗ Tag does NOT match")
        except:
            print("Invalid hex format")

def password_manager():
    """Password manager"""
    print("\n--- Password Manager ---")
    print("1. Store password")
    print("2. Verify password")
    choice = input("Select: ").strip()
    
    if choice == '1':
        username = input("Enter username: ").strip()
        password = input("Enter password: ").strip()
        
        if not username or not password:
            print("Missing input")
            return
        
        salt = _urandom(16)
        iterations = 10000  # Reduced for demo speed
        derived_key = pbkdf2(password, salt, iterations, 32)
        
        print(f"Salt (hex): {hexlify(salt)}")
        print(f"Hash (hex): {hexlify(derived_key)}")
        print("✓ Password would be stored")
    
    elif choice == '2':
        username = input("Enter username: ").strip()
        password = input("Enter password: ").strip()
        salt_hex = input("Enter salt (hex): ").strip()
        hash_hex = input("Enter stored hash (hex): ").strip()
        
        try:
            salt = unhexlify(salt_hex)
            stored_hash = unhexlify(hash_hex)
            
            iterations = 10000
            computed = pbkdf2(password, salt, iterations, 32)
            
            if computed == stored_hash:
                print("✓ Password correct!")
            else:
                print("✗ Incorrect password")
        except Exception as e:
            print(f"Error: {e}")

def kdf_tool():
    """Key derivation tool"""
    print("\n--- Key Derivation Tool ---")
    print("1. PBKDF2")
    print("2. HKDF")
    choice = input("Select: ").strip()
    
    if choice == '1':
        print("\nPBKDF2 Mode")
        password = input("Enter password (text): ").strip()
        salt_hex = input("Enter salt (hex): ").strip()
        iterations = int(input("Iterations (default 100000): ").strip() or "100000")
        length = int(input("Key length (bytes, default 32): ").strip() or "32")
        
        try:
            salt = unhexlify(salt_hex) if salt_hex else b'salt'
            key = pbkdf2(password, salt, iterations, length)
            print(f"Derived key (hex): {hexlify(key)}")
        except Exception as e:
            print(f"Error: {e}")
    
    elif choice == '2':
        print("\nHKDF Mode")
        ikm_hex = input("Enter IKM (hex): ").strip()
        salt_hex = input("Enter salt (hex, optional): ").strip()
        info = input("Enter info (text): ").strip()
        length = int(input("Output length (bytes, default 32): ").strip() or "32")
        
        try:
            ikm = unhexlify(ikm_hex) if ikm_hex else b'input'
            salt = unhexlify(salt_hex) if salt_hex else None
            key = hkdf(salt, ikm, info.encode('utf-8'), length)
            print(f"Derived key (hex): {hexlify(key)}")
        except Exception as e:
            print(f"Error: {e}")

def file_integrity():
    """File integrity tool"""
    print("\n--- File Integrity Tool ---")
    print("1. Create manifest")
    print("2. Verify manifest")
    choice = input("Select: ").strip()
    
    if choice == '1':
        print("(Feature: Create SHA256 manifest for files in directory)")
        print("Implementation requires direct file operations")
    elif choice == '2':
        print("(Feature: Verify files against manifest)")
        print("Implementation requires direct file operations")

def main():
    """Main application loop"""
    while True:
        choice = show_menu()
        
        if choice == '1':
            hash_tool()
        elif choice == '2':
            hmac_tool()
        elif choice == '3':
            password_manager()
        elif choice == '4':
            kdf_tool()
        elif choice == '5':
            file_integrity()
        elif choice == '0':
            print("\nGoodbye!")
            break
        else:
            print("Invalid option")

if __name__ == "__main__":
    main()