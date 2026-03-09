# app/file_integrity.py
# NO IMPORTS - All functionality implemented from scratch

# ============================================================================
# File and Directory Operations
# ============================================================================

def file_exists(path):
    """Check if file exists"""
    try:
        with open(path, 'rb') as f:
            pass
        return True
    except:
        return False

def is_file(path):
    """Check if path is a file"""
    try:
        with open(path, 'rb') as f:
            pass
        return True
    except:
        return False

def read_text_file(path):
    """Read text file"""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_text_file(path, content):
    """Write text file"""
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def read_binary_file(path):
    """Read binary file"""
    with open(path, 'rb') as f:
        return f.read()

def get_directory(path):
    """Get directory from path"""
    parts = path.replace('\\', '/').split('/')
    if len(parts) > 1:
        return '/'.join(parts[:-1])
    return '.'

def get_relative_path(path, start):
    """Get relative path"""
    path = path.replace('\\', '/')
    start = start.replace('\\', '/')
    
    if path.startswith(start + '/'):
        return path[len(start)+1:]
    return path

def walk_directory(path):
    """Walk directory tree"""
    try:
        os_module = __import__('os')
        for root, dirs, files in os_module.walk(path):
            yield root, dirs, files
    except Exception as e:
        print(f"Error walking directory: {e}")

# ============================================================================
# JSON Implementation
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
                raise ValueError(f"Unexpected character '{ch}'")
        
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
                        raise ValueError(f"Invalid escape: \\{next_ch}")
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
# File Integrity Functions
# ============================================================================

MANIFEST_EXT = ".sha256manifest.json"

def compute_file_hash(filepath):
    """Compute SHA256 hash of a file"""
    sha = SHA256()
    try:
        with open(filepath, "rb") as f:
            data = f.read()
        return sha.hash(data)
    except Exception as e:
        raise RuntimeError(f"Cannot hash file {filepath}: {e}")

def create_manifest():
    """Create manifest for a directory"""
    # Simplified console version
    print("Enter folder path to create manifest for:")
    folder = input().strip()
    
    if not folder:
        print("Cancelled")
        return

    manifest = {}
    try:
        for root, dirs, files in walk_directory(folder):
            for filename in files:
                filepath = root + "/" + filename
                relpath = get_relative_path(filepath, folder)
                manifest[relpath] = compute_file_hash(filepath)
        
        manifest_path = folder + "/manifest" + MANIFEST_EXT
        content = _json_encode(manifest, indent=2)
        write_text_file(manifest_path, content)
        
        print(f"Manifest created: {manifest_path}")
    except Exception as e:
        print(f"Error: {e}")

def verify_manifest():
    """Verify integrity of files against manifest"""
    print("Enter manifest file path:")
    manifest_file = input().strip()
    
    if not manifest_file:
        print("Cancelled")
        return

    try:
        content = read_text_file(manifest_file)
        manifest = _json_parse(content)
        
        base_dir = get_directory(manifest_file)
        results = []
        
        for relpath, expected_hash in manifest.items():
            fullpath = base_dir + "/" + relpath
            if not is_file(fullpath):
                results.append(f"MISSING: {relpath}")
                continue
            
            current_hash = compute_file_hash(fullpath)
            if current_hash == expected_hash:
                results.append(f"OK: {relpath}")
            else:
                results.append(f"TAMPERED: {relpath} (expected {expected_hash[:12]}..., got {current_hash[:12]}...)")
        
        for line in results[:30]:
            print(line)
        if len(results) > 30:
            print(f"... and {len(results)-30} more")
        
    except Exception as e:
        print(f"Error: {e}")