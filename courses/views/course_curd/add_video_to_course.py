from fastapi import HTTPException, UploadFile, File, Form, Path
from bson import ObjectId
from core.database import courses_collection
from courses.views.course_viedo.video_upload import upload_to_tencent_vod
from datetime import datetime

async def add_video_to_course_handler(
    course_id: str = Path(..., description="Course ID to add video to"),
    video_title: str = Form(..., description="Video title"),
    video_description: str = Form(..., description="Video description"),
    video_file: UploadFile = File(..., description="Video file to upload"),
    order: int = Form(..., description="Video order in the course")
):
    """Add a video to specific course with title, description, video file and order"""
    try:
        object_id = ObjectId(course_id)
        
        # Check if course exists
        course = await courses_collection.find_one({"_id": object_id})
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        # Check if order already exists
        existing_videos = course.get("videos", [])
        for existing_video in existing_videos:
            if existing_video.get("order") == order:
                raise HTTPException(status_code=400, detail=f"Video with order {order} already exists")

        # Upload video to Tencent VOD
        video_content = await video_file.read()
        video_result = await upload_to_tencent_vod(video_content, video_file.filename)
        
        # Create video object
        video_obj = {
            "order": order,
            "video_title": video_title,
            "video_description": video_description,
            "fileId": video_result["file_id"],
            "videoUrl": video_result["video_url"]
        }

        # Add video to course
        await courses_collection.update_one(
            {"_id": object_id},
            {
                "$push": {"videos": video_obj},
                "$set": {"updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            }
        )

        return {
            "success": True,
            "message": "Video added to course successfully",
            "data": video_obj
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))