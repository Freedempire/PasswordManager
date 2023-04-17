import sqlite3
import os
from backend.password_hashing import *
from backend.message_encrypting import *
import snowflake
from random import randint
from typing import Optional

class PMDatabase:
    def __init__(self) -> None:
        # only check if database exists and is connectable
        self._db_exists = os.path.isfile('pmd.db')
        try:
            self._con = sqlite3.connect('pmd.db')
        except Exception as e:
            raise RuntimeError('Failed to open database') from e
        else:
            if not self._db_exists:
                # create user table
                # CREATE TABLE IF NOT EXISTS user ...
                self._con.execute('''
                    CREATE TABLE user(
                        id INTEGER PRIMARY KEY,
                        username TEXT NOT NULL UNIQUE,
                        password BLOB NOT NULL,
                        salt BLOB NOT NULL,
                        timestamp REAL NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                # create password table
                self._con.execute('''
                    CREATE TABLE password(
                        id INTEGER PRIMARY KEY,
                        user_id INTEGER NOT NUll,
                        description TEXT NOT NULL,
                        site TEXT,
                        account_id TEXT NOT NULL,
                        password BLOB NOT NULL,
                        notes TEXT,
                        salt BLOB NOT NULL,
                        timestamp REAL NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES user(id)
                            ON UPDATE CASCADE
                            ON DELETE CASCADE
                    )
                ''')
                # create trigger for updating password entries
                # ref: https://www.sqlitetutorial.net/sqlite-trigger/
                #      https://stackoverflow.com/questions/6578439/on-update-current-timestamp-with-sqlite
                self._con.execute('''
                    CREATE TRIGGER password_updated
                    UPDATE OF salt ON password
                    BEGIN
                        UPDATE password SET timestamp = CURRENT_TIMESTAMP WHERE salt = old.salt;
                    END;
                ''')
            self._userinfo = dict()
            self._login = False


    def user_login(self, username: str, password: str) -> bool:
        """
        Log into the app with provided username and password.
        :return: True if log in successfully, otherwise False
        """
        # first check login status and user existence
        if (not self._login) and self.user_exists(username):
            res = self._con.execute('SELECT id, username, password, salt, timestamp FROM user WHERE username = ?', (username,)).fetchone()
            # check if password is correct
            if is_correct_password(password, res[2], res[3]):
                self._userinfo['userid'], self._userinfo['username'], *_, self._userinfo['usertimestamp'] = res
                self._userinfo['userpassword'] = password
                self._login = True
                return True
            else:
                return False
        else:
            return False
        
    def user_logout(self) -> None:
        self._userinfo = dict()
        self._login = False

    def add_new_user(self, username: str, password: str) -> bool:
        """
        Create a new user of the app.
        :return: True if add successfully, otherwise False
        """
        password_hash, salt = hash_password(password)
        try:
            with self._con:
                self._con.execute('INSERT INTO user(id, username, password, salt) VALUES(?, ?, ?, ?)',
                                  (generate_id(), username, password_hash, salt))
            return True
        except:
            return False
        
    def user_exists(self, username: str) -> bool:
        with self._con:
            res = self._con.execute('SELECT username FROM user WHERE username = ?', (username,)).fetchone()
        return False if res is None else True

    def user_authenticate(self, username: str, password: str) -> bool:
        """
        Check whether username and password match
        """
        with self._con:
            password_hash, salt = self._con.execute('SELECT password, salt FROM user WHERE username = ?', (username,)).fetchone()
        return is_correct_password(password, password_hash, salt)
     
    def get_all_users(self) -> list:
        with self._con:
            return self._con.execute('SELECT username FROM user').fetchall()

    def delete_user(self, username: str, password: str) -> bool:
        """
        Delete user after checking the password.
        """
        if self.user_authenticate(username, password):
            with self._con:
                self._con.execute('DELETE FROM user WHERE username = ?', (username,))
            return True
        else:
            return False
        
    def add_new_password(self, description: str, site: Optional[str], account_id: str, password: str, notes: Optional[str]) -> bool:
        """
        Add new entry in password table.
        """
        # first check login status
        if self._login:
            try:
                token, salt = encrypt_message(password, self._userinfo['userpassword'])
                with self._con:
                    self._con.execute('INSERT INTO password(id, user_id, description, site, account_id, password, notes, salt) VALUES(?, ?, ?, ?, ?, ?, ?, ?)',
                                      (generate_id(), self._userinfo['userid'], description, site, account_id, token, notes, salt))
                return True
            except:
                return False
        return False
        
    def show_all_passwords(self) -> Optional[list]:
        if self._login:
            with self._con:
                res = self._con.execute('SELECT id, description, site, account_id, password, notes, timestamp, salt FROM password WHERE user_id = ?', (self._userinfo['userid'],)).fetchall()
                self.decrypt_password(res)
            return res
        return None
    
    def search_password(self, keyword: str) -> Optional[list]:
        """
        Search keyword in columns (description, site, account_id, notes).
        """
        if self._login:
            with self._con:
                res = self._con.execute('''
                    SELECT id, description, site, account_id, password, notes, timestamp, salt FROM password
                    WHERE description LIKE ?1 OR site LIKE ?1 OR account_id LIKE ?1 OR notes LIKE ?1
                ''', ('%' + keyword + '%',)).fetchall()
            if len(res) > 0:
                self.decrypt_password(res)
            return res
        return None
        
    def update_password(self, id: int, description: str, site: Optional[str], account_id: str, password: str, notes: Optional[str]) -> Optional[bool]:
        """
        Update all the user-input info of a certain entry.
        The salt and timestamp will be changed automatically.
        """
        if self._login:
            token, salt = encrypt_message(password, self._userinfo['userpassword'])
            try:
                with self._con:
                    self._con.execute('''
                        UPDATE password SET
                            description = ?,
                            site = ?,
                            account_id = ?,
                            password = ?,
                            notes = ?,
                            salt = ?
                        WHERE id = ?
                    ''', (description, site, account_id, token, notes, salt, id))
                return True
            except:
                return False
        return None
    
    def delete_password(self, id: int) -> Optional[bool]:
        if self._login:
            try:
                with self._con:
                    self._con.execute('DELETE FROM password WHERE id = ?', (id,))
                return True
            except:
                return False
        return None
        
    def decrypt_password(self, res: list) -> list:
        """
        Decrypt the encrypted token in the result list.
        """
        for i in range(len(res)):
            # decrypt password in each row
            password = decrypt_message(res[i][4], self._userinfo['userpassword'], res[i][7])
            # slice the old tuple and concatenate the new value to replace the password hash
            res[i] = res[i][:4] + (password,) + res[i][5:]
        return res

def generate_id() -> int:
    """
    Generate a snowflake-style id.
    """
    return next(snowflake.SnowflakeGenerator(randint(1, 1023)))

if __name__ == '__main__':
    pmd = PMDatabase()
    print('all user: ', pmd.get_all_users())
    print('add user freedempire2: ', pmd.add_new_user('freedempire2', '12345'))
    print('all user: ', pmd.get_all_users())
    print('authenticate: ', pmd.user_authenticate('freedempire2', '12345'))
    # print('delete user freedempire2: ', pmd.delete_user('freedempire2', '12345'))
    # print('all user: ', pmd.get_all_users())
    print('login:', pmd.user_login('freedempire2', '12345'))
    # print(pmd.add_new_password('gmail', 'google.com', 'freedempire', '123456', 'gmail account'))
    # print(pmd.add_new_password('1gmaill', 'google.com gmail', 'tony', '1234567', '1gmail'))
    # print(pmd.add_new_password('gmail2', 'gmail', 'freedempire', '123456', 'gmail'))
    # print(pmd.add_new_password('trust wallet', 'trustwallet.com', 'djfkajlkfjlkdhi3uriu238473847837kdfdjfkj', '123456', 'trust wallet account'))
    # print(pmd.show_all_passwords())
    # print(pmd.search_password('trus'))
    # id = pmd._con.execute('SELECT id FROM password WHERE account_id = ?', ('freedempire',)).fetchone()[0]
    # print('id: ', id)
    # pmd.update_password(id, 'aaabcd', 'aaa.com', 'aaa_freedempire', '1234565', 'updatedd')
    print(pmd.show_all_passwords())
    # pmd.delete_password(id)
    # print(pmd.show_all_passwords())


    


