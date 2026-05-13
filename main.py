import customtkinter as ctk
from tkinter import messagebox
from database import Database
from bson.objectid import ObjectId

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
        for widget in self.container.winfo_children():
            widget.destroy()
        self.auth_frame = AuthFrame(self.container, self)
        self.auth_frame.place(relx=0.5, rely=0.5, anchor="center")

    def login_success(self, user):
        self.current_user = user
        for widget in self.container.winfo_children():
            widget.destroy()
        self.show_dashboard()

    # --- DASHBOARD & CRUD LOGIC ---

    def show_dashboard(self):
        # 1. Sidebar
        self.sidebar = ctk.CTkFrame(self.container, width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        
        ctk.CTkLabel(self.sidebar, text="SmartMeal Pro", font=("Helvetica", 20, "bold")).pack(pady=20)

        # FIXED: Added lambda to ensure the command points to this class instance
        self.add_btn = ctk.CTkButton(self.sidebar, text="+ Add Recipe", command=lambda: self.open_add_recipe())
        self.add_btn.pack(pady=10, padx=20)

        self.refresh_btn = ctk.CTkButton(self.sidebar, text="Refresh List", command=lambda: self.load_recipes())
        self.refresh_btn.pack(pady=10, padx=20)

        self.logout_btn = ctk.CTkButton(self.sidebar, text="Logout", fg_color="gray30", command=self.show_auth_page)
        self.logout_btn.pack(side="bottom", pady=20, padx=20)

        # 2. Main Content (Recipe List)
        self.recipe_list_frame = ctk.CTkFrame(self.container, corner_radius=15)
        self.recipe_list_frame.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        
        self.recipe_scroll = ctk.CTkScrollableFrame(self.recipe_list_frame, label_text="Your Recipe Vault")
        self.recipe_scroll.pack(fill="both", expand=True, padx=10, pady=10)

        # 3. Right Panel (Meal Planner)
        self.planner_frame = ctk.CTkFrame(self.container, width=300)
        self.planner_frame.pack(side="right", fill="y", padx=(0, 20), pady=20)
        
        ctk.CTkLabel(self.planner_frame, text="Meal Planner", font=("Helvetica", 18, "bold")).pack(pady=10)

        # The Calendar Widget
        from tkcalendar import Calendar
        self.cal = Calendar(self.planner_frame, selectmode='day', date_pattern='y-mm-dd')
        self.cal.pack(pady=10, padx=10)
        # When you click a date, it loads the plan for that day
        self.cal.bind("<<CalendarSelected>>", lambda e: self.load_selected_day_plan())

        # Display Area for Meals
        self.day_plan_box = ctk.CTkFrame(self.planner_frame, fg_color="transparent")
        self.day_plan_box.pack(fill="both", expand=True, padx=10)

        self.plan_labels = {} 
        for meal in ["Breakfast", "Lunch", "Dinner"]:
            ctk.CTkLabel(self.day_plan_box, text=meal, font=("Helvetica", 12, "gray")).pack(anchor="w")
            self.plan_labels[meal] = ctk.CTkLabel(self.day_plan_box, text="Not Scheduled", font=("Helvetica", 14))
            self.plan_labels[meal].pack(anchor="w", pady=(0, 10))

        ctk.CTkButton(self.planner_frame, text="Schedule Meal", command=self.assign_to_planner).pack(pady=10)
        
        self.load_recipes()

    def load_recipes(self):
        # Clear current list
        for widget in self.recipe_scroll.winfo_children():
            widget.destroy()
            
        recipes = self.db.get_user_recipes(self.current_user['username'])
        for res in recipes:
            # Command uses lambda to pass the specific recipe to the detail view
            btn = ctk.CTkButton(
                self.recipe_scroll, 
                text=f"{res['title']} ({res['category']})", 
                anchor="w", fg_color="transparent", border_width=1,
                command=lambda r=res: self.view_recipe_details(r)
            )
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

    def view_recipe_details(self, recipe):
        self.detail_win = ctk.CTkToplevel(self)
        self.detail_win.title(recipe['title'])
        self.detail_win.geometry("400x500")
        self.detail_win.attributes("-topmost", True)

        ctk.CTkLabel(self.detail_win, text=recipe['title'], font=("Helvetica", 22, "bold")).pack(pady=10)
        
        ings = "\n".join(recipe['ingredients'])
        ctk.CTkLabel(self.detail_win, text="Ingredients:", font=("Helvetica", 14, "bold")).pack(anchor="w", padx=20)
        ctk.CTkLabel(self.detail_win, text=ings, justify="left").pack(anchor="w", padx=40, pady=5)

        btn_frame = ctk.CTkFrame(self.detail_win, fg_color="transparent")
        btn_frame.pack(side="bottom", pady=20)

        ctk.CTkButton(btn_frame, text="Delete", fg_color="#FF4444", 
                      command=lambda: self.confirm_delete(recipe)).pack(side="left", padx=10)
        
        ctk.CTkButton(btn_frame, text="Edit", 
                      command=lambda: self.open_edit_recipe(recipe)).pack(side="left", padx=10)

    def confirm_delete(self, recipe):
        if messagebox.askyesno("Confirm", f"Delete {recipe['title']}?"):
            self.db.delete_recipe(recipe['_id'])
            self.detail_win.destroy()
            self.load_recipes()

    def open_edit_recipe(self, recipe):
        self.open_add_recipe()
        self.add_win.title(f"Editing: {recipe['title']}")
        
        self.title_ent.insert(0, recipe['title'])
        self.ing_txt.insert("0.0", "\n".join(recipe['ingredients']))
        self.cat_cmb.set(recipe['category'])
        
        # Re-map the button to handle update instead of save
        for widget in self.add_win.winfo_children():
            if isinstance(widget, ctk.CTkButton) and widget.cget("text") == "Save to Vault":
                widget.configure(text="Update Recipe", command=lambda: self.save_update(recipe['_id']))

    def save_update(self, recipe_id):
        updated_data = {
            "title": self.title_ent.get(),
            "ingredients": self.ing_txt.get("0.0", "end").strip().split("\n"),
            "category": self.cat_cmb.get()
        }
        if self.db.update_recipe(recipe_id, updated_data):
            messagebox.showinfo("Success", "Recipe Updated!")
            self.add_win.destroy()
            if hasattr(self, 'detail_win'): self.detail_win.destroy()
            self.load_recipes()

# --- AUTHENTICATION FRAME ---

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
        ctk.CTkButton(self, text="Create Account", fg_color="transparent", border_width=2, 
                      command=self.register, width=250).pack(pady=(0, 20))

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