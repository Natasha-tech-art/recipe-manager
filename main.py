import customtkinter as ctk
from tkinter import messagebox
from database import Database

# Theme Settings
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class MainApplication(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("SmartMeal Pro - Recipe Manager")
        self.geometry("1100x700")
        
        self.db = Database()
        self.current_user = None

        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)

        self.show_auth_page()

    def show_auth_page(self):
        for widget in self.container.winfo_children():
            widget.destroy()
        self.auth_frame = AuthFrame(self.container, self)
        self.auth_frame.place(relx=0.5, rely=0.5, anchor="center")

    def login_success(self, user):
        self.current_user = user
        for widget in self.container.winfo_children():
            widget.destroy()
        self.show_dashboard()

    def show_dashboard(self):
        # Sidebar
        self.sidebar = ctk.CTkFrame(self.container, width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        
        ctk.CTkLabel(self.sidebar, text="SmartMeal Pro", font=("Helvetica", 20, "bold")).pack(pady=20)
        
        ctk.CTkButton(self.sidebar, text="+ Add Recipe", command=self.open_add_recipe).pack(pady=10, padx=20)
        ctk.CTkButton(self.sidebar, text="Refresh List", command=self.load_recipes).pack(pady=10, padx=20)
        ctk.CTkButton(self.sidebar, text="Logout", fg_color="gray30", command=self.show_auth_page).pack(side="bottom", pady=20, padx=20)

        # Recipe List Panel
        self.recipe_list_frame = ctk.CTkFrame(self.container, corner_radius=15)
        self.recipe_list_frame.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        
        self.recipe_scroll = ctk.CTkScrollableFrame(self.recipe_list_frame, label_text=f"{self.current_user['username']}'s Vault")
        self.recipe_scroll.pack(fill="both", expand=True, padx=10, pady=10)

        # Right Planner Panel
        self.planner_frame = ctk.CTkFrame(self.container, width=250)
        self.planner_frame.pack(side="right", fill="y", padx=(0, 20), pady=20)
        ctk.CTkLabel(self.planner_frame, text="Meal Planner", font=("Helvetica", 18, "bold")).pack(pady=10)
        
        self.load_recipes()

    def load_recipes(self):
        # Clear current list
        for widget in self.recipe_scroll.winfo_children():
            widget.destroy()
            
        recipes = self.db.get_user_recipes(self.current_user['username'])
        for res in recipes:
            btn = ctk.CTkButton(self.recipe_scroll, text=f"{res['title']} ({res['category']})", 
                                anchor="w", fg_color="transparent", border_width=1)
            btn.pack(fill="x", pady=2, padx=5)

    def open_add_recipe(self):
        self.add_win = ctk.CTkToplevel(self)
        self.add_win.title("Add New Recipe")
        self.add_win.geometry("450x550")
        self.add_win.attributes("-topmost", True)

        ctk.CTkLabel(self.add_win, text="Recipe Title").pack(pady=(20,0))
        self.title_ent = ctk.CTkEntry(self.add_win, width=300)
        self.title_ent.pack(pady=10)

        ctk.CTkLabel(self.add_win, text="Ingredients (one per line)").pack()
        self.ing_txt = ctk.CTkTextbox(self.add_win, width=300, height=100)
        self.ing_txt.pack(pady=10)

        self.cat_cmb = ctk.CTkComboBox(self.add_win, values=["Breakfast", "Lunch", "Dinner", "Dessert"], width=300)
        self.cat_cmb.pack(pady=10)

        ctk.CTkButton(self.add_win, text="Save to Vault", command=self.save_recipe).pack(pady=20)

    def save_recipe(self):
        data = {
            "title": self.title_ent.get(),
            "ingredients": self.ing_txt.get("0.0", "end").strip().split("\n"),
            "category": self.cat_cmb.get(),
            "owner": self.current_user['username']
        }
        if self.db.add_recipe(data):
            messagebox.showinfo("Success", "Recipe Saved!")
            self.add_win.destroy()
            self.load_recipes()

class AuthFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, corner_radius=15, fg_color=("gray90", "gray16"))
        self.controller = controller
        
        ctk.CTkLabel(self, text="SmartMeal Pro", font=("Helvetica", 24, "bold")).pack(pady=20, padx=40)
        self.u_ent = ctk.CTkEntry(self, placeholder_text="Username", width=250)
        self.u_ent.pack(pady=10)
        self.p_ent = ctk.CTkEntry(self, placeholder_text="Password", show="*", width=250)
        self.p_ent.pack(pady=10)

        ctk.CTkButton(self, text="Login", command=self.login, width=250).pack(pady=(20, 10))
        ctk.CTkButton(self, text="Create Account", fg_color="transparent", border_width=2, command=self.register, width=250).pack(pady=(0, 20))

    def login(self):
        user = self.controller.db.login_user(self.u_ent.get(), self.p_ent.get())
        if user: self.controller.login_success(user)
        else: messagebox.showerror("Error", "Login Failed")

    def register(self):
        success, msg = self.controller.db.create_user(self.u_ent.get(), self.p_ent.get())
        messagebox.showinfo("Status", msg) if success else messagebox.showerror("Error", msg)

if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()