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