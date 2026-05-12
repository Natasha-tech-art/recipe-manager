import customtkinter as ctk
from tkinter import messagebox
from database import Database

# 1. GLOBAL SETTINGS
ctk.set_appearance_mode("dark") 
ctk.set_default_color_theme("blue") 

# 2. THE MAIN WINDOW CONTROLLER
class MainApplication(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("SmartMeal Pro")
        self.geometry("1100x700")
        
        self.db = Database()
        self.current_user = None

        # Container for switching pages
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)

        self.show_auth_page()

    def show_auth_page(self):
        for widget in self.container.winfo_children():
            widget.destroy()
        
        self.auth_frame = AuthFrame(self.container, self)
        # Use place to keep it centered
        self.auth_frame.place(relx=0.5, rely=0.5, anchor="center")

    def login_success(self, user):
        self.current_user = user
        for widget in self.container.winfo_children():
            widget.destroy()
        self.show_dashboard()

    def show_dashboard(self):
        # We will build this out in the next step!
        welcome_lbl = ctk.CTkLabel(
            self.container, 
            text=f"Welcome, {self.current_user['username']}!", 
            font=("Helvetica", 24, "bold")
        )
        welcome_lbl.pack(pady=40)
        
        logout_btn = ctk.CTkButton(self.container, text="Logout", command=self.show_auth_page)
        logout_btn.pack()

# 3. THE LOGIN/REGISTER COMPONENT
class AuthFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, corner_radius=15)
        self.controller = controller
        
        self.configure(fg_color=("gray90", "gray16")) 
        
        self.label = ctk.CTkLabel(self, text="SmartMeal Pro", font=("Helvetica", 28, "bold"))
        self.label.pack(pady=(30, 20), padx=50)

        self.user_entry = ctk.CTkEntry(self, placeholder_text="Username", width=280, height=45)
        self.user_entry.pack(pady=10, padx=50)

        self.pass_entry = ctk.CTkEntry(self, placeholder_text="Password", show="*", width=280, height=45)
        self.pass_entry.pack(pady=10, padx=50)

        self.login_btn = ctk.CTkButton(self, text="Login", command=self.login, width=280, height=45)
        self.login_btn.pack(pady=(20, 10))

        self.reg_btn = ctk.CTkButton(
            self, text="Create Account", fg_color="transparent", 
            border_width=2, command=self.register, width=280, height=45
        )
        self.reg_btn.pack(pady=(0, 30))

    def login(self):
        username = self.user_entry.get()
        password = self.pass_entry.get()
        user = self.controller.db.login_user(username, password)
        if user:
            self.controller.login_success(user)
        else:
            messagebox.showerror("Error", "Incorrect username or password")

    def register(self):
        username = self.user_entry.get()
        password = self.pass_entry.get()
        if not username or not password:
            messagebox.showwarning("Input Error", "Please fill in all fields")
            return
            
        success, msg = self.controller.db.create_user(username, password)
        if success:
            messagebox.showinfo("Success", msg)
        else:
            messagebox.showerror("Error", msg)

# 4. START THE APP
if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()
    
    def login(self):
        username = self.user_entry.get()
        password = self.pass_entry.get()
        
        print(f"Attempting login for: {username}") # DEBUG PRINT
        
        try:
            user = self.controller.db.login_user(username, password)
            print(f"Database response: {user}") # DEBUG PRINT
            
            if user:
                print("Login successful! Switching screens...") # DEBUG PRINT
                self.controller.login_success(user)
            else:
                print("Login failed: User not found.") # DEBUG PRINT
                messagebox.showerror("Error", "Incorrect username or password")
        except Exception as e:
            print(f"CRITICAL ERROR during login: {e}") # DEBUG PRINT
            messagebox.showerror("Database Error", str(e))