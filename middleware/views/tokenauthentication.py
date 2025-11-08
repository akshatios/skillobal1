from jose import jwt
from fastapi import Request
from bson import ObjectId
from core.config import security_settings
from starlette.responses import JSONResponse
from core.database import users_collection
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.datastructures import MutableHeaders
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AccessTokenAuthenticatorMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip OPTIONS requests and excluded paths
        origin = request.headers.get('origin', '*')
        cors_headers = {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Authorization, Content-Type, token",
            "Access-Control-Allow-Credentials": "true"
        }
        try:
            if request.method == "OPTIONS":
                return await call_next(request)
            
            excluded_paths = [
                "/",
                "/admin/login",
                "/docs",
                "/redoc",
                "/openapi.json"
            ]
            
            # Check exact path match only
            if request.url.path in excluded_paths:
                return await call_next(request)

            # Extract token from Authorization header, token header, or cookies
            token = None
            auth_header = request.headers.get("authorization")
            token_header = request.headers.get("token")
            cookie_token = request.cookies.get("access_token")
            
            if auth_header:
                if auth_header.lower().startswith("bearer "):
                    token = auth_header[7:]
                else:
                    token = auth_header
            elif token_header:
                token = token_header
            elif cookie_token:
                if cookie_token.startswith("Bearer "):
                    token = cookie_token[7:]
                else:
                    token = cookie_token

            # Propagate token to 'token' header if missing
            if token and not token_header:
                headers = MutableHeaders(request.headers)
                headers["token"] = token
                request._headers = headers
                # Update scope headers for ASGI
                new_headers = []
                for key, value in headers.items():
                    new_headers.append((key.lower().encode(), value.encode()))
                request.scope["headers"] = new_headers

            if not token:
                logger.warning(f"No token provided for path: {request.url.path}")
                return JSONResponse(
                    {"msg": "Token not present"},
                    status_code=401,
                    headers=cors_headers
                )
            
            try:
                # Use SUGAR_VALUE from .env (production method)
                decoded_token = jwt.decode(
                    token, security_settings.SUGAR_VALUE, algorithms=["HS256"]
                )
                logger.info("Token verified with SUGAR_VALUE - Enhanced security active")
                
                # Check both _id and sub fields for user ID
                user_id = decoded_token.get("_id") or decoded_token.get("sub")
                request.state.userId = user_id
                user = await users_collection.find_one({"_id": ObjectId(user_id)})
                if not user:
                    logger.warning(f"User not found for ID: {user_id}")
                    return JSONResponse({"msg": "User not found"}, status_code=404, headers=cors_headers)
                
                logger.debug(f"User authenticated: {user_id}")
            except jwt.ExpiredSignatureError:
                logger.warning("Token has expired")
                return JSONResponse({"msg": "Token has expired"}, status_code=401, headers=cors_headers)
            except jwt.InvalidTokenError:
                logger.warning("Invalid token provided")
                return JSONResponse({"msg": "Invalid token"}, status_code=401, headers=cors_headers)
            except Exception as e:
                logger.error(f"Token verification error: {str(e)}")
                return JSONResponse(
                    {"msg": "Authentication failed", "error": str(e)}, status_code=500, headers=cors_headers
                )

            response = await call_next(request)
            return response

        except Exception as e:
            logger.error(f"Middleware error: {str(e)}")
            logger.error(f"Error type: {type(e)}")
            logger.error(f"Request path: {request.url.path}")
            return JSONResponse(
                {"msg": "Authentication middleware error", "error": str(e)},
                status_code=500,
                headers=cors_headers
            )
