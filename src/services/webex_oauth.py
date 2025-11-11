"""
Webex OAuth 2.0 Authentication Service
Handles the OAuth flow for Webex Integration
"""
import os
import json
import logging
from typing import Optional, Dict
from datetime import datetime, timedelta
from pathlib import Path
import httpx
from urllib.parse import urlencode

logger = logging.getLogger(__name__)


class WebexOAuth:
    """Webex OAuth 2.0 handler"""

    def __init__(self):
        self.client_id = os.getenv("WEBEX_CLIENT_ID")
        self.client_secret = os.getenv("WEBEX_CLIENT_SECRET")
        self.redirect_uri = os.getenv("WEBEX_REDIRECT_URI")
        self.scopes = os.getenv("WEBEX_SCOPES", "")

        self.auth_url = os.getenv("WEBEX_AUTH_URL", "https://webexapis.com/v1/authorize")
        self.token_url = os.getenv("WEBEX_TOKEN_URL", "https://webexapis.com/v1/access_token")

        # Token storage file
        self.token_file = Path(".webex_tokens.json")

        # Storage for tokens
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None

        if not self.client_id or not self.client_secret:
            raise ValueError("WEBEX_CLIENT_ID and WEBEX_CLIENT_SECRET must be set")

        # Load tokens from file if available
        self._load_tokens()

    def get_authorization_url(self, state: str = "webex_auth") -> str:
        """
        Generate the authorization URL for the user to visit

        Args:
            state: A random string to prevent CSRF attacks

        Returns:
            Full authorization URL
        """
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": self.scopes,
            "state": state
        }

        url = f"{self.auth_url}?{urlencode(params)}"
        logger.info(f"Generated authorization URL with scopes: {self.scopes}")
        return url

    async def exchange_code_for_token(self, code: str) -> Dict[str, any]:
        """
        Exchange authorization code for access token

        Args:
            code: Authorization code from callback

        Returns:
            Token response including access_token, refresh_token, expires_in
        """
        data = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "redirect_uri": self.redirect_uri
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.token_url,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )

            if response.status_code != 200:
                logger.error(f"Token exchange failed: {response.status_code} - {response.text}")
                raise Exception(f"Failed to exchange code for token: {response.text}")

            token_data = response.json()

            # Store tokens
            self.access_token = token_data["access_token"]
            self.refresh_token = token_data.get("refresh_token")
            expires_in = token_data.get("expires_in", 86400)  # Default 24 hours
            self.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

            logger.info(f"Successfully obtained access token, expires in {expires_in} seconds")

            # Save tokens to file
            self._save_tokens()

            return token_data

    async def refresh_access_token(self) -> Dict[str, any]:
        """
        Refresh the access token using the refresh token

        Returns:
            New token response
        """
        if not self.refresh_token:
            raise Exception("No refresh token available")

        data = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.token_url,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )

            if response.status_code != 200:
                logger.error(f"Token refresh failed: {response.status_code} - {response.text}")
                raise Exception(f"Failed to refresh token: {response.text}")

            token_data = response.json()

            # Update tokens
            self.access_token = token_data["access_token"]
            if "refresh_token" in token_data:
                self.refresh_token = token_data["refresh_token"]

            expires_in = token_data.get("expires_in", 86400)
            self.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

            logger.info(f"Successfully refreshed access token, expires in {expires_in} seconds")

            # Save tokens to file
            self._save_tokens()

            return token_data

    def is_token_expired(self) -> bool:
        """Check if the access token is expired"""
        if not self.token_expires_at:
            return True
        return datetime.utcnow() >= self.token_expires_at

    async def get_valid_token(self) -> str:
        """
        Get a valid access token, refreshing if necessary

        Returns:
            Valid access token
        """
        if not self.access_token:
            raise Exception("No access token available. Please authenticate first.")

        if self.is_token_expired() and self.refresh_token:
            logger.info("Access token expired, refreshing...")
            await self.refresh_access_token()

        return self.access_token

    def _save_tokens(self):
        """Save tokens to file"""
        try:
            token_data = {
                "access_token": self.access_token,
                "refresh_token": self.refresh_token,
                "token_expires_at": self.token_expires_at.isoformat() if self.token_expires_at else None
            }
            with open(self.token_file, 'w') as f:
                json.dump(token_data, f, indent=2)
            logger.info("Tokens saved to file")
        except Exception as e:
            logger.error(f"Failed to save tokens: {e}")

    def _load_tokens(self):
        """Load tokens from file"""
        try:
            if self.token_file.exists():
                with open(self.token_file, 'r') as f:
                    token_data = json.load(f)

                self.access_token = token_data.get("access_token")
                self.refresh_token = token_data.get("refresh_token")

                expires_str = token_data.get("token_expires_at")
                if expires_str:
                    self.token_expires_at = datetime.fromisoformat(expires_str)

                logger.info("Tokens loaded from file")
        except Exception as e:
            logger.warning(f"Failed to load tokens: {e}")

    def get_token_info(self) -> Dict[str, any]:
        """Get current token information"""
        return {
            "has_access_token": bool(self.access_token),
            "has_refresh_token": bool(self.refresh_token),
            "token_expires_at": self.token_expires_at.isoformat() if self.token_expires_at else None,
            "is_expired": self.is_token_expired() if self.token_expires_at else True
        }


# Global OAuth instance
webex_oauth = WebexOAuth()
