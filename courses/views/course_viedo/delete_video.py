from fastapi import HTTPException
from bson import ObjectId
from core.database import courses_collection

async def delete_video_by_file_id(
    course_id: str,
    lesson_id: str, 
    fileId: str
):
    """Delete video by fileId from lesson"""
    try:
        # Check course exists
        course = await courses_collection.find_one({"_id": ObjectId(course_id)})
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        # Delete video from course lessons by fileId
        delete_result = await courses_collection.update_one(
            {
                "_id": ObjectId(course_id),
                "lessons.lesson_id": lesson_id
            },
            {
                "$pull": {
                    "lessons.$.videos": {"fileId": fileId}
                }
            }
        )

        if delete_result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Lesson not found")

        return {
            "success": True,
            "message": "Video deleted successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))