from fastapi import HTTPException, UploadFile, File, Form, Path
from bson import ObjectId
from core.database import courses_collection
from courses.views.course_viedo.video_upload import upload_to_tencent_vod
from datetime import datetime
from typing import List

async def add_multiple_videos_to_course_handler(
    course_id: str = Path(..., description="Course ID to add videos to"),
    video_title: str = Form(..., description="Video titles separated by comma"),
    video_description: str = Form(..., description="Video descriptions separated by comma"),
    video_file: List[UploadFile] = File(..., description="Multiple video files"),
    start_order: int = Form(0, description="Starting order number for videos")
):
    """Add multiple videos to specific course"""
    try:
        object_id = ObjectId(course_id)
        
        # Check if course exists
        course = await courses_collection.find_one({"_id": object_id})
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        # Split titles and descriptions
        titles = [title.strip() for title in video_title.split(',')]
        descriptions = [desc.strip() for desc in video_description.split(',')]
        
        # Validate counts match
        if len(titles) != len(video_file) or len(descriptions) != len(video_file):
            raise HTTPException(status_code=400, detail="Number of titles, descriptions and files must match")

        existing_videos = course.get("videos", [])
        
        # Find next available order
        existing_orders = [v.get("order", 0) for v in existing_videos]
        if existing_orders:
            max_order = max(existing_orders)
            if start_order <= max_order:
                start_order = max_order + 1
        
        video_objects = []
        
        # Process each video
        for i, video_file in enumerate(video_file):
            if not video_file.filename:
                continue
                
            current_order = start_order + i
            
            # Upload video
            video_content = await video_file.read()
            video_result = await upload_to_tencent_vod(video_content, video_file.filename)
            
            video_obj = {
                "order": current_order,
                "video_title": titles[i] if i < len(titles) else f"Video {i+1}",
                "video_description": descriptions[i] if i < len(descriptions) else "",
                "fileId": video_result["file_id"],
                "videoUrl": video_result["video_url"]
            }
            video_objects.append(video_obj)

        # Add all videos to course
        await courses_collection.update_one(
            {"_id": object_id},
            {
                "$push": {"videos": {"$each": video_objects}},
                "$set": {"updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            }
        )

        return {
            "success": True,
            "message": f"{len(video_objects)} videos added to course successfully",
            "data": video_objects
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))