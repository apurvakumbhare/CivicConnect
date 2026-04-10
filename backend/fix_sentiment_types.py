import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def fix_sentiment_types():
    client = AsyncIOMotorClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
    db = client.feedback_db
    # The collection name found earlier was 'feedback'
    collection = db.feedback
    
    feedbacks = await collection.find({}).to_list(None)
    print(f"Checking {len(feedbacks)} feedback records...")
    
    fixed_count = 0
    for fb in feedbacks:
        sentiment = fb.get("sentiment")
        if isinstance(sentiment, str):
            print(f"  [!] Found string sentiment for {fb.get('feedback_id')}: '{sentiment}'")
            
            # Map string to dictionary
            new_sentiment = {
                "label": sentiment,
                "score": 0.5,
                "explanation": "Converted from legacy string format."
            }
            
            await collection.update_one(
                {"_id": fb["_id"]},
                {"$set": {"sentiment": new_sentiment}}
            )
            fixed_count += 1
            
    print(f"Fixed {fixed_count} records.")

if __name__ == "__main__":
    asyncio.run(fix_sentiment_types())
