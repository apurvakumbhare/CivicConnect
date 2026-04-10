import httpx
import re
import logging
from typing import Dict, Optional
from services.AIAnalysis.shared.schemas import GrievanceData, RoutingResult
from services.AIAnalysis.utils.config import settings
from services.superuser_services.db.connection import get_database as get_superuser_db

logger = logging.getLogger(__name__)

class SmartRoutingAgent:
    def __init__(self):
        
        # Department mapping
        self.department_mapping = {
            "Electricity": "Electricity",
            "Water Supply": "Water Supply",
            "Roads": "Roads",
            "Sanitation": "Sanitation",
            "Street Lights": "Street Lights",
            "Drainage": "Drainage",
            "Public Safety": "Public Safety",
            "Parks": "Parks",
            "Buildings": "Buildings"
        }

        # Synonym mapping for AI-extracted categories
        self.synonym_map = {
            "electric": "Electricity",
            "electricity": "Electricity",
            "power": "Electricity",
            "water": "Water Supply",
            "plumbing": "Water Supply",
            "road": "Roads",
            "roads": "Roads",
            "infrastructure/roads": "Roads",
            "electrical": "Electricity",
            "sanitation": "Sanitation",
            "garbage": "Sanitation",
            "waste": "Sanitation",
            "drainage": "Drainage",
            "park": "Parks",
            "street light": "Street Lights",
            "street lights": "Street Lights",
            "health": "Health",
            "medical": "Health",
            "local": "General Administration"
        }

        
        # Estimated response times by urgency
        self.response_times = {
            "critical": "2 hours",
            "high": "12 hours",
            "medium": "24 hours",
            "low": "48 hours"
        }
    
    async def route_grievance(
        self, 
        grievance: GrievanceData, 
        urgency_level: str
    ) -> RoutingResult:
        """
        Route grievance to appropriate department and officer with tiered fallback
        """
        # 1. Normalize Category
        raw_cat = (grievance.category or "").lower().strip()
        department = "General Administration"
        
        # Check synonyms first
        if raw_cat in self.synonym_map:
            department = self.synonym_map[raw_cat]
        else:
            # Check direct mapping
            for key, val in self.department_mapping.items():
                if key.lower() == raw_cat:
                    department = val
                    break
        
        # 2. Find nodal officer with tiered fallback
        # Level 1: Specific Ward match
        officer = await self._find_nodal_officer(
            department=department,
            area_ward_name=grievance.area_ward_name
        )
        
        # Level 2: Fallback to any officer in department if Level 1 returned default
        if officer["officer_id"] == "DEFAULT_OFFICER":
             officer = await self._find_nodal_officer(
                department=department,
                area_ward_name=None # This triggers "any officer in dept"
            )
        
        # Level 3: Fallback to a Dept Admin if still no nodal officer
        if officer["officer_id"] == "DEFAULT_OFFICER":
            officer = await self._find_dept_admin(department)

        # Get estimated response time
        eta = self.response_times.get(urgency_level, "48 hours")
        
        return RoutingResult(
            department=department,
            officer_id=officer["officer_id"],
            officer_name=officer["officer_name"],
            estimated_response_time=eta
        )

    
    async def _find_nodal_officer(
        self, 
        department: str, 
        area_ward_name: str
    ) -> Dict[str, str]:
        """
        Query SuperUser DB staff_users collection to find the nodal officer.
        Uses fuzzy (partial, case-insensitive) matching on ward name.
        """
        try:
            db = get_superuser_db()  # Synchronous call
            collection = db.staff_users

            # Build base query
            query = {
                "role": "NODAL_OFFICER",
                "metadata.dept": department
            }

            # Add fuzzy ward match if provided (case-insensitive partial match)
            if area_ward_name and area_ward_name.strip():
                ward_term = area_ward_name.strip()
                ward_regex = {"$regex": f".*{re.escape(ward_term)}.*", "$options": "i"}
                query["metadata.ward"] = ward_regex

            # Query for nodal officer with matching dept and (fuzzy) ward
            officer_doc = await collection.find_one(query)

            if officer_doc:
                return {
                    "officer_id": str(officer_doc.get("_id", "DEFAULT_OFFICER")),
                    "officer_name": officer_doc.get("full_name", f"{department} - Nodal Officer")
                }
        except Exception as e:
            logger.exception("Error finding nodal officer in DB: %s", e)
        
        # Fallback if no specific officer found
        return {
            "officer_id": "DEFAULT_OFFICER",
            "officer_name": f"{department} - Nodal Officer"
        }

    async def _find_dept_admin(self, department: str) -> Dict[str, str]:
        """
        Fallback to find a Department Admin if no nodal officer found
        """
        try:
            db = get_superuser_db()
            collection = db.staff_users
            
            query = {
                "role": "DEPT_ADMIN",
                "metadata.dept": department
            }
            
            admin_doc = await collection.find_one(query)
            if admin_doc:
                return {
                    "officer_id": str(admin_doc.get("_id")),
                    "officer_name": admin_doc.get("full_name", f"{department} Admin")
                }
            
            # Secondary fallback: try SUPER_ADMIN
            query["role"] = "SUPER_ADMIN"
            super_doc = await collection.find_one(query)
            if super_doc:
                return {
                    "officer_id": str(super_doc.get("_id")),
                    "officer_name": super_doc.get("full_name", f"{department} Administrator")
                }
        except Exception as e:
            logger.exception("Error finding dept admin: %s", e)

            
        return {
            "officer_id": "DEFAULT_OFFICER",
            "officer_name": "General Administrator"
        }
