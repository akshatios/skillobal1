from core.database import courses_collection

async def get_visible_courses():
    """Get visible courses count and data"""
    # Fetch only courses where visible is true
    docs = await courses_collection.find({"visible": True}).to_list(length=10000)
    
    courses = [
        {
            "id": str(doc.get("_id")),
            "title": doc.get("title"),
            "description": doc.get("description"),
            "image_url": doc.get("image_url"),
            "rating": doc.get("rating"),
            "price": doc.get("price"),
            "visible": doc.get("visible"),
            "instructor": doc.get("instructor"),
            "cat_id": str(doc.get("cat_id")) if doc.get("cat_id") else None,
        }
        for doc in docs
    ]
    
    return {
        "total_visible_courses": len(courses),
        "courses": courses
    }
