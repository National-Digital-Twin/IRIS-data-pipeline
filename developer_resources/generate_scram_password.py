import base64
import hashlib
import os
import sys

def scramble_password(password):
    # Generate random salt
    salt = os.urandom(16)
    
    # Derive key using PBKDF2-HMAC-SHA256
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        4096,
        32
    )
    
    # Generate client key
    client_key = hashlib.sha256(key).digest()
    
    # Generate server key
    server_key = hashlib.sha256(key).digest()
    
    # Base64 encode the result
    encoded_result = (
        f'SCRAM-SHA-256$4096:{base64.b64encode(salt).decode()}'
        f'${base64.b64encode(client_key).decode()}:'
        f'{base64.b64encode(server_key).decode()}'
    )
    
    return encoded_result

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scram.py <password>")
        sys.exit(1)
    
    password = sys.argv[1]
    scrambled_password = scramble_password(password)
    print(scrambled_password)