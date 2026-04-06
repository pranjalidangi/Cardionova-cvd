from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGODB_URI") or os.getenv("MONGO_URI")  # handles both
client = MongoClient(MONGO_URI)
db = client["cardionova"]

predictions_collection = db["predictions"]

def get_db():
    return db

def ping_db():
    client.admin.command("ping")
    print("✅ MongoDB Atlas connected.")
