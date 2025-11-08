from fastapi import APIRouter
from middleware.views.adminLogin import admin_login
from middleware.views.checkAdmin import create_default_admin

auth_router = APIRouter(prefix="/admin", tags=["Admin"])

# Startup event moved to main.py (deprecated on router)

auth_router.add_api_route("/login", admin_login, methods=["POST"], description="Admin login authentication")

