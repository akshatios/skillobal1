from fastapi import HTTPException, UploadFile, File, Form
from bson import ObjectId
from core.database import courses_collection
from courses.views.course_viedo.video_upload import upload_to_tencent_vod
from courses.views.course_curd.delete_courses import delete_tencent_video
from typing import Optional, Union

async def replace_specific_video(
    course_id: str = Form(...),
    file_id: str = Form(...),
    video_title: Optional[str] = Form(None),
    video_description: Optional[str] = Form(None),
    video_file: UploadFile = File(...)
):
    """Replace specific video in course by course_id and fileId"""
    try:
        object_id = ObjectId(course_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid course ID format")
    
    # Get course
    course = await courses_collection.find_one({"_id": object_id})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    videos = course.get("videos", [])
    if not videos:
        raise HTTPException(status_code=404, detail="No videos found in course")
    
    # Find video by fileId
    video_index = -1
    old_video = None
    
    for i, video in enumerate(videos):
        if video.get("fileId") == file_id:
            video_index = i
            old_video = video
            break
    
    if video_index == -1:
        raise HTTPException(status_code=404, detail="Video not found with given fileId")
    
    # Upload new video to Tencent Cloud
    file_content = await video_file.read()
    tencent_result = await upload_to_tencent_vod(file_content, video_file.filename)
    
    # Delete old video from Tencent Cloud
    old_tencent_deleted = await delete_tencent_video(file_id)
    
    # Update video data in database
    video_updates = {
        f"videos.{video_index}.fileId": tencent_result["file_id"],
        f"videos.{video_index}.videoUrl": tencent_result["video_url"],
        f"videos.{video_index}.video_title": video_title or video_file.filename,
        f"videos.{video_index}.video_description": video_description or ""
    }
    
    await courses_collection.update_one(
        {"_id": object_id},
        {"$set": video_updates}
    )
    
    return {
        "success": True,
        "message": "Video replaced successfully in course and Tencent Cloud",
        "old_video": {
            "fileId": old_video.get("fileId"),
            "video_title": old_video.get("video_title"),
            "video_description": old_video.get("video_description"),
            "videoUrl": old_video.get("videoUrl")
        },
        "new_video": {
            "fileId": tencent_result["file_id"],
            "videoUrl": tencent_result["video_url"],
            "video_title": video_title or video_file.filename,
            "video_description": video_description or ""
        },
        "old_tencent_deleted": old_tencent_deleted,
        "course_id": course_id
    }