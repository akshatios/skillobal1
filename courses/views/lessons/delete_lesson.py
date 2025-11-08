from fastapi import HTTPException
from bson import ObjectId
from core.database import courses_collection

async def delete_lesson(course_id: str, lesson_id: str):
    """Delete a lesson from a course"""
    try:
        # Check if course exists
        course = await courses_collection.find_one({"_id": ObjectId(course_id)})
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        # Check if lesson exists
        lesson_found = False
        for lesson in course.get("lessons", []):
            if lesson.get("lesson_id") == lesson_id:
                lesson_found = True
                break

        if not lesson_found:
            raise HTTPException(status_code=404, detail="Lesson not found")

        # Remove lesson from course
        result = await courses_collection.update_one(
            {"_id": ObjectId(course_id)},
            {"$pull": {"lessons": {"lesson_id": lesson_id}}}
        )

        if result.modified_count == 0:
            raise HTTPException(status_code=400, detail="Failed to delete lesson")

        return {
            "success": True,
            "message": "Lesson deleted successfully",
            "data": {
                "lesson_id": lesson_id,
                "course_id": course_id
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))