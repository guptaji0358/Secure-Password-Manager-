"""Tkinter user interface for the password manager."""

import tkinter as tk
from tkinter import messagebox

import pyperclip

from .credential_store import CredentialStore
from .password_generator import generate_password


class PasswordManagerApp:
    def __init__(self, root: tk.Tk, store: CredentialStore, master_password: str, image_file: str):
        self.root = root
        self.store = store
        self.master_password = master_password
        self.image_file = image_file
        self.lock_image = None

        root.title("Secure Password Manager")
        root.config(padx=20, pady=20)

        self._build_login()
        self._build_manager()

    def _build_login(self) -> None:
        self.login_frame = tk.Frame(self.root)
        self.login_frame.pack()

        canvas = tk.Canvas(self.login_frame, width=220, height=220, highlightthickness=0)
        canvas.grid(row=0, column=0, pady=10)
        try:
            self.lock_image = tk.PhotoImage(file=self.image_file).subsample(2, 2)
            canvas.create_image(110, 110, image=self.lock_image)
        except tk.TclError:
            canvas.create_text(110, 110, text="IMAGE\nNOT FOUND", fill="red")

        tk.Label(self.login_frame, text="Master Password", font=("Arial", 12)).grid(row=1, column=0)
        self.login_entry = tk.Entry(self.login_frame, show="*", width=25)
        self.login_entry.grid(row=2, column=0, pady=5)
        self.login_entry.focus()
        tk.Button(self.login_frame, text="Login", width=15, command=self.login).grid(row=3, column=0, pady=8)

    def _build_manager(self) -> None:
        self.manager_frame = tk.Frame(self.root)
        for row, label in enumerate(("Website", "Email", "Password")):
            tk.Label(self.manager_frame, text=label).grid(row=row, column=0, sticky="w")

        self.website_entry = tk.Entry(self.manager_frame, width=28)
        self.email_entry = tk.Entry(self.manager_frame, width=28)
        self.password_entry = tk.Entry(self.manager_frame, width=28, show="*")
        for row, entry in enumerate((self.website_entry, self.email_entry, self.password_entry)):
            entry.grid(row=row, column=1)

        tk.Button(self.manager_frame, text="Search", width=10, command=self.search).grid(row=0, column=2, padx=5)
        tk.Button(self.manager_frame, text="Generate", width=10, command=self.generate).grid(row=2, column=2, padx=5)
        tk.Button(self.manager_frame, text="Save", width=20, command=self.save).grid(row=3, column=1, pady=8)
        tk.Button(self.manager_frame, text="Delete", width=20, command=self.delete).grid(row=4, column=1, pady=2)

        self.show_password = tk.IntVar()
        tk.Checkbutton(self.manager_frame, text="Show Password", variable=self.show_password, command=self.toggle_password).grid(row=5, column=1)

    def login(self) -> None:
        if self.login_entry.get() != self.master_password:
            messagebox.showerror("Error", "Wrong Password")
            return
        self.login_frame.pack_forget()
        self.manager_frame.pack()
        self.website_entry.focus()

    def generate(self) -> None:
        password = generate_password()
        self.password_entry.delete(0, tk.END)
        self.password_entry.insert(0, password)
        pyperclip.copy(password)

    def save(self) -> None:
        website = self.website_entry.get().strip()
        password = self.password_entry.get()
        if not website or not password:
            messagebox.showinfo("Error", "Empty Field")
            return
        self.store.save(website, self.email_entry.get(), password)
        self.website_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        messagebox.showinfo("Saved", "Password Stored")

    def search(self) -> None:
        website = self.website_entry.get().strip()
        if not website:
            messagebox.showinfo("Error", "Enter Website")
            return
        try:
            credential = self.store.find(website)
        except Exception:
            messagebox.showerror("Error", "Unable to decrypt this record")
            return
        if credential is None:
            messagebox.showinfo("Not Found", "No Record")
            return
        email, password = credential
        self.email_entry.delete(0, tk.END)
        self.email_entry.insert(0, email)
        self.password_entry.delete(0, tk.END)
        self.password_entry.insert(0, password)
        messagebox.showinfo("Found", f"Email: {email}\nPassword: {password}")

    def delete(self) -> None:
        website = self.website_entry.get().strip()
        if not website:
            messagebox.showinfo("Error", "Enter Website")
            return
        if not self.store.delete(website):
            messagebox.showinfo("Not Found", "No Record")
            return
        for entry in (self.website_entry, self.email_entry, self.password_entry):
            entry.delete(0, tk.END)
        messagebox.showinfo("Deleted", "Entry Removed")

    def toggle_password(self) -> None:
        self.password_entry.config(show="" if self.show_password.get() else "*")
