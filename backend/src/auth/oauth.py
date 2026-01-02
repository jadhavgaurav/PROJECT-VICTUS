import secrets
import requests
from urllib.parse import urlencode
from typing import Dict, Any, Tuple
from fastapi import HTTPException, status

from src.config import settings
from src.models.oauth import OAuthProvider

class OAuthService:
    @staticmethod
    def generate_state() -> str:
        return secrets.token_urlsafe(32)

    @staticmethod
    def get_google_auth_url(state: str) -> str:
        if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_REDIRECT_URI:
            raise HTTPException(status_code=500, detail="Google OAuth not configured")
        
        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "response_type": "code",
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "scope": "openid email profile",
            "state": state,
            "access_type": "offline",
            "prompt": "consent"
        }
        return f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"

    @staticmethod
    def get_microsoft_auth_url(state: str) -> str:
        if not settings.MS_CLIENT_ID or not settings.MICROSOFT_REDIRECT_URI:
            raise HTTPException(status_code=500, detail="Microsoft OAuth not configured")
        
        # Use 'common' for multi-tenant or specific tenant ID
        tenant = settings.MS_TENANT_ID or "common"
        
        params = {
            "client_id": settings.MS_CLIENT_ID,
            "response_type": "code",
            "redirect_uri": settings.MICROSOFT_REDIRECT_URI,
            "scope": "openid email profile offline_access User.Read",
            "state": state,
            "response_mode": "query",
            "prompt": "select_account"
        }
        return f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize?{urlencode(params)}"

    @staticmethod
    def exchange_google_code(code: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        }
        
        # 1. Get Token
        response = requests.post(token_url, data=data)
        if not response.ok:
            raise HTTPException(status_code=400, detail=f"Failed to exchange code: {response.text}")
        
        token_data = response.json()
        access_token = token_data.get("access_token")
        
        # 2. Get User Info
        user_info_url = "https://www.googleapis.com/oauth2/v3/userinfo"
        user_response = requests.get(user_info_url, headers={"Authorization": f"Bearer {access_token}"})
        if not user_response.ok:
            raise HTTPException(status_code=400, detail="Failed to get user info")
            
        return token_data, user_response.json()

    @staticmethod
    def exchange_microsoft_code(code: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        tenant = settings.MS_TENANT_ID or "common"
        token_url = f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"
        
        data = {
            "client_id": settings.MS_CLIENT_ID,
            "client_secret": settings.MS_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": settings.MICROSOFT_REDIRECT_URI,
        }
        
        # 1. Get Token
        response = requests.post(token_url, data=data)
        if not response.ok:
             # Basic error handling
             raise HTTPException(status_code=400, detail=f"Failed to exchange MS code: {response.text}")
        
        token_data = response.json()
        access_token = token_data.get("access_token")
        
        # 2. Get User Info
        user_info_url = "https://graph.microsoft.com/v1.0/me"
        user_response = requests.get(user_info_url, headers={"Authorization": f"Bearer {access_token}"})
        if not user_response.ok:
             raise HTTPException(status_code=400, detail="Failed to get MS user info")
        
        return token_data, user_response.json()
