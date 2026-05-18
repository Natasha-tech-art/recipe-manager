import customtkinter as ctk
from tkinter import messagebox
from tkcalendar import Calendar

class MealPlannerFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, corner_radius=15)
        self.controller = controller
        
        # --- TOP TITLE BAR ---
        self.header = ctk.CTkLabel(self, text="📅 Smart Meal Planner & Shopping Assistant", font=("Helvetica", 22, "bold"))
        self.header.pack(pady=15)

        # --- THREE-PANEL LAYOUT CONTAINER ---
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=15, pady=10)

        # PANEL 1: Left Side (Calendar Control)
        self.left_panel = ctk.CTkFrame(self.main_container, width=300, corner_radius=10)
        self.left_panel.pack(side="left", fill="both", padx=10, pady=5)
        
        ctk.CTkLabel(self.left_panel, text="Select Date", font=("Helvetica", 14, "bold")).pack(pady=10)
        self.cal = Calendar(self.left_panel, selectmode='day', date_pattern='y-mm-dd')
        self.cal.pack(pady=5, padx=10)
        self.cal.bind("<<CalendarSelected>>", lambda e: self.load_day_plan())

        # PANEL 2: Center (Meal Schedule Viewer)
        self.center_panel = ctk.CTkFrame(self.main_container, corner_radius=10, fg_color=("gray90", "gray16"))
        self.center_panel.pack(side="left", fill="both", expand=True, padx=10, pady=5)
        
        ctk.CTkLabel(self.center_panel, text="Today's Menu Slots", font=("Helvetica", 14, "bold"), text_color="#4CAF50").pack(pady=10)

        self.meal_labels = {}
        for meal in ["Breakfast", "Lunch", "Dinner"]:
            meal_box = ctk.CTkFrame(self.center_panel, fg_color=("gray85", "gray22"), corner_radius=6)
            meal_box.pack(fill="x", padx=15, pady=6)
            
            ctk.CTkLabel(meal_box, text=f"{meal}:", font=("Helvetica", 12, "bold"), text_color="gray").pack(anchor="w", padx=10, pady=2)
            self.meal_labels[meal] = ctk.CTkLabel(meal_box, text="No Meal Scheduled", font=("Helvetica", 14, "bold"))
            self.meal_labels[meal].pack(anchor="w", padx=20, pady=(0, 5))

        # PANEL 3: Right Side (Shopping List Generator)
        self.right_panel = ctk.CTkFrame(self.main_container, width=280, corner_radius=10)
        self.right_panel.pack(side="right", fill="both", padx=10, pady=5)
        
        ctk.CTkLabel(self.right_panel, text="🛒 Auto Shopping List", font=("Helvetica", 14, "bold")).pack(pady=10)
        
        self.list_box = ctk.CTkTextbox(self.right_panel, width=240, height=250, font=("Helvetica", 12))
        self.list_box.pack(padx=10, pady=5, fill="both", expand=True)
        
        ctk.CTkButton(self.right_panel, text="Generate From Plan", fg_color="#4CAF50", hover_color="#388E3C",
                      command=self.generate_shopping_list).pack(fill="x", padx=15, pady=10)

        # --- BOTTOM ACTION NAVIGATION BAR ---
        self.btn_container = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_container.pack(side="bottom", pady=15)

        ctk.CTkButton(self.btn_container, text="Assign Recipe to Slot", command=self.add_meal).pack(side="left", padx=10)
        ctk.CTkButton(self.btn_container, text="Return to Vault", fg_color="gray30", 
                      command=self.controller.show_dashboard).pack(side="left", padx=10)
        
        self.load_day_plan()

    def load_day_plan(self):
        selected_date = self.cal.get_date()
        try:
            plan = self.controller.db.get_meal_plan(selected_date, self.controller.current_user['username'])
            for meal in ["Breakfast", "Lunch", "Dinner"]:
                if plan and plan.get(meal.lower()):
                    self.meal_labels[meal].configure(text=plan[meal.lower()])
                else:
                    self.meal_labels[meal].configure(text="No Meal Scheduled")
        except Exception as e:
            print(f"Error reading meal layout: {e}")

    def add_meal(self):
        meal_type = ctk.CTkInputDialog(text="Enter window slot (Breakfast / Lunch / Dinner):", title="Schedule Menu").get_input()
        if not meal_type: return
        meal_type = meal_type.strip().capitalize()
        
        if meal_type not in ["Breakfast", "Lunch", "Dinner"]:
            messagebox.showwarning("Selection Error", "Please type either Breakfast, Lunch, or Dinner.")
            return

        recipe_name = ctk.CTkInputDialog(text=f"What recipe title are you cooking for {meal_type}?", title="Recipe Matching").get_input()
        if not recipe_name or not recipe_name.strip(): return

        plan_data = {
            "date": self.cal.get_date(),
            "owner": self.controller.current_user['username'],
            meal_type.lower(): recipe_name.strip()
        }
        
        try:
            self.controller.db.save_meal_plan(plan_data)
            self.load_day_plan()
            messagebox.showinfo("Schedule Updated", f"{recipe_name} assigned to {meal_type}!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed saving schedule slot: {e}")

    def generate_shopping_list(self):
        self.list_box.delete("0.0", "end")
        selected_date = self.cal.get_date()
        username = self.controller.current_user['username']
        
        try:
            plan = self.controller.db.get_meal_plan(selected_date, username)
            if not plan:
                self.list_box.insert("0.0", f"No plans found for {selected_date}.\nSchedule a meal first!")
                return
                
            ingredients_needed = []
            all_recipes = self.controller.db.get_user_recipes(username)
            
            # Map out planned dishes
            planned_dishes = [plan.get("breakfast"), plan.get("lunch"), plan.get("dinner")]
            planned_dishes = [d.lower() for d in planned_dishes if d]
            
            for recipe in all_recipes:
                if recipe['title'].lower() in planned_dishes:
                    ingredients_needed.extend(recipe['ingredients'])
            
            if not ingredients_needed:
                self.list_box.insert("0.0", "No matching recipe ingredient checklists found in your vault database.")
                return
                
            # Clean list values and output checkboxes
            self.list_box.insert("0.0", f"📋 SHOPPING LIST FOR {selected_date}\n=====================\n\n")
            unique_ingredients = sorted(list(set([i.strip() for i in ingredients_needed if i.strip()])))
            for ing in unique_ingredients:
                self.list_box.insert("end", f"[ ] {ing}\n")
                
        except Exception as e:
            messagebox.showerror("Aggregation Error", f"Could not map shopping list details:\n{e}")