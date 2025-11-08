from fastapi import APIRouter
from dashboard.views.home import dashboard_home

dashboard_router = APIRouter(prefix="/admin", tags=["Dashboard"])

dashboard_router.add_api_route("/dashboard", dashboard_home, methods=["GET"], description="Get dashboard data")
