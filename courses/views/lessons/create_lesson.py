from fastapi import HTTPException, Form
from pydantic import BaseModel
from bson import ObjectId
from core.database import courses_collection
from typing import Optional, List
from datetime import datetime
import uuid

class LessonModel(BaseModel):
    lesson_title: str
    lesson_description: Optional[str] = None
    order: int

class VideoModel(BaseModel):
    video_title: str
    video_description: Optional[str] = None
    videoUrl: str

async def create_lesson(
    course_id: str,
    lesson_title: str = Form(...),
    lesson_description: Optional[str] = Form(None),
    order: int = Form(...),
    videos: Optional[List[dict]] = None
):
    """Create a new lesson for a course"""
    try:
        # Check if course exists
        course = await courses_collection.find_one({"_id": ObjectId(course_id)})
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        # Generate unique lesson ID
        lesson_id = str(uuid.uuid4())
        
        # Create lesson object
        new_lesson = {
            "lesson_id": lesson_id,
            "lesson_title": lesson_title,
            "lesson_description": lesson_description,
            "order": order,
            "videos": videos or [],
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # Add lesson to course
        result = await courses_collection.update_one(
            {"_id": ObjectId(course_id)},
            {"$push": {"lessons": new_lesson}}
        )

        if result.modified_count == 0:
            raise HTTPException(status_code=400, detail="Failed to add lesson")

        return {
            "success": True,
            "message": "Lesson created successfully",
            "data": {
                "lesson_id": lesson_id,
                "course_id": course_id,
                "lesson": new_lesson
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))