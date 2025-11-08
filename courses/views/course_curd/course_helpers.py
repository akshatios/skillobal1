from core.database import courses_collection, short_videos_collection
from bson import ObjectId

async def get_course_with_videos(course_id: str):
    """Get course with populated video details from short_videos collection"""
    try:
        object_id = ObjectId(course_id)
        course = await courses_collection.find_one({"_id": object_id})
        
        if not course:
            return None
            
        # Get video details from short_videos collection
        if course.get("short_video_objectId"):
            video_ids = [ObjectId(vid_id) for vid_id in course["short_video_objectId"]]
            videos = await short_videos_collection.find({"_id": {"$in": video_ids}}).to_list(None)
            
            # Convert ObjectIds to strings and sort by order
            for video in videos:
                video["_id"] = str(video["_id"])
            
            # Sort videos by order
            videos.sort(key=lambda x: x.get("order", 0))
            course["videos"] = videos
        
        # Convert ObjectIds to strings
        course["_id"] = str(course["_id"])
        if course.get("instructor_id"):
            course["instructor_id"] = str(course["instructor_id"])
        if course.get("category_id"):
            course["category_id"] = str(course["category_id"])
            
        return course
        
    except Exception as e:
        print(f"Error getting course with videos: {e}")
        return None

async def delete_course_videos(course_id: str):
    """Delete all videos associated with a course from short_videos collection"""
    try:
        await short_videos_collection.delete_many({"course_id": course_id})
        return True
    except Exception as e:
        print(f"Error deleting course videos: {e}")
        return False