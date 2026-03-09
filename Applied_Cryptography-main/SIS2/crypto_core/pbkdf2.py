from crypto_core.hmac import hmac_sha256

def pbkdf2(password, salt, iterations, dk_len):
    if isinstance(password, str): password = password.encode()
    if isinstance(salt, str): salt = salt.encode()
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

# Usage: key = pbkdf2('password', os.urandom(16), 100000, 32)