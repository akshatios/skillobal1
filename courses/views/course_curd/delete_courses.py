from fastapi import HTTPException
from pydantic import BaseModel, Field
from bson import ObjectId
from core.database import courses_collection
from courses.views.course_curd.layoutdata_update import update_layout_by_rating
from core.config import settings
from tencentcloud.vod.v20180717 import vod_client, models
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
import logging

logger = logging.getLogger(__name__)

# Initialize Tencent client
try:
    cred = credential.Credential(settings.TENCENT_SECRET_ID, settings.TENCENT_SECRET_KEY)
    client_profile = ClientProfile(httpProfile=HttpProfile(endpoint="vod.tencentcloudapi.com"))
    vod_client_instance = vod_client.VodClient(cred, settings.TENCENT_REGION, client_profile)
except Exception as e:
    logger.error(f"Tencent client initialization failed: {e}")
    vod_client_instance = None

async def delete_tencent_video(fileId: str):
    """Delete video from Tencent Cloud VOD"""
    if not vod_client_instance:
        logger.warning(f"Tencent client not available, skipping cloud deletion for {fileId}")
        return False, "Tencent client not available"
    
    try:
        params = models.DeleteMediaRequest()
        params.FileId = fileId
        params.SubAppId = int(settings.TENCENT_SUB_APP_ID)
        
        response = vod_client_instance.DeleteMedia(params)
        logger.info(f"Video deleted from Tencent Cloud: {fileId}")
        return True, "Success"
    except Exception as e:
        error_msg = str(e)
        # If file doesn't exist, consider it as successful deletion
        if "ResourceNotFound" in error_msg or "file not exist" in error_msg:
            logger.info(f"Video {fileId} already deleted or doesn't exist in Tencent Cloud")
            return True, "Already deleted or not found"
        else:
            logger.error(f"Failed to delete video {fileId} from Tencent Cloud: {error_msg}")
            return False, error_msg

async def delete_course(course_id: str):
    """Delete a course by ID and its videos from Tencent Cloud"""
    try:
        object_id = ObjectId(course_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid course ID format")
    
    # First get the course to retrieve video file IDs
    course = await courses_collection.find_one({"_id": object_id})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Delete all videos from Tencent Cloud
    deleted_videos = []
    failed_videos = []
    
    # Delete course level videos
    if course.get("videos"):
        for video in course["videos"]:
            fileId = video.get("tencent_id") or video.get("fileId")
            if fileId:
                logger.info(f"Deleting course video: {fileId}")
                success, error_msg = await delete_tencent_video(fileId)
                if success:
                    deleted_videos.append(fileId)
                else:
                    failed_videos.append({"fileId": fileId, "error": error_msg, "type": "course_video"})
    
    # Delete intro_video
    intro_video = course.get("intro_video") or course.get("thumbnail_video")
    if intro_video:
        intro_fileId = None
        
        # Handle both new object format and old URL format
        if isinstance(intro_video, dict):
            intro_fileId = intro_video.get("fileId")
            logger.info(f"Found intro_video object with fileId: {intro_fileId}")
        elif isinstance(intro_video, str):
            logger.info(f"Found intro_video URL: {intro_video}")
            from courses.views.course_viedo.video_upload import extract_file_id_from_url
            intro_fileId = extract_file_id_from_url(intro_video)
            logger.info(f"Extracted intro_video fileId: {intro_fileId}")
        
        if intro_fileId:
            logger.info(f"Deleting intro video: {intro_fileId}")
            success, error_msg = await delete_tencent_video(intro_fileId)
            if success:
                deleted_videos.append(intro_fileId)
            else:
                failed_videos.append({"fileId": intro_fileId, "error": error_msg, "type": "intro_video"})
    
    # Delete lesson videos
    if course.get("lessons"):
        for lesson in course["lessons"]:
            if lesson.get("videos"):
                for video in lesson["videos"]:
                    fileId = video.get("fileId")
                    if fileId:
                        logger.info(f"Deleting lesson video: {fileId}")
                        success, error_msg = await delete_tencent_video(fileId)
                        if success:
                            deleted_videos.append(fileId)
                        else:
                            failed_videos.append({"fileId": fileId, "error": error_msg, "type": "lesson_video"})
    
    # Delete course from database
    result = await courses_collection.delete_one({"_id": object_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Course not found")

    # Auto-update layout after deletion
    try:
        await update_layout_by_rating()
    except Exception:
        pass  # Don't fail deletion if layout update fails

    return {
        "success": True,
        "message": "Course and videos deleted successfully",
        "deleted_course_id": course_id,
        "deleted_videos": deleted_videos,
        "failed_videos": failed_videos
    }
