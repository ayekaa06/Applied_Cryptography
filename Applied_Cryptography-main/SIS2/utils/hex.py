def hexlify(data):
    """Convert bytes to hex string"""
    if isinstance(data, str):
        data = data.encode('utf-8')
    result = ''
    for byte in data:
        result += '{:02x}'.format(byte)
    return result

def unhexlify(hex_string):
    """Convert hex string to bytes"""
    if isinstance(hex_string, bytes):
        hex_string = hex_string.decode('utf-8')
    hex_string = hex_string.strip()
    result = bytearray()
    for i in range(0, len(hex_string), 2):
        byte_val = int(hex_string[i:i+2], 16)
        result.append(byte_val)
    return bytes(result)