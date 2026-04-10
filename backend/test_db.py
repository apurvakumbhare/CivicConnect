import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

async def check_users():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    # Check staff users
    users = await client.superuserdb.staff_users.find({}).to_list(100)
    print("--- Staff Users ---")
    for u in users:
        print(f"ID: {u.get('_id')}, Name: {u.get('full_name')}, Role: {u.get('role')}, Dept: {u.get('metadata', {}).get('dept')}, Ward: {u.get('metadata', {}).get('ward')}")
    
    # Check grievances in analysis_records
    records = await client.ai_analysis_db.analysis_records.find({}).to_list(100)
    print("\n--- Analysis Records ---")
    for r in records:
        print(f"Form: {r.get('form_id')}, Officer: {r.get('assigned_officer_id')}, Dept: {r.get('department')}, Ward: {r.get('area_ward_name')}")

if __name__ == "__main__":
    asyncio.run(check_users())
