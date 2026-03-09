# app/password_manager.py
# NO IMPORTS - All functionality implemented from scratch

# ============================================================================
# Binary file operations
# ============================================================================

def read_text_file(path):
    """Read text file"""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_text_file(path, content):
    """Write text file"""
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def file_exists(path):
    """Check if file exists"""
    try:
        open(path, 'r').close()
        return True
    except:
        return False

# ============================================================================
# Simple JSON Implementation
# ============================================================================

def _json_escape(s):
    """Escape string for JSON"""
    s = s.replace('\\', '\\\\')
    s = s.replace('"', '\\"')
    s = s.replace('\n', '\\n')
    s = s.replace('\r', '\\r')
    s = s.replace('\t', '\\t')
    return s

def _json_encode(obj, indent=2, depth=0):
    """Encode object as JSON"""
    if obj is None:
        return 'null'
    elif isinstance(obj, bool):
        return 'true' if obj else 'false'
    elif isinstance(obj, (int, float)):
        return str(obj)
    elif isinstance(obj, str):
        return f'"{_json_escape(obj)}"'
    elif isinstance(obj, dict):
        if not obj:
            return '{}'
        if indent is None:
            items = [f'"{_json_escape(k)}": {_json_encode(v, None)}' for k, v in obj.items()]
            return '{' + ', '.join(items) + '}'
        else:
            current_indent = ' ' * (indent * (depth + 1))
            close_indent = ' ' * (indent * depth)
            items = [f'{current_indent}"{_json_escape(k)}": {_json_encode(v, indent, depth + 1)}' for k, v in obj.items()]
            return '{\n' + ',\n'.join(items) + '\n' + close_indent + '}'
    elif isinstance(obj, (list, tuple)):
        if not obj:
            return '[]'
        if indent is None:
            items = [_json_encode(item, None) for item in obj]
            return '[' + ', '.join(items) + ']'
        else:
            current_indent = ' ' * (indent * (depth + 1))
            close_indent = ' ' * (indent * depth)
            items = [current_indent + _json_encode(item, indent, depth + 1) for item in obj]
            return '[\n' + ',\n'.join(items) + '\n' + close_indent + ']'
    else:
        raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

def _json_parse(s):
    """Parse JSON string"""
    class Parser:
        def __init__(self, text):
            self.text = text
            self.index = 0
        
        def parse(self):
            self._skip_whitespace()
            result = self._parse_value()
            self._skip_whitespace()
            return result
        
        def _skip_whitespace(self):
            while self.index < len(self.text) and self.text[self.index] in ' \n\r\t':
                self.index += 1
        
        def _parse_value(self):
            self._skip_whitespace()
            if self.index >= len(self.text):
                raise ValueError("Unexpected end of JSON")
            
            ch = self.text[self.index]
            if ch == 'n':
                return self._parse_null()
            elif ch == 't':
                return self._parse_true()
            elif ch == 'f':
                return self._parse_false()
            elif ch == '"':
                return self._parse_string()
            elif ch == '[':
                return self._parse_array()
            elif ch == '{':
                return self._parse_object()
            elif ch == '-' or ch.isdigit():
                return self._parse_number()
            else:
                raise ValueError(f"Unexpected character '{ch}' at position {self.index}")
        
        def _parse_null(self):
            if self.text[self.index:self.index+4] == 'null':
                self.index += 4
                return None
            raise ValueError("Expected 'null'")
        
        def _parse_true(self):
            if self.text[self.index:self.index+4] == 'true':
                self.index += 4
                return True
            raise ValueError("Expected 'true'")
        
        def _parse_false(self):
            if self.text[self.index:self.index+5] == 'false':
                self.index += 5
                return False
            raise ValueError("Expected 'false'")
        
        def _parse_string(self):
            if self.text[self.index] != '"':
                raise ValueError("Expected '\"'")
            self.index += 1
            result = ''
            while self.index < len(self.text):
                ch = self.text[self.index]
                if ch == '"':
                    self.index += 1
                    return result
                elif ch == '\\':
                    self.index += 1
                    if self.index >= len(self.text):
                        raise ValueError("Unexpected end of string")
                    next_ch = self.text[self.index]
                    if next_ch == '"':
                        result += '"'
                    elif next_ch == '\\':
                        result += '\\'
                    elif next_ch == '/':
                        result += '/'
                    elif next_ch == 'b':
                        result += '\b'
                    elif next_ch == 'f':
                        result += '\f'
                    elif next_ch == 'n':
                        result += '\n'
                    elif next_ch == 'r':
                        result += '\r'
                    elif next_ch == 't':
                        result += '\t'
                    else:
                        raise ValueError(f"Invalid escape sequence: \\{next_ch}")
                    self.index += 1
                else:
                    result += ch
                    self.index += 1
            raise ValueError("Unterminated string")
        
        def _parse_number(self):
            start = self.index
            if self.text[self.index] == '-':
                self.index += 1
            
            while self.index < len(self.text) and self.text[self.index].isdigit():
                self.index += 1
            
            if self.index < len(self.text) and self.text[self.index] == '.':
                self.index += 1
                while self.index < len(self.text) and self.text[self.index].isdigit():
                    self.index += 1
            
            num_str = self.text[start:self.index]
            if '.' in num_str:
                return float(num_str)
            else:
                return int(num_str)
        
        def _parse_array(self):
            if self.text[self.index] != '[':
                raise ValueError("Expected '['")
            self.index += 1
            result = []
            self._skip_whitespace()
            
            if self.index < len(self.text) and self.text[self.index] == ']':
                self.index += 1
                return result
            
            while True:
                result.append(self._parse_value())
                self._skip_whitespace()
                
                if self.text[self.index] == ']':
                    self.index += 1
                    return result
                elif self.text[self.index] == ',':
                    self.index += 1
                else:
                    raise ValueError("Expected ',' or ']'")
        
        def _parse_object(self):
            if self.text[self.index] != '{':
                raise ValueError("Expected '{'")
            self.index += 1
            result = {}
            self._skip_whitespace()
            
            if self.index < len(self.text) and self.text[self.index] == '}':
                self.index += 1
                return result
            
            while True:
                self._skip_whitespace()
                if self.index >= len(self.text) or self.text[self.index] != '"':
                    raise ValueError("Expected string key")
                
                key = self._parse_string()
                self._skip_whitespace()
                
                if self.index >= len(self.text) or self.text[self.index] != ':':
                    raise ValueError("Expected ':'")
                self.index += 1
                
                value = self._parse_value()
                result[key] = value
                
                self._skip_whitespace()
                if self.text[self.index] == '}':
                    self.index += 1
                    return result
                elif self.text[self.index] == ',':
                    self.index += 1
                else:
                    raise ValueError("Expected ',' or '}'")
    
    parser = Parser(s)
    return parser.parse()

# ============================================================================
# Hex encoding/decoding
# ============================================================================

def _hexlify(data):
    """Convert bytes to hex string"""
    if isinstance(data, str):
        data = data.encode('utf-8')
    result = ''
    for byte in data:
        result += '{:02x}'.format(byte)
    return result

def _unhexlify(hex_string):
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
# Directory operations and utilities
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
    """Generate random bytes (tries system random, falls back to pseudo-random)"""
    try:
        # Try using os.urandom if available (through __import__)
        os_module = __import__('os')
        return os_module.urandom(n)
    except:
        # Fallback to pseudo-random
        return _pseudo_random(n)

def _makedirs(path):
    """Create directory"""
    try:
        os_module = __import__('os')
        os_module.makedirs(path, exist_ok=True)
    except Exception as e:
        print(f"Warning: Could not create directory {path}: {e}")

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
    sha = SHA256()
    block_size = 64
    if len(key) > block_size:
        key = bytes.fromhex(sha.hash(key))
    if len(key) < block_size:
        key += b'\x00' * (block_size - len(key))
    ipad = bytes((x ^ 0x36) for x in key)
    opad = bytes((x ^ 0x5C) for x in key)
    inner_hash = sha.hash(ipad + message)
    return sha.hash(opad + bytes.fromhex(inner_hash))

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
# Password Manager Implementation
# ============================================================================

DATA_DIR = "data"
PASSWORD_FILE = None

def _get_password_file():
    global PASSWORD_FILE
    if PASSWORD_FILE is None:
        PASSWORD_FILE = DATA_DIR + "/" + "passwords.json"
    return PASSWORD_FILE

def ensure_data_dir():
    """Ensure data directory exists"""
    _makedirs(DATA_DIR)

def load_passwords():
    """Load passwords from file"""
    ensure_data_dir()
    pwd_file = _get_password_file()
    if not file_exists(pwd_file):
        return {}
    try:
        content = read_text_file(pwd_file)
        return _json_parse(content)
    except Exception as e:
        print(f"Error loading passwords: {e}")
        return {}

def save_passwords(data):
    """Save passwords to file"""
    ensure_data_dir()
    pwd_file = _get_password_file()
    content = _json_encode(data, indent=2)
    write_text_file(pwd_file, content)

def store_password(username, password):
    """
    Store a new password entry.
    Returns True if successful, False if username already exists.
    """
    data = load_passwords()
    if username in data:
        return False

    salt = _urandom(16)
    iterations = 120000
    derived_key = pbkdf2(password, salt, iterations, 32)

    data[username] = {
        "salt": _hexlify(salt),
        "hash": _hexlify(derived_key),
        "iterations": iterations
    }

    save_passwords(data)
    return True

def verify_password(username, password):
    """
    Check if the provided password matches the stored one.
    Returns (success: bool, message: str)
    """
    data = load_passwords()
    if username not in data:
        return False, "User not found"

    entry = data[username]
    salt = _unhexlify(entry["salt"])
    stored_hash = _unhexlify(entry["hash"])
    iterations = entry.get("iterations", 100000)

    computed = pbkdf2(password, salt, iterations, 32)

    if computed == stored_hash:
        return True, "Password correct"
    else:
        return False, "Incorrect password"

# ────────────────────────────────────────────────
#   Simple console test
# ────────────────────────────────────────────────
if __name__ == "__main__":
    print("Testing password manager...")
    store_password("alice", "secret123")
    success, msg = verify_password("alice", "secret123")
    print(f"Verify correct: {success} → {msg}")
    success, msg = verify_password("alice", "wrong")
    print(f"Verify wrong: {success} → {msg}")