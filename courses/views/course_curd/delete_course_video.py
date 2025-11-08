from fastapi import HTTPException
from bson import ObjectId
from core.database import courses_collection
from courses.views.course_viedo.video_upload import delete_from_tencent_vod

async def delete_course_video(course_id: str, file_id: str):
    """Delete specific video from course by FileId"""
    try:
        # Validate ObjectId
        if not ObjectId.is_valid(course_id):
            raise HTTPException(status_code=400, detail="Invalid course ID format")
        
        # Find course
        course = await courses_collection.find_one({"_id": ObjectId(course_id)})
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        # Find and remove video from course videos array
        videos = course.get("videos", [])
        video_found = False
        updated_videos = []
        
        for video in videos:
            if video.get("fileId") == file_id:
                video_found = True
                # Delete from Tencent
                await delete_from_tencent_vod(file_id)
            else:
                updated_videos.append(video)
        
        if not video_found:
            raise HTTPException(status_code=404, detail="Video not found in course")
        
        # Update course with remaining videos
        await courses_collection.update_one(
            {"_id": ObjectId(course_id)},
            {"$set": {"videos": updated_videos}}
        )
        
        return {
            "success": True,
            "message": "Video deleted successfully from course and Tencent",
            "data": {
                "course_id": course_id,
                "deleted_file_id": file_id,
                "remaining_videos": len(updated_videos)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))