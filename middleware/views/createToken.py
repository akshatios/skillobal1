from core.config import security_settings
from jose import jwt
from datetime import datetime, timedelta

def create_token(data: dict):
    try:
        # Use SUGAR_VALUE consistently across all auth functions
        token = jwt.encode(data, security_settings.SUGAR_VALUE, algorithm="HS256")
        return token
    except Exception as e:
        raise ValueError(str("Error in token generation"))
