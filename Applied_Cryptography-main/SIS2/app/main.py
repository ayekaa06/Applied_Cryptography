from crypto_core.sha256 import SHA256
from crypto_core.hmac import hmac_sha256
from crypto_core.pbkdf2 import pbkdf2
from crypto_core.hkdf import hkdf, hkdf_extract
from utils.random import _urandom
from utils.hex import hexlify, unhexlify
from app.file_integrity import create_manifest, verify_manifest
from app.password_manager import store_password, verify_password

def show_menu():
    """Display main menu"""
    print("\n" + "="*60)
    print("   SHA-256 Cryptographic Tools")
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
    def _looks_like_hex(s):
        if len(s) % 2 != 0:
            return False
        for ch in s:
            if ch not in "0123456789abcdefABCDEF":
                return False
        return True
    print("\n--- HMAC Tool ---")
    key_input = input("Enter key (hex or text): ").strip()
    msg = input("Enter message (text): ").strip()
    
    if not key_input or not msg:
        print("Missing input")
        return
    
    if _looks_like_hex(key_input):
        key = unhexlify(key_input)
    elif key_input.startswith(('0x', '0X')):
        key = unhexlify(key_input[2:])
    else:
        key = key_input.encode('utf-8')

    message = msg.encode('utf-8')
    tag = hmac_sha256(key, message)
    print(f"HMAC Tag: {tag.hex()}")
    
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
        print("saving...")
        success = store_password(username, password)
        if success:
            print("✓ Password stored successfully")
        else:
            print("✗ Username already exists")

    elif choice == '2':
        username = input("Enter username: ").strip()
        password = input("Enter password: ").strip()

        if not username or not password:
            print("Missing input")
            return

        success, msg = verify_password(username, password)
        if success:
            print(f"✓ {msg}")
        else:
            print(f"✗ {msg}")

    else:
        print("Invalid option")

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
            prk = hkdf_extract(salt, ikm)
            okm = hkdf(salt, ikm, info.encode('utf-8'), length)
            print(f"PRK (hex): {hexlify(prk)}")
            print(f"OKM (hex): {hexlify(okm)}")
        except Exception as e:
            print(f"Error: {e}")

def file_integrity():
    """File integrity tool"""
    print("\n--- File Integrity Tool ---")
    print("1. Create manifest")
    print("2. Verify manifest")
    choice = input("Select: ").strip()
    
    if choice == '1':
        create_manifest()
    elif choice == '2':
        verify_manifest()
    else:
        print("Invalid option")
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