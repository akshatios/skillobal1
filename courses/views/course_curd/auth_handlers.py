# Authentication handled by middleware
from fastapi import Query
from courses.views.course_curd.visible_courses import get_visible_courses
from courses.views.course_curd.top_courses import get_top_courses
from courses.views.course_curd.delete_courses import delete_course
from courses.views.course_curd.update_courses import UpdateCourseModel, update_course_with_video
from courses.views.course_curd.visible_T_F import toggle_course_visibility
from courses.views.course_curd.course_details import get_course_details
from courses.views.course_curd.all_courses_details import get_all_courses_details
from courses.views.course_curd.layoutdata_update import update_layout_by_rating, get_layout_courses
from courses.views.course_curd.categories import get_all_categories
from courses.views.course_curd.instructor import get_all_instructors
from courses.views.course_curd.specific_course_specific_viedo_delete import delete_specific_video
from courses.views.course_curd.replace_specific_video import replace_specific_video
from courses.views.course_curd.course_lessons_count import get_course_lessons_count
from courses.views.course_curd.delete_course_video import delete_course_video

async def get_visible_courses_handler():
    """Get visible courses - authentication handled by middleware"""
    return await get_visible_courses()

async def get_top_courses_handler():
    """Get top courses - authentication handled by middleware"""
    return await get_top_courses()

async def delete_course_handler(course_id: str):
    """Delete course - authentication handled by middleware"""
    return await delete_course(course_id)

async def get_course_details_handler(course_id: str):
    """Get course details - authentication handled by middleware"""
    return await get_course_details(course_id)

async def get_all_courses_details_handler(page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100)):
    """Get all courses details with pagination - authentication handled by middleware"""
    return await get_all_courses_details(page, limit)

from fastapi import Form, File, UploadFile
from typing import Optional, Union, List

async def update_course_with_video_handler(
    course_id: str,
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    image_url: Optional[str] = Form(None),
    rating: Union[float, str, None] = Form(None),
    price: Union[float, str, None] = Form(None),
    visible: Optional[bool] = Form(None),
    instructor_id: Optional[str] = Form(None),
    category_id: Optional[str] = Form(None),
    licence_key: Optional[str] = Form(None),
    content_language: Optional[str] = Form(None),
    thumbnail_video: Optional[UploadFile] = File(None),
    thumbnail_img: Optional[UploadFile] = File(None)
):
    """Update course with video upload - authentication handled by middleware"""
    return await update_course_with_video(
        course_id, title, description, image_url, rating, price,
        visible, instructor_id, category_id, licence_key, content_language,
        thumbnail_video, thumbnail_img
    )

async def update_layout_handler():
    """Update layout based on course ratings - authentication handled by middleware"""
    return await update_layout_by_rating()

async def get_layout_courses_handler(layout_id: str):
    """Get courses for specific layout - authentication handled by middleware"""
    return await get_layout_courses(layout_id)

async def toggle_course_visibility_handler(course_id: str):
    """Toggle course visibility - authentication handled by middleware"""
    return await toggle_course_visibility(course_id)

async def get_all_categories_handler():
    """Get all categories - authentication handled by middleware"""
    return await get_all_categories()

async def get_all_instructors_handler():
    """Get all instructors - authentication handled by middleware"""
    return await get_all_instructors()

async def delete_specific_video_handler(course_id: str, file_id: str):
    """Delete specific video by fileId - authentication handled by middleware"""
    return await delete_specific_video(course_id, file_id)

async def replace_specific_video_handler(
    course_id: str,
    file_id: str,
    video_title: Optional[str] = Form(None),
    video_description: Optional[str] = Form(None),
    video_file: UploadFile = File(...)
):
    """Replace specific video by fileId - authentication handled by middleware"""
    return await replace_specific_video(course_id, file_id, video_title, video_description, video_file)

async def get_course_lessons_count_handler(course_id: str):
    """Get total lessons count for a course - authentication handled by middleware"""
    return await get_course_lessons_count(course_id)

async def delete_course_video_handler(course_id: str, file_id: str):
    """Delete specific video from course by FileId - authentication handled by middleware"""
    return await delete_course_video(course_id, file_id)