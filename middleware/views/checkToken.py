from fastapi import HTTPException, Header, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from bson import ObjectId
from typing import Optional
from jose import jwt
from core.config import jwt_settings
from core.database import admins_collection

# Security scheme for Swagger UI
security = HTTPBearer()

# Removed redundant auth functions - middleware handles all authentication

async def get_current_admin(token: Optional[str] = Header(None), authorization: Optional[str] = Header(None)):
    """Authentication dependency that works with both 'token' header and 'Authorization' Bearer header."""
    try:
        # Try to get token from either header
        auth_token = None
        if authorization and authorization.lower().startswith("bearer "):
            auth_token = authorization[7:]  # Remove 'Bearer ' prefix
        elif token:
            auth_token = token
        
        if not auth_token:
            raise HTTPException(status_code=401, detail="Token not provided in either 'token' or 'Authorization' header")
        
        payload = jwt.decode(auth_token, jwt_settings.SUGAR_VALUE, algorithms=["HS256"])
        user_id = payload.get("_id") or payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token: missing user ID")
        
        user = await admins_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication error: {str(e)}")