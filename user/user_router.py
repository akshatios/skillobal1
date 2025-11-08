from fastapi import APIRouter
from user.views.list_users import list_users

user_router = APIRouter(prefix="/admin", tags=["User"])

user_router.add_api_route("/users", list_users, methods=["GET"], description="Get all users list")

