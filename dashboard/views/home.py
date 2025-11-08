from user.views.list_users import list_users
from core.database import slider_collection
from courses.views.course_curd.top_courses import get_top_courses

async def dashboard_home():
    # Reuse existing user logic to get users list and active courses count
    user_data = await list_users()  # returns { total, activeCourses, users }
    # Get slider count separately
    total_sliders = await slider_collection.count_documents({})
    # Get top courses list from layout-linked courses
    top_courses_data = await get_top_courses()  # returns { top_courses, total, ... }

    # Combine and return
    return {
        "users": user_data.get("users", []),
        "total_users": user_data.get("total", 0),
        "activeCourses": user_data.get("activeCourses", 0),
        "total_sliders": total_sliders,
        "top_courses": top_courses_data.get("top_courses", [])
    }
