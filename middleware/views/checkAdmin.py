from core.database import users_collection
from core.utils import hash_password

async def create_default_admin():
    """Create default admin if not exists"""
    admin = await users_collection.find_one({"email": "admin@gmail.com"})
    if not admin:
        await users_collection.insert_one({
            "email": "admin@gmail.com",
            "password": hash_password("Admin12345")
        })
