from fastapi import HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field
from bson import ObjectId
from core.database import courses_collection
from courses.views.course_viedo.video_upload import upload_to_tencent_vod
from courses.views.course_curd.layoutdata_update import update_layout_by_rating
from typing import Optional
from datetime import datetime

class AddCourseModel(BaseModel):
    title: str
    description: str
    image_url: str
    rating: float = Field(ge=0, le=5)
    price: float
    visible: bool = True
    instructor_id: str
    category_id: Optional[str] = None
    licence_key: Optional[str] = None
    content_language: Optional[str] = None

async def add_course(
    title: str = Form(...),
    description: str = Form(...),
    image_url: str = Form(...),
    rating: float = Form(...),
    price: float = Form(...),
    instructor_id: str = Form(...),
    visible: bool = Form(True),
    category_id: Optional[str] = Form(None),
    licence_key: Optional[str] = Form(None),
    content_language: Optional[str] = Form(None),
    thumbnail_video: Optional[UploadFile] = File(None),
    thumbnail_img: Optional[UploadFile] = File(None)
):
    """Add new course with optional video upload"""
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Handle thumbnail uploads
        thumbnail_video_url = None
        thumbnail_img_url = None
        
        if thumbnail_video and thumbnail_video.filename:
            thumb_video_content = await thumbnail_video.read()
            thumb_video_result = await upload_to_tencent_vod(thumb_video_content, thumbnail_video.filename)
            thumbnail_video_url = thumb_video_result["video_url"]
            
        if thumbnail_img and thumbnail_img.filename:
            thumb_img_content = await thumbnail_img.read()
            thumb_img_result = await upload_to_tencent_vod(thumb_img_content, thumbnail_img.filename)
            thumbnail_img_url = thumb_img_result["video_url"]

        new_course = {
            "title": title,
            "description": description,
            "image_url": image_url,
            "rating": rating,
            "price": price,
            "visible": visible,
            "instructor_id": ObjectId(instructor_id) if instructor_id and instructor_id != "string" else None,
            "category_id": ObjectId(category_id) if category_id and category_id != "string" else None,
            "licence_key": licence_key,
            "content_language": content_language,
            "thumbnail_video": thumbnail_video_url,
            "thumbnail_img": thumbnail_img_url,
            "created_at": current_time,
            "updated_at": current_time
        }

        result = await courses_collection.insert_one(new_course)
        course_id = str(result.inserted_id)

        new_course["_id"] = course_id
        if new_course["instructor_id"]:
            new_course["instructor_id"] = str(new_course["instructor_id"])
        if new_course["category_id"]:
            new_course["category_id"] = str(new_course["category_id"])

        # Auto-update layout based on rating
        try:
            await update_layout_by_rating()
        except Exception:
            pass

        return {
            "success": True,
            "message": "Course added successfully",
            "data": new_course
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def add_course_by_model(course: AddCourseModel):
    """Handle POST request to add a course using the model"""
    return await add_course(
        title=course.title,
        description=course.description,
        image_url=course.image_url,
        rating=course.rating,
        price=course.price,
        instructor_id=course.instructor_id,
        visible=course.visible,
        category_id=course.category_id,
        licence_key=course.licence_key,
        content_language=course.content_language
    )