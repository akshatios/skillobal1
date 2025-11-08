from fastapi import HTTPException
from bson import ObjectId
from core.database import courses_collection

async def get_course_lessons_count(course_id: str):
    """Get total lessons count for a specific course"""
    try:
        # Validate ObjectId
        if not ObjectId.is_valid(course_id):
            raise HTTPException(status_code=400, detail="Invalid course ID format")
        
        # Find course and get lessons count
        course = await courses_collection.find_one({"_id": ObjectId(course_id)})
        
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        # Count lessons in the course
        lessons = course.get("lessons", [])
        total_lessons = len(lessons) if lessons else 0
        
        return {
            "success": True,
            "message": "Course lessons count retrieved successfully",
            "data": {
                "course_id": course_id,
                "total_lessons": total_lessons
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))