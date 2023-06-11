<div align="center">

<img src="./passwordmanager/img/cyber-crime.png" width="40%" height="40%" alt="logo" />
<h1>Password Manager</h1>
<h3>A simple desktop password management tool</h3>

</div>

The **Password Manager** is a simple windows desktop application that allows users to manage their passwords securely and easily. It uses [scrypt](https://en.wikipedia.org/wiki/Scrypt) password-based key derivation function from standard package [hashlib](https://docs.python.org/3/library/hashlib.html) for hashing the master password for each user of the app, and stores the hash value in a database. The password records to be managed are encrypted with unique salt using [Fernet](https://cryptography.io/en/latest/fernet/) from [cryptography](https://pypi.org/project/cryptography/) package.

## Screenshots

### Login / Signup Frame

![login](passwordmanager/img/screenshot%20-%20login.png)

### Password Entries Frame

![passwords](passwordmanager/img/screenshot%20-%20passwords.png)

## Features

- **Multiple** users can use the app, each with their own password and unique salt.
- Master password is hashed using **scrypt** and stored in database.
- Password records are encrypted with unique salt using `Fernet` from `cryptography` package.
- Records can be easily **searched** and **manipulated**.
- App can generate **random** passwords triggered by typing '[random]' in the password input box.

## Installation

1. Clone the repository to your local machine using `git clone https://github.com/Freedempire/PasswordManager.git`
2. Install the required dependencies using `pip install -r requirements.txt`
3. Run the app using `python pmapp.py`

## Basic Usage

1. Create a new user account by entering a new username and password then clicking on the "Sign Up" button and finish the password confirmation.
2. Log in to the app using your username and password then clicking on the "Log In" button.
3. To add a new password record, fill in the required details then click on the "Add" button.
4. To edit a password record, first double-click the record from the list and make modifications as you wish, finally click on the "Update" button.
5. To delete a password record, double-click the record from the list and then click on the "Delete" button.
6. To generate a random password, simply type in '[random]' in the Password input box of the details section, then press <kbd>Tab</kbd> or <kbd>Enter</kbd> to trigger the auto generation.
7. You can also use <kbd>Tab</kbd> or <kbd>Enter</kbd> to jump from one input box to the next while editing password entry.
8. The "Clear" button can be used to clear all inputs in the input boxes. It also clears the current selection status, i.e. the status shows which has been lastly double-clicked.

## Security

This app takes security seriously and implements several measures to ensure the safety of user data. The use of scrypt for hashing the master password and unique salt with Fernet for encrypting the password records provide strong protection against brute force and dictionary attacks. Additionally, the app does not store any plaintext passwords or the master key, further reducing the risk of data breaches.

## License

This project is licensed under the MIT License - see the [LICENSE](https://opensource.org/license/mit/) file for details.

Copyright © Freedempire. All rights reserved.
