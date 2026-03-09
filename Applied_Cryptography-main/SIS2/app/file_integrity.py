from crypto_core.sha256 import SHA256
# File and Directory Operations

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

# JSON Implementation


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


# File Integrity Functions


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
    print("Enter folder path to create manifest for:")
    folder = input().strip()
    
    if not folder:
        print("Cancelled")
        return

    manifest = {}
    try:
        for root, dirs, files in walk_directory(folder):
            for filename in files:
                if filename.endswith(MANIFEST_EXT):
                    continue
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

    ok_count = 0
    tampered_count = 0
    missing_count = 0
    
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
                missing_count += 1
                continue
            
            current_hash = compute_file_hash(fullpath)
            if current_hash == expected_hash:
                results.append(f"OK: {relpath}")
                ok_count += 1
            else:
                results.append(f"TAMPERED: {relpath} (expected {expected_hash[:12]}..., got {current_hash[:12]}...)")
                tampered_count += 1
        
        for line in results[:30]:
            print(line)
        if len(results) > 30:
            print(f"... and {len(results)-30} more")
        print("\nSummary:")
        print(f"OK: {ok_count}")
        print(f"TAMPERED: {tampered_count}")
        print(f"MISSING: {missing_count}")
        
    except Exception as e:
        print(f"Error: {e}")