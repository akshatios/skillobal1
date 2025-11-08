from fastapi import HTTPException
from bson import ObjectId
from core.database import courses_collection

async def get_course_details(course_id: str):
    """Get specific course details by ID"""
    try:
        # Validate ObjectId
        if not ObjectId.is_valid(course_id):
            raise HTTPException(status_code=400, detail="Invalid course ID format")
        
        # Find course by ID
        course = await courses_collection.find_one({"_id": ObjectId(course_id)})
        
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        # Convert ObjectId to string
        course["_id"] = str(course["_id"])
        if course.get("category_id"):
            course["category_id"] = str(course["category_id"])
        if course.get("instructor_id"):
            course["instructor_id"] = str(course["instructor_id"])
        
        # Convert timestamps to string if needed
        if course.get("created_at") and not isinstance(course["created_at"], str):
            course["created_at"] = str(course["created_at"])
        if course.get("updated_at") and not isinstance(course["updated_at"], str):
            course["updated_at"] = str(course["updated_at"])
        
        return {
            "success": True,
            "message": "Course details retrieved successfully",
            "data": course
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))