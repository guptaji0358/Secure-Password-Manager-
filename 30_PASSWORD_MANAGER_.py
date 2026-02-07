from tkinter import *
from tkinter import messagebox
import random, json, os, string, pyperclip
from cryptography.fernet import Fernet

BASE_DIR = r"E:\Program Files\RobinData\PYTHON\RawData"

DATA_FILE = os.path.join(BASE_DIR, "passwords.json")
KEY_FILE = os.path.join(BASE_DIR, "secret.key")
IMAGE_FILE = os.path.join(BASE_DIR, "PASSWORD_LOCK.png")

MASTER_PASSWORD = "1234"   # CHANGE THIS

def load_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
    else:
        with open(KEY_FILE, "rb") as f:
            key = f.read()
    return key

KEY = load_key()
cipher = Fernet(KEY)

root = Tk()
root.title("Secure Password Manager")
root.config(padx=20, pady=20)

lock_image = None

def encrypt(text):
    return cipher.encrypt(text.encode()).decode()

def decrypt(text):
    return cipher.decrypt(text.encode()).decode()

def generate_password():
    chars = string.ascii_letters + string.digits + string.punctuation
    password = "".join(random.choice(chars) for _ in range(14))
    pass_entry.delete(0, END)
    pass_entry.insert(0, password)
    pyperclip.copy(password)

def save_password():
    website = site_entry.get()
    email = email_entry.get()
    password = pass_entry.get()

    if not website or not password:
        messagebox.showinfo("Error", "Empty Field")
        return

    new_data = {website: {"email": encrypt(email), "password": encrypt(password)}}

    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try: data = json.load(f)
            except: data = {}
    else:
        data = {}

    data.update(new_data)

    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

    site_entry.delete(0, END)
    pass_entry.delete(0, END)

    messagebox.showinfo("Saved", "Password Stored")

def search_password():
    website = site_entry.get()

    if not website:
        messagebox.showinfo("Error", "Enter Website")
        return

    if not os.path.exists(DATA_FILE):
        messagebox.showinfo("Error", "No Data File")
        return

    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    if website in data:
        email = decrypt(data[website]["email"])
        password = decrypt(data[website]["password"])

        email_entry.delete(0, END)
        email_entry.insert(0, email)

        pass_entry.delete(0, END)
        pass_entry.insert(0, password)

        messagebox.showinfo("Found", f"Email: {email}\nPassword: {password}")
    else:
        messagebox.showinfo("Not Found", "No Record")

def delete_password():
    website = site_entry.get()

    if not website:
        messagebox.showinfo("Error", "Enter Website")
        return

    if not os.path.exists(DATA_FILE):
        return

    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    if website in data:
        del data[website]

        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)

        site_entry.delete(0, END)
        email_entry.delete(0, END)
        pass_entry.delete(0, END)

        messagebox.showinfo("Deleted", "Entry Removed")

def toggle_password():
    pass_entry.config(show="" if show_var.get() else "*")

def login_check():
    if login_entry.get() == MASTER_PASSWORD:
        login_frame.pack_forget()
        app_frame.pack()
        site_entry.focus()
    else:
        messagebox.showerror("Error", "Wrong Password")

# ---------- LOGIN ---------- #

login_frame = Frame(root)
login_frame.pack()

canvas = Canvas(login_frame, width=220, height=220, highlightthickness=0)
canvas.grid(row=0, column=0, pady=10)

if os.path.exists(IMAGE_FILE):
    lock_image = PhotoImage(file=IMAGE_FILE)
    lock_image = lock_image.subsample(2,2)
    canvas.create_image(110,110,image=lock_image)
else:
    canvas.create_text(110,110,text="IMAGE\nNOT FOUND",fill="red")

Label(login_frame, text="Master Password", font=("Arial",12)).grid(row=1,column=0)

login_entry = Entry(login_frame, show="*", width=25)
login_entry.grid(row=2,column=0,pady=5)
login_entry.focus()

Button(login_frame, text="Login", width=15, command=login_check).grid(row=3,column=0,pady=8)

# ---------- APP ---------- #

app_frame = Frame(root)

Label(app_frame,text="Website").grid(row=0,column=0,sticky="w")
Label(app_frame,text="Email").grid(row=1,column=0,sticky="w")
Label(app_frame,text="Password").grid(row=2,column=0,sticky="w")

site_entry = Entry(app_frame,width=28)
site_entry.grid(row=0,column=1)

email_entry = Entry(app_frame,width=28)
email_entry.grid(row=1,column=1)

pass_entry = Entry(app_frame,width=28,show="*")
pass_entry.grid(row=2,column=1)

Button(app_frame,text="Search",width=10,command=search_password).grid(row=0,column=2,padx=5)
Button(app_frame,text="Generate",width=10,command=generate_password).grid(row=2,column=2,padx=5)

Button(app_frame,text="Save",width=20,command=save_password).grid(row=3,column=1,pady=8)
Button(app_frame,text="Delete",width=20,command=delete_password).grid(row=4,column=1,pady=2)

show_var = IntVar()
Checkbutton(app_frame,text="Show Password",variable=show_var,command=toggle_password).grid(row=5,column=1)

root.mainloop()
