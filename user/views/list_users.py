from core.database import users_collection, courses_collection

async def list_users():
    """Get total users and all user info, plus active (visible) courses count"""
    # Fetch users from MongoDB
    docs = await users_collection.find().to_list(length=10000)
    users = [
        {   
            "name": doc.get("name"),
            "id": str(doc.get("_id")),
            "email": doc.get("email"),
            "created_at": doc.get("created_at"),
        }
        for doc in docs
    ]

    # Count active (visible) courses
    active_courses = await courses_collection.count_documents({"visible": True})

    return {"total": len(users), "activeCourses": active_courses, "users": users}
