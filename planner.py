import customtkinter as ctk
from tkinter import messagebox
from tkcalendar import Calendar
from datetime import date, datetime  # Handlers for current timeline tracking

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

        # Core tkcalendar Widget Instantiation
        # mindate=date.today() automatically blocks out all previous calendar days visually!
        self.calendar = Calendar(
            self.left_panel, 
            selectmode="day",
            year=date.today().year,
            month=date.today().month,
            day=date.today().day,
            mindate=date.today(),  # Visual roadblock for past dates
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
        ctk.CTkLabel(self.right_panel, text="Meal Segment Target:", font=("Helvetica", 12, "bold")).pack(anchor="w", padx=20, pady=(10, 2))
        self.slot_cmb = ctk.CTkComboBox(self.right_panel, values=["Breakfast", "Lunch", "Dinner", "Snack", "Dessert"], width=240)
        self.slot_cmb.pack(padx=20)

        ctk.CTkLabel(self.right_panel, text="Select Formulated Recipe:", font=("Helvetica", 12, "bold")).pack(anchor="w", padx=20, pady=(10, 2))
        self.recipe_cmb = ctk.CTkComboBox(self.right_panel, values=["No Recipes Loaded"], width=240)
        self.recipe_cmb.pack(padx=20)

        # Action Buttons Layout Form Tracker
        self.save_btn = ctk.CTkButton(self.right_panel, text="Commit Meal Plan", 
                                       fg_color="#4CAF50", command=self.save_meal_plan, width=240)
        self.save_btn.pack(pady=25, padx=20)

        # Real-time visual panel display of what's already saved for the chosen date
        self.agenda_box = ctk.CTkTextbox(self.right_panel, width=260, height=240, font=("Helvetica", 12))
        self.agenda_box.pack(pady=10, padx=20)
        
        # Populate initial values instantly
        self.refresh_recipe_dropdown()
        self.load_selected_day_plan()

    def go_back(self):
        self.controller.show_dashboard()

    def refresh_recipe_dropdown(self):
        """Fetches your created recipes from MongoDB and populates the dropdown menu option slot"""
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
        """Validates restrictions and writes scheduling documents down to Database collection"""
        selected_date_str = self.calendar.get_date()  # Typically returns "MM/DD/YY" or "M/D/YY"
        
        # --- STRATEGIC SAFETY GUARD LAYER START ---
        try:
            # Parse tkcalendar text out to compare values exactly with current system date
            parsed_date = datetime.strptime(selected_date_str, "%m/%d/%y").date()
            if parsed_date < date.today():
                messagebox.showwarning("Timeline Violation", "You cannot schedule a meal plan for a day that has already passed!")
                return
        except Exception as e:
            print(f"Date structural safety guard validation bypassed or format variant: {e}")
        # --- STRATEGIC SAFETY GUARD LAYER END ---

        recipe_choice = self.recipe_cmb.get()
        if recipe_choice in ["No Recipes Loaded", "Please add recipes first", ""]:
            messagebox.showwarning("Missing Item", "Please select a valid recipe from your library before saving!")
            return

        plan_data = {
            "username": self.controller.current_user['username'],
            "date": selected_date_str,
            "slot": self.slot_cmb.get(),
            "recipe_title": recipe_choice
        }

        try:
            # Write out to your MongoDB collection cluster index tracking
            self.db.save_meal_plan(plan_data)
            messagebox.showinfo("Success", f"{self.slot_cmb.get()} plan successfully locked in!")
            self.load_selected_day_plan()
        except Exception as e:
            messagebox.showerror("Database Write Failure", f"Failed pushing planner log profile:\n{e}")

    def load_selected_day_plan(self):
        """Reads selected calendar slot dates and displays existing configurations"""
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