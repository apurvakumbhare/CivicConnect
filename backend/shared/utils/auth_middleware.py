from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .auth_utils import verify_token
from services.user_service.src.db.connection import get_users_collection

security = HTTPBearer()

import logging

logger = logging.getLogger(__name__)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    logger.debug(f"Verifying token: {token[:10]}...")
    mobile = verify_token(token)
    if mobile is None:
        logger.warning("Token verification failed: verify_token returned None")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    users_col = get_users_collection()
    logger.debug(f"Looking up user with mobile_number: {mobile}")
    user = await users_col.find_one({"mobile_number": mobile})
    if not user:
        logger.warning(f"User lookup failed for mobile_number: {mobile}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
    user_id = str(user["_id"])
    logger.debug(f"User authenticated: {user_id}")
    return user_id
