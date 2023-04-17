from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from typing import Optional
import ctypes

from database.pm_database import *
from view.password_dialog import *

from backend.password_utils import generate_password

class PasswordsFrame(Frame):
    """
    The frame for passwords display and manipulation.
    """
    def __init__(self, master, pmd: PMDatabase):
        self.master = master
        self.pmd = pmd
        super().__init__(master)
        self.grid()

        # first group: search area and view all button
        subframe_search = Frame(self)
        subframe_search.grid(row=0, column=0, padx=20, pady=(20, 10))
        self.entry_search = Entry(subframe_search, font='Consolas 20', width=72)
        self.entry_search.grid(row=0, column=0, columnspan=3, padx=(0, 10), ipady=10)
        self.button_search = Button(subframe_search, text='Search', command=self.search, width=10, font='Arial 20')
        self.button_search.grid(row=0, column=3, padx=(10, 10))
        self.showall_button = Button(subframe_search, text='View All', command=self.showall, width=10, font='Arial 20')
        self.showall_button.grid(row=0, column=4, padx=(10, 0))
        # bind enter-key event
        self.entry_search.bind('<Return>', self.search_event)

        # second group: details of each password entry
        subframe_details = LabelFrame(self, text='Details', font='Arial 18')
        subframe_details.grid(row=1, column=0, padx=20, pady=10, sticky='ew')
        Label(subframe_details, text="Description", font='Arial 20').grid(row=0, column=0, padx=(40, 10), pady=(20, 10))
        self.entry_description = Entry(subframe_details, font='Consolas 20', width=80)
        self.entry_description.grid(row=0, column=1, columnspan=4, padx=(10, 0), pady=(20, 10), ipady=10)
        Label(subframe_details, text="Site", font='Arial 20').grid(row=1, column=0, padx=(40, 10), pady=10)
        self.entry_site = Entry(subframe_details, font='Consolas 20', width=80)
        self.entry_site.grid(row=1, column=1, columnspan=4, padx=(10, 0), pady=10, ipady=10)
        Label(subframe_details, text="Account ID", font='Arial 20').grid(row=2, column=0, padx=(40, 10), pady=10)
        self.entry_accountid = Entry(subframe_details, font='Consolas 20', width=80)
        self.entry_accountid.grid(row=2, column=1, columnspan=4, padx=(10, 0), pady=10, ipady=10)
        Label(subframe_details, text="Password", font='Arial 20').grid(row=3, column=0, padx=(40, 10), pady=10)
        self.text_password = Text(subframe_details, font='Consolas 20', width=80, height=3)
        self.text_password.grid(row=3, column=1, columnspan=4, padx=(10, 0), pady=10, ipady=10)
        Label(subframe_details, text="Notes", font='Arial 20').grid(row=4, column=0, padx=(40, 10), pady=10)
        self.text_notes = Text(subframe_details, font='Consolas 20', width=80, height=3)
        self.text_notes.grid(row=4, column=1, columnspan=4, padx=(10, 0), pady=10, ipady=10)
        Label(subframe_details, text="Modified At", font='Arial 20').grid(row=5, column=0, padx=(40, 10), pady=(10, 20))
        self.label_modifiedat = Label(subframe_details, font='Consolas 20', width=80, anchor='w')
        self.label_modifiedat.grid(row=5, column=1, columnspan=4, padx=(10, 0), pady=(10, 20))
        # bind enter-key event
        self.entry_description.bind('<Return>', self.focus_next_input)
        self.entry_site.bind('<Return>', self.focus_next_input)
        self.entry_accountid.bind('<Return>', self.focus_next_input)
        self.text_password.bind('<Return>', self.focus_next_and_change)
        self.text_notes.bind('<Return>', self.focus_next_input)
        # also bind tab-key event for text widgets
        self.text_password.bind('<Tab>', self.focus_next_and_change)
        self.text_notes.bind('<Tab>', self.focus_next_input)
        
        # third group: buttons for logout and password manipulation
        subframe_ldau = Frame(self)
        subframe_ldau.grid(row=2, column=0, padx=20, pady=10)
        self.button_logout = Button(subframe_ldau, text='Log Out', command=self.logout, width=10, font='Arial 20 bold')
        self.button_logout.grid(row=0, column=0, padx=(0, 10))
        self.button_delete = Button(subframe_ldau, text='Delete', command=self.delete, width=10, font='Arial 20', state='disabled')
        self.button_delete.grid(row=0, column=1, padx=10)
        self.button_add = Button(subframe_ldau, text='Add', command=self.add, width=10, font='Arial 20')
        self.button_add.grid(row=0, column=2, padx=10)
        self.button_update = Button(subframe_ldau, text='Update', command=self.update, width=10, font='Arial 20', state='disabled')
        self.button_update.grid(row=0, column=3, padx=10)
        self.button_clear = Button(subframe_ldau, text='Clear', command=self.clear, width=10, font='Arial 20')
        self.button_clear.grid(row=0, column=4, padx=10)

        # fourth group: treeview for list of password entries
        subframe_treeview = Frame(self)
        subframe_treeview.grid(row=3, column=0, padx=20, pady=(10, 20), sticky='ew')
        style = ttk.Style()
        style.configure('Treeview', font=('Consolas', 20), rowheight=40)
        style.configure('Treeview.Heading', font=('Arial', 22, 'bold'))
        columns = ('ID', 'Description', 'Site', 'Account ID', 'Password', 'Notes', 'Modified At', 'Salt')
        display_columns = ('Description', 'Site', 'Account ID', 'Password', 'Notes', 'Modified At')
        self.treeview_passwords = ttk.Treeview(subframe_treeview, columns=columns, displaycolumns=display_columns, show='headings', style='Treeview')
        # x, y scroll bars
        scrollbar_x = ttk.Scrollbar(subframe_treeview, command=self.treeview_passwords.xview, orient=HORIZONTAL)
        scrollbar_y = ttk.Scrollbar(subframe_treeview, command=self.treeview_passwords.yview, orient=VERTICAL)
        self.treeview_passwords.configure(xscrollcommand=scrollbar_x.set)
        self.treeview_passwords.configure(yscrollcommand=scrollbar_y.set)
        for column in columns:
            self.treeview_passwords.heading(column, text=column)
            self.treeview_passwords.column(column, minwidth=180, width=234, stretch=False)
        self.treeview_passwords.grid(row=0, column=0, padx=(0, 5), pady=(0, 5))
        scrollbar_x.grid(row=1, column=0, pady=(5, 0), sticky='ew')
        scrollbar_y.grid(row=0, column=1, padx=(5, 0), pady=(0, 5), sticky='ns')
        # bind double-click event
        self.treeview_passwords.bind('<Double-1>', self.load_details)

    def search(self) -> None:
        """
        Search pmd for the keyword in entry_search.
        """
        keyword = self.entry_search.get().strip()
        if keyword:
            res = self.pmd.search_password(keyword)
            if res:
                self.showall(res)
            else:
                messagebox.showinfo('Info', 'No matching results were found.')
    
    def showall(self, records: Optional[list] = None) -> None:
        """
        Show all passwords from records or pmd.
        """
        # delete all entires first
        self.treeview_passwords.delete(*self.treeview_passwords.get_children())
        if records:
            # insert from records
            for record in records:
                self.treeview_passwords.insert('', 'end', values=record)
        else:
            # insert from pmd
            records = self.pmd.show_all_passwords()
            if not records:
                messagebox.showinfo('Info', 'No passwords found.')
                return
            for record in self.pmd.show_all_passwords():
                self.treeview_passwords.insert('', 'end', values=record)

    def add(self):
        """
        Add the password in details section as a new password entry.
        """
        inputs = self.get_inputs()
        # check if account, password, and description are not empty before add new entry
        if inputs:
            if messagebox.askyesno('Addition Confirmation', 'Are you sure you want to add the password to the database?'):
                # add to pmd
                if not self.pmd.add_new_password(*inputs):
                    messagebox.showerror('Error', 'Password addition failed!')
                self.showall()
                # clear inputs after addition
                self.clear_inputs()
                self.button_update['state'] = 'disabled'
                self.button_delete['state'] = 'disabled'

    def update(self):
        """
        Update the password info in the details section to the entry double-clicked before.
        """
        inputs = self.get_inputs()
        if inputs:
            if messagebox.askyesno('Update Confirmation', 'Are you sure you want to update the password to the database?'):
                if not self.pmd.update_password(self.passwordid, *inputs):
                    messagebox.showerror('Error', 'Password updating failed!')
                else:
                    self.passwordid = None
                    self.showall()
                    self.clear_inputs()
                    # disable update button after updated
                    self.button_update['state'] = 'disabled'
                    # disable delete button after updated
                    self.button_delete['state'] = 'disabled'

    def delete(self):
        """
        Delete the password that has been double-clicked before and is currently shown in the details section.
        """
        if messagebox.askyesno('Deletion Confirmation', 'Are you sure you want to delete the password from the database?'):
            if self.pmd.delete_password(self.passwordid):
                self.passwordid = None
                self.showall()
                self.clear_inputs()
                # disable delete button after deletion
                self.button_delete['state'] = 'disabled'
                # disable update button after deletion
                self.button_update['state'] = 'disabled'
            else:
                messagebox.showerror('Error', 'Password deletion failed!')

    def logout(self):
        """
        Log out the current user as shown in the window title.
        """
        self.pmd.user_logout()
        from view.entry_frame import EntryFrame
        EntryFrame(self.master, self.pmd)
        self.destroy()

    def get_inputs(self) -> Optional[tuple]:
        description = self.entry_description.get().strip()
        site = self.entry_site.get().strip()
        accountid = self.entry_accountid.get().strip()
        password = self.text_password.get('1.0', 'end-1c')
        # generate random password, if password=='[random]'
        if password == '[random]':
            password = generate_password()
        notes = self.text_notes.get('1.0', 'end-1c').strip()
        # description, accountid and password must not be empty
        if not (description and accountid and password):
            messagebox.showwarning('Warning', 'Description, account ID and password cannot be empty!')
            return None
        return description, site, accountid, password, notes

    def clear_inputs(self):
        """
        Clear inputs in details section, including the modified-at label.
        """
        self.entry_description.delete(0, 'end')
        self.entry_site.delete(0, 'end')
        self.entry_accountid.delete(0, 'end')
        self.text_password.delete('1.0', 'end')
        self.text_notes.delete('1.0', 'end')
        self.label_modifiedat.config(text='')
        self.entry_description.focus()
    
    def clear(self):
        """
        Clear inputs and set passwordid to None.
        """
        self.clear_inputs()
        self.passwordid = None
        self.button_update['state'] = 'disabled'
        self.button_delete['state'] = 'disabled'

    def search_event(self, event):
        self.search()

    def focus_next_input(self, event):
        event.widget.tk_focusNext().focus()
        return 'break'

    def focus_next_and_change(self, event):
        if self.text_password.get('1.0', 'end-1c') == '[random]':
            self.text_password.delete(1.0, 'end')
            self.text_password.insert(1.0, generate_password())
        event.widget.tk_focusNext().focus()
        return 'break'

    def load_details(self, event):
        """
        Load password detail in the treeview list to the details section.
        Passwords can only be edited, updated or deleted after loading to the details section.
        """
        selection = self.treeview_passwords.selection()
        if selection:
            # get selected row's internal id in the treeview
            selection_id = selection[0]
            # get values from selected item
            values = self.treeview_passwords.item(selection_id, 'values')
            # get the id of the password entry in password table
            self.passwordid = values[0]
            # first clear all existing inputs in details seciton
            self.clear_inputs()
            # then load details to entries and textbox
            self.entry_description.insert(0, values[1])
            self.entry_site.insert(0, values[2])
            self.entry_accountid.insert(0, values[3])
            self.text_password.insert('1.0', values[4])
            self.text_notes.insert('1.0', values[5])
            self.label_modifiedat.config(text=values[6])
            # enable edit button
            self.button_update['state'] = 'normal'
            # enable delete button
            self.button_delete['state'] = 'normal'

if __name__ == '__main__':
    app = Tk()
    ctypes.windll.shcore.SetProcessDpiAwareness(2)

    # Disable resize window from both x and y axis
    app.resizable(False, False)

    app.title('Password Manager')
    pmd = PMDatabase()
    PasswordsFrame(app, pmd)
    app.mainloop()