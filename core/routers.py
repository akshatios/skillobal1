from fastapi import APIRouter
from middleware.auth_router import auth_router
from dashboard.dashboard_router import dashboard_router
from user.user_router import user_router
from courses.courses_router import courses_router
from slider.slider_router import slider_router

api_router = APIRouter()

# Include all module routers
api_router.include_router(auth_router)
api_router.include_router(dashboard_router)
api_router.include_router(user_router)
api_router.include_router(courses_router)
api_router.include_router(slider_router)


