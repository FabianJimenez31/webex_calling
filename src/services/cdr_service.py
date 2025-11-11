"""
CDR Service with Database Caching
Manages CDR storage, retrieval, and background sync
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from uuid import uuid4
from sqlalchemy import select, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_db
from src.models.cdr import CallDetailRecord
from src.services.webex_client import webex_client

logger = logging.getLogger(__name__)


class CDRService:
    """Service for managing CDR caching and retrieval"""

    def __init__(self):
        self._sync_task: Optional[asyncio.Task] = None
        self._is_syncing = False

    async def get_cdrs_from_db(
        self,
        hours: int = 24,
        limit: int = 200,
        session: Optional[AsyncSession] = None
    ) -> List[Dict]:
        """
        Get CDRs from database

        Args:
            hours: Hours to look back
            limit: Maximum number of CDRs
            session: Optional database session

        Returns:
            List of CDR dictionaries
        """
        try:
            should_close = False
            if session is None:
                session = await get_async_db().__anext__()
                should_close = True

            try:
                # Calculate time range
                end_time = datetime.utcnow()
                start_time = end_time - timedelta(hours=hours)

                # Query CDRs from database
                query = (
                    select(CallDetailRecord)
                    .where(
                        and_(
                            CallDetailRecord.start_time >= start_time,
                            CallDetailRecord.start_time <= end_time
                        )
                    )
                    .order_by(desc(CallDetailRecord.start_time))
                    .limit(limit)
                )

                result = await session.execute(query)
                cdrs = result.scalars().all()

                logger.info(f"Retrieved {len(cdrs)} CDRs from database")

                # Convert to dict format
                return [self._cdr_to_dict(cdr) for cdr in cdrs]

            finally:
                if should_close:
                    await session.close()

        except Exception as e:
            logger.error(f"Failed to get CDRs from DB: {str(e)}")
            return []

    async def save_cdrs_to_db(
        self,
        cdrs: List[Dict],
        session: Optional[AsyncSession] = None
    ) -> int:
        """
        Save CDRs to database

        Args:
            cdrs: List of CDR dictionaries
            session: Optional database session

        Returns:
            Number of CDRs saved
        """
        try:
            should_close = False
            if session is None:
                session = await get_async_db().__anext__()
                should_close = True

            try:
                saved_count = 0

                for cdr_data in cdrs:
                    try:
                        # Check if CDR already exists by correlation_id
                        correlation_id = cdr_data.get('Correlation ID')
                        if correlation_id:
                            query = select(CallDetailRecord).where(
                                CallDetailRecord.correlation_id == correlation_id
                            )
                            result = await session.execute(query)
                            existing = result.scalar_one_or_none()

                            if existing:
                                logger.debug(f"CDR {correlation_id} already exists, skipping")
                                continue

                        # Create new CDR record
                        cdr = CallDetailRecord(
                            call_id=correlation_id or str(uuid4()),  # Use correlation_id as call_id
                            correlation_id=cdr_data.get('Correlation ID'),
                            start_time=datetime.fromisoformat(cdr_data['Start time'].replace('Z', '+00:00')) if cdr_data.get('Start time') else None,
                            answer_time=datetime.fromisoformat(cdr_data['Answer time'].replace('Z', '+00:00')) if cdr_data.get('Answer time') else None,
                            duration=cdr_data.get('Duration'),
                            calling_number=cdr_data.get('Calling number'),
                            called_number=cdr_data.get('Called number'),
                            direction=cdr_data.get('Direction'),
                            call_type=cdr_data.get('Call type'),
                            answered=cdr_data.get('Answered') == 'true',
                            calling_user_type=cdr_data.get('User type'),  # Fixed: use calling_user_type
                            user=cdr_data.get('User'),
                            site_uuid=cdr_data.get('Site UUID'),
                            site_name=cdr_data.get('Site'),
                            location=cdr_data.get('Location'),
                            hunt_group_name=cdr_data.get('Call queue name'),
                            release_reason=cdr_data.get('Release reason'),
                            original_reason=cdr_data.get('Original reason'),
                            redirect_reason=cdr_data.get('Redirect reason'),
                            related_call_id=cdr_data.get('Related call ID'),
                            local_session_id=cdr_data.get('Local session ID'),
                            remote_session_id=cdr_data.get('Remote session ID'),
                            raw_data=cdr_data
                        )

                        session.add(cdr)
                        saved_count += 1

                    except Exception as e:
                        import traceback
                        logger.error(f"Failed to save individual CDR: {str(e)}")
                        logger.error(f"Traceback: {traceback.format_exc()}")
                        logger.error(f"CDR data keys: {list(cdr_data.keys())}")
                        continue

                await session.commit()
                logger.info(f"Saved {saved_count} new CDRs to database")
                return saved_count

            finally:
                if should_close:
                    await session.close()

        except Exception as e:
            logger.error(f"Failed to save CDRs to DB: {str(e)}")
            return 0

    async def sync_cdrs_from_api(
        self,
        hours: int = 24,
        limit: int = 1000
    ) -> Dict[str, any]:
        """
        Sync CDRs from Webex API to database (background task)

        Args:
            hours: Hours to look back
            limit: Maximum CDRs to fetch

        Returns:
            Sync statistics
        """
        if self._is_syncing:
            logger.warning("Sync already in progress, skipping")
            return {"status": "skipped", "reason": "sync_in_progress"}

        self._is_syncing = True
        start_time_sync = datetime.utcnow()

        try:
            logger.info(f"Starting background CDR sync (last {hours} hours)...")

            # Fetch from API
            end_time = datetime.utcnow() - timedelta(minutes=5)
            start_time = end_time - timedelta(hours=hours)

            cdrs = await webex_client.get_cdrs(
                start_time=start_time,
                end_time=end_time,
                limit=limit
            )

            if not cdrs:
                logger.info("No CDRs fetched from API")
                return {
                    "status": "completed",
                    "fetched": 0,
                    "saved": 0,
                    "duration_seconds": (datetime.utcnow() - start_time_sync).total_seconds()
                }

            # Save to database
            saved_count = await self.save_cdrs_to_db(cdrs)

            duration = (datetime.utcnow() - start_time_sync).total_seconds()

            result = {
                "status": "completed",
                "fetched": len(cdrs),
                "saved": saved_count,
                "duration_seconds": duration,
                "timestamp": datetime.utcnow().isoformat()
            }

            logger.info(f"Background sync completed: {result}")
            return result

        except Exception as e:
            logger.error(f"Background sync failed: {str(e)}")
            return {
                "status": "failed",
                "error": str(e),
                "duration_seconds": (datetime.utcnow() - start_time_sync).total_seconds()
            }

        finally:
            self._is_syncing = False

    async def get_cdrs_with_background_sync(
        self,
        hours: int = 24,
        limit: int = 200
    ) -> List[Dict]:
        """
        Get CDRs from database and trigger background sync

        This is the main method to use from the chat endpoint:
        1. Returns CDRs from DB immediately (fast)
        2. Starts background sync to update DB (non-blocking)

        Args:
            hours: Hours to look back
            limit: Maximum CDRs to return

        Returns:
            List of CDR dictionaries from database
        """
        # Get CDRs from database (fast)
        cdrs = await self.get_cdrs_from_db(hours=hours, limit=limit)

        # Start background sync (non-blocking)
        if not self._is_syncing:
            asyncio.create_task(self.sync_cdrs_from_api(hours=hours))
            logger.info("Background CDR sync started")

        return cdrs

    def _cdr_to_dict(self, cdr: CallDetailRecord) -> Dict:
        """Convert CDR model to dictionary"""
        if cdr.raw_data:
            return cdr.raw_data

        # Fallback: construct from model fields
        return {
            'Correlation ID': cdr.correlation_id,
            'Start time': cdr.start_time.isoformat() if cdr.start_time else None,
            'Answer time': cdr.answer_time.isoformat() if cdr.answer_time else None,
            'Duration': cdr.duration,
            'Calling number': cdr.calling_number,
            'Called number': cdr.called_number,
            'Direction': cdr.direction,
            'Call type': cdr.call_type,
            'Answered': 'true' if cdr.answered else 'false',
            'User type': cdr.user_type,
            'User': cdr.user,
            'Site UUID': cdr.site_uuid,
            'Site': cdr.site_name,
            'Location': cdr.location,
            'Call queue name': cdr.hunt_group_name,
            'Release reason': cdr.release_reason,
            'Original reason': cdr.original_reason,
            'Redirect reason': cdr.redirect_reason,
            'Related call ID': cdr.related_call_id,
            'Local session ID': cdr.local_session_id,
            'Remote session ID': cdr.remote_session_id,
        }

    async def get_sync_status(self) -> Dict:
        """Get current sync status"""
        return {
            "is_syncing": self._is_syncing,
            "status": "syncing" if self._is_syncing else "idle"
        }


# Global instance
cdr_service = CDRService()
