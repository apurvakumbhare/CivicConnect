import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

async def verify():
    client = AsyncIOMotorClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
    db = client.ai_analysis_db
    collection = db.analysis_records
    
    # Check if any records still have "Rate-limited"
    count = await collection.count_documents({"priority_reasoning": {"$regex": "Rate-limited"}})
    print(f"Remaining rate-limited records: {count}")
    
    # Check a sample record
    doc = await collection.find_one({"document_insights": "No specific insights extracted for this ticket."})
    if doc:
        print(f"Sample Form ID: {doc['form_id']}")
        print(f"Insights: {doc['document_insights']}")
        print(f"Reasoning: {doc['priority_reasoning'][:50]}...")
    else:
        print("No cleaned records found via match - check regex.")

if __name__ == "__main__":
    asyncio.run(verify())
