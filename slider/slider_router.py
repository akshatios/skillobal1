from fastapi import APIRouter
from slider.views.home import slider_home

slider_router = APIRouter(prefix="/admin", tags=["Slider"])

slider_router.add_api_route("/slider", slider_home, methods=["GET"], description="Get all slider data")
