"""
Authentication Routes
OAuth 2.0 flow for Webex Integration
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import RedirectResponse, HTMLResponse
from pydantic import BaseModel
import logging

from src.services.webex_oauth import webex_oauth

logger = logging.getLogger(__name__)

router = APIRouter()


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = "Bearer"


class TokenInfoResponse(BaseModel):
    has_access_token: bool
    has_refresh_token: bool
    token_expires_at: Optional[str]
    is_expired: bool


@router.get("/login")
async def login():
    """
    Start the OAuth flow by redirecting to Webex authorization page
    """
    auth_url = webex_oauth.get_authorization_url()
    logger.info(f"Redirecting to Webex authorization URL")
    return RedirectResponse(url=auth_url)


@router.get("/callback")
async def oauth_callback(code: str, state: str = None):
    """
    OAuth callback endpoint
    Exchanges the authorization code for access token

    Args:
        code: Authorization code from Webex
        state: State parameter for CSRF protection
    """
    try:
        logger.info(f"Received OAuth callback with code")

        # Exchange code for token
        token_data = await webex_oauth.exchange_code_for_token(code)

        # Return success page with token info
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Webex Authentication Successful</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background: linear-gradient(135deg, #E30519 0%, #A80313 100%);
                }}
                .container {{
                    background: white;
                    padding: 40px;
                    border-radius: 12px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                    max-width: 600px;
                    text-align: center;
                }}
                h1 {{
                    color: #E30519;
                    margin-bottom: 20px;
                }}
                .success-icon {{
                    font-size: 64px;
                    margin-bottom: 20px;
                }}
                .info {{
                    background: #f5f5f5;
                    padding: 20px;
                    border-radius: 8px;
                    margin-top: 20px;
                    text-align: left;
                }}
                .info p {{
                    margin: 10px 0;
                    font-family: monospace;
                    font-size: 14px;
                }}
                .button {{
                    display: inline-block;
                    margin-top: 20px;
                    padding: 12px 24px;
                    background: #E30519;
                    color: white;
                    text-decoration: none;
                    border-radius: 6px;
                    font-weight: bold;
                }}
                .button:hover {{
                    background: #C70416;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="success-icon">✅</div>
                <h1>¡Autenticación Exitosa!</h1>
                <p>Tu aplicación está ahora conectada a Webex Calling.</p>

                <div class="info">
                    <p><strong>Status:</strong> Connected</p>
                    <p><strong>Token Type:</strong> {token_data.get('token_type', 'Bearer')}</p>
                    <p><strong>Expires In:</strong> {token_data.get('expires_in', 0)} seconds</p>
                    <p><strong>Scopes:</strong> {token_data.get('scope', 'N/A')}</p>
                </div>

                <a href="http://localhost:5173" class="button">Ir al Dashboard →</a>
            </div>
        </body>
        </html>
        """

        return HTMLResponse(content=html_content)

    except Exception as e:
        logger.error(f"OAuth callback failed: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Authentication failed: {str(e)}")


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token():
    """
    Refresh the access token using the refresh token
    """
    try:
        token_data = await webex_oauth.refresh_access_token()
        return TokenResponse(
            access_token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token", webex_oauth.refresh_token),
            expires_in=token_data.get("expires_in", 86400)
        )
    except Exception as e:
        logger.error(f"Token refresh failed: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Token refresh failed: {str(e)}")


@router.get("/status", response_model=TokenInfoResponse)
async def get_auth_status():
    """
    Get current authentication status
    """
    info = webex_oauth.get_token_info()
    return TokenInfoResponse(**info)


@router.post("/logout")
async def logout():
    """
    Logout and clear tokens (Note: doesn't revoke token on Webex side)
    """
    webex_oauth.access_token = None
    webex_oauth.refresh_token = None
    webex_oauth.token_expires_at = None

    return {"message": "Logged out successfully"}
