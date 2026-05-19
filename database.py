from pymongo import MongoClient
from bson.objectid import ObjectId

class Database:
    def __init__(self):
        # The explicit connection URI linked to your local MongoDB engine
        self.uri = "mongodb+srv://natashabolyn4_db_user:xuOfmtUe3zgxk4AD@recipe-manager.gjr3epx.mongodb.net/?appName=recipe-manager"
        self.client = MongoClient(self.uri)
        
        # Establishing database reference
        self.db = self.client["smartmeal_db"]
        
        # Mapping collections firmly so planner.py and main.py see them instantly
        self.users = self.db["users"]
        self.recipes = self.db["recipes"]
        self.meals = self.db["meals"]
        
        print("🚀 Successfully connected to MongoDB via self.uri!")

    # ==========================================
    # USER ACCOUNT AUTHENTICATION
    # ==========================================
    def create_user(self, username, password):
        if not username or not password:
            return False, "Username and password cannot be empty."
        if self.users.find_one({"username": username}):
            return False, "Username already exists!"
        
        self.users.insert_one({"username": username, "password": password})
        return True, "Account created successfully!"

    def login_user(self, username, password):
        return self.users.find_one({"username": username, "password": password})

    # ==========================================
    # RECIPE VAULT MANAGEMENT
    # ==========================================
    def add_recipe(self, recipe_data):
        return self.recipes.insert_one(recipe_data)

    def get_user_recipes(self, username):
        return list(self.recipes.find({"owner": username}))

    def search_recipes(self, username, query):
        return list(self.recipes.find({
            "owner": username,
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"cuisine": {"$regex": query, "$options": "i"}}
            ]
        }))

    def update_recipe(self, recipe_id, updated_data):
        return self.recipes.update_one({"_id": ObjectId(recipe_id)}, {"$set": updated_data})

    def delete_recipe(self, recipe_id):
        return self.recipes.delete_one({"_id": ObjectId(recipe_id)})

    # ==========================================
    # MEAL PLANNER INTERFACES
    # ==========================================
    def save_meal_plan(self, plan_data):
        """Saves or updates a planned meal segment slot"""
        return self.meals.update_one(
            {
                "username": plan_data["username"],
                "date": plan_data["date"],
                "slot": plan_data["slot"]
            },
            {"$set": plan_data},
            upsert=True
        )

    def get_meal_plans(self, username, date_str):
        """Fetches all scheduled recipe items for a given day."""
        return list(self.meals.find({"username": username, "date": date_str}))