import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def list_all_staff():
    client = AsyncIOMotorClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
    db = client.superuserdb
    users = await db.staff_users.find({}).to_list(100)
    print("--- Staff Users ---")
    for u in users:
        print(f"Name: {u.get('full_name')}, Email: {u.get('email')}, Role: {u.get('role')}")

if __name__ == "__main__":
    asyncio.run(list_all_staff())
