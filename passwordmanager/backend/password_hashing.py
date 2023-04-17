"""
Functions relating to master password hashing
"""

import hashlib
import os
# from typing import Union
from typing import Optional
import hmac 

# def hash_password(password: str, salt: Union[bytes, None] = None) -> tuple[bytes, bytes]:
def hash_password(password: str, salt: Optional[bytes] = None) -> tuple[bytes, bytes]:
    """
    Hash the provided password with a randomly-generated or provided salt and return the salt and hash.
    """
    # use os.urandom to generate random bytes from an OS-specific randomness source
    # salt should be about 16 or more bytes from a proper source, e.g. os.urandom()
    if salt is None:
        salt = os.urandom(32)
    password_hash = hashlib.scrypt(password.encode(), salt=salt, n=16384, r=8, p=1, dklen=32)
    return password_hash, salt

def is_correct_password(password_provided: str, password_hash_stored: bytes, salt_stored: bytes) -> bool:
    """
    Check wether a password provided by user while logging in, with previously stored password hash and salt.
    """
    # hmac.compare_digest uses an approach designed to prevent timing analysis by avoiding
    # content-based short circuiting behaviour, making it appropriate for cryptography
    return hmac.compare_digest(hash_password(password_provided, salt_stored)[0], password_hash_stored)

if __name__ == '__main__':
    password_hash, salt = hash_password('hello')
    print(password_hash)
    print(salt)
    assert is_correct_password('hello', password_hash, salt)
    assert not is_correct_password('hellooo', password_hash, salt)
    assert not is_correct_password('Tr0ub4dor&3', password_hash, salt)

