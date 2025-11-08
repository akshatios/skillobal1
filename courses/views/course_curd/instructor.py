from core.database import instructors_collection

async def get_all_instructors():
    """Get all instructors with id and instructor_name"""
    docs = await instructors_collection.find({}).to_list(length=10000)  
    instructors = [
        {
            "id": str(doc.get("_id")),
            "instructor_name": doc.get("name")
        }
        for doc in docs
    ]
    return {
        "total_instructors": len(instructors),
        "instructors": instructors
    }