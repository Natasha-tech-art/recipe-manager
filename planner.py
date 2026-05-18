import customtkinter as ctk
from tkcalendar import Calendar
from tkinter import messagebox

class MealPlannerFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        # We use 'parent' to attach to the main window container
        super().__init__(parent, corner_radius=15)
        self.controller = controller
        
        # 1. Page Header
        ctk.CTkLabel(self, text="📅 Meal Planner", font=("Helvetica", 24, "bold")).pack(pady=20)

        # 2. The Calendar (Picking the date)
        # Per your instructions: pick a date to see the meal for that day
        self.cal = Calendar(self, selectmode='day', date_pattern='y-mm-dd')
        self.cal.pack(pady=10, padx=20)
        
        # This triggers load_day_plan every time you click a date
        self.cal.bind("<<CalendarSelected>>", lambda e: self.load_day_plan())

        # 3. The Meal Display (Showing what to prepare)
        self.display_frame = ctk.CTkFrame(self, corner_radius=10)
        self.display_frame.pack(pady=20, padx=40, fill="both", expand=True)

        self.meal_labels = {}
        for meal in ["Breakfast", "Lunch", "Dinner"]:
            ctk.CTkLabel(self.display_frame, text=meal, font=("Helvetica", 12, "gray")).pack(pady=(10, 0))
            self.meal_labels[meal] = ctk.CTkLabel(self.display_frame, text="Empty", font=("Helvetica", 16, "bold"))
            self.meal_labels[meal].pack(pady=(0, 10))

        # 4. Action Buttons
        self.btn_container = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_container.pack(pady=20)

        ctk.CTkButton(self.btn_container, text="Schedule Meal", command=self.add_meal).pack(side="left", padx=10)
        ctk.CTkButton(self.btn_container, text="Back to Vault", fg_color="gray30", 
                      command=self.controller.show_dashboard).pack(side="left", padx=10)

    def load_day_plan(self):
        selected_date = self.cal.get_date()
        # Uses the database functions from the main controller
        plan = self.controller.db.get_meal_plan(selected_date, self.controller.current_user['username'])
        
        for meal in ["Breakfast", "Lunch", "Dinner"]:
            if plan and meal.lower() in plan:
                self.plan_text = plan[meal.lower()]
                self.meal_labels[meal].configure(text=self.plan_text)
            else:
                self.meal_labels[meal].configure(text="No Meal Planned")

    def add_meal(self):
        self.meal_type = ctk.CTkInputDialog(text="Meal (Breakfast/Lunch/Dinner):", title="Slot").get_input()
        if not self.meal_type: return
        
        self.recipe_name = ctk.CTkInputDialog(text="Recipe Name:", title="Selection").get_input()
        
        if self.recipe_name:
            self.plan_data = {
                "date": self.cal.get_date(),
                "owner": self.controller.current_user['username'],
                self.meal_type.lower(): self.recipe_name
            }
            self.controller.db.save_meal_plan(self.plan_data)
            self.load_day_plan()