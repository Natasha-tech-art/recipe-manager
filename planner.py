import customtkinter as ctk
from tkinter import messagebox
from tkcalendar import Calendar
from datetime import date, datetime

class MealPlannerFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, corner_radius=15, fg_color="transparent")
        self.controller = controller
        self.db = controller.db

        # Split left and right windows layout
        self.left_panel = ctk.CTkFrame(self, corner_radius=15)
        self.left_panel.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self.right_panel = ctk.CTkFrame(self, width=320, corner_radius=15)
        self.right_panel.pack(side="right", fill="y", padx=10, pady=10)

        # Back Navigation
        back_btn = ctk.CTkButton(self.left_panel, text="⬅️ Return to Dashboard", 
                                 fg_color="gray30", width=160, command=self.go_back)
        back_btn.pack(anchor="w", padx=15, pady=15)

        ctk.CTkLabel(self.left_panel, text="Select Planning Date Slot", 
                     font=("Helvetica", 16, "bold")).pack(pady=(5, 5))

        # Core Date Picker
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

        # Scheduling Forms Config
        ctk.CTkLabel(self.right_panel, text="Assign Scheduled Menu", 
                     font=("Helvetica", 16, "bold"), text_color="#4CAF50").pack(pady=15)

        ctk.CTkLabel(self.right_panel, text="Meal Segment Target:", font=("Helvetica", 12, "bold")).pack(anchor="w", padx=20, pady=(5, 2))
        self.slot_cmb = ctk.CTkComboBox(self.right_panel, values=["Breakfast", "Lunch", "Dinner", "Snack", "Dessert"], width=240)
        self.slot_cmb.pack(padx=20)

        ctk.CTkLabel(self.right_panel, text="Select Formulated Recipe:", font=("Helvetica", 12, "bold")).pack(anchor="w", padx=20, pady=(10, 2))
        self.recipe_cmb = ctk.CTkComboBox(self.right_panel, values=["No Recipes Loaded"], width=240)
        self.recipe_cmb.pack(padx=20)

        self.save_btn = ctk.CTkButton(self.right_panel, text="Commit Meal Plan", 
                                       fg_color="#4CAF50", command=self.save_meal_plan, width=240)
        self.save_btn.pack(pady=20, padx=20)

        # Dynamic Schedule Display Window box
        self.agenda_box = ctk.CTkTextbox(self.right_panel, width=260, height=180, font=("Helvetica", 12))
        self.agenda_box.pack(pady=10, padx=20)
        
        # Shopping Manifest Engine
        self.shop_btn = ctk.CTkButton(self.right_panel, text="🛒 Generate Shopping List", 
                                      fg_color="#1F6AA5", hover_color="#144B75", 
                                      command=self.generate_shopping_list, width=240)
        self.shop_btn.pack(pady=(10, 20), padx=20)
        
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
            print(f"Dropdown error: {e}")

    def save_meal_plan(self):
        selected_date_str = self.calendar.get_date()
        
        recipe_choice = self.recipe_cmb.get()
        if recipe_choice in ["No Recipes Loaded", "Please add recipes first", ""]:
            messagebox.showwarning("Missing Item", "Select a valid recipe from your collection first!")
            return

        plan_data = {
            "owner": self.controller.current_user['username'],
            "username": self.controller.current_user['username'],
            "date": selected_date_str,
            "slot": self.slot_cmb.get(),
            "recipe_title": recipe_choice
        }

        try:
            self.db.save_meal_plan(plan_data)
            messagebox.showinfo("Success", f"{self.slot_cmb.get()} plan logged perfectly!")
            self.load_selected_day_plan()
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not log meal plan profile:\n{e}")

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
                self.agenda_box.insert("end", "No meals scheduled for this date slot yet.")
        except Exception as e:
            self.agenda_box.insert("end", f"Error pulling agenda lists:\n{e}")
            
        self.agenda_box.configure(state="disabled")

    def generate_shopping_list(self):
        selected_date_str = self.calendar.get_date()
        try:
            plans = self.db.get_meal_plans(self.controller.current_user['username'], selected_date_str)
            if not plans:
                messagebox.showinfo("Shopping List", f"No scheduled meals found for {selected_date_str}.")
                return

            all_ingredients = []
            user_recipes = self.db.get_user_recipes(self.controller.current_user['username'])
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
                messagebox.showinfo("Shopping List", "No ingredients listed inside these scheduled items.")
                return

            cleaned_ingredients = sorted(list(set([i.strip() for i in all_ingredients if i.strip()])))
            shopping_manifest = f"🛒 Shopping Ingredients List for {selected_date_str}:\n\n"
            shopping_manifest += "\n".join([f" [ ]  {item}" for item in cleaned_ingredients])

            shop_win = ctk.CTkToplevel(self)
            shop_win.title("Your Auto-Generated Shopping List")
            shop_win.geometry("420x500")
            shop_win.attributes("-topmost", True)

            txt_display = ctk.CTkTextbox(shop_win, font=("Helvetica", 13))
            txt_display.pack(fill="both", expand=True, padx=15, pady=15)
            txt_display.insert("0.0", shopping_manifest)
            txt_display.configure(state="disabled")

        except Exception as e:
            messagebox.showerror("Error", f"Failed compiling items manifest:\n{e}")