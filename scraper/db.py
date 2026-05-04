import os
import hashlib
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DATABASE_NAME", "obituary_db")

class Database:
    def __init__(self):
        if not MONGO_URI:
            raise ValueError("MONGODB_URI is not set in environment variables")
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DB_NAME]
        self.collection = self.db["obituaries"]
        self._setup_indexes()

    def _setup_indexes(self):
        # Create indexes for fast lookup and uniqueness
        self.collection.create_index([("slug", ASCENDING)], unique=True)
        self.collection.create_index([("hash", ASCENDING)], unique=True)
        self.collection.create_index([("created_at", DESCENDING)])

    def generate_hash(self, text):
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    def insert_obituary(self, data):
        """
        Inserts obituary if hash and slug are unique.
        """
        try:
            # Ensure hash is present
            if 'hash' not in data or not data['hash']:
                data['hash'] = self.generate_hash(data['content'])
            
            result = self.collection.insert_one(data)
            return str(result.inserted_id)
        except DuplicateKeyError:
            print(f"Duplicate entry found for slug: {data.get('slug')} or hash")
            return None
        except Exception as e:
            print(f"Error inserting into DB: {e}")
            return None
