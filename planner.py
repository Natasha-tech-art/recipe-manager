import customtkinter as ctk
from tkcalendar import Calendar
from tkinter import messagebox

class MealPlannerFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, corner_radius=15)
        self.controller = controller
        
        # Title
        ctk.CTkLabel(self, text="Meal Planner & Calendar", font=("Helvetica", 24, "bold")).pack(pady=20)

        # Calendar Widget
        self.cal = Calendar(self, selectmode='day', date_pattern='y-mm-dd')
        self.cal.pack(pady=10, padx=20, fill="x")
        
        # Bind clicking a date to load that day's meal
        self.cal.bind("<<CalendarSelected>>", lambda e: self.load_day_plan())

        # Display Area
        self.info_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.info_frame.pack(pady=20, padx=20, fill="both", expand=True)

        self.meal_labels = {}
        for meal in ["Breakfast", "Lunch", "Dinner"]:
            ctk.CTkLabel(self.info_frame, text=meal, font=("Helvetica", 12, "gray")).pack(anchor="w")
            self.meal_labels[meal] = ctk.CTkLabel(self.info_frame, text="Not Scheduled", font=("Helvetica", 16, "bold"))
            self.meal_labels[meal].pack(anchor="w", pady=(0, 10))

        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        ctk.CTkButton(btn_frame, text="Schedule Meal", command=self.add_meal_popup).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Back to Vault", fg_color="gray30", command=self.controller.show_dashboard).pack(side="left", padx=10)

    def load_day_plan(self):
        selected_date = self.cal.get_date()
        plan = self.controller.db.get_meal_plan(selected_date, self.controller.current_user['username'])
        
        for meal in ["Breakfast", "Lunch", "Dinner"]:
            if plan and meal.lower() in plan:
                self.meal_labels[meal].configure(text=plan[meal.lower()])
            else:
                self.meal_labels[meal].configure(text="Not Scheduled")

    def add_meal_popup(self):
        meal_type = ctk.CTkInputDialog(text="Enter Meal (Breakfast/Lunch/Dinner):", title="Meal Slot").get_input()
        if not meal_type: return
        
        recipe_name = ctk.CTkInputDialog(text="Enter Recipe Name:", title="Select Recipe").get_input()
        
        if meal_type and recipe_name:
            plan_data = {
                "date": self.cal.get_date(),
                "owner": self.controller.current_user['username'],
                meal_type.lower(): recipe_name
            }
            self.controller.db.save_meal_plan(plan_data)
            self.load_day_plan()
            messagebox.showinfo("Success", f"{recipe_name} added to {meal_type}!")