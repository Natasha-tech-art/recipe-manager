import hashlib
from pymongo import MongoClient
from pymongo.server_api import ServerApi

class Database:
    def __init__(self):
        # Replace the string below with your actual MongoDB URI
        self.uri = "mongodb+srv://natashabolyn4_db_user:xuOfmtUe3zgxk4AD@recipe-manager.gjr3epx.mongodb.net/?appName=recipe-manager"
        self.client = MongoClient(self.uri, server_api=ServerApi('1'))
        self.db = self.client['RecipeManagerDB']
        
        # Collections
        self.recipes = self.db['recipes']
        self.meal_plans = self.db['meal_plans']
        self.users = self.db['users']
        
        def create_user(self, username, password):
            if self.users.find_one({"username": username}):
                return False, "Username already exists"
            
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            self.users.insert_one({"username": username, "password": hashed_password})
            return True, "User created successfully"

    def login_user(self, username, password):
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        return self.users.find_one({"username": username, "password": hashed_password})

    def test_connection(self):
        try:
            self.client.admin.command('ping')
            print("Successfully connected to MongoDB!")
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False

# For testing purposes
if __name__ == "__main__":
    db_manager = Database()
    db_manager.test_connection()
    
    def add_recipe(self, recipe_data):
        try:
            result = self.recipes.insert_one(recipe_data)
            return result.inserted_id
        except Exception as e:
            print(f"Error adding recipe: {e}")
            return None