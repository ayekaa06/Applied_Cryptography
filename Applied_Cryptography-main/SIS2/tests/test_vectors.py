from crypto_core.sha256 import SHA256
from crypto_core.hmac import hmac_sha256
from crypto_core.pbkdf2 import pbkdf2
from crypto_core.hkdf import hkdf
from utils.random import _urandom
from utils.hex import hexlify, unhexlify


def test_sha256():
    """Test SHA256 with known test vectors"""
    sha = SHA256()
    
    result = sha.hash("abc")
    expected = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    assert result == expected, f"Test 1 failed: {result} != {expected}"
    print("✓ Test 1 passed: SHA256('abc')")
    
    result = sha.hash("")
    expected = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    assert result == expected, f"Test 2 failed: {result} != {expected}"
    print("✓ Test 2 passed: SHA256('')")
    
    result = sha.hash("abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq")
    expected = "248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1"
    assert result == expected, f"Test 3 failed: {result} != {expected}"
    print("✓ Test 3 passed: SHA256('abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq')")
    
    print("\nAll SHA256 tests passed!")

def test_hmac():
    """Test HMAC-SHA256"""
    
    key = bytes.fromhex("0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b")
    msg = b"Hi There"
    result = hmac_sha256(key, msg)

    expected = bytes.fromhex("b0344c61d8db38535ca8afceaf0bf12b881dc200c9833da726e9376c2e32cff7")
    
    assert result == expected, f"HMAC test failed: {result} != {expected}"
    print("✓ HMAC-SHA256 test passed")

def test_pbkdf2():
    """Test PBKDF2"""
    
    password = "password"
    salt = b"salt"
    result = pbkdf2(password, salt, 1, 20)
    expected = bytes.fromhex("120fb6cffcf8b32c43e7225256c4f837a86548c9")

    assert len(result) == 20, f"PBKDF2 length test failed: {len(result)} != 20"
    assert isinstance(result, bytes), "PBKDF2 should return bytes"
    assert result == expected, f"HMAC test failed: {result} != {expected}"
    print("✓ PBKDF2 test passed")

def test_hkdf():
    ikm = bytes.fromhex("0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b")  
    salt = bytes.fromhex("000102030405060708090a0b0c")
    info = bytes.fromhex("f0f1f2f3f4f5f6f7f8f9")
    length = 42

    result = hkdf(salt, ikm, info, length)
    expected = bytes.fromhex(
        "3cb25f25faacd57a90434f64d0362f2a"
        "2d2d0a90cf1a5a4c5db02d56ecc4c5bf"
        "34007208d5b887185865"
    )

    assert result == expected
    print("✓ HKDF test passed")

if __name__ == "__main__":
    print("Running cryptographic test vectors...\n")
    test_sha256()
    test_hmac()
    test_pbkdf2()
    test_hkdf()
    print("\n✓ All tests pass!")