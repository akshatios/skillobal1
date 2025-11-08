import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

# Database Configuration
class DatabaseSettings(BaseSettings):
    CONNECTION_STRING: str = os.getenv("MONGO_URI", "")
    DB_NAME: str = os.getenv("DB_NAME", "admin_panel")

# JWT Configuration  
class JWTSettings(BaseSettings):
    SECRET_KEY: str = os.getenv("JWT_SECRET", "")
    ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Security Configuration
class SecuritySettings(BaseSettings):
    SUGAR_VALUE: str = os.getenv("SUGAR_VALUE", "")
    DECODE_PROJECT_ID: str = os.getenv("DECODE_PROJECT_ID", "")

# Tencent Cloud VOD Configuration
class TencentSettings(BaseSettings):
    TENCENT_SUB_APP_ID: str = os.getenv("TENCENT_SUB_APP_ID", "1500042575")
    TENCENT_SECRET_ID: str = os.getenv("TENCENT_SECRET_ID", "")
    TENCENT_SECRET_KEY: str = os.getenv("TENCENT_SECRET_KEY", "")
    TENCENT_REGION: str = os.getenv("TENCENT_REGION", "ap-singapore")

# Initialize settings instances
db_settings = DatabaseSettings()
jwt_settings = JWTSettings() 
# api_settings = APISettings()
security_settings = SecuritySettings()
tencent_settings = TencentSettings()

# Main settings object
class Settings:
    def __init__(self):
        self.TENCENT_SUB_APP_ID = tencent_settings.TENCENT_SUB_APP_ID
        self.TENCENT_SECRET_ID = tencent_settings.TENCENT_SECRET_ID
        self.TENCENT_SECRET_KEY = tencent_settings.TENCENT_SECRET_KEY
        self.TENCENT_REGION = tencent_settings.TENCENT_REGION

settings = Settings()


JWT_SECRET = jwt_settings.SECRET_KEY  # DEPRECATED: Use jwt_settings.SECRET_KEY instead
JWT_ALGORITHM = jwt_settings.ALGORITHM  # DEPRECATED: Use jwt_settings.ALGORITHM instead
SUGAR_VALUE = security_settings.SUGAR_VALUE  # DEPRECATED: Use security_settings.SUGAR_VALUE instead
MONGO_URI = db_settings.CONNECTION_STRING  # DEPRECATED: Use db_settings.CONNECTION_STRING instead
DB_NAME = db_settings.DB_NAME  # DEPRECATED: Use db_settings.DB_NAME instead
