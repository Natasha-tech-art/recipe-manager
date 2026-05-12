import hashlib
from pymongo import MongoClient
from pymongo.server_api import ServerApi

class Database:
    def __init__(self):
        # Replace the URI below with your actual MongoDB connection string
        self.uri = "mongodb+srv://natashabolyn4_db_user:xuOfmtUe3zgxk4AD@recipe-manager.gjr3epx.mongodb.net/?appName=recipe-manager"
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