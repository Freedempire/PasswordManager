from tkinter import *
from tkinter import messagebox
import ctypes

from database.pm_database import *
from view.password_dialog import PasswordDialog

class EntryFrame(Frame):
    """
    The initial frame when starting the app, provding entry point for login and signup.
    """
    def __init__(self, master, pmd: PMDatabase):
        self.master = master
        super().__init__(master)
        self.grid()
        Label(self, text="Username:", font='Arial 20 bold').grid(row=0, column=0, padx=(20, 10), pady=(20, 10))
        self.entry_username = Entry(self, font='Consolas 20', width=40)
        self.entry_username.grid(row=0, column=1, columnspan=5, padx=(10, 20), pady=(20, 10), ipadx=10, ipady=10)
        Label(self, text="Password:", font='Arial 20 bold').grid(row=1, column=0, padx=(20, 10), pady=10)
        self.entry_password = Entry(self, font='Consolas 20', show='*', width=40)
        self.entry_password.grid(row=1, column=1, columnspan=5, padx=(10, 20), pady=10, ipadx=10, ipady=10)
        self.button_login = Button(self, text='Log in', command=self.login, width=10, font='Arial 20 bold')
        self.button_login.grid(row=2, column=1, padx=10, pady=(10, 20))
        self.button_signup = Button(self, text='Sign up', command=self.signup, width=10, font='Arial 20 bold')
        self.button_signup.grid(row=2, column=2, padx=10, pady=(10, 20))
        self.pmd = pmd
        # bind enter-key event
        # for entry_password
        self.entry_password.bind('<Return>', self.login_event)
        # for login button
        self.button_login.bind('<Return>', lambda event: self.button_login.invoke())
        # for signup button
        self.button_signup.bind('<Return>', lambda event: self.button_signup.invoke())

    def login(self) -> None:
        from view.passwords_frame import PasswordsFrame
        username = self.entry_username.get().strip()
        password = self.entry_password.get()
        if username and password:
            if self.pmd.user_login(username, password):
                PasswordsFrame(self.master, self.pmd)
                self.master.title(f'Password Manager: [{username}]')
                self.destroy()
            else:
                messagebox.showerror('Error', 'Username or password is incorrect!')
        else:
            messagebox.showerror('Error', 'Username or password cannot be empty!')

    def login_event(self, event):
        self.login()

    def signup(self) -> bool:
        username = self.entry_username.get().strip()
        password = self.entry_password.get()
        if username and password:
            if self.pmd.user_exists(username):
                messagebox.showwarning('Warning', 'Username already exists!')
                self.entry_username.delete(0, 'end')
            else:
                password_confirmed = PasswordDialog('Password Confirmation', 'Enter the password again to confirm it:').result
                if password == password_confirmed:
                    if self.pmd.add_new_user(username, password):
                        messagebox.showinfo('Info', f'User [{username}] has been created successfully.')
                        return True
                    else:
                        messagebox.showerror('Error', f'User [{username}] creation failed!')
                elif password_confirmed is None: # cancelld, do nothing
                    pass
                else:
                    messagebox.showerror('Error', 'Password confirmation failed!')
            self.entry_password.delete(0, 'end')
            self.entry_username.focus()
            return False
        else:
            messagebox.showerror('Error', 'Username or password cannot be empty!')
            return False

if __name__ == '__main__':
    app = Tk()
    ctypes.windll.shcore.SetProcessDpiAwareness(2)

    # Disable resize window from both x and y axis
    app.resizable(False, False)

    app.title('Password Manager')
    pmd = PMDatabase()
    EntryFrame(app, pmd)
    app.mainloop()