import customtkinter as ctk
from tkinter import messagebox
from tkcalendar import Calendar
from datetime import date, datetime

class MealPlannerFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, corner_radius=15, fg_color="transparent")
        self.controller = controller
        self.db = controller.db

        # Main dynamic viewport layout splitting
        self.left_panel = ctk.CTkFrame(self, corner_radius=15)
        self.left_panel.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self.right_panel = ctk.CTkFrame(self, width=320, corner_radius=15)
        self.right_panel.pack(side="right", fill="y", padx=10, pady=10)

        # Back Button Navigation Element
        back_btn = ctk.CTkButton(self.left_panel, text="⬅️ Return to Dashboard", 
                                 fg_color="gray30", width=160, command=self.go_back)
        back_btn.pack(anchor="w", padx=15, pady=15)

        # ==========================================
        # LEFT PANEL: THE CALENDAR ENGINE
        # ==========================================
        ctk.CTkLabel(self.left_panel, text="Select Planning Date Slot", 
                     font=("Helvetica", 16, "bold")).pack(pady=(5, 5))

        # Core tkcalendar Widget Instantiation with past dates blocked out
        self.calendar = Calendar(
            self.left_panel, 
            selectmode="day",
            year=date.today().year,
            month=date.today().month,
            day=date.today().day,
            mindate=date.today(),  
            background="#1F6AA5", 
            foreground="white", 
            headersbackground="gray20",
            headersforeground="white",
            selectbackground="#4CAF50",
            selectforeground="white",
            normalbackground="gray25",
            normalforeground="white",
            weekendbackground="gray22",
            weekendforeground="white",
            othermonthbackground="gray30",
            othermonthforeground="gray50"
        )
        self.calendar.pack(pady=10, padx=15, fill="both", expand=True)
        self.calendar.bind("<<CalendarSelected>>", lambda e: self.load_selected_day_plan())

        # ==========================================
        # RIGHT PANEL: SCHEDULING INTERFACE
        # ==========================================
        ctk.CTkLabel(self.right_panel, text="Assign Scheduled Menu", 
                     font=("Helvetica", 16, "bold"), text_color="#4CAF50").pack(pady=15)

        # Dropdown Setup Elements for Menu Form Slots
        ctk.CTkLabel(self.right_panel, text="Meal Segment Target:", font=("Helvetica", 12, "bold")).pack(anchor="w", padx=20, pady=(5, 2))
        self.slot_cmb = ctk.CTkComboBox(self.right_panel, values=["Breakfast", "Lunch", "Dinner", "Snack", "Dessert"], width=240)
        self.slot_cmb.pack(padx=20)

        ctk.CTkLabel(self.right_panel, text="Select Formulated Recipe:", font=("Helvetica", 12, "bold")).pack(anchor="w", padx=20, pady=(10, 2))
        self.recipe_cmb = ctk.CTkComboBox(self.right_panel, values=["No Recipes Loaded"], width=240)
        self.recipe_cmb.pack(padx=20)

        # Action Button to Commit Plans
        self.save_btn = ctk.CTkButton(self.right_panel, text="Commit Meal Plan", 
                                       fg_color="#4CAF50", command=self.save_meal_plan, width=240)
        self.save_btn.pack(pady=20, padx=20)

        # Real-time visual panel display of what's already saved for the chosen date
        self.agenda_box = ctk.CTkTextbox(self.right_panel, width=260, height=180, font=("Helvetica", 12))
        self.agenda_box.pack(pady=10, padx=20)
        
        # --- SHOPPING LIST ACTION BUTTON ---
        # Restored right beneath your text schedule layout view box
        self.shop_btn = ctk.CTkButton(self.right_panel, text="🛒 Generate Shopping List", 
                                      fg_color="#1F6AA5", hover_color="#144B75", 
                                      command=self.generate_shopping_list, width=240)
        self.shop_btn.pack(pady=(10, 20), padx=20)
        
        # Populate initial values instantly
        self.refresh_recipe_dropdown()
        self.load_selected_day_plan()

    def go_back(self):
        self.controller.show_dashboard()

    def refresh_recipe_dropdown(self):
        try:
            recipes = self.db.get_user_recipes(self.controller.current_user['username'])
            titles = [r['title'] for r in recipes]
            if titles:
                self.recipe_cmb.configure(values=titles)
                self.recipe_cmb.set(titles[0])
            else:
                self.recipe_cmb.configure(values=["Please add recipes first"])
                self.recipe_cmb.set("Please add recipes first")
        except Exception as e:
            print(f"Failed pulling recipes context for dropdown lists: {e}")

    def save_meal_plan(self):
        selected_date_str = self.calendar.get_date()
        
        # Safety Guard Layer for Past Timelines
        try:
            parsed_date = datetime.strptime(selected_date_str, "%m/%d/%y").date()
            if parsed_date < date.today():
                messagebox.showwarning("Timeline Violation", "You cannot schedule a meal plan for a day that has already passed!")
                return
        except Exception as e:
            print(f"Date validation bypass: {e}")

        recipe_choice = self.recipe_cmb.get()
        if recipe_choice in ["No Recipes Loaded", "Please add recipes first", ""]:
            messagebox.showwarning("Missing Item", "Please select a valid recipe from your library before saving!")
            return

        # FIXED HERE: Providing BOTH 'owner' and 'username' keys so it satisfies whatever your database.py script checks for!
        plan_data = {
            "owner": self.controller.current_user['username'],
            "username": self.controller.current_user['username'],
            "date": selected_date_str,
            "slot": self.slot_cmb.get(),
            "recipe_title": recipe_choice
        }

        try:
            self.db.save_meal_plan(plan_data)
            messagebox.showinfo("Success", f"{self.slot_cmb.get()} plan successfully locked in!")
            self.load_selected_day_plan()
        except Exception as e:
            messagebox.showerror("Database Write Failure", f"Failed pushing planner log profile:\n{e}")

    def load_selected_day_plan(self):
        selected_date_str = self.calendar.get_date()
        self.agenda_box.configure(state="normal")
        self.agenda_box.delete("0.0", "end")
        
        header = f"📅 Schedule for {selected_date_str}\n" + ("=" * 30) + "\n\n"
        self.agenda_box.insert("0.0", header)

        try:
            plans = self.db.get_meal_plans(self.controller.current_user['username'], selected_date_str)
            if plans:
                for p in plans:
                    self.agenda_box.insert("end", f"• {p['slot']}:\n   {p['recipe_title']}\n\n")
            else:
                self.agenda_box.insert("end", "No meals scheduled for this date slot yet.\n\nUse the panel above to build one!")
        except Exception as e:
            self.agenda_box.insert("end", f"Error tracking index logs:\n{e}")
            
        self.agenda_box.configure(state="disabled")

    def generate_shopping_list(self):
        """Compiles an ingredients check list based on the active scheduled meals for the chosen day"""
        selected_date_str = self.calendar.get_date()
        try:
            plans = self.db.get_meal_plans(self.controller.current_user['username'], selected_date_str)
            if not plans:
                messagebox.showinfo("Shopping List", f"No scheduled meals found for {selected_date_str}. Add some meals first!")
                return

            all_ingredients = []
            user_recipes = self.db.get_user_recipes(self.controller.current_user['username'])
            
            # Map out database matches
            recipe_map = {r['title'].lower().strip(): r for r in user_recipes}

            for plan in plans:
                title_lookup = plan['recipe_title'].lower().strip()
                if title_lookup in recipe_map:
                    target_recipe = recipe_map[title_lookup]
                    ingredients = target_recipe.get('ingredients', [])
                    if isinstance(ingredients, list):
                        all_ingredients.extend(ingredients)
                    elif isinstance(ingredients, str):
                        all_ingredients.append(ingredients)

            if not all_ingredients:
                messagebox.showinfo("Shopping List", "The scheduled meals do not have any ingredients listed.")
                return

            # Format list with clean bullet points
            cleaned_ingredients = sorted(list(set([i.strip() for i in all_ingredients if i.strip()])))
            shopping_manifest = f"🛒 Shopping Ingredients List for {selected_date_str}:\n\n"
            shopping_manifest += "\n".join([f" [ ]  {item}" for item in cleaned_ingredients])

            # Show the generated list in a scrollable pop-up window
            shop_win = ctk.CTkToplevel(self)
            shop_win.title("Your Auto-Generated Shopping List")
            shop_win.geometry("420x500")
            shop_win.attributes("-topmost", True)

            txt_display = ctk.CTkTextbox(shop_win, font=("Helvetica", 13))
            txt_display.pack(fill="both", expand=True, padx=15, pady=15)
            txt_display.insert("0.0", shopping_manifest)
            txt_display.configure(state="disabled")

        except Exception as e:
            messagebox.showerror("Error", f"Could not generate items manifest list:\n{e}")