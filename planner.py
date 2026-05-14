import customtkinter as ctk
from tkcalendar import Calendar
from tkinter import messagebox

class MealPlannerFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        # We give it a slightly different color so you know it switched!
        super().__init__(parent, corner_radius=15, fg_color=("gray95", "gray12"))
        self.controller = controller
        
        # Title
        ctk.CTkLabel(self, text="📅 Weekly Meal Planner", font=("Helvetica", 24, "bold")).pack(pady=20)

        # 1. THE CALENDAR
        # This is where you pick the date as per your instructions
        self.cal = Calendar(self, selectmode='day', date_pattern='y-mm-dd')
        self.cal.pack(pady=10, padx=20)
        
        # Bind the click event
        self.cal.bind("<<CalendarSelected>>", lambda e: self.load_day_plan())

        # 2. THE DISPLAY AREA
        # This shows what is to be prepared on that day
        self.display_frame = ctk.CTkFrame(self, corner_radius=10)
        self.display_frame.pack(pady=20, padx=40, fill="both", expand=True)

        self.meal_labels = {}
        for meal in ["Breakfast", "Lunch", "Dinner"]:
            ctk.CTkLabel(self.display_frame, text=meal, font=("Helvetica", 12, "gray")).pack(pady=(10, 0))
            self.meal_labels[meal] = ctk.CTkLabel(self.display_frame, text="Empty Slot", font=("Helvetica", 16, "bold"))
            self.meal_labels[meal].pack(pady=(0, 10))

        # 3. ACTION BUTTONS
        btn_container = ctk.CTkFrame(self, fg_color="transparent")
        btn_container.pack(pady=20)

        ctk.CTkButton(btn_container, text="Assign Recipe", command=self.add_meal).pack(side="left", padx=10)
        ctk.CTkButton(btn_container, text="Go to Vault", fg_color="gray30", 
                      command=self.controller.show_dashboard).pack(side="left", padx=10)

    def load_day_plan(self):
        selected_date = self.cal.get_date()
        # Fetch from DB using the controller's database instance
        plan = self.controller.db.get_meal_plan(selected_date, self.controller.current_user['username'])
        
        for meal in ["Breakfast", "Lunch", "Dinner"]:
            if plan and meal.lower() in plan:
                self.meal_labels[meal].configure(text=plan[meal.lower()])
            else:
                self.meal_labels[meal].configure(text="No Meal Planned")

    def add_meal(self):
        meal_type = ctk.CTkInputDialog(text="Enter Meal Type (Breakfast/Lunch/Dinner):", title="Schedule").get_input()
        if not meal_type: return
        
        recipe_name = ctk.CTkInputDialog(text="Enter the Recipe Name:", title="Recipe Selection").get_input()
        
        if recipe_name:
            plan_data = {
                "date": self.cal.get_date(),
                "owner": self.controller.current_user['username'],
                meal_type.lower(): recipe_name
            }
            self.controller.db.save_meal_plan(plan_data)
            self.load_day_plan() # Refresh the view immediately
            messagebox.showinfo("Success", f"{recipe_name} scheduled for {meal_type}!")