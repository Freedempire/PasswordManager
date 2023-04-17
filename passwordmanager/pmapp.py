from tkinter import *
import ctypes

from database.pm_database import PMDatabase
from view.entry_frame import EntryFrame

app = Tk()

# improve Tkinter window resolution
# https://coderslegacy.com/python/problem-solving/improve-tkinter-resolution/
# https://stackoverflow.com/questions/44398075/can-dpi-scaling-be-enabled-disabled-programmatically-on-a-per-session-basis
ctypes.windll.shcore.SetProcessDpiAwareness(2)

# Disable resize window from both x and y axis
app.resizable(False, False)

app.title('Password Manager')

# set icon
# photo = PhotoImage(file='./passwordmanager/img/key-gear.png')
photo = PhotoImage(file='./passwordmanager/img/cyber-crime.png')
app.wm_iconphoto(False, photo)

pmd = PMDatabase()
EntryFrame(app, pmd)
app.mainloop()

