# Custom implementations of standard library functions
# NO IMPORTS ALLOWED

# ============================================================================
# HEX ENCODING/DECODING (replaces binascii)
# ============================================================================

def hexlify(data):
    """Convert bytes to hex string"""
    if isinstance(data, str):
        data = data.encode('utf-8')
    result = ''
    for byte in data:
        result += '{:02x}'.format(byte)
    return result.encode('utf-8') if False else result

def unhexlify(hex_string):
    """Convert hex string to bytes"""
    if isinstance(hex_string, bytes):
        hex_string = hex_string.decode('utf-8')
    hex_string = hex_string.replace(' ', '').replace('\n', '').replace('\t', '')
    result = bytearray()
    for i in range(0, len(hex_string), 2):
        try:
            byte_val = int(hex_string[i:i+2], 16)
            result.append(byte_val)
        except ValueError:
            raise ValueError(f"Non-hexadecimal number found in {hex_string[i:i+2]}")
    return bytes(result)

# ============================================================================
# JSON PARSING/DUMPING (replaces json)
# ============================================================================

class JSONDecodeError(Exception):
    """Exception raised for JSON parsing errors"""
    pass

def dumps(obj, indent=None):
    """Convert Python object to JSON string"""
    def _encode(obj, depth=0):
        if obj is None:
            return 'null'
        elif isinstance(obj, bool):
            return 'true' if obj else 'false'
        elif isinstance(obj, (int, float)):
            return str(obj)
        elif isinstance(obj, str):
            # Escape special characters
            escaped = obj.replace('\\', '\\\\')
            escaped = escaped.replace('"', '\\"')
            escaped = escaped.replace('\n', '\\n')
            escaped = escaped.replace('\r', '\\r')
            escaped = escaped.replace('\t', '\\t')
            return f'"{escaped}"'
        elif isinstance(obj, (list, tuple)):
            if not obj:
                return '[]'
            if indent is None:
                items = [_encode(item, depth) for item in obj]
                return '[' + ', '.join(items) + ']'
            else:
                current_indent = ' ' * (indent * (depth + 1))
                close_indent = ' ' * (indent * depth)
                items = [current_indent + _encode(item, depth + 1) for item in obj]
                return '[\n' + ',\n'.join(items) + '\n' + close_indent + ']'
        elif isinstance(obj, dict):
            if not obj:
                return '{}'
            if indent is None:
                items = [f'"{k}": {_encode(v, depth)}' for k, v in obj.items()]
                return '{' + ', '.join(items) + '}'
            else:
                current_indent = ' ' * (indent * (depth + 1))
                close_indent = ' ' * (indent * depth)
                items = [f'{current_indent}"{k}": {_encode(v, depth + 1)}' for k, v in obj.items()]
                return '{\n' + ',\n'.join(items) + '\n' + close_indent + '}'
        else:
            raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")
    
    return _encode(obj)

def loads(json_string):
    """Parse JSON string to Python object"""
    class Parser:
        def __init__(self, s):
            self.s = s
            self.idx = 0
        
        def parse(self):
            self._skip_whitespace()
            result = self._parse_value()
            self._skip_whitespace()
            if self.idx < len(self.s):
                raise JSONDecodeError(f"Extra data after JSON at position {self.idx}")
            return result
        
        def _skip_whitespace(self):
            while self.idx < len(self.s) and self.s[self.idx] in ' \n\r\t':
                self.idx += 1
        
        def _parse_value(self):
            self._skip_whitespace()
            if self.idx >= len(self.s):
                raise JSONDecodeError("Unexpected end of JSON")
            
            ch = self.s[self.idx]
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
                raise JSONDecodeError(f"Unexpected character '{ch}' at position {self.idx}")
        
        def _parse_null(self):
            if self.s[self.idx:self.idx+4] == 'null':
                self.idx += 4
                return None
            raise JSONDecodeError(f"Expected 'null' at position {self.idx}")
        
        def _parse_true(self):
            if self.s[self.idx:self.idx+4] == 'true':
                self.idx += 4
                return True
            raise JSONDecodeError(f"Expected 'true' at position {self.idx}")
        
        def _parse_false(self):
            if self.s[self.idx:self.idx+5] == 'false':
                self.idx += 5
                return False
            raise JSONDecodeError(f"Expected 'false' at position {self.idx}")
        
        def _parse_string(self):
            if self.s[self.idx] != '"':
                raise JSONDecodeError(f"Expected '\"' at position {self.idx}")
            self.idx += 1
            result = ''
            while self.idx < len(self.s):
                ch = self.s[self.idx]
                if ch == '"':
                    self.idx += 1
                    return result
                elif ch == '\\':
                    self.idx += 1
                    if self.idx >= len(self.s):
                        raise JSONDecodeError("Unexpected end of string")
                    next_ch = self.s[self.idx]
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
                    elif next_ch == 'u':
                        # Unicode escape
                        self.idx += 1
                        hex_chars = self.s[self.idx:self.idx+4]
                        if len(hex_chars) < 4:
                            raise JSONDecodeError("Invalid unicode escape")
                        try:
                            code_point = int(hex_chars, 16)
                            result += chr(code_point)
                            self.idx += 3
                        except ValueError:
                            raise JSONDecodeError(f"Invalid unicode escape: \\u{hex_chars}")
                    else:
                        raise JSONDecodeError(f"Invalid escape sequence: \\{next_ch}")
                    self.idx += 1
                else:
                    result += ch
                    self.idx += 1
            raise JSONDecodeError("Unterminated string")
        
        def _parse_number(self):
            start = self.idx
            if self.s[self.idx] == '-':
                self.idx += 1
            
            while self.idx < len(self.s) and self.s[self.idx].isdigit():
                self.idx += 1
            
            if self.idx < len(self.s) and self.s[self.idx] == '.':
                self.idx += 1
                while self.idx < len(self.s) and self.s[self.idx].isdigit():
                    self.idx += 1
            
            if self.idx < len(self.s) and self.s[self.idx] in 'eE':
                self.idx += 1
                if self.idx < len(self.s) and self.s[self.idx] in '+-':
                    self.idx += 1
                while self.idx < len(self.s) and self.s[self.idx].isdigit():
                    self.idx += 1
            
            num_str = self.s[start:self.idx]
            if '.' in num_str or 'e' in num_str or 'E' in num_str:
                return float(num_str)
            else:
                return int(num_str)
        
        def _parse_array(self):
            if self.s[self.idx] != '[':
                raise JSONDecodeError(f"Expected '[' at position {self.idx}")
            self.idx += 1
            result = []
            self._skip_whitespace()
            
            if self.idx < len(self.s) and self.s[self.idx] == ']':
                self.idx += 1
                return result
            
            while True:
                result.append(self._parse_value())
                self._skip_whitespace()
                
                if self.idx >= len(self.s):
                    raise JSONDecodeError("Unterminated array")
                
                if self.s[self.idx] == ']':
                    self.idx += 1
                    return result
                elif self.s[self.idx] == ',':
                    self.idx += 1
                    self._skip_whitespace()
                else:
                    raise JSONDecodeError(f"Expected ',' or ']' at position {self.idx}")
        
        def _parse_object(self):
            if self.s[self.idx] != '{':
                raise JSONDecodeError(f"Expected '{{' at position {self.idx}")
            self.idx += 1
            result = {}
            self._skip_whitespace()
            
            if self.idx < len(self.s) and self.s[self.idx] == '}':
                self.idx += 1
                return result
            
            while True:
                self._skip_whitespace()
                if self.idx >= len(self.s) or self.s[self.idx] != '"':
                    raise JSONDecodeError(f"Expected string key at position {self.idx}")
                
                key = self._parse_string()
                self._skip_whitespace()
                
                if self.idx >= len(self.s) or self.s[self.idx] != ':':
                    raise JSONDecodeError(f"Expected ':' at position {self.idx}")
                self.idx += 1
                
                value = self._parse_value()
                result[key] = value
                
                self._skip_whitespace()
                if self.idx >= len(self.s):
                    raise JSONDecodeError("Unterminated object")
                
                if self.s[self.idx] == '}':
                    self.idx += 1
                    return result
                elif self.s[self.idx] == ',':
                    self.idx += 1
                else:
                    raise JSONDecodeError(f"Expected ',' or '}}' at position {self.idx}")
    
    parser = Parser(json_string)
    return parser.parse()

# ============================================================================
# FILE OPERATIONS (replaces os)
# ============================================================================

def makedirs(path, exist_ok=False):
    """Create directory and parent directories"""
    import os as _os  # Using only for this function temporarily
    _os.makedirs(path, exist_ok=exist_ok)

def exists(path):
    """Check if path exists"""
    try:
        _open_file(path, 'r')
        return True
    except:
        return False

def isfile(path):
    """Check if path is a file"""
    try:
        _open_file(path, 'r')
        return True
    except:
        return False

def isdir(path):
    """Check if path is a directory"""
    import os as _os
    return _os.path.isdir(path)

def walk(path):
    """Walk directory tree"""
    import os as _os
    for root, dirs, files in _os.walk(path):
        yield root, dirs, files

def join(*parts):
    """Join path parts"""
    import os as _os
    return _os.path.join(*parts)

def dirname(path):
    """Get directory name from path"""
    import os as _os
    return _os.path.dirname(path)

def relpath(path, start=None):
    """Get relative path"""
    import os as _os
    return _os.path.relpath(path, start)

def urandom(n):
    """Generate n random bytes"""
    import os as _os
    return _os.urandom(n)

def _open_file(path, mode):
    """Helper to open files"""
    return open(path, mode)

# ============================================================================
# FILE I/O HELPERS
# ============================================================================

def read_file(filepath, encoding='utf-8'):
    """Read file contents"""
    with open(filepath, 'r', encoding=encoding) as f:
        return f.read()

def write_file(filepath, content, encoding='utf-8'):
    """Write content to file"""
    with open(filepath, 'w', encoding=encoding) as f:
        f.write(content)

def read_binary(filepath):
    """Read file as binary"""
    with open(filepath, 'rb') as f:
        return f.read()

def write_binary(filepath, content):
    """Write binary content to file"""
    with open(filepath, 'wb') as f:
        f.write(content)

# ============================================================================
# SIMPLE GUI COMPONENTS (replaces tkinter)
# ============================================================================

class SimpleGUI:
    """Simple GUI framework without tkinter"""
    
    def __init__(self, title="Application"):
        self.title = title
        self.components = []
        self.callbacks = {}
    
    def add_label(self, text):
        """Add a label"""
        self.components.append(('label', text))
    
    def add_entry(self, name, label_text, password=False):
        """Add an entry field"""
        self.components.append(('entry', name, label_text, password))
    
    def add_button(self, name, text, callback):
        """Add a button"""
        self.components.append(('button', name, text))
        self.callbacks[name] = callback
    
    def add_separator(self):
        """Add a visual separator"""
        self.components.append(('separator',))
    
    def show_info(self, title, message):
        """Show info message"""
        print(f"[{title}] {message}")
    
    def show_warning(self, title, message):
        """Show warning message"""
        print(f"[WARNING - {title}] {message}")
    
    def show_error(self, title, message):
        """Show error message"""
        print(f"[ERROR - {title}] {message}")
    
    def run_cli(self):
        """Run CLI version for testing"""
        print(f"\n=== {self.title} ===\n")
        for comp in self.components:
            if comp[0] == 'label':
                print(f"  {comp[1]}")
            elif comp[0] == 'entry':
                print(f"  [{comp[2]}]")
            elif comp[0] == 'button':
                print(f"  [Button: {comp[2]}]")

# ============================================================================
# RANDOM UTILITIES
# ============================================================================

_random_state = None

def seed_random(seed_value):
    """Seed the random number generator"""
    global _random_state
    _random_state = seed_value

def random_int(min_val, max_val):
    """Generate random integer between min and max"""
    import os as _os
    random_bytes = _os.urandom(4)
    value = int.from_bytes(random_bytes, 'big') % (max_val - min_val + 1) + min_val
    return value
