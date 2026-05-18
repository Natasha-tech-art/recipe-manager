import customtkinter as ctk
from tkinter import messagebox
from tkcalendar import Calendar
from datetime import datetime

class MealPlannerFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, corner_radius=15)
        self.controller = controller
        self.db = controller.db
        
        # Capture current system date timestamp
        self.today_date = datetime.now().strftime("%Y-%m-%d")
        self.selected_date = self.today_date

        # Left Column Layout Panel: Interactive Calendar Layout
        self.left_panel = ctk.CTkFrame(self, width=400)
        self.left_panel.pack(side="left", fill="both", expand=True, padx=15, pady=15)

        ctk.CTkLabel(self.left_panel, text="Select Planning Date Slot", font=("Helvetica", 16, "bold")).pack(pady=10)

        # Main Graphic Calendar Element
        self.cal = Calendar(self.left_panel, selectmode="day", date_pattern="yyyy-mm-dd",
                            background="#1F6AA5", foreground="white", headersbackground="gray20")
        self.cal.pack(pady=10, padx=10, fill="both", expand=True)
        self.cal.bind("<<CalendarSelected>>", self.on_date_changed)

        # Right Column Layout Panel: Menu Input Form Layout
        self.right_panel = ctk.CTkFrame(self, corner_radius=10)
        self.right_panel.pack(side="right", fill="both", expand=True, padx=15, pady=15)

        # Dynamic Date Display Header Panel
        self.date_header_lbl = ctk.CTkLabel(self.right_panel, text=f"📅 Menu Schedule for: {self.selected_date}", 
                                           font=("Helvetica", 18, "bold"), text_color="#4CAF50")
        self.date_header_lbl.pack(pady=15)

        # Pull clean user recipes list array values straight from database layer
        self.user_recipes = self.db.get_user_recipes(self.controller.current_user['username'])
        self.recipe_options = [" [ Clear Option ] "] + [r['title'] for r in self.user_recipes]

        # Menu Options ComboBox Dropdowns Initialization
        ctk.CTkLabel(self.right_panel, text="🍳 Breakfast Selection Menu", font=("Helvetica", 12, "bold")).pack(pady=(10,2))
        self.bf_cmb = ctk.CTkComboBox(self.right_panel, values=self.recipe_options, width=320)
        self.bf_cmb.pack(pady=5)

        ctk.CTkLabel(self.right_panel, text="🥗 Lunch Selection Menu", font=("Helvetica", 12, "bold")).pack(pady=(10,2))
        self.lh_cmb = ctk.CTkComboBox(self.right_panel, values=self.recipe_options, width=320)
        self.lh_cmb.pack(pady=5)

        ctk.CTkLabel(self.right_panel, text="🍗 Dinner Selection Menu", font=("Helvetica", 12, "bold")).pack(pady=(10,2))
        self.dn_cmb = ctk.CTkComboBox(self.right_panel, values=self.recipe_options, width=320)
        self.dn_cmb.pack(pady=5)

        # Sync Action Panel
        btn_frame = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        btn_frame.pack(pady=25)

        ctk.CTkButton(btn_frame, text="Commit Menu Plan", fg_color="#4CAF50", command=self.commit_plan_vault).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Generate Shopping List", fg_color="#FF9800", text_color="white", command=self.open_shopping_list_sheet).pack(side="left", padx=10)
        ctk.CTkButton(self.right_panel, text="↩️ Dashboard Home", fg_color="gray30", command=self.controller.show_dashboard).pack(side="bottom", pady=15)

        # Load any existing meal plans for today's date automatically
        self.fetch_saved_plan_details(self.selected_date)

    def on_date_changed(self, event=None):
        self.selected_date = self.cal.get_date()
        # Actively change heading layout element text instantly above dropdown options sheet
        self.date_header_lbl.configure(text=f"📅 Menu Schedule for: {self.selected_date}")
        self.fetch_saved_plan_details(self.selected_date)

    def fetch_saved_plan_details(self, date_string):
        try:
            plan = self.db.db.meal_plans.find_one({"date": date_string, "owner": self.controller.current_user['username']})
            if plan:
                self.bf_cmb.set(plan.get('breakfast', ' [ Clear Option ] '))
                self.lh_cmb.set(plan.get('lunch', ' [ Clear Option ] '))
                self.dn_cmb.set(plan.get('dinner', ' [ Clear Option ] '))
            else:
                self.bf_cmb.set(' [ Clear Option ] ')
                self.lh_cmb.set(' [ Clear Option ] ')
                self.dn_cmb.set(' [ Clear Option ] ')
        except Exception:
            pass

    def commit_plan_vault(self):
        # Strict Calendar Date Lock Validation Engine
        if self.selected_date < self.today_date:
            messagebox.showerror("Validation Action Blocked", "Past calendars cannot be updated. Please select an upcoming date slot.")
            return

        def clean_val(val):
            return "" if val == " [ Clear Option ] " else val

        plan_document = {
            "date": self.selected_date,
            "owner": self.controller.current_user['username'],
            "breakfast": clean_val(self.bf_cmb.get()),
            "lunch": clean_val(self.lh_cmb.get()),
            "dinner": clean_val(self.dn_cmb.get())
        }
        try:
            self.db.db.meal_plans.update_one(
                {"date": self.selected_date, "owner": self.controller.current_user['username']},
                {"$set": plan_document},
                upsert=True
            )
            messagebox.showinfo("Success", f"Meal plan cleanly locked for {self.selected_date}!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed syncing plan entry:\n{e}")

    def open_shopping_list_sheet(self):
        # Extract and bundle list array items together
        meals = [self.bf_cmb.get(), self.lh_cmb.get(), self.dn_cmb.get()]
        cleared_meals = [m for m in meals if m and m != " [ Clear Option ] "]
        
        shopping_ingredients = []
        for meal_title in cleared_meals:
            recipe = self.db.db.recipes.find_one({"title": meal_title, "owner": self.controller.current_user['username']})
            if recipe and "ingredients" in recipe:
                shopping_ingredients.extend(recipe["ingredients"])

        # Display window
        list_win = ctk.CTkToplevel(self)
        list_win.title(f"Shopping List: {self.selected_date}")
        list_win.geometry("450x550")
        list_win.attributes("-topmost", True)

        ctk.CTkLabel(list_win, text=f"Shopping Checklist ({self.selected_date})", font=("Helvetica", 16, "bold")).pack(pady=15)
        
        txt_area = ctk.CTkTextbox(list_win, width=380, height=400, font=("Helvetica", 13))
        txt_area.pack(padx=20, pady=10)

        unique_items = list(set([i.strip() for i in shopping_ingredients if i.strip()]))
        if unique_items:
            txt_area.insert("0.0", "\n".join([f" [ ]  {item}" for item in unique_items]))
        else:
            txt_area.insert("0.0", "No ingredients found. Make sure your planned recipes have ingredient checklists saved!")
        txt_area.configure(state="disabled")