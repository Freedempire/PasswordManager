"""
Functions relating to encrypting messages
"""

from cryptography.fernet import Fernet
from typing import Optional
from backend.password_hashing import hash_password
import os
import base64

def generate_key(master_password: str, salt: Optional[bytes] = None) -> tuple[bytes, bytes]:
    """
    Generate key from master_password and salt (if not already exists in database) for further encryption / decryption.
    :return: a tuple of salt and hash value as the key
    """
    if salt is None:
        salt = os.urandom(32)
    # get the hash and convert it to a URL-safe base64-encoded 32-byte key to suit Fernet's requirement
    key = base64.urlsafe_b64encode(hash_password(master_password, salt)[0])
    return key, salt

def encrypt_message(message: str, master_password: str) -> tuple[bytes, bytes]:
    """
    Encrypt message with master_password and unique salt.
    :return: a tuple of salt and encrypted token
    """
    key, salt = generate_key(master_password)
    return Fernet(key).encrypt(message.encode()), salt

def decrypt_message(token: bytes, master_password: str, salt: bytes) -> Optional[str]:
    """
    Decrypt token with master_password and salt.
    :return: message decrypted
    """
    key = generate_key(master_password, salt)[0]
    try:
        return Fernet(key).decrypt(token).decode()
    except:
        # if exception shows up during decryption, return None
        return None

if __name__ == '__main__':
    token, salt = encrypt_message('play the world', 'hello')
    message = decrypt_message(token, 'hello', salt)
    print(salt, token, message)

