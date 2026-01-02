"""
Frontend page serving endpoints
"""

import os
from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter(tags=["Pages"])


@router.get("/")
async def read_root():
    """Serve the main frontend page."""
    if os.path.exists("static/index.html"):
        return FileResponse('static/index.html')
    else:
        return {"message": "Project VICTUS API", "docs": "/docs"}


@router.get("/login")
async def login_page():
    """Serve the login page."""
    if os.path.exists("static/login.html"):
        return FileResponse('static/login.html')
    else:
        return {"message": "Login page not found"}


@router.get("/signup")
async def signup_page():
    """Serve the signup page."""
    if os.path.exists("static/signup.html"):
        return FileResponse('static/signup.html')
    else:
        return {"message": "Signup page not found"}


@router.get("/manifest.json")
async def manifest():
    """Serve the PWA manifest."""
    if os.path.exists("static/manifest.json"):
        return FileResponse('static/manifest.json', media_type='application/manifest+json')
    else:
        return {"error": "Manifest not found"}

