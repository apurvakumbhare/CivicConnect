import asyncio
import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Add current directory to path so we can import services
sys.path.append(os.getcwd())

from services.AIAnalysis.agents.priority_scorer import PriorityScorerAgent
from services.AIAnalysis.shared.schemas import GrievanceData

async def scrub_historical_errors():
    print("Connecting to databases...")
    client = AsyncIOMotorClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
    
    # AI Analysis DB
    ai_db = client.ai_analysis_db
    analysis_coll = ai_db.analysis_records
    
    # Grievance DB
    grievance_db = client.grievance_db
    forms_coll = grievance_db.grievance_forms
    
    scorer = PriorityScorerAgent()
    
    # Find records with error text
    print("Searching for records with historical parsing errors...")
    query = {"priority_reasoning": {"$regex": "Error response 401"}}
    error_records = await analysis_coll.find(query).to_list(None)
    
    print(f"Found {len(error_records)} records with error messages.")
    
    for record in error_records:
        form_id = record["form_id"]
        print(f"Re-analyzing {form_id}...")
        
        # Get the latest form data
        form_doc = await forms_coll.find_one({"form_id": form_id})
        if not form_doc:
            print(f"  [!] Form document not found for {form_id}, skipping.")
            continue
            
        # Mock GrievanceData
        grievance = GrievanceData(
            form_id=form_id,
            user_id=form_doc.get("user_id") or form_doc.get("citizen_id") or "unknown",
            title=form_doc.get("title") or form_doc.get("subject") or "No Title",
            full_description=form_doc.get("description") or form_doc.get("full_description") or "",
            category=form_doc.get("category", ""),
            area_ward_name=form_doc.get("area_ward_name"),
            impacted_population=str(form_doc.get("impacted_population", "unknown")),
            is_recurring=bool(form_doc.get("is_recurring", False)),
            document_paths=form_doc.get("document_paths", [])
        )
        
        # Run priority scorer
        try:
            priority_result = await scorer.score_priority(grievance)
            print(f"  [+] New Priority: {priority_result.urgency_level} ({priority_result.score})")
            
            # Update Analysis Record
            await analysis_coll.update_one(
                {"_id": record["_id"]},
                {"$set": {
                    "urgency_level": priority_result.urgency_level,
                    "priority_score": priority_result.score,
                    "priority_reasoning": priority_result.reasoning,
                    "document_insights": priority_result.reasoning # Also used for insights in some views
                }}
            )
        except Exception as e:
            print(f"  [!] Failed to re-analyze {form_id}: {e}")

    print("Scrubbing complete.")

if __name__ == "__main__":
    asyncio.run(scrub_historical_errors())
