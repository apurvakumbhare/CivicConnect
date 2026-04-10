import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def check_colls():
    client = AsyncIOMotorClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
    db = client.feedback_db
    colls = await db.list_collection_names()
    print(f"Collections in feedback_db: {colls}")
    
    for coll_name in colls:
        count = await db[coll_name].count_documents({})
        print(f"  {coll_name}: {count} documents")
        if count > 0:
            doc = await db[coll_name].find_one({})
            print(f"    Sample: {doc.get('feedback_id', 'no id')}")

if __name__ == "__main__":
    asyncio.run(check_colls())
