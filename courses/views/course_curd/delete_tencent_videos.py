from fastapi import HTTPException
from courses.views.course_viedo.video_upload import delete_from_tencent_vod
from core.database import courses_videos_collection, course_intro_video_collection, courses_collection
from bson import ObjectId

async def delete_video_by_fileid(file_id: str):
    """Delete specific video from Tencent Cloud by fileId"""
    try:
        result = await delete_from_tencent_vod(file_id)
        return {
            "success": result["success"],
            "message": result.get("message", result.get("error", "Unknown result")),
            "file_id": file_id,
            "details": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def delete_multiple_videos_by_fileids(file_ids: list):
    """Delete multiple videos from Tencent Cloud by fileIds"""
    try:
        results = []
        for file_id in file_ids:
            try:
                result = await delete_from_tencent_vod(file_id)
                results.append({
                    "file_id": file_id,
                    "success": result["success"],
                    "message": result.get("message", result.get("error", "Unknown result"))
                })
            except Exception as e:
                results.append({
                    "file_id": file_id,
                    "success": False,
                    "message": str(e)
                })
        
        return {
            "success": True,
            "message": f"Processed {len(file_ids)} videos",
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def cleanup_orphan_tencent_videos():
    """Clean up all videos from database collections that exist in Tencent"""
    try:
        deleted_videos = []
        failed_videos = []
        
        # Get all videos from courses_videos collection
        async for video_container in courses_videos_collection.find():
            if "videos" in video_container:
                for video in video_container["videos"]:
                    if "fileId" in video:
                        try:
                            result = await delete_from_tencent_vod(video["fileId"])
                            if result["success"]:
                                deleted_videos.append(video["fileId"])
                            else:
                                failed_videos.append({"fileId": video["fileId"], "error": result.get("error", "Unknown error")})
                        except Exception as e:
                            failed_videos.append({"fileId": video["fileId"], "error": str(e)})
        
        # Get all intro videos
        async for intro_video in course_intro_video_collection.find():
            if "fileId" in intro_video:
                try:
                    result = await delete_from_tencent_vod(intro_video["fileId"])
                    if result["success"]:
                        deleted_videos.append(intro_video["fileId"])
                    else:
                        failed_videos.append({"fileId": intro_video["fileId"], "error": result.get("error", "Unknown error")})
                except Exception as e:
                    failed_videos.append({"fileId": intro_video["fileId"], "error": str(e)})
        
        # Get all lesson videos from courses
        async for course in courses_collection.find():
            if "lessons" in course:
                for lesson in course["lessons"]:
                    if "videos" in lesson:
                        for video in lesson["videos"]:
                            if "fileId" in video:
                                try:
                                    result = await delete_from_tencent_vod(video["fileId"])
                                    if result["success"]:
                                        deleted_videos.append(video["fileId"])
                                    else:
                                        failed_videos.append({"fileId": video["fileId"], "error": result.get("error", "Unknown error")})
                                except Exception as e:
                                    failed_videos.append({"fileId": video["fileId"], "error": str(e)})
        
        return {
            "success": True,
            "message": f"Cleanup completed. Deleted: {len(deleted_videos)}, Failed: {len(failed_videos)}",
            "deleted_videos": deleted_videos,
            "failed_videos": failed_videos
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))