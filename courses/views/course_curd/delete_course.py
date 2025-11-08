from fastapi import HTTPException
from bson import ObjectId
from core.database import courses_collection, courses_videos_collection, course_intro_video_collection
from courses.views.course_viedo.video_upload import delete_from_tencent_vod

async def delete_course(course_id: str):
    """Delete course and all related videos from all collections"""
    try:
        # Convert string to ObjectId
        course_object_id = ObjectId(course_id)
        
        # Check if course exists
        course = await courses_collection.find_one({"_id": course_object_id})
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        # Get video container and delete videos from Tencent Cloud
        video_container = await courses_videos_collection.find_one({"course_id": course_id})
        if video_container and "videos" in video_container:
            for video in video_container["videos"]:
                if "fileId" in video:
                    try:
                        result = await delete_from_tencent_vod(video["fileId"])
                    except Exception:
                        pass  # Continue even if Tencent deletion fails
        
        # Get intro video and delete from Tencent Cloud
        intro_video = await course_intro_video_collection.find_one({"course_id": course_id})
        if intro_video and "fileId" in intro_video:
            try:
                result = await delete_from_tencent_vod(intro_video["fileId"])
            except Exception:
                pass  # Continue even if Tencent deletion fails
        
        # Delete lesson videos from Tencent Cloud
        if course.get("lessons"):
            for lesson in course["lessons"]:
                if lesson.get("videos"):
                    for video in lesson["videos"]:
                        if "fileId" in video:
                            try:
                                result = await delete_from_tencent_vod(video["fileId"])
                            except Exception:
                                pass  # Continue even if Tencent deletion fails
        
        # Delete from courses_videos collection (video container)
        await courses_videos_collection.delete_many({"course_id": course_id})
        
        # Delete from course_intro_video collection
        await course_intro_video_collection.delete_many({"course_id": course_id})
        
        # Delete main course
        result = await courses_collection.delete_one({"_id": course_object_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Course not found")
        
        return {
            "success": True,
            "message": "Course and all related videos deleted successfully",
            "course_id": course_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def delete_multiple_courses(course_ids: list):
    """Delete multiple courses and all their related videos"""
    try:
        deleted_courses = []
        errors = []
        
        for course_id in course_ids:
            try:
                result = await delete_course(course_id)
                deleted_courses.append(course_id)
            except Exception as e:
                errors.append({"course_id": course_id, "error": str(e)})
        
        return {
            "success": True,
            "message": f"{len(deleted_courses)} courses deleted successfully",
            "deleted_courses": deleted_courses,
            "errors": errors if errors else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))