import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

async def check():
    client = AsyncIOMotorClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
    db = client.ai_analysis_db
    doc = await db.analysis_records.find_one()
    if doc:
        print("Keys:", list(doc.keys()))
        print("document_insights type:", type(doc.get("document_insights")))
        print("document_insights value:", doc.get("document_insights"))
    else:
        print("No documents found")

if __name__ == "__main__":
    asyncio.run(check())
