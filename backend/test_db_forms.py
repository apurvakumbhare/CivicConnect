import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def check_grievance_forms():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client.grievance_db
    forms = await db.grievance_forms.find({}).to_list(10)
    print("--- Grievance Forms ---")
    for f in forms:
        print(f"ID: {f.get('form_id')}, Title: {f.get('title')}, Category: {f.get('category')}, Ward: {f.get('area_ward_name')}, Status: {f.get('status')}")

if __name__ == "__main__":
    asyncio.run(check_grievance_forms())
