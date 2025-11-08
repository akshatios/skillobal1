from fastapi import HTTPException
from bson import ObjectId
from core.database import courses_collection
from courses.views.course_curd.delete_courses import delete_tencent_video

async def delete_specific_video(course_id: str, file_id: str):
    """Delete specific video from course by course_id and fileId"""
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
    video_to_delete = None
    video_index = -1
    
    for i, video in enumerate(videos):
        if video.get("fileId") == file_id:
            video_to_delete = video
            video_index = i
            break
    
    if not video_to_delete:
        raise HTTPException(status_code=404, detail="Video not found with given fileId")
    
    # Delete from Tencent Cloud
    tencent_deleted = await delete_tencent_video(file_id)
    
    # Remove video from course array
    await courses_collection.update_one(
        {"_id": object_id},
        {"$pull": {"videos": {"fileId": file_id}}}
    )
    
    return {
        "success": True,
        "message": "Video deleted successfully from this course",
        "deleted_video": {
            "fileId": video_to_delete.get("fileId"),
            "video_title": video_to_delete.get("video_title"),
            "video_description": video_to_delete.get("video_description"),
            "videoUrl": video_to_delete.get("videoUrl")
        },
        "tencent_cloud_deleted": tencent_deleted,
        "course_id": course_id
    }