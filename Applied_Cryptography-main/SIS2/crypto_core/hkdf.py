from crypto_core.hmac import hmac_sha256

def hkdf_extract(salt, ikm):
    if salt is None: salt = b'\x00' * 32
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

# Usage: key = hkdf(b'salt', b'ikm', b'info', 42)