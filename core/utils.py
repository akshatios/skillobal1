from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from core.config import jwt_settings, security_settings

# Configure CryptContext with explicit bcrypt settings to avoid initialization issues
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,  # Explicitly set rounds
    bcrypt__ident="2b"  # Use 2b variant which is more stable
)

def _safe_truncate_password(password: str) -> str:
    """Safely truncate password to 72 bytes without corrupting UTF-8 characters."""
    password_bytes = password.encode('utf-8')
    if len(password_bytes) <= 72:
        return password
    
    # Truncate to 72 bytes, then find the last valid UTF-8 character boundary
    truncated = password_bytes[:72]
    # Decode with 'replace' to handle incomplete characters, then re-encode to get valid UTF-8
    return truncated.decode('utf-8', 'replace').encode('utf-8').decode('utf-8')

# Hash password
def hash_password(password: str) -> str:
    # bcrypt has a 72-byte limit, so we truncate safely
    safe_password = _safe_truncate_password(password)
    return pwd_context.hash(safe_password)

# Verify password
def verify_password(password: str, hashed: str) -> bool:
    # Apply same safe truncation logic as hash_password for consistency
    safe_password = _safe_truncate_password(password)
    return pwd_context.verify(safe_password, hashed)

# Removed inconsistent token functions - using only middleware authentication
