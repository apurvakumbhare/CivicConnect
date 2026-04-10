import asyncio
import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Add current directory to path so we can import services
sys.path.append(os.getcwd())

from services.AIAnalysis.agents.smart_routing import SmartRoutingAgent
from services.AIAnalysis.shared.schemas import GrievanceData
from services.AIAnalysis.db.connection import get_database as get_analysis_db
from services.superuser_services.db.connection import connect_to_mongo as connect_superuser_db

async def reassign_orphaned_tickets():
    print("Connecting to databases...")
    await connect_superuser_db()
    client = AsyncIOMotorClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))

    
    # AI Analysis DB
    ai_db = client.ai_analysis_db
    analysis_coll = ai_db.analysis_records
    
    # Grievance DB
    grievance_db = client.grievance_db
    forms_coll = grievance_db.grievance_forms
    
    routing_agent = SmartRoutingAgent()
    
    # Find orphaned records
    print("Searching for orphaned tickets (assigned to DEFAULT_OFFICER)...")
    orphaned_records = await analysis_coll.find({"assigned_officer_id": "DEFAULT_OFFICER"}).to_list(None)
    
    print(f"Found {len(orphaned_records)} orphaned records.")
    
    for record in orphaned_records:
        form_id = record["form_id"]
        print(f"Processing {form_id}...")
        
        # Get the latest form data to get category/ward
        form_doc = await forms_coll.find_one({"form_id": form_id})
        if not form_doc:
            print(f"  [!] Form document not found for {form_id}, skipping.")
            continue
            
        # Mock GrievanceData for routing agent
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

        
        # Run improved routing
        # Urgency level might be stored in record
        urgency = record.get("urgency_level", "medium")
        routing_result = await routing_agent.route_grievance(grievance, urgency)
        
        if routing_result.officer_id != "DEFAULT_OFFICER":
            print(f"  [+] Reassigned to: {routing_result.officer_name} ({routing_result.officer_id}) in {routing_result.department}")
            
            # Update Analysis Record
            await analysis_coll.update_one(
                {"_id": record["_id"]},
                {"$set": {
                    "assigned_officer_id": routing_result.officer_id,
                    "assigned_officer_name": routing_result.officer_name,
                    "assigned_department": routing_result.department,
                    "estimated_response_time": routing_result.estimated_response_time
                }}
            )
            
            # Update Grievance Form (to show in citizen view)
            await forms_coll.update_one(
                {"form_id": form_id},
                {"$set": {
                    "officer_id": routing_result.officer_id,
                    "officer_name": routing_result.officer_name,
                    "assigned_department": routing_result.department
                }}
            )
        else:
            print(f"  [-] Still could not find an officer for {form_id}. Category was: '{grievance.category}'")

    print("Reassignment complete.")

if __name__ == "__main__":
    asyncio.run(reassign_orphaned_tickets())
