"""
Webex API Client
Handles all API calls to Webex Calling API including CDRs
"""
import os
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import httpx
from .webex_oauth import webex_oauth

logger = logging.getLogger(__name__)


class WebexClient:
    """Client for Webex Calling API"""

    def __init__(self):
        self.base_url = os.getenv("WEBEX_BASE_URL", "https://webexapis.com/v1")
        self.analytics_url = "https://analytics.webexapis.com/v1"  # For CDRs
        self.oauth = webex_oauth

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        base_url: Optional[str] = None
    ) -> Dict:
        """
        Make an authenticated request to Webex API

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (e.g., "/telephony/config/calling-detail-records")
            params: Query parameters
            data: Request body
            base_url: Optional override base URL (e.g., for analytics API)

        Returns:
            API response as dict
        """
        # Get valid token (auto-refresh if needed)
        token = await self.oauth.get_valid_token()

        url = f"{base_url or self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(
                method,
                url,
                headers=headers,
                params=params,
                json=data
            )

            if response.status_code == 401:
                # Token might be invalid, try to refresh
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

            if response.status_code not in [200, 201]:
                logger.error(f"API request failed: {response.status_code} - {response.text}")
                raise Exception(f"Webex API error: {response.status_code} - {response.text}")

            return response.json()

    async def get_organization_info(self) -> Dict:
        """
        Get organization information

        Returns:
            Organization details
        """
        logger.info("Fetching organization information...")
        result = await self._make_request("GET", "/organizations")
        orgs = result.get("items", [])

        if not orgs:
            raise Exception("No organizations found")

        org = orgs[0]  # Get first organization
        logger.info(f"Organization: {org.get('displayName')} - {org.get('id')}")

        return org

    async def get_cdrs(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
        locations: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Get Call Detail Records (CDRs) from Webex Calling

        Args:
            start_time: Start datetime for CDRs (default: 24 hours ago)
            end_time: End datetime for CDRs (default: now)
            limit: Maximum number of records to return
            locations: List of location IDs to filter by

        Returns:
            List of CDR records
        """
        # Default time range: last 24 hours
        # NOTE: Webex requires endTime to be at least 5 minutes in the past
        if not end_time:
            end_time = datetime.utcnow() - timedelta(minutes=5)
        if not start_time:
            start_time = end_time - timedelta(hours=24)

        # Format datetimes as ISO 8601
        params = {
            "startTime": start_time.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "endTime": end_time.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "max": min(limit, 1000)  # Webex API max is 1000
        }

        if locations:
            params["locations"] = ",".join(locations)

        logger.info(f"Fetching CDRs from {start_time} to {end_time}...")

        # Webex Detailed Call History endpoint (analytics API)
        endpoint = "/cdr_feed"

        try:
            result = await self._make_request(
                "GET",
                endpoint,
                params=params,
                base_url=self.analytics_url
            )
            items = result.get("items", [])

            logger.info(f"Retrieved {len(items)} CDR records")
            return items

        except Exception as e:
            logger.error(f"Failed to fetch CDRs: {str(e)}")
            raise

    async def get_locations(self) -> List[Dict]:
        """
        Get all locations in the organization

        Returns:
            List of location objects
        """
        logger.info("Fetching locations...")
        result = await self._make_request("GET", "/locations")
        locations = result.get("items", [])

        logger.info(f"Found {len(locations)} locations")
        return locations

    async def get_people(self, email: Optional[str] = None, max_results: int = 100) -> List[Dict]:
        """
        Get people (users) in the organization

        Args:
            email: Filter by email address
            max_results: Maximum number of results

        Returns:
            List of person objects
        """
        params = {"max": max_results}
        if email:
            params["email"] = email

        logger.info(f"Fetching people{' for email: ' + email if email else ''}...")
        result = await self._make_request("GET", "/people", params=params)
        people = result.get("items", [])

        logger.info(f"Found {len(people)} people")
        return people

    async def get_telephony_config(self, location_id: str) -> Dict:
        """
        Get telephony configuration for a location

        Args:
            location_id: Location ID

        Returns:
            Telephony configuration
        """
        logger.info(f"Fetching telephony config for location: {location_id}")
        result = await self._make_request(
            "GET",
            f"/telephony/config/locations/{location_id}"
        )
        return result

    async def get_report_templates(self) -> List[Dict]:
        """
        Get list of available report templates

        Returns:
            List of report template objects
        """
        logger.info("Fetching report templates...")
        result = await self._make_request("GET", "/report-templates")
        templates = result.get("items", [])

        logger.info(f"Found {len(templates)} report templates")
        return templates

    async def create_report(
        self,
        template_id: int,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict:
        """
        Create a new analytics report

        Args:
            template_id: Template ID for the report type
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            Report object with ID
        """
        data = {"templateId": template_id}

        if start_date:
            data["startDate"] = start_date
        if end_date:
            data["endDate"] = end_date

        logger.info(f"Creating report with template {template_id}, dates: {start_date} to {end_date}")
        result = await self._make_request("POST", "/reports", data=data)

        logger.info(f"Report created: {result.get('id')}")
        return result

    async def get_reports(
        self,
        service: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None
    ) -> List[Dict]:
        """
        Get list of generated reports

        Args:
            service: Filter by service type
            from_date: Filter from date
            to_date: Filter to date

        Returns:
            List of report objects
        """
        params = {}
        if service:
            params["service"] = service
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date

        logger.info(f"Fetching reports with filters: {params}")
        result = await self._make_request("GET", "/reports", params=params)
        reports = result.get("items", [])

        logger.info(f"Found {len(reports)} reports")
        return reports

    async def get_report(self, report_id: str) -> Dict:
        """
        Get details of a specific report

        Args:
            report_id: Report ID

        Returns:
            Report object with download URL
        """
        logger.info(f"Fetching report: {report_id}")
        result = await self._make_request("GET", f"/reports/{report_id}")

        return result

    async def test_connection(self) -> Dict:
        """
        Test the connection to Webex API

        Returns:
            Status information
        """
        try:
            org = await self.get_organization_info()

            return {
                "status": "connected",
                "org_id": org.get("id"),
                "org_name": org.get("displayName"),
                "token_info": self.oauth.get_token_info()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "token_info": self.oauth.get_token_info()
            }


# Global Webex client instance
webex_client = WebexClient()
