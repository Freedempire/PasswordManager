import os
import secrets
import hashlib
import json
import base64
from getpass import getpass
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def initial_menu():
    """
    Initial menu
    Password Manager level
    """
    print('-' * 60)
    print(f'{"Python Password Manger":^60}')
    print('1. New password manager')
    print('2. Enter password manager')
    print('3. Exit')
    print('-' * 60)


def main_menu(filename):
    """
    Main menu
    Inner password manager operations
    """
    print('-' * 60)
    print(f'{"Python Password Manager":^60}')
    print(f'{"current: " + os.path.basename(filename):>60}')
    print('1. Add password')
    print('2. Find password')
    print('3. Edit password')
    print('4. Delete password')
    print('5. Back')
    print('6. Exit')
    print('-' * 60)


def get_option(option_range):
    option = ''
    while option not in option_range:
        option = input('Enter the respective number: ')
    return option


def get_input(message, length=0, password=False):
    if password:
        info = getpass(prompt=message)
        while not info or len(info) < length:
            print(f'Password must be nonempty and length >= {length}!')
            info = getpass()
    else:
        print(message, end='')
        info = input()
        if length:
            while not info or len(info) < length:
                print(f'Input must be nonempty and length >= {length}!\nTry again: ', end='')
                info = input()
    return info


def create_new_manager(filename):
    """
    Create a new manager file according to the given filename/path
    Check if existed before creating
    :param filename: path to the new manager
    :return: password manager file
    """
    if os.path.isfile(filename):
        print('Warning! Existing manager found!')
        print('This will erase the old manager.')
        print('Do you want to continue? Y / N: ', end='')
        if input().lower() != 'y':
            return None
    try:
        return open(filename, 'w')
    except:
        print('Create new manager failed!')
        return None


def authenticate(master_password, salt, hash_value):
    return get_hash(master_password + salt) == hash_value


def generate_salt(n=32):
    # return a random byte string containing n bytes number of bytes
    return secrets.token_bytes(32)


def get_hash(bytes):
    # return hash in hexadecimal digits
    return hashlib.sha256(bytes).hexdigest()


def generate_password(length=16):
    valid_chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-$*()#@!%/'
    return ''.join(secrets.choice(valid_chars) for i in range(length))


def generate_key(master_password, salt, iteration=100000):
    """
    Generate key for fernet encryption, same key will be derived from the same password and salt
    """
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=iteration)
    return base64.urlsafe_b64encode(kdf.derive(master_password))


def add_pw():
    pass


def find_pw():
    pass


def edit_pw():
    pass


def delete_pw():
    pass


while True:
    initial_menu()
    option = get_option([str(i) for i in range(1, 4)])
    if option == '1':  # create new manager
        filename = get_input('Input filename for the new password manager: ', 4)
        pm = create_new_manager(filename)
        if pm:  # if created a new pm file
            # get master password from user and convert it to bytes with utf-8 by default
            master_password = get_input('Input the master password to the manager (length at least 8): ', 8,
                                        True).encode()
            salt = generate_salt()  # get salt in bytes
            hash_value = get_hash(master_password + salt)
            pm.write(salt.hex() + '\n')  # write salt in hex to first line of pm file
            pm.write(hash_value + '\n')  # write hash value in hex to the second line
            pm.close()
        else:
            continue  # back to initial menu if not created
    elif option == '2':  # enter existing one
        filename = get_input('The filename of your password manager: ', 4)
        if os.path.isfile(filename):
            with open(filename) as fp:
                salt = bytes.fromhex(fp.readline())
                hash_value = fp.readline().strip()
            for i in range(3):  # authenticate master password 3 times at most
                master_password = get_input('Enter your master password: ', 8, True).encode()
                if authenticate(master_password, salt, hash_value):
                    break
                print(f'Wrong password! Left times: {2 - i}')
            if i >= 3:  # i == 3 means not authenticated, back to initial menu
                continue
        else:
            print('No such manager!')
            continue
    elif option == '3':
        break  # exit the outer loop, terminate the program

    # get into a specific manager after creating or authenticating
    with open(filename, 'a+') as fp:
        while True:
            main_menu(filename)
            fernet_key = generate_key(master_password, salt)
            option = get_option([str(i) for i in range(1, 7)])
            if option == '1':       # add
                account = get_input('Account: ', 1)
                # generate a random password or get from user
                if get_input('Generate a random password? Y / N: ').lower() == 'y':
                    password = generate_password()
                    print(f'Your password: {password}')
                else:
                    password = get_input('Input your own password: ', 8)
                description = get_input('Description: ', 1)
                website = get_input('Website (optional): ')
                email = get_input('Email (optional): ')
                entry_json = json.dumps({'account': account, 'password': password, 'description': description,
                                         'website': website, 'email': email})
                # use fernet to encrypt json form of entry, write it to file in hex
                fp.write(Fernet(fernet_key).encrypt(entry_json.encode()).hex() + '\n')
            elif option == '2':     # find
                fp.seek(0, 0)       # change position to the start of file
                entries = fp.readlines()[2:]
                dicts = []
                for e in entries:
                    dicts.append(json.loads(Fernet(fernet_key).decrypt(bytes.fromhex(e)).decode()))
                print(*dicts, sep='\n')
            elif option == '3':     # edit
                # delete the old line, insert a new line
                break
            elif option == '4':     # delete
                # delete the designated line
                break
            elif option == '5':
                break
            elif option == '6':
                raise SystemExit  # exit the program from the inner loop
