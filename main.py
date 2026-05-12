import tkinter as tk
from tkinter import ttk, messagebox
from database import Database

class RecipeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SmartMeal Pro - Recipe & Meal Planner")
        self.root.geometry("1200x700")
        
        # Initialize Database
        self.db = Database()
        if not self.db.test_connection():
            messagebox.showerror("Error", "Could not connect to Database.")
        
        self.setup_layout()

    def setup_layout(self):
        # Main Container
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left Panel (Recipe List)
        self.left_panel = ttk.LabelFrame(self.main_container, text="Recipes", width=300)
        self.left_panel.pack(side="left", fill="y", padx=5, pady=5)
        
        # Center Panel (Details)
        self.center_panel = ttk.LabelFrame(self.main_container, text="Recipe Details")
        self.center_panel.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        # Right Panel (Planner)
        self.right_panel = ttk.LabelFrame(self.main_container, text="Meal Planner", width=250)
        self.right_panel.pack(side="right", fill="y", padx=5, pady=5)

if __name__ == "__main__":
    root = tk.Tk()
    app = RecipeApp(root)
    root.mainloop()
    
    def setup_layout(self):
        # ... (Keep your existing panel code) ...
        
        # Add a "New Recipe" button to the left panel
        self.add_btn = ttk.Button(self.left_panel, text="+ Add New Recipe", command=self.open_add_recipe_window)
        self.add_btn.pack(fill="x", padx=10, pady=10)

    def open_add_recipe_window(self):
        # Create a new pop-up window
        self.add_win = tk.Toplevel(self.root)
        self.add_win.title("Add New Recipe")
        self.add_win.geometry("400x500")

        # Basic Fields
        ttk.Label(self.add_win, text="Recipe Title:").pack(pady=5)
        self.title_entry = ttk.Entry(self.add_win, width=40)
        self.title_entry.pack()

        ttk.Label(self.add_win, text="Ingredients (comma separated):").pack(pady=5)
        self.ing_entry = ttk.Entry(self.add_win, width=40)
        self.ing_entry.pack()

        ttk.Label(self.add_win, text="Category:").pack(pady=5)
        self.cat_combo = ttk.Combobox(self.add_win, values=["Breakfast", "Lunch", "Dinner", "Dessert"])
        self.cat_combo.pack()

        # Save Button
        ttk.Button(self.add_win, text="Save to Database", command=self.save_recipe).pack(pady=20)

    def save_recipe(self):
        # Gather data from the form
        recipe = {
            "title": self.title_entry.get(),
            "ingredients": self.ing_entry.get().split(","), # Turns string into a list
            "category": self.cat_combo.get(),
            "created_at": "2026-05-12" # Use current date
        }

        # Send to Database
        if self.db.add_recipe(recipe):
            messagebox.showinfo("Success", "Recipe saved to MongoDB!")
            self.add_win.destroy() # Close the pop-up
        else:
            messagebox.showerror("Error", "Failed to save recipe.")