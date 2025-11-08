import motor.motor_asyncio
from core.config import MONGO_URI, DB_NAME

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]  # database name from env
users_collection = db["users"]
admins_collection = db["admins"]
courses_collection = db["courses"]
slider_collection = db["sliders"]
layout_collection = db["layout"]
categories_collection = db["categories"]
instructors_collection = db["instructor"]
