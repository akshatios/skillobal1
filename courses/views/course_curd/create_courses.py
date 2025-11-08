from fastapi import HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field
from bson import ObjectId
from core.database import courses_collection
from courses.views.course_viedo.video_upload import upload_to_tencent_vod
from courses.views.course_curd.layoutdata_update import update_layout_by_rating
import uuid
from typing import Optional, Union, List
from datetime import datetime

class CourseModel(BaseModel):
    title: str
    description: str
    image_url: str
    rating: float = Field(ge=0, le=5)
    price: float
    visible: bool = True
    instructor_id: str
    category_id: str | None = None

    content_language: str | None = None
    video_title: str | None = None
    video_description: str | None = None

async def create_course(
    title: str = Form(...),
    description: str = Form(...),
    image_url: str = Form(...),
    rating: float = Form(...),
    price: float = Form(...),
    instructor_id: str = Form(...),
    visible: bool = Form(True),
    category_id: Optional[str] = Form(None),

    content_language: Optional[str] = Form(None),
    video_title: Optional[str] = Form(None),
    video_description: Optional[str] = Form(None),
    video_file: List[UploadFile] = File([]),
    intro_video: Optional[UploadFile] = File(None),

):
    """Create course with optional video upload"""
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Handle multiple video files upload
        videos = []
        
        if video_file and len(video_file) > 0 and video_file[0].filename:
            titles = video_title.split(',') if video_title else []
            descriptions = video_description.split(',') if video_description else []
            
            for i, vid_file in enumerate(video_file):
                if vid_file.filename:
                    video_content = await vid_file.read()
                    video_result = await upload_to_tencent_vod(video_content, vid_file.filename)
                    
                    video_obj = {
                        "order": i,
                        "video_title": titles[i].strip() if i < len(titles) else f"Video {i+1}",
                        "video_description": descriptions[i].strip() if i < len(descriptions) else "",
                        "fileId": video_result["file_id"],
                        "videoUrl": video_result["video_url"]
                    }
                    videos.append(video_obj)
        
        # Handle intro video upload
        intro_video_data = None
        
        if intro_video and intro_video.filename:
            intro_video_content = await intro_video.read()
            intro_video_result = await upload_to_tencent_vod(intro_video_content, intro_video.filename)
            intro_video_data = {
                "fileId": intro_video_result["file_id"],
                "videoUrl": intro_video_result["video_url"]
            }
            


        new_course = {
            "title": title,
            "description": description,
            "image_url": image_url,
            "rating": rating,
            "price": price,
            "visible": visible,
            "instructor_id": ObjectId(instructor_id) if instructor_id and instructor_id != "string" else None,
            "category_id": ObjectId(category_id) if category_id and category_id != "string" else None,

            "content_language": content_language,
            "videos": videos,
            "intro_video": intro_video_data,

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
            pass  # Don't fail course creation if layout update fails

        # Timestamps are already strings
        return {
            "success": True,
            "message": "Course created successfully",
            "data": new_course
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))