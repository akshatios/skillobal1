from fastapi import HTTPException, Response
from pydantic import BaseModel, EmailStr
from datetime import datetime
from core.database import users_collection, admins_collection
from core.utils import verify_password
from .createToken import create_token

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

async def admin_login(request: LoginRequest, response: Response):
    """Admin login endpoint - verifies credentials and returns JWT token."""
    user = await users_collection.find_one({"email": request.email})
    if not user or not verify_password(request.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Update last login time in users_collection (single source of truth)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    await users_collection.update_one(
        {"_id": user["_id"]},
        {"$set": {"last_login_at": now}}
    )

    token = create_token({"sub": str(user["_id"]), "email": user["email"]})
    
    # Set token in cookie for automatic use in Swagger UI
    response.set_cookie(
        key="access_token",
        value=f"Bearer {token}",
        httponly=False,  # Allow JavaScript access for Swagger UI
        secure=False,    # Set to True in production with HTTPS
        samesite="lax"
    )
    
    return {"access_token": token, "token_type": "bearer"}
