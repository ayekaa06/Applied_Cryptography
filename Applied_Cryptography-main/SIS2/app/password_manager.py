from app.file_integrity import read_text_file, write_text_file, file_exists, _json_escape, _json_encode, _json_parse
from utils.hex import hexlify, unhexlify
from utils.random import _urandom
from crypto_core.sha256 import SHA256
from crypto_core.hmac import hmac_sha256
from crypto_core.pbkdf2 import pbkdf2
import os


def _makedirs(path):
    """Create directory"""
    try:
        os.makedirs(path, exist_ok=True)
    except Exception as e:
        print(f"Warning: Could not create directory {path}: {e}")


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
        "salt": hexlify(salt),
        "hash": hexlify(derived_key),
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
    salt = unhexlify(entry["salt"])
    stored_hash = unhexlify(entry["hash"])
    iterations = entry.get("iterations", 120000)

    computed = pbkdf2(password, salt, iterations, 32)

    if computed == stored_hash:
        return True, "Password correct"
    else:
        return False, "Incorrect password"

# console test
if __name__ == "__main__":
    print("Testing password manager...")
    store_password("alice", "secret123")
    success, msg = verify_password("alice", "secret123")
    print(f"Verify correct: {success} → {msg}")
    success, msg = verify_password("alice", "wrong")
    print(f"Verify wrong: {success} → {msg}")