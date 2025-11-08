from fastapi import Form, File, UploadFile
from courses.views.lessons.create_lesson import create_lesson
from courses.views.lessons.update_lesson import update_lesson
from courses.views.lessons.delete_lesson import delete_lesson
from courses.views.lessons.get_lessons import get_lessons, get_lesson_details
from courses.views.lessons.lesson_video_ops import (
    add_video_to_lesson,
    delete_video_from_lesson,
    update_video_in_lesson
)
from typing import Optional, List

async def create_lesson_handler(
    course_id: str,
    lesson_title: str = Form(...),
    lesson_description: Optional[str] = Form(None),
    order: int = Form(...)
):
    """Create new lesson - authentication handled by middleware"""
    return await create_lesson(course_id, lesson_title, lesson_description, order)

async def update_lesson_handler(
    course_id: str,
    lesson_id: str,
    lesson_title: Optional[str] = Form(None),
    lesson_description: Optional[str] = Form(None),
    order: Optional[int] = Form(None)
):
    """Update lesson - authentication handled by middleware"""
    return await update_lesson(course_id, lesson_id, lesson_title, lesson_description, order)

async def delete_lesson_handler(
    course_id: str,
    lesson_id: str
):
    """Delete lesson - authentication handled by middleware"""
    return await delete_lesson(course_id, lesson_id)

async def get_lessons_handler(course_id: str):
    """Get all lessons for a course - authentication handled by middleware"""
    return await get_lessons(course_id)

async def get_lesson_details_handler(
    course_id: str,
    lesson_id: str
):
    """Get specific lesson details - authentication handled by middleware"""
    return await get_lesson_details(course_id, lesson_id)

async def add_video_to_lesson_handler(
    course_id: str,
    lesson_id: str,
    video_title: str = Form(...),
    video_description: Optional[str] = Form(None),
    video_file: UploadFile = File(...)
):
    """Add video to lesson - authentication handled by middleware"""
    return await add_video_to_lesson(course_id, lesson_id, video_title, video_description, video_file)

async def delete_video_from_lesson_handler(
    course_id: str,
    lesson_id: str,
    video_id: str
):
    """Delete video from lesson - authentication handled by middleware"""
    return await delete_video_from_lesson(course_id, lesson_id, video_id)

async def update_video_in_lesson_handler(
    course_id: str,
    lesson_id: str,
    video_id: str,
    video_title: Optional[str] = Form(None),
    video_description: Optional[str] = Form(None)
):
    """Update video in lesson - authentication handled by middleware"""
    return await update_video_in_lesson(course_id, lesson_id, video_id, video_title, video_description)