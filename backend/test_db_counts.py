import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def check_counts():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client.ai_analysis_db
    records = await db.analysis_records.find({}).to_list(100)
    
    counts = {}
    for r in records:
        oid = r.get('assigned_officer_id')
        name = r.get('assigned_officer_name', 'Unknown')
        counts[oid] = counts.get(oid, 0) + 1
        
    print("--- Ticket Counts per Officer ---")
    for oid, count in counts.items():
        print(f"Officer ID: {oid}, Tickets: {count}")

if __name__ == "__main__":
    asyncio.run(check_counts())
