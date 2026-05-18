import customtkinter as ctk
from tkcalendar import Calendar
from tkinter import messagebox

class MealPlannerFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, corner_radius=15)
        self.controller = controller
        
        # Page Title
        ctk.CTkLabel(self, text="📅 Weekly Meal Planner", font=("Helvetica", 24, "bold")).pack(pady=20)

        # Calendar View
        self.cal = Calendar(self, selectmode='day', date_pattern='y-mm-dd')
        self.cal.pack(pady=10, padx=20)
        self.cal.bind("<<CalendarSelected>>", lambda e: self.load_day_plan())

        # Meal Menu Breakdown Box
        self.display_frame = ctk.CTkFrame(self, corner_radius=10)
        self.display_frame.pack(pady=20, padx=40, fill="both", expand=True)

        self.meal_labels = {}
        for meal in ["Breakfast", "Lunch", "Dinner"]:
            ctk.CTkLabel(self.display_frame, text=meal, font=("Helvetica", 12, "gray")).pack(pady=(10, 0))
            self.meal_labels[meal] = ctk.CTkLabel(self.display_frame, text="No Meal Planned", font=("Helvetica", 16, "bold"))
            self.meal_labels[meal].pack(pady=(0, 10))

        # Bottom Buttons
        self.btn_container = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_container.pack(side="bottom", pady=20)

        ctk.CTkButton(self.btn_container, text="Schedule Meal", command=self.add_meal).pack(side="left", padx=10)
        ctk.CTkButton(self.btn_container, text="Back to Vault", fg_color="gray30", 
                      command=self.controller.show_dashboard).pack(side="left", padx=10)
        
        # Load automatically for the currently highlighted date on open
        self.load_day_plan()

    def load_day_plan(self):
        selected_date = self.cal.get_date()
        plan = self.controller.db.get_meal_plan(selected_date, self.controller.current_user['username'])
        
        for meal in ["Breakfast", "Lunch", "Dinner"]:
            if plan and meal.lower() in plan:
                self.meal_labels[meal].configure(text=plan[meal.lower()])
            else:
                self.meal_labels[meal].configure(text="No Meal Planned")

    def add_meal(self):
        meal_type = ctk.CTkInputDialog(text="Enter Meal Type (Breakfast/Lunch/Dinner):", title="Meal Slot").get_input()
        if not meal_type: return
        meal_type = meal_type.strip().capitalize()
        
        if meal_type not in ["Breakfast", "Lunch", "Dinner"]:
            messagebox.showwarning("Input Error", "Please type Breakfast, Lunch, or Dinner.")
            return

        recipe_name = ctk.CTkInputDialog(text=f"What are you cooking for {meal_type}?", title="Recipe Name").get_input()
        if not recipe_name: return

        plan_data = {
            "date": self.cal.get_date(),
            "owner": self.controller.current_user['username'],
            meal_type.lower(): recipe_name.strip()
        }
        
        self.controller.db.save_meal_plan(plan_data)
        self.load_day_plan()
        messagebox.showinfo("Success", f"Scheduled {recipe_name} for {meal_type}!")