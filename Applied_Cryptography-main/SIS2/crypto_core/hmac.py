from crypto_core.sha256 import SHA256

def hmac_sha256(key, message):
    sha = SHA256()
    block_size = 64

    if isinstance(key, str):
        key = key.encode('utf-8')
    if isinstance(message, str):
        message = message.encode('utf-8')

    if len(key) > block_size:
        key = bytes.fromhex(sha.hash(key))

    if len(key) < block_size:
        key += b'\x00' * (block_size - len(key))

    ipad = bytes((x ^ 0x36) for x in key)
    opad = bytes((x ^ 0x5C) for x in key)

    inner_hash_hex = sha.hash(ipad + message)
    inner_hash_bytes = bytes.fromhex(inner_hash_hex)

    outer_hash_hex = sha.hash(opad + inner_hash_bytes)
    return bytes.fromhex(outer_hash_hex)
# Usage: tag = hmac_sha256(b'mykey', b'message').hex()