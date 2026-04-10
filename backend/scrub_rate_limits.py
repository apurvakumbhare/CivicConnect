import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

async def scrub_rate_limits():
    client = AsyncIOMotorClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
    db = client.ai_analysis_db
    collection = db.analysis_records
    
    # 1. Clean document_insights
    # Find records where document_insights is a string containing "Error" or "Fallback" or "Venice"
    query = {
        "document_insights": {"$regex": "(?i)Error|Fallback|Venice|Rate-limited"}
    }
    
    records = await collection.find(query).to_list(None)
    print(f"Found {len(records)} records with noisy insights.")
    
    for record in records:
        print(f"  Cleaning {record['form_id']}...")
        await collection.update_one(
            {"_id": record["_id"]},
            {"$set": {"document_insights": "No specific insights extracted for this ticket."}}
        )
        
    # 2. Clean priority_reasoning specifically for rate limited ones
    query_reasoning = {
        "priority_reasoning": {"$regex": "(?i)Rate-limited|Error code: 429"}
    }
    records_reasoning = await collection.find(query_reasoning).to_list(None)
    print(f"Found {len(records_reasoning)} records with rate-limited reasoning.")
    
    for record in records_reasoning:
        print(f"  Resetting reasoning for {record['form_id']}...")
        await collection.update_one(
            {"_id": record["_id"]},
            {"$set": {
                "priority_reasoning": "Priority assigned based on category severity. Detailed AI reasoning unavailable due to temporary provider limit.",
                "urgency_level": record.get("urgency_level") or "medium" # Keep existing urgency if possible
            }}
        )

    print("Data cleanup complete.")

if __name__ == "__main__":
    asyncio.run(scrub_rate_limits())
