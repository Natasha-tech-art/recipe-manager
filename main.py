import customtkinter as ctk
from tkinter import messagebox
from database import Database

# Global UI Settings
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class MainApplication(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("SmartMeal Pro - Recipe Manager")
        self.geometry("1100x700")
        
        # Initialize Database connection
        self.db = Database()
        self.current_user = None

        # Main container that swaps between Login and Dashboard
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)

        self.show_auth_page()

    def show_auth_page(self):
        # Clear the window
        for widget in self.container.winfo_children():
            widget.destroy()
        
        # Load the Login Card
        self.auth_frame = AuthFrame(self.container, self)
        self.auth_frame.place(relx=0.5, rely=0.5, anchor="center")

    def login_success(self, user):
        self.current_user = user
        # Clear window for the dashboard
        for widget in self.container.winfo_children():
            widget.destroy()
        self.show_dashboard()

    def show_dashboard(self):
        # 1. Sidebar (Navigation)
        self.sidebar = ctk.CTkFrame(self.container, width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        
        self.logo_label = ctk.CTkLabel(self.sidebar, text="SmartMeal Pro", font=("Helvetica", 20, "bold"))
        self.logo_label.pack(pady=20, padx=20)

        self.add_btn = ctk.CTkButton(self.sidebar, text="+ Add Recipe", command=self.open_add_recipe)
        self.add_btn.pack(pady=10, padx=20)

        self.logout_btn = ctk.CTkButton(self.sidebar, text="Logout", fg_color="gray30", command=self.show_auth_page)
        self.logout_btn.pack(side="bottom", pady=20, padx=20)

        # 2. Main Content (Recipe List)
        self.recipe_list_frame = ctk.CTkFrame(self.container, corner_radius=15)
        self.recipe_list_frame.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        
        self.list_title = ctk.CTkLabel(self.recipe_list_frame, text=f"Welcome, {self.current_user['username']}!", font=("Helvetica", 22, "bold"))
        self.list_title.pack(pady=20)

        self.info_lbl = ctk.CTkLabel(self.recipe_list_frame, text="Your saved recipes will appear here.")
        self.info_lbl.pack(pady=10)

        # 3. Right Panel (Meal Planner)
        self.planner_frame = ctk.CTkFrame(self.container, width=250)
        self.planner_frame.pack(side="right", fill="y", padx=(0, 20), pady=20)
        
        self.plan_label = ctk.CTkLabel(self.planner_frame, text="Weekly Plan", font=("Helvetica", 18, "bold"))
        self.plan_label.pack(pady=10, padx=20)

    def open_add_recipe(self):
        messagebox.showinfo("Coming Soon", "We will build the Add Recipe form in the next step!")

class AuthFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, corner_radius=15)
        self.controller = controller
        
        # UI Styling
        self.configure(fg_color=("gray90", "gray16"))
        
        self.title_lbl = ctk.CTkLabel(self, text="Login / Register", font=("Helvetica", 24, "bold"))
        self.title_lbl.pack(pady=(20, 10), padx=40)

        self.user_entry = ctk.CTkEntry(self, placeholder_text="Username", width=250, height=40)
        self.user_entry.pack(pady=10, padx=40)

        self.pass_entry = ctk.CTkEntry(self, placeholder_text="Password", show="*", width=250, height=40)
        self.pass_entry.pack(pady=10, padx=40)

        # Login Button
        self.login_btn = ctk.CTkButton(self, text="Login", command=self.login, width=250, height=40)
        self.login_btn.pack(pady=(20, 10))

        # Register Button
        self.reg_btn = ctk.CTkButton(
            self, text="Create Account", fg_color="transparent", 
            border_width=2, command=self.register, width=250, height=40
        )
        self.reg_btn.pack(pady=(0, 20))

    def login(self):
        username = self.user_entry.get()
        password = self.pass_entry.get()
        
        if not username or not password:
            messagebox.showwarning("Input Error", "Please enter both username and password.")
            return

        user = self.controller.db.login_user(username, password)
        if user:
            self.controller.login_success(user)
        else:
            messagebox.showerror("Error", "Invalid credentials. Try again.")

    def register(self):
        username = self.user_entry.get()
        password = self.pass_entry.get()
        
        if not username or not password:
            messagebox.showwarning("Input Error", "Please enter both username and password.")
            return

        success, msg = self.controller.db.create_user(username, password)
        if success:
            messagebox.showinfo("Success", msg)
        else:
            messagebox.showerror("Error", msg)

if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()