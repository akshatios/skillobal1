from fastapi import HTTPException, UploadFile, File, Form, Path
from bson import ObjectId
from core.database import courses_collection
from courses.views.course_viedo.video_upload import upload_to_tencent_vod, delete_from_tencent_vod

async def update_specific_video(
    course_id: str = Path(...),
    fileId: str = Path(...),

    video_title: str = Form(...),
    video_description: str = Form(...),
    video_file: UploadFile = File(...)
):
    """Update a specific video in course by fileId"""
    try:
        object_id = ObjectId(course_id)
        
        course = await courses_collection.find_one({"_id": object_id})
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        videos = course.get("videos", [])
        video_index = None
        old_video = None
        
        # Find video by fileId
        for i, video in enumerate(videos):
            if video.get("fileId") == fileId:
                video_index = i
                old_video = video
                break
        
        if video_index is None:
            raise HTTPException(status_code=404, detail="Video not found")

        # Delete old video from Tencent
        await delete_from_tencent_vod(fileId)

        # Upload new video
        video_content = await video_file.read()
        video_result = await upload_to_tencent_vod(video_content, video_file.filename)
        
        # Update video object
        new_video = {
            "order": old_video.get("order", 0),
            "video_title": video_title,
            "video_description": video_description,
            "fileId": video_result["file_id"],
            "videoUrl": video_result["video_url"]
        }

        # Replace video in array
        await courses_collection.update_one(
            {"_id": object_id},
            {"$set": {f"videos.{video_index}": new_video}}
        )

        return {
            "success": True,
            "message": "Video updated successfully",
            "data": new_video
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))