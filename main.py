import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime

# Import your database class from database.py
from database import Database
# Import your planner frame from planner.py
from planner import MealPlannerFrame

# Set up CustomTkinter appearance settings
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ==========================================
# AUTHENTICATION FRAME
# ==========================================
class AuthFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, corner_radius=15, fg_color=("gray90", "gray16"))
        self.controller = controller
        
        ctk.CTkLabel(self, text="🍳 SmartMeal Pro", font=("Helvetica", 24, "bold"), text_color="#4CAF50").pack(pady=20, padx=40)
        
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
            messagebox.showerror("Database Error", f"Authentication failed:\n{e}")

    def register(self):
        try:
            success, msg = self.controller.db.create_user(self.u_ent.get(), self.p_ent.get())
            if success:
                messagebox.showinfo("Status", msg)
            else:
                messagebox.showerror("Error", msg)
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not complete registration:\n{e}")


# ==========================================
# MAIN APPLICATION ENGINE
# ==========================================
class MainApplication(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("SmartMeal Pro - Recipe Manager")
        self.geometry("1150x740")
        
        # Initialize database engine from database.py
        self.db = Database()
        self.current_user = None
        self.selected_category_filter = "All"

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

        # Side Controller Panel
        self.sidebar = ctk.CTkFrame(self.container, width=220, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        
        ctk.CTkLabel(self.sidebar, text="SmartMeal Pro", font=("Helvetica", 18, "bold"), text_color="#4CAF50").pack(pady=20, padx=10)
        
        ctk.CTkButton(self.sidebar, text="+ Add New Recipe", command=self.open_add_recipe).pack(pady=10, padx=20)
        ctk.CTkButton(self.sidebar, text="📅 Meal Planner", command=self.show_planner).pack(pady=10, padx=20)
        ctk.CTkButton(self.sidebar, text="Sync Hub", command=self.load_recipes).pack(pady=10, padx=20)
        ctk.CTkButton(self.sidebar, text="Logout", fg_color="gray30", command=self.show_auth_page).pack(side="bottom", pady=20, padx=20)

        # Center View Workspace
        self.recipe_list_frame = ctk.CTkFrame(self.container, corner_radius=15)
        self.recipe_list_frame.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        
        # Live Filter Bar Panel
        self.search_frame = ctk.CTkFrame(self.recipe_list_frame, fg_color="transparent")
        self.search_frame.pack(fill="x", padx=10, pady=(10, 2))

        self.search_entry = ctk.CTkEntry(self.search_frame, placeholder_text="🔍 Live search title or cuisine...", width=300)
        self.search_entry.pack(side="left", padx=(0, 10), expand=True, fill="x")
        self.search_entry.bind("<KeyRelease>", lambda e: self.filter_recipes())

        # Quick Category Filter Row Panel
        self.filter_buttons_frame = ctk.CTkFrame(self.recipe_list_frame, fg_color="transparent")
        self.filter_buttons_frame.pack(fill="x", padx=10, pady=(0, 10))

        categories = ["All", "Breakfast", "Lunch", "Dinner", "Dessert", "Snack"]
        self.filter_buttons = {}
        for cat in categories:
            btn = ctk.CTkButton(self.filter_buttons_frame, text=cat, width=90, height=28,
                                fg_color="#1F6AA5" if cat == "All" else "gray30",
                                command=lambda c=cat: self.set_category_filter(c))
            btn.pack(side="left", padx=4)
            self.filter_buttons[cat] = btn

        self.recipe_scroll = ctk.CTkScrollableFrame(self.recipe_list_frame, label_text="Your Personal Digital Cookbook Vault")
        self.recipe_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.load_recipes()

    def set_category_filter(self, category):
        self.selected_category_filter = category
        for cat, btn in self.filter_buttons.items():
            if cat == category:
                btn.configure(fg_color="#1F6AA5")
            else:
                btn.configure(fg_color="gray30")
        self.filter_recipes()

    def show_planner(self):
        for widget in self.container.winfo_children():
            widget.destroy()
        self.planner_view = MealPlannerFrame(self.container, self)
        self.planner_view.pack(fill="both", expand=True, padx=20, pady=20)

    def load_recipes(self):
        for widget in self.recipe_scroll.winfo_children():
            widget.destroy()
        try:
            recipes = self.db.get_user_recipes(self.current_user['username'])
            self.populate_scroll_list(recipes)
        except Exception as e:
            print(f"Error loading dashboard profiles: {e}")

    def filter_recipes(self):
        query = self.search_entry.get().strip()
        try:
            # Gather base records via database layer matching text query
            if query:
                base_recipes = self.db.search_recipes(self.current_user['username'], query)
            else:
                base_recipes = self.db.get_user_recipes(self.current_user['username'])

            # Apply layout filter mapping matching category selections
            if self.selected_category_filter != "All":
                filtered = [r for r in base_recipes if r.get('category', '').lower() == self.selected_category_filter.lower()]
            else:
                filtered = base_recipes

            for widget in self.recipe_scroll.winfo_children():
                widget.destroy()
            self.populate_scroll_list(filtered)
        except Exception as e:
            print(f"Filter tracking query exception: {e}")

    def populate_scroll_list(self, recipes):
        for res in recipes:
            cuisine_tag = res.get('cuisine', 'General')
            rating = res.get('rating', '⭐ Unrated')
            btn_text = f"{res['title']} ({cuisine_tag}) — Category: {res['category']}  |  Score: {rating}"
            btn = ctk.CTkButton(self.recipe_scroll, text=btn_text, anchor="w", 
                                fg_color="transparent", border_width=1,
                                command=lambda r=res: self.view_recipe_details(r))
            btn.pack(fill="x", pady=4, padx=5)

    def open_add_recipe(self):
        self.add_win = ctk.CTkToplevel(self)
        self.add_win.title("Add New Recipe Profile")
        self.add_win.geometry("520x640")
        self.add_win.attributes("-topmost", True)

        ctk.CTkLabel(self.add_win, text="Recipe Title", font=("Helvetica", 12, "bold")).pack(pady=(12,2))
        self.title_ent = ctk.CTkEntry(self.add_win, width=380)
        self.title_ent.pack()

        ctk.CTkLabel(self.add_win, text="Cuisine Classification (e.g., Italian, Mexican)", font=("Helvetica", 12, "bold")).pack(pady=(8,2))
        self.cuisine_ent = ctk.CTkEntry(self.add_win, width=380)
        self.cuisine_ent.pack()

        ctk.CTkLabel(self.add_win, text="Meal Category Slot", font=("Helvetica", 12, "bold")).pack(pady=(8,2))
        self.cat_cmb = ctk.CTkComboBox(self.add_win, values=["Breakfast", "Lunch", "Dinner", "Dessert", "Snack"], width=380)
        self.cat_cmb.pack()

        ctk.CTkLabel(self.add_win, text="Ingredients (One item per line)", font=("Helvetica", 12, "bold")).pack(pady=(8,2))
        self.ing_txt = ctk.CTkTextbox(self.add_win, width=380, height=90)
        self.ing_txt.pack()

        ctk.CTkLabel(self.add_win, text="Cooking & Preparation Instructions", font=("Helvetica", 12, "bold")).pack(pady=(8,2))
        self.ins_txt = ctk.CTkTextbox(self.add_win, width=380, height=120)
        self.ins_txt.pack()

        self.action_btn = ctk.CTkButton(self.add_win, text="Commit to Vault", command=self.save_recipe, width=200, fg_color="#4CAF50")
        self.action_btn.pack(pady=20)

    def save_recipe(self):
        if not self.title_ent.get().strip():
            messagebox.showwarning("Missing Requirements", "A recipe title layout is required!")
            return
            
        data = {
            "title": self.title_ent.get().strip(),
            "cuisine": self.cuisine_ent.get().strip() if self.cuisine_ent.get().strip() else "General",
            "category": self.cat_cmb.get(),
            "rating": "⭐ Unrated", # Preserved data structure default fallback
            "ingredients": self.ing_txt.get("0.0", "end").strip().split("\n"),
            "instructions": self.ins_txt.get("0.0", "end").strip(),
            "owner": self.current_user['username']
        }
        try:
            self.db.add_recipe(data)
            messagebox.showinfo("Success", "Recipe safely cataloged!")
            self.add_win.destroy()
            self.load_recipes()
        except Exception as e:
            messagebox.showerror("Error", f"Failed saving data profile: {e}")

    def view_recipe_details(self, recipe):
        if hasattr(self, 'detail_win') and self.detail_win.winfo_exists():
            self.detail_win.destroy()

        self.detail_win = ctk.CTkToplevel(self)
        self.detail_win.title(f"Recipe: {recipe['title']}")
        self.detail_win.geometry("580x680")
        self.detail_win.attributes("-topmost", True)
        self.detail_win.focus()

        scroll_content = ctk.CTkScrollableFrame(self.detail_win, fg_color="transparent")
        scroll_content.pack(fill="both", expand=True, padx=15, pady=(15, 80))

        ctk.CTkLabel(scroll_content, text=recipe['title'], font=("Helvetica", 24, "bold"), text_color="#4CAF50").pack(pady=(10, 5), anchor="w")
        
        meta_text = f"Cuisine: {recipe.get('cuisine', 'General')}  |  Type: {recipe['category']}"
        ctk.CTkLabel(scroll_content, text=meta_text, font=("Helvetica", 12, "italic"), text_color="gray").pack(pady=(0, 20), anchor="w")

        ctk.CTkLabel(scroll_content, text="📋 Required Ingredients Checklist:", font=("Helvetica", 14, "bold"), text_color="#FFF").pack(anchor="w", pady=(10, 5))
        
        ingredients_list = recipe.get('ingredients', [])
        if isinstance(ingredients_list, list):
            ings = "\n".join([f"  •  {i.strip()}" for i in ingredients_list if i.strip()])
        else:
            ings = str(ingredients_list)
            
        if not ings.strip():
            ings = "  • No ingredients listed profile."

        ing_display = ctk.CTkTextbox(scroll_content, width=500, height=120, font=("Helvetica", 13), fg_color=("gray85", "gray22"))
        ing_display.pack(fill="x", pady=5, anchor="w")
        ing_display.insert("0.0", ings)
        ing_display.configure(state="disabled")

        ctk.CTkLabel(scroll_content, text="🍳 Preparation Guide Instructions:", font=("Helvetica", 14, "bold"), text_color="#FFF").pack(anchor="w", pady=(20, 5))
        
        ins_box = ctk.CTkTextbox(scroll_content, width=500, height=180, font=("Helvetica", 13), fg_color=("gray85", "gray22"))
        ins_box.pack(fill="x", pady=5, anchor="w")
        ins_box.insert("0.0", recipe.get('instructions', 'No directions listed.'))
        ins_box.configure(state="disabled")

        btn_frame = ctk.CTkFrame(self.detail_win, fg_color=("gray95", "gray14"), height=70, corner_radius=0)
        btn_frame.place(relx=0.0, rely=1.0, relwidth=1.0, anchor="sw")

        ctk.CTkButton(btn_frame, text="🗑️ Delete Entry", fg_color="#FF4444", hover_color="#CC0000", font=("Helvetica", 13, "bold"),
                      command=lambda: self.confirm_delete(recipe)).pack(side="left", padx=25, pady=20, expand=True, fill="x")
        
        ctk.CTkButton(btn_frame, text="✏️ Edit Details", fg_color="#FF9800", hover_color="#E65100", font=("Helvetica", 13, "bold"), text_color="white",
                      command=lambda: self.open_edit_recipe(recipe)).pack(side="right", padx=25, pady=20, expand=True, fill="x")

    def confirm_delete(self, recipe):
        if messagebox.askyesno("Confirm Drop", f"Delete {recipe['title']} permanently from index?"):
            try:
                self.db.delete_recipe(recipe['_id'])
                messagebox.showinfo("Success", "Recipe permanently removed from your vault.")
                self.detail_win.destroy()
                self.load_recipes()
            except Exception as e:
                messagebox.showerror("Error", f"Could not clear profile reference: {e}")

    def open_edit_recipe(self, recipe):
        self.detail_win.destroy()
        
        self.edit_win = ctk.CTkToplevel(self)
        self.edit_win.title(f"Editing: {recipe['title']}")
        self.edit_win.geometry("520x660")
        self.edit_win.attributes("-topmost", True)

        ctk.CTkLabel(self.edit_win, text="Modify Recipe Title", font=("Helvetica", 12, "bold")).pack(pady=(12,2))
        self.edit_title_ent = ctk.CTkEntry(self.edit_win, width=380)
        self.edit_title_ent.pack()
        self.edit_title_ent.insert(0, recipe['title'])

        ctk.CTkLabel(self.edit_win, text="Cuisine Classification", font=("Helvetica", 12, "bold")).pack(pady=(8,2))
        self.edit_cuisine_ent = ctk.CTkEntry(self.edit_win, width=380)
        self.edit_cuisine_ent.pack()
        self.edit_cuisine_ent.insert(0, recipe.get('cuisine', 'General'))

        ctk.CTkLabel(self.edit_win, text="Meal Category Slot", font=("Helvetica", 12, "bold")).pack(pady=(8,2))
        self.edit_cat_cmb = ctk.CTkComboBox(self.edit_win, values=["Breakfast", "Lunch", "Dinner", "Dessert", "Snack"], width=380)
        self.edit_cat_cmb.pack()
        self.edit_cat_cmb.set(recipe['category'])

        ctk.CTkLabel(self.edit_win, text="Ingredients (One item per line)", font=("Helvetica", 12, "bold")).pack(pady=(8,2))
        self.edit_ing_txt = ctk.CTkTextbox(self.edit_win, width=380, height=90)
        self.edit_ing_txt.pack()
        self.edit_ing_txt.insert("0.0", "\n".join(recipe['ingredients']))

        ctk.CTkLabel(self.edit_win, text="Cooking & Preparation Instructions", font=("Helvetica", 12, "bold")).pack(pady=(8,2))
        self.edit_ins_txt = ctk.CTkTextbox(self.edit_win, width=380, height=120)
        self.edit_ins_txt.pack()
        self.edit_ins_txt.insert("0.0", recipe.get('instructions', ''))

        ctk.CTkButton(self.edit_win, text="Save Changes", command=lambda: self.save_update(recipe['_id']), width=200, fg_color="#FF9800").pack(pady=20)

    def save_update(self, recipe_id):
        if not self.edit_title_ent.get().strip():
            messagebox.showwarning("Missing Field", "Title cannot be blank!")
            return

        updated_data = {
            "title": self.edit_title_ent.get().strip(),
            "cuisine": self.edit_cuisine_ent.get().strip() if self.edit_cuisine_ent.get().strip() else "General",
            "category": self.edit_cat_cmb.get(),
            "ingredients": self.edit_ing_txt.get("0.0", "end").strip().split("\n"),
            "instructions": self.edit_ins_txt.get("0.0", "end").strip()
        }
        try:
            self.db.update_recipe(recipe_id, updated_data)
            messagebox.showinfo("Success", "Recipe changes saved successfully!")
            self.edit_win.destroy()
            self.load_recipes()
        except Exception as e:
            messagebox.showerror("Update Error", f"Could not push modifications:\n{e}")

# ==========================================
# APPLICATION START EVENT LOOP
# ==========================================
if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()