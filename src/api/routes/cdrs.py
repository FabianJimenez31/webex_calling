"""
Call Detail Records (CDR) Routes
Endpoints for fetching and managing CDRs from Webex Calling
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from src.services.webex_client import webex_client

logger = logging.getLogger(__name__)

router = APIRouter()


class CDRRecord(BaseModel):
    """CDR Record model"""
    callId: Optional[str] = None
    startTime: Optional[str] = None
    endTime: Optional[str] = None
    duration: Optional[int] = None
    callingNumber: Optional[str] = None
    calledNumber: Optional[str] = None
    direction: Optional[str] = None
    callType: Optional[str] = None
    location: Optional[str] = None
    userEmail: Optional[str] = None


class CDRListResponse(BaseModel):
    """CDR list response"""
    total: int
    items: List[dict]
    start_time: str
    end_time: str


class WebexStatusResponse(BaseModel):
    """Webex connection status"""
    status: str
    org_id: Optional[str] = None
    org_name: Optional[str] = None
    token_info: dict


@router.get("/", response_model=CDRListResponse)
async def get_cdrs(
    start_time: Optional[str] = Query(None, description="Start time in ISO format"),
    end_time: Optional[str] = Query(None, description="End time in ISO format"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records"),
    locations: Optional[str] = Query(None, description="Comma-separated location IDs")
):
    """
    Get Call Detail Records (CDRs) from Webex Calling

    Args:
        start_time: Start datetime (default: 24 hours ago)
        end_time: End datetime (default: now)
        limit: Maximum number of records (default: 100)
        locations: Filter by location IDs

    Returns:
        List of CDR records
    """
    try:
        # Parse timestamps
        end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00')) if end_time else None
        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00')) if start_time else None

        # Parse locations
        location_list = locations.split(',') if locations else None

        logger.info(f"Fetching CDRs with limit={limit}, locations={location_list}")

        # Fetch CDRs from Webex
        cdrs = await webex_client.get_cdrs(
            start_time=start_dt,
            end_time=end_dt,
            limit=limit,
            locations=location_list
        )

        # Use actual times or defaults
        actual_end = end_dt or datetime.utcnow()
        actual_start = start_dt or (actual_end - timedelta(hours=24))

        return CDRListResponse(
            total=len(cdrs),
            items=cdrs,
            start_time=actual_start.isoformat(),
            end_time=actual_end.isoformat()
        )

    except Exception as e:
        logger.error(f"Failed to fetch CDRs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch CDRs: {str(e)}")


@router.get("/status", response_model=WebexStatusResponse)
async def get_webex_status():
    """
    Test connection to Webex API and get organization info
    """
    try:
        status = await webex_client.test_connection()
        return WebexStatusResponse(**status)
    except Exception as e:
        logger.error(f"Failed to get Webex status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to connect to Webex: {str(e)}")


@router.get("/locations")
async def get_locations():
    """
    Get all locations in the organization
    """
    try:
        locations = await webex_client.get_locations()
        return {
            "total": len(locations),
            "items": locations
        }
    except Exception as e:
        logger.error(f"Failed to fetch locations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch locations: {str(e)}")


@router.get("/people")
async def get_people(
    email: Optional[str] = Query(None, description="Filter by email"),
    max_results: int = Query(100, ge=1, le=1000)
):
    """
    Get people (users) in the organization
    """
    try:
        people = await webex_client.get_people(email=email, max_results=max_results)
        return {
            "total": len(people),
            "items": people
        }
    except Exception as e:
        logger.error(f"Failed to fetch people: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch people: {str(e)}")


@router.post("/sync")
async def sync_cdrs():
    """
    Sync CDRs from Webex to local database
    This endpoint will be used by cron jobs
    """
    try:
        # Fetch last 24 hours of CDRs
        cdrs = await webex_client.get_cdrs()

        # TODO: Store CDRs in database
        # For now, just return count
        logger.info(f"Synced {len(cdrs)} CDR records")

        return {
            "status": "success",
            "records_synced": len(cdrs),
            "message": f"Successfully synced {len(cdrs)} CDR records"
        }

    except Exception as e:
        logger.error(f"Failed to sync CDRs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to sync CDRs: {str(e)}")
