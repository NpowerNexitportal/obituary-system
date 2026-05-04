import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DATABASE_NAME", "obituary_db")

if not MONGO_URI:
    raise ValueError("MONGODB_URI is not set. Please set it in .env file.")

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]
collection = db["obituaries"]
