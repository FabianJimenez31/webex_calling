"""
Recordings API endpoints
Manage Webex Calling recordings with processing pipeline
"""
import os
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import List, Optional
from datetime import datetime, timedelta

from src.database import get_async_db
from src.models.recording import Recording, ProcessingStatus
from src.services.webex_recordings import webex_recordings_service
from src.services.recording_processor import recording_processor
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()


@router.get("/")
async def list_recordings(
    db: AsyncSession = Depends(get_async_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    status: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None
):
    """
    List all recordings from database

    Query params:
    - skip: Number of records to skip (pagination)
    - limit: Max number of records to return
    - status: Filter by processing status (pending, completed, failed, etc.)
    - from_date: Filter from date (ISO format)
    - to_date: Filter to date (ISO format)
    """
    logger.info(f"Listing recordings: skip={skip}, limit={limit}, status={status}")

    query = select(Recording).where(Recording.is_deleted == False)

    # Apply filters
    if status:
        try:
            status_enum = ProcessingStatus(status)
            query = query.where(Recording.processing_status == status_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")

    if from_date:
        try:
            from_dt = datetime.fromisoformat(from_date)
            query = query.where(Recording.timestamp >= from_dt)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid from_date format")

    if to_date:
        try:
            to_dt = datetime.fromisoformat(to_date)
            query = query.where(Recording.timestamp <= to_dt)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid to_date format")

    # Order by timestamp desc
    query = query.order_by(desc(Recording.timestamp))

    # Apply pagination
    query = query.offset(skip).limit(limit)

    # Execute query
    result = await db.execute(query)
    recordings = result.scalars().all()

    return {
        "total": len(recordings),
        "skip": skip,
        "limit": limit,
        "items": [rec.to_dict() for rec in recordings]
    }


@router.get("/{recording_id}")
async def get_recording(
    recording_id: str,
    db: AsyncSession = Depends(get_async_db)
):
    """Get details of a specific recording"""
    result = await db.execute(
        select(Recording).where(Recording.recording_id == recording_id)
    )
    recording = result.scalar_one_or_none()

    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")

    return recording.to_dict()


@router.post("/fetch")
async def fetch_new_recordings(
    hours: int = Query(24, ge=1, le=168),  # Max 7 days
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Fetch new recordings from Webex and process them

    This endpoint:
    1. Queries Webex for recordings in the specified time range
    2. Downloads audio and transcripts
    3. Generates summaries using AI
    4. Stores everything in the database

    Query params:
    - hours: How many hours back to fetch recordings (default: 24)
    - limit: Maximum number of recordings to process (default: 100)
    """
    logger.info(f"Fetching recordings from last {hours} hours (limit: {limit})")

    try:
        recordings = await recording_processor.fetch_and_process_new_recordings(
            db=db,
            hours=hours,
            limit=limit
        )

        return {
            "success": True,
            "processed_count": len(recordings),
            "recordings": [rec.to_dict() for rec in recordings]
        }

    except Exception as e:
        logger.error(f"Failed to fetch recordings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{recording_id}/reprocess")
async def reprocess_recording(
    recording_id: str,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Reprocess an existing recording

    Useful if processing failed or you want to regenerate summaries
    """
    logger.info(f"Reprocessing recording: {recording_id}")

    # Get existing recording
    result = await db.execute(
        select(Recording).where(Recording.recording_id == recording_id)
    )
    recording = result.scalar_one_or_none()

    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")

    try:
        # Fetch fresh data from Webex
        webex_data = await webex_recordings_service.get_recording_details(recording_id)

        # Delete old record and create new
        await db.delete(recording)
        await db.commit()

        # Process again
        new_recording = await recording_processor.process_recording(db, {"id": recording_id, **webex_data})

        return new_recording.to_dict()

    except Exception as e:
        logger.error(f"Failed to reprocess recording: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{recording_id}")
async def delete_recording(
    recording_id: str,
    delete_from_webex: bool = Query(False),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Delete a recording

    Query params:
    - delete_from_webex: Also delete from Webex (default: false, only soft-delete in DB)
    """
    logger.info(f"Deleting recording: {recording_id} (from_webex={delete_from_webex})")

    result = await db.execute(
        select(Recording).where(Recording.recording_id == recording_id)
    )
    recording = result.scalar_one_or_none()

    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")

    # Delete from Webex if requested
    if delete_from_webex:
        try:
            await webex_recordings_service.delete_recording(recording_id)
        except Exception as e:
            logger.error(f"Failed to delete from Webex: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to delete from Webex: {e}")

    # Soft delete in database
    recording.is_deleted = True
    await db.commit()

    return {"success": True, "message": "Recording deleted"}


@router.get("/stats/summary")
async def get_recordings_stats(
    db: AsyncSession = Depends(get_async_db)
):
    """Get summary statistics about recordings"""

    # Total recordings
    total_result = await db.execute(
        select(func.count(Recording.id)).where(Recording.is_deleted == False)
    )
    total = total_result.scalar()

    # By status
    status_counts = {}
    for status in ProcessingStatus:
        count_result = await db.execute(
            select(func.count(Recording.id)).where(
                Recording.processing_status == status,
                Recording.is_deleted == False
            )
        )
        status_counts[status.value] = count_result.scalar()

    # Recordings with transcripts
    transcript_result = await db.execute(
        select(func.count(Recording.id)).where(
            Recording.transcript_text.isnot(None),
            Recording.is_deleted == False
        )
    )
    with_transcripts = transcript_result.scalar()

    # Recordings with summaries
    summary_result = await db.execute(
        select(func.count(Recording.id)).where(
            Recording.summary_text.isnot(None),
            Recording.is_deleted == False
        )
    )
    with_summaries = summary_result.scalar()

    # Average quality score
    quality_result = await db.execute(
        select(func.avg(Recording.quality_score)).where(
            Recording.quality_score.isnot(None),
            Recording.is_deleted == False
        )
    )
    avg_quality = quality_result.scalar() or 0.0

    # Total storage size
    size_result = await db.execute(
        select(func.sum(Recording.audio_size_bytes)).where(
            Recording.audio_size_bytes.isnot(None),
            Recording.is_deleted == False
        )
    )
    total_size_bytes = size_result.scalar() or 0

    return {
        "total_recordings": total,
        "by_status": status_counts,
        "with_transcripts": with_transcripts,
        "with_summaries": with_summaries,
        "average_quality_score": round(avg_quality, 2),
        "total_storage_mb": round(total_size_bytes / (1024 * 1024), 2)
    }


@router.get("/test/webex-access")
async def test_webex_access():
    """Test access to Webex Recordings API"""
    logger.info("Testing Webex Recordings API access...")

    result = await webex_recordings_service.test_recordings_access()

    return result


@router.get("/download/{recording_id}/audio")
async def download_audio(
    recording_id: str,
    db: AsyncSession = Depends(get_async_db)
):
    """Get download URL for recording audio"""
    result = await db.execute(
        select(Recording).where(Recording.recording_id == recording_id)
    )
    recording = result.scalar_one_or_none()

    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")

    if not recording.audio_local_path and not recording.audio_url:
        raise HTTPException(status_code=404, detail="No audio file available")

    # Return local path or Webex URL
    audio_path = recording.audio_local_path or recording.audio_url

    return {
        "recording_id": recording_id,
        "audio_url": audio_path,
        "format": recording.audio_format,
        "size_bytes": recording.audio_size_bytes
    }


@router.post("/{recording_id}/transcribe")
async def transcribe_recording(
    recording_id: str,
    force: bool = Query(False, description="Force re-transcription even if transcript exists"),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Transcribe a recording using Whisper AI

    This endpoint manually triggers Whisper transcription for a recording.
    Useful when:
    - Recording doesn't have Webex transcript
    - You want to re-transcribe with Whisper for better accuracy
    - Initial processing failed
    """
    from src.services.whisper_transcription import whisper_service
    from src.services.recording_processor import recording_processor

    # Get recording from database
    result = await db.execute(
        select(Recording).where(Recording.recording_id == recording_id)
    )
    recording = result.scalar_one_or_none()

    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")

    # Check if already has transcript (unless force=true)
    if recording.transcript_text and not force:
        return {
            "success": False,
            "message": "Recording already has transcript. Use force=true to re-transcribe",
            "existing_transcript": {
                "source": recording.transcript_source,
                "length": len(recording.transcript_text),
                "language": recording.detected_language
            }
        }

    # Check if audio file exists - if not, download it from Webex
    if not recording.audio_local_path or not os.path.exists(recording.audio_local_path):
        logger.info(f"Audio not found locally for {recording_id}, downloading from Webex...")

        try:
            # Get recording details from Webex to get download URL
            webex_details = await webex_recordings_service.get_recording_details(recording_id)

            # Check if temporaryDirectDownloadLinks exists
            if not webex_details.get("temporaryDirectDownloadLinks"):
                raise HTTPException(
                    status_code=400,
                    detail="No download link available for this recording from Webex"
                )

            # Get the audio download URL (usually recordingDownloadLink)
            download_url = webex_details["temporaryDirectDownloadLinks"].get("recordingDownloadLink")
            if not download_url:
                raise HTTPException(
                    status_code=400,
                    detail="Audio download link not available for this recording"
                )

            # Generate local storage path
            storage_path = await webex_recordings_service.get_recording_storage_path(recording_id)
            audio_path = f"{storage_path}.mp3"

            # Download the audio file
            downloaded_path = await webex_recordings_service.download_recording_file(
                download_url=download_url,
                output_path=audio_path
            )

            # Update recording with audio path
            recording.audio_local_path = downloaded_path
            recording.audio_size_bytes = os.path.getsize(downloaded_path)
            recording.audio_format = "mp3"

            await db.commit()
            await db.refresh(recording)

            logger.info(f"Audio downloaded successfully to {downloaded_path}")

        except Exception as e:
            logger.error(f"Failed to download audio for {recording_id}: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to download audio from Webex: {str(e)}"
            )

    # Check if Whisper is available
    if not whisper_service.is_available():
        raise HTTPException(
            status_code=503,
            detail="Whisper service not available. OPENAI_API_KEY not configured."
        )

    try:
        # Estimate cost first
        cost_estimate = await whisper_service.estimate_cost(recording.audio_local_path)

        # Transcribe using Whisper
        whisper_result = await whisper_service.transcribe_audio(
            recording.audio_local_path,
            language=None  # Auto-detect
        )

        # Update recording with transcript
        recording.transcript_text = whisper_result["text"]
        recording.transcript_source = "whisper"
        recording.detected_language = whisper_result.get("language")
        recording.audio_duration_seconds = whisper_result.get("duration")

        if whisper_result.get("segments"):
            recording.transcript_segments = whisper_result["segments"]

        # Update processing status if needed
        if recording.processing_status == ProcessingStatus.PARTIAL:
            # Try to generate summary now that we have transcript
            if recording.transcript_text:
                try:
                    summary_data = await recording_processor._generate_summary(recording.transcript_text)
                    recording.summary_text = summary_data.get("summary")
                    recording.summary_bullet_points = summary_data.get("bullet_points")
                    recording.key_topics = summary_data.get("topics")
                    recording.action_items = summary_data.get("action_items")
                    recording.sentiment_score = summary_data.get("sentiment_score")
                    recording.sentiment_label = summary_data.get("sentiment_label")
                    recording.summary_source = "openrouter"

                    # Update to completed if all steps done
                    recording.processing_status = ProcessingStatus.COMPLETED
                except Exception as e:
                    logger.warning(f"Failed to generate summary after Whisper transcription: {e}")

        await db.commit()
        await db.refresh(recording)

        return {
            "success": True,
            "message": "Transcription completed successfully",
            "recording_id": recording_id,
            "transcript": {
                "text": recording.transcript_text[:500] + "..." if len(recording.transcript_text) > 500 else recording.transcript_text,
                "full_length": len(recording.transcript_text),
                "language": recording.detected_language,
                "duration_seconds": recording.audio_duration_seconds,
                "segments_count": len(whisper_result.get("segments", [])),
                "source": "whisper"
            },
            "cost_estimate": cost_estimate,
            "processing_status": recording.processing_status.value
        }

    except Exception as e:
        logger.error(f"Whisper transcription failed for {recording_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")


@router.get("/{recording_id}/transcript")
async def get_transcript(
    recording_id: str,
    include_segments: bool = Query(False, description="Include timestamped segments"),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get transcript for a recording

    Returns the full transcript text and optionally timestamped segments
    """
    result = await db.execute(
        select(Recording).where(Recording.recording_id == recording_id)
    )
    recording = result.scalar_one_or_none()

    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")

    if not recording.transcript_text:
        raise HTTPException(
            status_code=404,
            detail="No transcript available. Use POST /{recording_id}/transcribe to generate one."
        )

    response = {
        "recording_id": recording_id,
        "transcript_text": recording.transcript_text,
        "source": recording.transcript_source,
        "language": recording.detected_language,
        "duration_seconds": recording.audio_duration_seconds,
        "character_count": len(recording.transcript_text)
    }

    if include_segments and recording.transcript_segments:
        response["segments"] = recording.transcript_segments

    return response
