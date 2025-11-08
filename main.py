from fastapi import FastAPI
from core.routers import api_router
from middleware.views.tokenauthentication import AccessTokenAuthenticatorMiddleware
from middleware.views.checkAdmin import create_default_admin
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Skillobal API")

# Create default admin on startup
@app.on_event("startup")
async def startup_event():
    await create_default_admin()

# CORS config - Must be added first
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,  # Fixed: Set to False for wildcard origins
    allow_methods=["*"],
    allow_headers=["*"],
)

# Token Authentication Middleware (add after CORS)
app.add_middleware(AccessTokenAuthenticatorMiddleware)

app.include_router(api_router)

@app.get("/", description="Get API status")
def home():
    return {
        "message": "Welcome to Skillobal backend API",
        "status": "running",
        "endpoints": {
            "admin_login": "/admin/login",
        }
    }


            