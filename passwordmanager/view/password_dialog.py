from tkinter import *
from tkinter import simpledialog
from tkinter import messagebox

class PasswordDialog(simpledialog.Dialog):
    def __init__(self, title, prompt, parent=None):
        self.prompt = prompt
        simpledialog.Dialog.__init__(self, parent, title)

    def body(self, master):
        Label(master, text=self.prompt, font='Arial 24').grid(row=0, padx=20, pady=(20, 10))
        self.entry_password = Entry(master, font='Consolas 20', show='*', width=40)
        self.entry_password.grid(row=1, padx=20, pady=10, ipadx=10, ipady=10)
        return self.entry_password

    def buttonbox(self):
        box = Frame(self)
        Button(box, text="OK", width=10, command=self.ok, default=ACTIVE, font='Arial 20 bold').pack(side=LEFT, padx=20, pady=20)
        Button(box, text="Cancel", width=10, command=self.cancel, font='Arial 20 bold').pack(side=LEFT, padx=20, pady=20)
        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)
        box.pack()

    def validate(self):
        """
        Override validate(), makes it always valid for non-empty value in entry
        :return: string value of entry
        """
        result = self.entry_password.get()
        if not result:
            messagebox.showwarning('Warning', 'Master password cannot be empty, try again.', parent=self)
            return 0
        self.result = result
        return 1

    def destroy(self):
        self.entry_password = None
        simpledialog.Dialog.destroy(self)

if __name__ == '__main__':
    PasswordDialog('Master Password', 'Input your master password:')