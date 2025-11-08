from fastapi import APIRouter

# Import handlers
from courses.views.course_curd.auth_handlers import (
    get_visible_courses_handler,
    get_top_courses_handler,
    delete_course_handler,
    get_course_details_handler,
    get_all_courses_details_handler,
    toggle_course_visibility_handler,
    update_layout_handler,
    get_layout_courses_handler,
    get_all_categories_handler,
    get_all_instructors_handler,
    get_course_lessons_count_handler,
    delete_course_video_handler,
)
from courses.views.course_viedo.auth_handlers import (
    update_video_handler,
    delete_video_handler,
)
from courses.views.course_curd.create_courses import create_course
from courses.views.course_curd.update_courses import update_course_with_video, remove_video_from_course
from courses.views.course_curd.update_specific_video import update_specific_video
from courses.views.lessons.auth_handlers import (
    create_lesson_handler,
    update_lesson_handler,
    delete_lesson_handler,
    get_lessons_handler,
    get_lesson_details_handler,
    add_video_to_lesson_handler,
)

courses_router = APIRouter(prefix="/admin", tags=["Courses"])

# Course Routes
courses_router.add_api_route("/courses", get_visible_courses_handler, methods=["GET"], description="Get visible courses")
courses_router.add_api_route("/courses/all_course_full_details", get_all_courses_details_handler, methods=["GET"], description="Get all courses with full details")
courses_router.add_api_route("/courses/top", get_top_courses_handler, methods=["GET"], description="Get top courses")
courses_router.add_api_route("/courses/add", create_course, methods=["POST"], description="Create new course")

courses_router.add_api_route("/courses/{course_id}/update-course", update_course_with_video, methods=["PUT"], description="Update course with video")

courses_router.add_api_route("/courses/delete", delete_course_handler, methods=["DELETE"], description="Delete course")


courses_router.add_api_route("/courses/{course_id}/toggle-visibility", toggle_course_visibility_handler, methods=["POST"], description="Toggle course visibility")


courses_router.add_api_route("/courses/specific-course-details/{course_id}", get_course_details_handler, methods=["GET"], description="Get specific course details")
courses_router.add_api_route("/courses/{course_id}/lessons-count", get_course_lessons_count_handler, methods=["GET"], description="Get course lessons count")
courses_router.add_api_route("/courses/{course_id}/videos/{file_id}", delete_course_video_handler, methods=["DELETE"], description="Delete course video by file ID")
courses_router.add_api_route("/courses/{course_id}/delete-video/{video_order}", remove_video_from_course, methods=["DELETE"], description="Remove video from course by order")
courses_router.add_api_route("/courses/{course_id}/update-video/{fileId}", update_specific_video, methods=["PUT"], description="Update specific video")

# Video Routes
courses_router.add_api_route("/courses/{course_id}/lessons/{lesson_id}/videos/{fileId}", update_video_handler, methods=["PUT"], description="Update lesson video")
courses_router.add_api_route("/courses/{course_id}/lessons/{lesson_id}/videos/{fileId}", delete_video_handler, methods=["DELETE"], description="Delete lesson video")

# Layout Routes
courses_router.add_api_route("/layout/update", update_layout_handler, methods=["POST"], description="Update layout")
courses_router.add_api_route("/layout/{layout_id}/courses", get_layout_courses_handler, methods=["GET"], description="Get courses by layout")

# Categories and Instructors Routes
courses_router.add_api_route("/categories", get_all_categories_handler, methods=["GET"], description="Get all categories")
courses_router.add_api_route("/instructors", get_all_instructors_handler, methods=["GET"], description="Get all instructors")

# Lesson Routes
courses_router.add_api_route("/courses/{course_id}/lessons", create_lesson_handler, methods=["POST"], description="Create new lesson")
courses_router.add_api_route("/courses/{course_id}/lessons", get_lessons_handler, methods=["GET"], description="Get course lessons")
courses_router.add_api_route("/courses/{course_id}/lessons/{lesson_id}", get_lesson_details_handler, methods=["GET"], description="Get lesson details")
courses_router.add_api_route("/courses/{course_id}/lessons/{lesson_id}", update_lesson_handler, methods=["PUT"], description="Update lesson")
courses_router.add_api_route("/courses/{course_id}/lessons/{lesson_id}", delete_lesson_handler, methods=["DELETE"], description="Delete lesson")

# Lesson Video Routes
courses_router.add_api_route("/courses/{course_id}/lessons/{lesson_id}/videos", add_video_to_lesson_handler, methods=["POST"], description="Add video to lesson")



