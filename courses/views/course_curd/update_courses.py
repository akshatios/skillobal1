from fastapi import HTTPException, UploadFile, File, Form, Path
from pydantic import BaseModel, Field
from bson import ObjectId
from core.database import courses_collection
from courses.views.course_viedo.video_upload import upload_to_tencent_vod, delete_from_tencent_vod, extract_file_id_from_url
from courses.views.course_curd.layoutdata_update import update_layout_by_rating
import uuid
from typing import Optional, Union, List
from datetime import datetime

class UpdateCourseModel(BaseModel):
    course_id: str = Field(..., description="The ID of the course to update")
    title: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    rating: Optional[float] = Field(None, ge=0, le=5)
    price: Optional[float] = None
    visible: Optional[bool] = None
    instructor_id: Optional[str] = None
    category_id: Optional[str] = None

    content_language: Optional[str] = None
    video_title: Optional[str] = None
    video_description: Optional[str] = None
    order: Optional[int] = None

async def update_course_with_video(
    course_id: str = Path(..., description="Course ID to update"),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    image_url: Optional[str] = Form(None),
    rating: Union[float, str, None] = Form(None),
    price: Union[float, str, None] = Form(None),
    visible: Optional[bool] = Form(None),
    instructor_id: Optional[str] = Form(None),
    category_id: Optional[str] = Form(None),

    content_language: Optional[str] = Form(None),
    video_title: Optional[str] = Form(None),
    video_description: Optional[str] = Form(None),
    video_file: Optional[List[UploadFile]] = File(None),
    order: Optional[int] = Form(None),
    intro_video: Optional[UploadFile] = File(None),

):
    """Update course with optional video upload"""
    try:
        object_id = ObjectId(course_id)
        
        existing_course = await courses_collection.find_one({"_id": object_id})
        if not existing_course:
            raise HTTPException(status_code=404, detail="Course not found")

        update_data = {}
        if title is not None and title.strip() != "":
            update_data["title"] = title
        if description is not None and description.strip() != "":
            update_data["description"] = description
        if image_url is not None and image_url.strip() != "":
            update_data["image_url"] = image_url
        if rating is not None and rating != "":
            try:
                update_data["rating"] = float(rating) if isinstance(rating, str) else rating
            except (ValueError, TypeError):
                pass
        if price is not None and price != "":
            try:
                update_data["price"] = float(price) if isinstance(price, str) else price
            except (ValueError, TypeError):
                pass
        if visible is not None:
            update_data["visible"] = visible
        if instructor_id is not None and instructor_id.strip() != "":
            try:
                update_data["instructor_id"] = ObjectId(instructor_id)
            except Exception:
                raise HTTPException(status_code=400, detail="Invalid instructor_id format")
        if category_id is not None and category_id != "string" and category_id.strip() != "":
            try:
                update_data["category_id"] = ObjectId(category_id)
            except Exception:
                raise HTTPException(status_code=400, detail="Invalid category_id format")

        if content_language is not None and content_language.strip() != "":
            update_data["content_language"] = content_language
        if video_title is not None and video_title.strip() != "":
            update_data["video_title"] = video_title
        if video_description is not None and video_description.strip() != "":
            update_data["video_description"] = video_description
        if order is not None:
            update_data["order"] = order
            
        # Handle video files upload
        if video_file and len(video_file) > 0 and video_file[0].filename:
            old_videos = existing_course.get("videos", [])
            for old_video in old_videos:
                old_fileId = old_video.get("fileId")
                if old_fileId:
                    await delete_from_tencent_vod(old_fileId)
            
            videos = []
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
            
            update_data["videos"] = videos
            
        # Handle intro video upload - Delete old and upload new
        if intro_video and intro_video.filename:
            # Delete old intro_video from Tencent
            old_intro_video = existing_course.get("intro_video")
            if old_intro_video:
                # Handle both old URL format and new object format
                old_fileId = None
                if isinstance(old_intro_video, dict):
                    old_fileId = old_intro_video.get("fileId")
                elif isinstance(old_intro_video, str):
                    old_fileId = extract_file_id_from_url(old_intro_video)
                
                if old_fileId:
                    await delete_from_tencent_vod(old_fileId)
            
            # Upload new intro_video
            intro_video_content = await intro_video.read()
            intro_video_result = await upload_to_tencent_vod(intro_video_content, intro_video.filename)
            update_data["intro_video"] = {
                "fileId": intro_video_result["file_id"],
                "videoUrl": intro_video_result["video_url"]
            }
            


        # Add updated_at timestamp
        update_data["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Debug: Log what's being updated
        print(f"Updating course {course_id} with data: {update_data}")
        
        # Update course fields
        await courses_collection.update_one(
            {"_id": object_id},
            {"$set": update_data}
        )

        # Auto-update layout based on rating
        try:
            await update_layout_by_rating()
        except Exception:
            pass  # Don't fail course update if layout update fails

        updated_course = await courses_collection.find_one({"_id": object_id})
        updated_course["_id"] = str(updated_course["_id"])
        if updated_course.get("instructor_id"):
            updated_course["instructor_id"] = str(updated_course["instructor_id"])
        if updated_course.get("category_id"):
            updated_course["category_id"] = str(updated_course["category_id"])
        
        # Timestamps are already strings
        if updated_course.get("created_at") and not isinstance(updated_course["created_at"], str):
            updated_course["created_at"] = str(updated_course["created_at"])
        if updated_course.get("updated_at") and not isinstance(updated_course["updated_at"], str):
            updated_course["updated_at"] = str(updated_course["updated_at"])

        return {
            "success": True,
            "message": "Course updated successfully",
            "data": updated_course
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



async def update_course_by_model(course: UpdateCourseModel):
    """Handle PUT request to update a course using the model"""
    return await update_course_with_video(
        course_id=course.course_id,
        title=course.title,
        description=course.description,
        image_url=course.image_url,
        rating=course.rating,
        price=course.price,
        visible=course.visible,
        instructor_id=course.instructor_id,
        category_id=course.category_id,

        content_language=course.content_language,
        video_title=course.video_title,
        video_description=course.video_description
    )

async def get_course_videos(course_id: str = Path(...)):
    """Get all videos for a course"""
    try:
        object_id = ObjectId(course_id)
        
        course = await courses_collection.find_one({"_id": object_id})
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        videos = course.get("videos", [])
        videos.sort(key=lambda x: x.get("order", 0))

        return {
            "success": True,
            "data": videos
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def add_video_to_course(
    course_id: str = Path(...),
    video_title: str = Form(...),
    video_description: str = Form(...),
    video_file: UploadFile = File(...)
):
    """Add a single video to existing course"""
    try:
        object_id = ObjectId(course_id)
        
        course = await courses_collection.find_one({"_id": object_id})
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        video_content = await video_file.read()
        video_result = await upload_to_tencent_vod(video_content, video_file.filename)
        
        existing_videos = course.get("videos", [])
        next_order = len(existing_videos)
        
        video_obj = {
            "order": next_order,
            "video_title": video_title,
            "video_description": video_description,
            "fileId": video_result["file_id"],
            "videoUrl": video_result["video_url"]
        }

        await courses_collection.update_one(
            {"_id": object_id},
            {"$push": {"videos": video_obj}}
        )

        return {
            "success": True,
            "message": "Video added successfully",
            "data": video_obj
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def remove_video_from_course(
    course_id: str = Path(...),
    video_order: int = Path(...)
):
    """Remove a video from course by order"""
    try:
        object_id = ObjectId(course_id)
        
        course = await courses_collection.find_one({"_id": object_id})
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        videos = course.get("videos", [])
        video_to_remove = None
        
        for video in videos:
            if video.get("order") == video_order:
                video_to_remove = video
                break
        
        if not video_to_remove:
            raise HTTPException(status_code=404, detail="Video not found")

        fileId = video_to_remove.get("fileId")
        if fileId:
            await delete_from_tencent_vod(fileId)

        await courses_collection.update_one(
            {"_id": object_id},
            {"$pull": {"videos": {"order": video_order}}}
        )

        return {
            "success": True,
            "message": "Video removed successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

