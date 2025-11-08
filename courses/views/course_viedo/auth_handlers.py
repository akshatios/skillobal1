# Video handlers - Authentication handled by middleware
from fastapi import UploadFile, File, Form
from .video_upload import upload_course_video, get_course_videos
from .update_video import update_video_by_file_id
from .delete_video import delete_video_by_file_id
from typing import Optional


# Video Upload Handlers
async def upload_video_handler(
    course_id: str = Form(...),
    video_file: UploadFile = File(...)
):
    """Video upload - authentication handled by middleware"""
    return await upload_course_video(course_id, video_file)

async def get_videos_handler(course_id: str):
    """Get videos - authentication handled by middleware"""
    return await get_course_videos(course_id)

async def update_video_handler(
    course_id: str,
    lesson_id: str,
    fileId: str,
    video_file: UploadFile = File(...),
    video_title: Optional[str] = Form(None),
    video_description: Optional[str] = Form(None),
    order: Optional[int] = Form(None)
):
    """Update video - authentication handled by middleware"""
    return await update_video_by_file_id(
        course_id, lesson_id, fileId, video_file, 
        video_title, video_description, order
    )

async def delete_video_handler(
    course_id: str,
    lesson_id: str,
    fileId: str
):
    """Delete video - authentication handled by middleware"""
    return await delete_video_by_file_id(course_id, lesson_id, fileId)

