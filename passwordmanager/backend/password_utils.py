"""
Functions relating to password generating, password strength checking
"""

import string
import secrets
import random

PASSWORD_CHARS_UPPERS = string.ascii_uppercase
PASSWORD_CHARS_LOWERS = string.ascii_lowercase
PASSWORD_CHARS_DIGITS = string.digits
PASSWORD_CHARS_SYMBOLS = string.punctuation
PASSWORD_CHARS = (PASSWORD_CHARS_UPPERS, PASSWORD_CHARS_LOWERS, PASSWORD_CHARS_DIGITS, PASSWORD_CHARS_SYMBOLS)
PASSWORD_LEN = 16

def generate_password(characters: tuple = PASSWORD_CHARS, length: int = PASSWORD_LEN) -> str:
    """
    Generate a random password with at least one character from each category in provided password character tuple. 
    """
    password_chars = []
    # First, get one random character from each category in characters so that the final password contains characters from all categories.
    for char_category in characters:
        # secrets.choice(sequence) returns a randomly chosen element from a non-empty sequence.
        password_chars.append(secrets.choice(char_category))
    # Second, get the rest characters.
    password_chars += [secrets.choice(secrets.choice(characters)) for i in range(length - len(password_chars))]
    # Third, shuffle the password_chars list in place.
    random.shuffle(password_chars)
    return ''.join(password_chars)

def check_password_strength(password: str) -> bool:
    pass

if __name__ == '__main__':
    print(generate_password())
