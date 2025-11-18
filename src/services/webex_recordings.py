"""
Webex Recordings API Service
Handles integration with Webex Converged Recordings API
"""
import os
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import httpx
from pathlib import Path

from .webex_oauth import webex_oauth

logger = logging.getLogger(__name__)


class WebexRecordingsService:
    """Service for interacting with Webex Converged Recordings API"""

    def __init__(self):
        self.base_url = "https://webexapis.com/v1"
        self.oauth = webex_oauth

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
    ) -> Dict:
        """
        Make an authenticated request to Webex Recordings API

        Args:
            method: HTTP method (GET, POST, DELETE, etc.)
            endpoint: API endpoint
            params: Query parameters
            data: Request body

        Returns:
            API response as dict
        """
        token = await self.oauth.get_valid_token()

        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.request(
                method,
                url,
                headers=headers,
                params=params,
                json=data
            )

            # Handle token refresh on 401
            if response.status_code == 401:
                logger.warning("Received 401, attempting to refresh token...")
                await self.oauth.refresh_access_token()
                token = await self.oauth.get_valid_token()
                headers["Authorization"] = f"Bearer {token}"

                # Retry request
                response = await client.request(
                    method,
                    url,
                    headers=headers,
                    params=params,
                    json=data
                )

            if response.status_code not in [200, 201, 204]:
                logger.error(f"Recordings API error: {response.status_code} - {response.text}")
                raise Exception(f"Webex Recordings API error: {response.status_code} - {response.text}")

            # Return empty dict for 204 No Content
            if response.status_code == 204:
                return {}

            return response.json()

    async def list_recordings(
        self,
        service_type: str = "calling",
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        max_results: int = 100,
        owner_id: Optional[str] = None,
        location_id: Optional[str] = None
    ) -> List[Dict]:
        """
        List converged recordings

        GET /v1/admin/convergedRecordings (admin endpoint required for spark-admin:recordings_read scope)

        Args:
            service_type: Type of service ("calling", "meetings", etc.)
            from_date: Start date for recordings (default: 30 days ago)
            to_date: End date for recordings (default: now)
            max_results: Maximum number of results (default: 100)
            owner_id: Filter by owner ID
            location_id: Filter by location ID

        Returns:
            List of recording objects
        """
        # Default date range: last 30 days
        if not from_date:
            from_date = datetime.utcnow() - timedelta(days=30)
        if not to_date:
            to_date = datetime.utcnow()

        params = {
            "serviceType": service_type,
            "from": from_date.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "to": to_date.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "max": min(max_results, 1000)  # API max is 1000
        }

        if owner_id:
            params["ownerId"] = owner_id
        if location_id:
            params["locationId"] = location_id

        logger.info(f"Listing recordings: {service_type} from {from_date} to {to_date}")

        # IMPORTANT: Use /admin/convergedRecordings for spark-admin:recordings_read scope
        result = await self._make_request("GET", "/admin/convergedRecordings", params=params)
        items = result.get("items", [])

        logger.info(f"Found {len(items)} recording(s)")
        return items

    async def get_recording_details(self, recording_id: str) -> Dict:
        """
        Get details of a specific recording

        GET /v1/convergedRecordings/{recordingId} (no /admin prefix for detail endpoint)

        Args:
            recording_id: The recording ID

        Returns:
            Recording details including download URLs, participants, etc.
        """
        logger.info(f"Fetching recording details: {recording_id}")

        # Note: Detail endpoint does NOT use /admin/ prefix, only list does
        result = await self._make_request("GET", f"/convergedRecordings/{recording_id}")

        logger.info(f"Recording details retrieved: {result.get('topic', 'N/A')}")
        return result

    async def get_recording_metadata(self, recording_id: str) -> Dict:
        """
        Get extended metadata for a recording

        GET /v1/convergedRecordings/{recordingId}/metadata (no /admin prefix)

        This includes:
        - Network information
        - Call flow details
        - Participant relationships
        - Privacy flags
        - Correlation IDs

        Args:
            recording_id: The recording ID

        Returns:
            Extended metadata
        """
        logger.info(f"Fetching recording metadata: {recording_id}")

        try:
            # Note: Metadata endpoint also does NOT use /admin/ prefix
            result = await self._make_request(
                "GET",
                f"/convergedRecordings/{recording_id}/metadata"
            )

            logger.info(f"Metadata retrieved for recording: {recording_id}")
            return result
        except Exception as e:
            logger.warning(f"Could not fetch metadata for {recording_id}: {e}")
            return {}

    async def download_recording_file(
        self,
        download_url: str,
        output_path: str
    ) -> str:
        """
        Download recording audio file from Webex

        Args:
            download_url: The download URL from recording details
            output_path: Local path to save the file

        Returns:
            Path to downloaded file
        """
        logger.info(f"Downloading recording to: {output_path}")

        token = await self.oauth.get_valid_token()
        headers = {"Authorization": f"Bearer {token}"}

        # Create directory if it doesn't exist
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        async with httpx.AsyncClient(timeout=300.0) as client:  # 5 min timeout for downloads
            response = await client.get(download_url, headers=headers)

            if response.status_code != 200:
                raise Exception(f"Failed to download recording: {response.status_code}")

            # Write to file
            with open(output_path, 'wb') as f:
                f.write(response.content)

            file_size = os.path.getsize(output_path)
            logger.info(f"Recording downloaded: {file_size} bytes")

            return output_path

    async def download_transcript(
        self,
        transcript_url: str,
        output_path: str
    ) -> str:
        """
        Download transcript file (VTT format) from Webex

        Args:
            transcript_url: The transcript download URL
            output_path: Local path to save the VTT file

        Returns:
            Path to downloaded transcript file
        """
        logger.info(f"Downloading transcript to: {output_path}")

        token = await self.oauth.get_valid_token()
        headers = {"Authorization": f"Bearer {token}"}

        # Create directory if it doesn't exist
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(transcript_url, headers=headers)

            if response.status_code != 200:
                raise Exception(f"Failed to download transcript: {response.status_code}")

            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(response.text)

            logger.info(f"Transcript downloaded: {output_path}")

            return output_path

    async def delete_recording(self, recording_id: str) -> bool:
        """
        Delete a recording

        DELETE /v1/convergedRecordings/{recordingId} (no /admin prefix)

        Args:
            recording_id: The recording ID

        Returns:
            True if deleted successfully
        """
        logger.info(f"Deleting recording: {recording_id}")

        # Note: Delete endpoint also does NOT use /admin/ prefix
        await self._make_request("DELETE", f"/convergedRecordings/{recording_id}")

        logger.info(f"Recording deleted: {recording_id}")
        return True

    async def get_recording_storage_path(self, recording_id: str) -> str:
        """
        Generate local storage path for recording

        Args:
            recording_id: The recording ID

        Returns:
            Local file path
        """
        # Storage structure: data/recordings/YYYY/MM/DD/{recording_id}.mp3
        now = datetime.utcnow()
        base_dir = Path("data/recordings")
        date_dir = base_dir / now.strftime("%Y/%m/%d")

        date_dir.mkdir(parents=True, exist_ok=True)

        return str(date_dir / f"{recording_id}.mp3")

    async def get_transcript_storage_path(self, recording_id: str) -> str:
        """
        Generate local storage path for transcript

        Args:
            recording_id: The recording ID

        Returns:
            Local file path for VTT transcript
        """
        now = datetime.utcnow()
        base_dir = Path("data/transcripts")
        date_dir = base_dir / now.strftime("%Y/%m/%d")

        date_dir.mkdir(parents=True, exist_ok=True)

        return str(date_dir / f"{recording_id}.vtt")

    def parse_vtt_transcript(self, vtt_path: str) -> str:
        """
        Parse VTT transcript file and extract plain text

        Args:
            vtt_path: Path to VTT file

        Returns:
            Plain text transcript
        """
        try:
            with open(vtt_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Skip VTT header and metadata, extract only text
            text_lines = []
            skip_next = False

            for line in lines:
                line = line.strip()

                # Skip VTT header
                if line.startswith("WEBVTT") or line.startswith("NOTE"):
                    continue

                # Skip timestamp lines
                if "-->" in line:
                    skip_next = False
                    continue

                # Skip empty lines and cue identifiers
                if not line or line.isdigit():
                    continue

                text_lines.append(line)

            transcript_text = " ".join(text_lines)
            logger.info(f"Parsed VTT transcript: {len(transcript_text)} characters")

            return transcript_text

        except Exception as e:
            logger.error(f"Failed to parse VTT transcript: {e}")
            return ""

    async def test_recordings_access(self) -> Dict:
        """
        Test access to Webex Recordings API

        Returns:
            Status information
        """
        try:
            # Try to list recordings
            recordings = await self.list_recordings(max_results=1)

            return {
                "status": "success",
                "has_access": True,
                "recordings_count": len(recordings),
                "message": "Successfully accessed Webex Recordings API"
            }
        except Exception as e:
            return {
                "status": "error",
                "has_access": False,
                "error": str(e),
                "message": "Failed to access Webex Recordings API"
            }


# Global instance
webex_recordings_service = WebexRecordingsService()
