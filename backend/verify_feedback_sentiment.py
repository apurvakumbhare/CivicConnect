import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def verify():
    client = AsyncIOMotorClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
    db = client.feedback_db
    feedbacks = await db.feedbacks.find({}).to_list(100)
    for fb in feedbacks:
        print(f"ID: {fb.get('feedback_id')}, Sentiment: {fb.get('sentiment')}, Type: {type(fb.get('sentiment'))}")

if __name__ == "__main__":
    asyncio.run(verify())
