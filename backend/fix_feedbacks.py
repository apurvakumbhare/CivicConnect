import asyncio
import os
import sys

# Import necessary modules
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

# Ensure we can import backend properly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from services.feedback_service.db.feedback_db import feedback_db
from services.feedback_service.utils.sentiment_analyzer import analyze_sentiment
from services.feedback_service.utils.conflict_resolver import conflict_resolver
from services.AIFormFilling.src.db.connection import get_database as get_grievance_db

async def run_fix():
    print("Connecting to DB...")
    # Initialize connection via Motor if they are not active
    # Using existing connections is easier
    client = AsyncIOMotorClient(os.getenv("MONGODB_URL", "mongodb://localhost:27017"))
    # The actual database used by backend is feedback_db for feedback and grievance_db for grievances
    feedback_db = client.feedback_db
    feedback_coll = feedback_db.feedback
    grievance_db = client.grievance_db
    grievance_coll = grievance_db.grievance_forms
    
    print("Fetching feedbacks...")
    cursor = feedback_coll.find({})
    feedbacks = await cursor.to_list(length=100)
    
    for fb in feedbacks:
        fb_id = fb.get("feedback_id")
        comments = fb.get("user_comment", "")
        
        print(f"Processing feedback {fb_id}")
        
        # 1. Re-run sentiment analysis
        sentiment = None
        try:
            sentiment = analyze_sentiment(comments)
            print(f"New sentiment: {sentiment}")
        except Exception as e:
            print(f"Sentiment failed: {e}")
            
        # 2. Re-run conflict resolver
        print("Rechecking conflict...")
        # Resolver needs grievance context. Get it from grievance DB
        grievance = await grievance_coll.find_one({"form_id": fb_id}) or {}
        
        negative_sentiment = False
        try:
             if sentiment:
                 negative_sentiment = (
                     (isinstance(sentiment.get("label"), str) and sentiment.get("label").lower() == "negative")
                     or (isinstance(sentiment.get("score"), (int, float)) and sentiment.get("score", 0) > 0.6)
                 )
        except Exception:
             negative_sentiment = False

        low_rating = False
        if "ratings" in fb and "overall" in fb["ratings"]:
            low_rating = fb["ratings"]["overall"] <= 2

        conflict_detected = False
        escalated = False
        action = fb.get("action", "")
        is_resolved = fb.get("is_resolved_by_user", True)
        
        if (not is_resolved) or negative_sentiment or low_rating:
            conflict_detected = True
            escalated = True if (low_rating or negative_sentiment) else False
            action = "reopened_by_citizen" if not is_resolved else "escalated"
            
        # Update Document
        update_doc = {
            "sentiment": sentiment.get("label") if sentiment else "neutral",
            "sentiment_score": sentiment.get("score") if sentiment else 0.5,
            "sentiment_note": sentiment.get("explanation") if sentiment else "",
            "conflict_detected": conflict_detected,
            "escalated": escalated,
            "action": action
        }
        
        await feedback_coll.update_one(
            {"_id": fb["_id"]},
            {"$set": update_doc}
        )
        print(f"Updated feedback {fb_id}")
        
    print("Repair complete.")

if __name__ == "__main__":
    asyncio.run(run_fix())
