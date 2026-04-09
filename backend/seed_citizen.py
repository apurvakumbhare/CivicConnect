import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from shared.utils.auth_utils import get_password_hash
from dotenv import load_dotenv

load_dotenv()

async def seed_citizen():
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/civicConnect")
    client = AsyncIOMotorClient(mongo_uri)
    db = client.user_db
    users_collection = db.users

    # Check if test citizen exists
    mobile = "9876543210"
    existing = await users_collection.find_one({"mobile_number": mobile})
    
    if existing:
        print(f"Citizen with mobile {mobile} already exists.")
        return

    citizen_data = {
        "full_name": "Test Citizen",
        "mobile_number": mobile,
        "residential_address": "123 Civic Lane, Mumbai",
        "email": "citizen@example.com",
        "language_preference": "English",
        "password": get_password_hash("Citizen@123")
    }

    result = await users_collection.insert_one(citizen_data)
    print(f"Test Citizen created with ID: {result.inserted_id}")
    print(f"Mobile: {mobile}")
    print(f"Password: Citizen@123")

if __name__ == "__main__":
    asyncio.run(seed_citizen())
