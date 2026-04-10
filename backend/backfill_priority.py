"""Backfill 'priority' field for all grievance forms that have urgency_level but no priority.
Also checks all known databases where grievance_forms may live.
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

async def backfill():
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/civicConnect")
    base_uri = mongo_uri.rsplit("/", 1)[0]  # strip db name from URI
    client = AsyncIOMotorClient(base_uri)

    # Try all possible DB names where grievance_forms may live
    db_names = ["grievance_db", "civicConnect", "ai_analysis_db", "user_db"]

    for db_name in db_names:
        db = client[db_name]
        forms = db.grievance_forms

        total = await forms.count_documents({})
        if total == 0:
            print(f"[{db_name}] No documents in grievance_forms, skipping.")
            continue

        print(f"\n[{db_name}] Found {total} grievance forms.")

        # Count with urgency_level
        with_urgency = await forms.count_documents({"urgency_level": {"$exists": True}})
        print(f"[{db_name}] Forms with urgency_level: {with_urgency}")

        modified = 0
        async for form in forms.find({"urgency_level": {"$exists": True}}):
            urgency = form.get("urgency_level")
            current_priority = form.get("priority")
            if urgency and not current_priority:
                await forms.update_one(
                    {"form_id": form["form_id"]},
                    {"$set": {"priority": urgency}}
                )
                modified += 1
                print(f"  Updated form {form.get('form_id')}: priority={urgency}")

        print(f"[{db_name}] Backfilled {modified} forms with priority field.")

        # verify
        sample = await forms.find_one({"urgency_level": {"$exists": True}})
        if sample:
            print(f"[{db_name}] Sample: form_id={sample.get('form_id')}, urgency_level={sample.get('urgency_level')}, priority={sample.get('priority')}")

asyncio.run(backfill())
