import customtkinter as ctk
from tkinter import messagebox
from database import Database
from planner import MealPlannerFrame

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class MainApplication(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("SmartMeal Pro - Recipe Manager")
        self.geometry("1100x700")
        
        self.db = Database()
        self.current_user = None

        # Absolute Root Frame Viewport Manager Window
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
        self.show_dashboard()

    def show_dashboard(self):
        for widget in self.container.winfo_children():
            widget.destroy()

        # 1. Sidebar Frame
        self.sidebar = ctk.CTkFrame(self.container, width=220, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        
        ctk.CTkLabel(self.sidebar, text="SmartMeal Pro", font=("Helvetica", 20, "bold")).pack(pady=20)
        
        ctk.CTkButton(self.sidebar, text="+ Add Recipe", command=lambda: self.open_add_recipe()).pack(pady=10, padx=20)
        ctk.CTkButton(self.sidebar, text="📅 Meal Planner", command=lambda: self.show_planner()).pack(pady=10, padx=20)
        ctk.CTkButton(self.sidebar, text="Refresh Vault", command=lambda: self.load_recipes()).pack(pady=10, padx=20)
        ctk.CTkButton(self.sidebar, text="Logout", fg_color="gray30", command=self.show_auth_page).pack(side="bottom", pady=20, padx=20)

        # 2. Main content view block
        self.recipe_list_frame = ctk.CTkFrame(self.container, corner_radius=15)
        self.recipe_list_frame.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        
        self.search_frame = ctk.CTkFrame(self.recipe_list_frame, fg_color="transparent")
        self.search_frame.pack(fill="x", padx=10, pady=10)

        self.search_entry = ctk.CTkEntry(self.search_frame, placeholder_text="Search title, cuisine, or category...", width=300)
        self.search_entry.pack(side="left", padx=(0, 10), expand=True, fill="x")
        self.search_entry.bind("<KeyRelease>", lambda e: self.filter_recipes())

        self.recipe_scroll = ctk.CTkScrollableFrame(self.recipe_list_frame, label_text="Your Recipe Vault")
        self.recipe_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.load_recipes()

    def show_planner(self):
        # Destroy all active panels to prevent layout frame stacking overlaps
        for widget in self.container.winfo_children():
            widget.destroy()
        
        # Structural Mount injection framework fix
        self.planner_view = MealPlannerFrame(self.container, self)
        self.planner_view.pack(fill="both", expand=True, padx=20, pady=20)

    def load_recipes(self):
        for widget in self.recipe_scroll.winfo_children():
            widget.destroy()
        try:
            recipes = self.db.get_user_recipes(self.current_user['username'])
            self.populate_scroll_list(recipes)
        except Exception as e:
            print(f"Error loading recipes: {e}")

    def filter_recipes(self):
        query = self.search_entry.get().strip()
        if not query:
            self.load_recipes()
            return
        try:
            recipes = self.db.search_recipes(self.current_user['username'], query)
            for widget in self.recipe_scroll.winfo_children():
                widget.destroy()
            self.populate_scroll_list(recipes)
        except Exception as e:
            print(f"Filter error: {e}")

    def populate_scroll_list(self, recipes):
        for res in recipes:
            cuisine_tag = res.get('cuisine', 'General')
            btn_text = f"{res['title']} ({cuisine_tag}) — {res['category']}"
            btn = ctk.CTkButton(self.recipe_scroll, text=btn_text, anchor="w", 
                                fg_color="transparent", border_width=1,
                                command=lambda r=res: self.view_recipe_details(r))
            btn.pack(fill="x", pady=2, padx=5)

    def open_add_recipe(self):
        self.add_win = ctk.CTkToplevel(self)
        self.add_win.title("Add New Recipe")
        self.add_win.geometry("500x720")
        self.add_win.attributes("-topmost", True)

        ctk.CTkLabel(self.add_win, text="Recipe Title", font=("Helvetica", 12, "bold")).pack(pady=(15,2))
        self.title_ent = ctk.CTkEntry(self.add_win, width=380)
        self.title_ent.pack()

        ctk.CTkLabel(self.add_win, text="Cuisine Type (e.g., Italian, Indian)", font=("Helvetica", 12, "bold")).pack(pady=(10,2))
        self.cuisine_ent = ctk.CTkEntry(self.add_win, width=380)
        self.cuisine_ent.pack()

        ctk.CTkLabel(self.add_win, text="Category", font=("Helvetica", 12, "bold")).pack(pady=(10,2))
        self.cat_cmb = ctk.CTkComboBox(self.add_win, values=["Breakfast", "Lunch", "Dinner", "Dessert"], width=380)
        self.cat_cmb.pack()

        ctk.CTkLabel(self.add_win, text="Ingredients (One item per line)", font=("Helvetica", 12, "bold")).pack(pady=(10,2))
        self.ing_txt = ctk.CTkTextbox(self.add_win, width=380, height=100)
        self.ing_txt.pack()

        ctk.CTkLabel(self.add_win, text="Preparation Instructions", font=("Helvetica", 12, "bold")).pack(pady=(10,2))
        self.ins_txt = ctk.CTkTextbox(self.add_win, width=380, height=140)
        self.ins_txt.pack()

        self.action_btn = ctk.CTkButton(self.add_win, text="Save to Vault", command=self.save_recipe, width=200)
        self.action_btn.pack(pady=25)

    def save_recipe(self):
        if not self.title_ent.get().strip():
            messagebox.showwarning("Missing Data", "Recipe Title is required!")
            return
            
        data = {
            "title": self.title_ent.get().strip(),
            "cuisine": self.cuisine_ent.get().strip() if self.cuisine_ent.get().strip() else "General",
            "category": self.cat_cmb.get(),
            "ingredients": self.ing_txt.get("0.0", "end").strip().split("\n"),
            "instructions": self.ins_txt.get("0.0", "end").strip(),
            "owner": self.current_user['username']
        }
        try:
            self.db.add_recipe(data)
            messagebox.showinfo("Success", "Recipe securely saved in your Online Cloud Vault!")
            self.add_win.destroy()
            self.load_recipes()
        except Exception as e:
            messagebox.showerror("Cloud Write Error", f"Failed saving data upstream:\n{e}")

    def view_recipe_details(self, recipe):
        self.detail_win = ctk.CTkToplevel(self)
        self.detail_win.title(recipe['title'])
        self.detail_win.geometry("520x620")
        self.detail_win.attributes("-topmost", True)

        ctk.CTkLabel(self.detail_win, text=recipe['title'], font=("Helvetica", 24, "bold")).pack(pady=(15,2))
        ctk.CTkLabel(self.detail_win, text=f"Cuisine: {recipe.get('cuisine', 'General')} | Category: {recipe['category']}", 
                     font=("Helvetica", 13, "italic", "gray")).pack(pady=(0,15))

        ctk.CTkLabel(self.detail_win, text="Ingredients List:", font=("Helvetica", 14, "bold")).pack(anchor="w", padx=25)
        ings = "\n".join([f"• {i}" for i in recipe['ingredients'] if i.strip()])
        ctk.CTkLabel(self.detail_win, text=ings, justify="left", font=("Helvetica", 13)).pack(anchor="w", padx=40, pady=5)

        ctk.CTkLabel(self.detail_win, text="Cooking Instructions:", font=("Helvetica", 14, "bold")).pack(anchor="w", padx=25, pady=(15,2))
        ins_box = ctk.CTkTextbox(self.detail_win, width=460, height=180)
        ins_box.insert("0.0", recipe.get('instructions', 'No specific preparation rules provided.'))
        ins_box.configure(state="disabled")
        ins_box.pack(padx=25, pady=5)

        btn_frame = ctk.CTkFrame(self.detail_win, fg_color="transparent")
        btn_frame.pack(side="bottom", pady=20)

        ctk.CTkButton(btn_frame, text="Delete Recipe", fg_color="#FF4444", hover_color="#CC0000",
                      command=lambda: self.confirm_delete(recipe)).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Edit Details", command=lambda: self.open_edit_recipe(recipe)).pack(side="left", padx=10)

    def confirm_delete(self, recipe):
        if messagebox.askyesno("Confirm Deletion", f"Permanently remove {recipe['title']}?"):
            try:
                self.db.delete_recipe(recipe['_id'])
                self.detail_win.destroy()
                self.load_recipes()
            except Exception as e:
                messagebox.showerror("Delete Error", f"Could not perform request:\n{e}")

    def open_edit_recipe(self, recipe):
        self.open_add_recipe()
        self.add_win.title(f"Editing: {recipe['title']}")
        
        self.title_ent.insert(0, recipe['title'])
        self.cuisine_ent.insert(0, recipe.get('cuisine', 'General'))
        self.cat_cmb.set(recipe['category'])
        self.ing_txt.insert("0.0", "\n".join(recipe['ingredients']))
        self.ins_txt.insert("0.0", recipe.get('instructions', ''))
        
        self.action_btn.configure(text="Update Details", command=lambda: self.save_update(recipe['_id']))

    def save_update(self, recipe_id):
        updated_data = {
            "title": self.title_ent.get().strip(),
            "cuisine": self.cuisine_ent.get().strip(),
            "category": self.cat_cmb.get(),
            "ingredients": self.ing_txt.get("0.0", "end").strip().split("\n"),
            "instructions": self.ins_txt.get("0.0", "end").strip()
        }
        try:
            self.db.update_recipe(recipe_id, updated_data)
            messagebox.showinfo("Success", "Recipe configurations changed successfully!")
            self.add_win.destroy()
            if hasattr(self, 'detail_win'): self.detail_win.destroy()
            self.load_recipes()
        except Exception as e:
            messagebox.showerror("Update Error", f"Could not push modifications online:\n{e}")

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
        try:
            user = self.controller.db.login_user(self.u_ent.get(), self.p_ent.get())
            if user: 
                self.controller.login_success(user)
            else: 
                messagebox.showerror("Error", "Login Details Incorrect.")
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not connect to MongoDB Atlas cluster cloud.\nError:\n{e}")

    def register(self):
        try:
            success, msg = self.controller.db.create_user(self.u_ent.get(), self.p_ent.get())
            messagebox.showinfo("Status", msg) if success else messagebox.showerror("Error", msg)
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not write configuration online.\nError:\n{e}")

if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()