from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter import simpledialog
from tkinter import ttk
import ctypes
import secrets
import hashlib
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def ishex(string):
    """
    Check whether string is hexadecimal
    """
    for c in string:
        if c.lower() not in '0123456789abcdef':
            return False
    return True


def validate_pm(fp):
    """
    Check whether the chosen file is a valid .pm file
    :param fp: file pointer to the chosen file
    :return: a tuple of salt and hash value if valid, empty strings otherwise
    """
    info = []
    for i in range(2):
        try:
            temp = fp.readline()[:-1]  # strip the trailing newline character
            if len(temp) == 64 and ishex(temp): # 32 bytes have 64 hexidigits
                info.append(temp)
            else:
                return '', ''
        except:
            print('Error Occurred when reading .pm file.')
    return tuple(info)


def authenticate(master_password, salt, hash_value):
    return get_hash(master_password + salt) == hash_value


def get_hash(bytes):
    # return hash in hexadecimal digits
    return hashlib.sha256(bytes).hexdigest()


def generate_salt(n=32):
    # return a random byte string containing n bytes number of bytes
    return secrets.token_bytes(32)


def generate_key(master_password, salt, iteration=100000):
    """
    Generate key for fernet encryption, same key will be derived from the same password and salt
    """
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=iteration)
    return base64.urlsafe_b64encode(kdf.derive(master_password))


def generate_password(length=16):
    valid_chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-$*()#@!%/'
    return ''.join(secrets.choice(valid_chars) for i in range(length))


def decrypt_records(records, fernet_key):
    decrypted = []
    for record in records:
        decrypted.append([base64.b64decode(item.encode()).decode() for item in
                          Fernet(fernet_key).decrypt(bytes.fromhex(record[:-1])).decode().split(',')])
    return decrypted


def encrypt_record(info, fernet_key):
    """
    each item in info tuple is converted as follows:
        encoded to bytes
        => base64 bytes
        => join together with b','
        => encrypt with fernet_key
        => converted the encrypted bytes to hex string
    :return: the encrypted hex string
    """
    # if use csv format data, then no need of converting to base64 first
    # regex: "(?:^|,)(?=[^"]|(")?)"?((?(1)[^"]*|[^,"]*))"?(?=,|$)"
    return Fernet(fernet_key).encrypt(b','.join(base64.b64encode(item.encode()) for item in info)).hex()


class PasswordDialog(simpledialog.Dialog):
    def __init__(self, title, prompt, parent=None, entries=1):
        self.prompt = prompt
        self.entries = entries
        simpledialog.Dialog.__init__(self, parent, title)

    def body(self, master):
        Label(master, text=self.prompt, font='Arial 32', width=30).grid(row=0, padx=5, pady=10)
        self.entry = Entry(master, font='Arial 28', show='*', width=40)
        self.entry.grid(row=1, padx=5, pady=10, ipady=10)
        if self.entries == 2:
            self.entry2 = Entry(master, font='Arial 28', show='*', width=40)
            self.entry2.grid(row=2, padx=5, pady=10, ipady=10)
        return self.entry

    def buttonbox(self):
        box = Frame(self)
        Button(box, text="OK", width=10, command=self.ok, default=ACTIVE, font='Arial 20').pack(side=LEFT, padx=28,
                                                                                                pady=20)
        Button(box, text="Cancel", width=10, command=self.cancel, font='Arial 20').pack(side=LEFT, padx=28, pady=20)
        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)
        box.pack()

    def validate(self):
        """
        Override validate(), makes it always valid for non-empty value in entry
        :return: string value of entry
        """
        if self.entries == 2 and self.entry.get() != self.entry2.get():
            messagebox.showwarning('Warning', 'Passwords dosen\'t match.')
            self.entry.delete(0, END)
            self.entry2.delete(0, END)
            self.entry.focus()
            return 0
        result = self.entry.get()
        if not result:
            messagebox.showwarning('Warning', 'Master password can\'t be empty, try again.', parent=self)
            return 0
        self.result = result
        return 1

    def destroy(self):
        self.entry = None
        simpledialog.Dialog.destroy(self)


class InitialFrame(Frame):
    """
    The initial frame when starting the app
    """

    def __init__(self, master):
        self.master = master
        super().__init__(master)
        self.grid()
        Label(self, text="Password Manager", font='Arial 36').grid(row=0, column=0, columnspan=2, padx=70, pady=20)
        Button(self, text='Open', command=self.open_pm, width=10, font='Arial 20').grid(row=1, column=0, padx=10,
                                                                                        pady=20, sticky='E')
        Button(self, text='New', command=self.new_pm, width=10, font='Arial 20').grid(row=1, column=1, padx=10, pady=20,
                                                                                      sticky='W')

    def open_pm(self):
        pm = filedialog.askopenfile(filetypes=(('password manager file', '.pm'),))
        if pm:
            salt, hash_value = validate_pm(pm)
            # convert salt from hex string to bytes
            salt = bytes.fromhex(salt)
            if salt and hash_value:
                # print('Valid pm file.')
                # simpledialog.askstring('Input', 'Input the master password to this manager:')
                passwordDiaglog = PasswordDialog('Master Password', 'Input your master password:')
                if passwordDiaglog.result:
                    master_password = passwordDiaglog.result.encode()
                    if not authenticate(master_password, salt, hash_value):
                        messagebox.showerror('Error', "Wrong master password.")
                    else:
                        fernet_key = generate_key(master_password, salt)
                        records = decrypt_records(pm.readlines(), fernet_key)
                        # enter frame for manipulate entries
                        OperationFrame(self.master, pm.name, fernet_key, records)
                        self.master.title('Password Manager: ' + os.path.basename(pm.name))
                        self.destroy()
            else:
                messagebox.showerror('Error', 'Invalid pm file, please choose another file.')
            pm.close()

    def new_pm(self):
        pm = filedialog.asksaveasfile(defaultextension='.pm', filetypes=(('password manager file', '.pm'),))
        if pm:
            passwordDiaglog = PasswordDialog('Master Password', 'Set your master password:', entries=2)
            if passwordDiaglog.result:
                master_password = passwordDiaglog.result.encode()
                salt = generate_salt()
                hash_value = get_hash(master_password + salt)
                pm.write(salt.hex() + '\n')  # write salt in hex to first line of pm file
                pm.write(hash_value + '\n')  # write hash value in hex to the second line

                # start a new frame for manipulate entries
                fernet_key = generate_key(master_password, salt)
                OperationFrame(self.master, pm.name, fernet_key, [])
                self.master.title('Password Manager: ' + os.path.basename(pm.name))
                self.destroy()
            pm.close()


class OperationFrame(Frame):
    """
    The frame for CRUD operations
    """

    def __init__(self, master, pm_path, fernet_key, records):
        self.master = master
        self.pm_path = pm_path
        self.fernet_key = fernet_key
        self.records = records
        super().__init__(master)
        self.grid()

        # first line search and view all
        self.search_entry = Entry(self, font='Consolas 20', width=36)
        self.search_entry.grid(row=0, column=0, columnspan=2, padx=5, pady=20, ipady=10, sticky='E')
        self.search_button = Button(self, text='Search', command=self.search, width=10, font='Arial 20')
        self.search_button.grid(row=0, column=2, padx=5, pady=20)
        self.viewall_button = Button(self, text='View All', command=self.viewall, width=10, font='Arial 20')
        self.viewall_button.grid(row=0, column=3, padx=5, pady=20)
        # bind search_entry with enter key
        self.search_entry.bind('<Return>', self.search_event)

        # second group for add and edit a single entry
        Label(self, text="Account", font='Arial 20').grid(row=1, column=0, padx=5, pady=5)
        self.account_entry = Entry(self, font='Consolas 20', width=42)
        self.account_entry.grid(row=1, column=1, columnspan=3, padx=5, pady=5, ipady=10)
        Label(self, text="Password", font='Arial 20').grid(row=2, column=0, padx=5, pady=5)
        self.password_text = Text(self, font='Consolas 20', width=42, height=3)
        self.password_text.grid(row=2, column=1, columnspan=3, padx=5, pady=5, ipady=10)
        Label(self, text="Description", font='Arial 20').grid(row=3, column=0, padx=5, pady=5)
        self.description_entry = Entry(self, font='Consolas 20', width=42)
        self.description_entry.grid(row=3, column=1, columnspan=3, padx=5, pady=5, ipady=10)
        Label(self, text="Website", font='Arial 20').grid(row=4, column=0, padx=5, pady=5)
        self.website_entry = Entry(self, font='Consolas 20', width=42)
        self.website_entry.grid(row=4, column=1, columnspan=3, padx=5, pady=5, ipady=10)
        Label(self, text="Email", font='Arial 20').grid(row=5, column=0, padx=5, pady=5)
        self.email_entry = Entry(self, font='Consolas 20', width=42)
        self.email_entry.grid(row=5, column=1, columnspan=3, padx=5, pady=5, ipady=10)
        # buttons
        self.switch_button = Button(self, text='Switch PM', command=self.switch_pm, width=10, font='Arial 20')
        self.switch_button.grid(row=6, column=0, padx=5, pady=5, sticky='E')
        self.delete_button = Button(self, text='Delete', command=self.delete, width=10, font='Arial 20',
                                    state='disabled')
        self.delete_button.grid(row=6, column=1, padx=5, pady=5, sticky='E')
        self.add_button = Button(self, text='Add', command=self.add, width=10, font='Arial 20')
        self.add_button.grid(row=6, column=2, padx=5, pady=5)
        self.edit_button = Button(self, text='Edit', command=self.edit, width=10, font='Arial 20', state='disabled')
        self.edit_button.grid(row=6, column=3, padx=5, pady=5)

        style = ttk.Style()
        style.configure('Treeview', font=('Consolas', 20), rowheight=40)
        style.configure('Treeview.Heading', font=('Arial', 20, 'bold'))
        columns = ('Account', 'Password', 'Description', 'Website', 'Email')
        self.entries_treeview = ttk.Treeview(self, columns=columns, show='headings', style='Treeview')
        for column in columns:
            self.entries_treeview.heading(column, text=column)
            self.entries_treeview.column(column, minwidth=0, width=180)
        self.entries_treeview.grid(row=7, column=0, columnspan=4, padx=5, pady=20)
        self.entries_treeview.bind('<Double-1>', self.load_details)

    def search(self):
        text = self.search_entry.get()
        if text:
            results = []
            for record in self.records:
                for i in range(len(record)):
                    if i != 1 and text in record[i]:
                        results.append(record)
                        continue
            if results:
                self.viewall(results)
            else:
                messagebox.showinfo('Info', 'Nothing Found.')

    def viewall(self, records=None):
        # delete all entires first
        self.entries_treeview.delete(*self.entries_treeview.get_children())
        if records:
            # insert from records
            for record in records:
                self.entries_treeview.insert('', 'end', values=record)
        else:
            # insert from self.records
            for record in self.records:
                self.entries_treeview.insert('', 'end', values=record)

    def add(self):
        inputs = self.get_inputs()
        # check if account, password, and description are not empty before add new entry
        if inputs:
            # append to the treeview
            self.entries_treeview.insert('', 'end', values=inputs)
            # append to the pm file
            with open(self.pm_path, 'a+') as pm:
                pm.write(encrypt_record(inputs, self.fernet_key) + '\n')
                pm.seek(0)
                # update self.records after adding new entry
                self.records = decrypt_records(pm.readlines()[2:], self.fernet_key)
            # clear inputs from widgets after added
            self.clear_inputs()
            self.edit_button['state'] = 'disabled'
            self.delete_button['state'] = 'disabled'

    def edit(self):
        inputs = self.get_inputs()
        if inputs:
            with open(self.pm_path, 'r+') as pm:
                lines = pm.readlines()
                # replace the target line with new encrypted inputs
                lines[self.row_num + 2] = encrypt_record(inputs, self.fernet_key) + '\n'
                pm.seek(0)
                pm.writelines(lines)
                pm.truncate()
                pm.seek(0)
                # update self.records after editing new entry
                self.records = decrypt_records(pm.readlines()[2:], self.fernet_key)
            self.viewall()
            self.clear_inputs()
            # disable edit button after edited
            self.edit_button['state'] = 'disabled'
            # disable delete button after edited
            self.delete_button['state'] = 'disabled'

    def delete(self):
        with open(self.pm_path, 'r+') as pm:
            lines = pm.readlines()
            # replace the target line with new encrypted inputs
            del lines[self.row_num + 2]
            pm.seek(0)
            pm.writelines(lines)
            pm.truncate()
            pm.seek(0)
            # update self.records after deleting entry
            self.records = decrypt_records(pm.readlines()[2:], self.fernet_key)
        self.viewall()
        # disable delete button after deleted
        self.delete_button['state'] = 'disabled'
        # disable edit button after deleted
        self.edit_button['state'] = 'disabled'

    def switch_pm(self):
        InitialFrame(app)
        self.destroy()

    def get_inputs(self):
        account = self.account_entry.get()
        password = self.password_text.get('1.0', 'end-1c')
        # generate random password, if password=='[random]'
        if password == '[random]':
            password = generate_password()
        description = self.description_entry.get()
        website = self.website_entry.get()
        email = self.email_entry.get()
        if not (account and password and description):
            messagebox.showwarning('Warning', 'Account, password, and description can\'t be empty.')
            return None
        return account, password, description, website, email

    def clear_inputs(self):
        self.account_entry.delete(0, END)
        self.password_text.delete('1.0', END)
        self.description_entry.delete(0, END)
        self.website_entry.delete(0, END)
        self.email_entry.delete(0, END)
        self.account_entry.focus()

    def search_event(self, event):
        self.search()

    def load_details(self, event):
        selection = self.entries_treeview.selection()
        if selection:
            # get id of selected row
            selected = selection[0]
            # get row number of selected row, start from 1
            self.row_num = self.entries_treeview.index(selected)
            # get values from selected item
            values = self.entries_treeview.item(selected, 'values')
            # first clear all inputs from entries and textbox
            self.clear_inputs()
            # then load details to entries and textbox
            self.account_entry.insert(0, values[0])
            self.password_text.insert('1.0', values[1])
            self.description_entry.insert(0, values[2])
            self.website_entry.insert(0, values[3])
            self.email_entry.insert(0, values[4])
            # enable edit button
            self.edit_button['state'] = 'normal'
            # enable delete button
            self.delete_button['state'] = 'normal'


if __name__ == '__main__':
    app = Tk()

    # set the position when start the app
    # app.geometry(f'+{app.winfo_screenwidth() // 2 - app.winfo_reqwidth() // 2}+{app.winfo_screenheight() // 3 - app.winfo_reqheight() // 2}')

    # set DPI awareness to 2 which will adjust the scale factor whenever DPI changes
    ctypes.windll.shcore.SetProcessDpiAwareness(2)

    # Disable resize window from both x and y axis
    app.resizable(False, False)

    app.title('Password Manager')
    pm_filename = ''
    InitialFrame(app)
    app.mainloop()
