import hashlib
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId

class Database:
    def __init__(self):
        # Replace this URI with your actual MongoDB connection string
        self.uri = "mongodb+srv://natashabolyn4_db_user:xuOfmtUe3zgxk4AD@recipe-manager.gjr3ep.mongodb.net/?retryWrites=true&w=majority"
        self.client = MongoClient(self.uri, server_api=ServerApi('1'))
        self.db = self.client['RecipeManagerDB']
        
        # Collections
        self.users = self.db['users']
        self.recipes = self.db['recipes']
        self.meal_plans = self.db['meal_plans']

    def create_user(self, username, password):
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        if self.users.find_one({"username": username}):
            return False, "Username already exists!"
        self.users.insert_one({"username": username, "password": hashed_pw})
        return True, "Account created successfully!"

    def login_user(self, username, password):
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        user = self.users.find_one({"username": username, "password": hashed_pw})
        return user if user else None

    def add_recipe(self, recipe_data):
        try:
            return self.recipes.insert_one(recipe_data)
        except Exception as e:
            print(f"DB Error: {e}")
            return None

    def get_user_recipes(self, username):
        return list(self.recipes.find({"owner": username}))

    def update_recipe(self, recipe_id, updated_data):
        try:
            return self.recipes.update_one(
                {"_id": ObjectId(recipe_id)}, 
                {"$set": updated_data}
            )
        except Exception as e:
            print(f"Update Error: {e}")
            return None

    def delete_recipe(self, recipe_id):
        try:
            return self.recipes.delete_one({"_id": ObjectId(recipe_id)})
        except Exception as e:
            print(f"Delete Error: {e}")
            return None

    def search_recipes(self, username, query):
        try:
            return list(self.recipes.find({
                "owner": username,
                "$or": [
                    {"title": {"$regex": query, "$options": "i"}},
                    {"category": {"$regex": query, "$options": "i"}},
                    {"cuisine": {"$regex": query, "$options": "i"}}
                ]
            }))
        except Exception as e:
            print(f"Search Error: {e}")
            return []

    def save_meal_plan(self, plan_data):
        try:
            return self.meal_plans.update_one(
                {"date": plan_data["date"], "owner": plan_data["owner"]},
                {"$set": plan_data},
                upsert=True
            )
        except Exception as e:
            print(f"Planner Save Error: {e}")
            return None

    def get_meal_plan(self, date, username):
        try:
            return self.meal_plans.find_one({"date": date, "owner": username})
        except Exception as e:
            print(f"Planner Get Error: {e}")
            return None