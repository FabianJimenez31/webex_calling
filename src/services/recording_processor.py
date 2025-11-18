"""
Recording Processing Service
Orchestrates the complete recording processing pipeline:
1. Fetch recordings from Webex
2. Download audio and transcripts
3. Generate transcriptions (if needed)
4. Generate summaries
5. Translate (optional)
6. Store in database
"""
import os
import logging
from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.recording import Recording, ProcessingStatus, RecordingType
from .webex_recordings import webex_recordings_service
from .anomaly_detector import AnomalyDetector

logger = logging.getLogger(__name__)


class RecordingProcessor:
    """Service for processing Webex recordings"""

    def __init__(self):
        self.recordings_service = webex_recordings_service

    async def fetch_and_process_new_recordings(
        self,
        db: AsyncSession,
        hours: int = 24,
        limit: int = 100
    ) -> List[Recording]:
        """
        Fetch new recordings from Webex and process them

        Args:
            db: Database session
            hours: Hours back to fetch recordings (default: 24)
            limit: Maximum number of recordings to process

        Returns:
            List of processed Recording objects
        """
        logger.info(f"Fetching recordings from last {hours} hours...")

        # Calculate date range
        from_date = datetime.utcnow() - timedelta(hours=hours)
        to_date = datetime.utcnow()

        # Fetch recordings from Webex
        webex_recordings = await self.recordings_service.list_recordings(
            service_type="calling",
            from_date=from_date,
            to_date=to_date,
            max_results=limit
        )

        logger.info(f"Found {len(webex_recordings)} recordings from Webex")

        processed_recordings = []

        for webex_rec in webex_recordings:
            recording_id = webex_rec.get("id")

            # Check if already exists in database
            result = await db.execute(
                select(Recording).where(Recording.recording_id == recording_id)
            )
            existing = result.scalar_one_or_none()

            if existing:
                logger.info(f"Recording {recording_id} already exists, skipping")
                continue

            # Process new recording
            try:
                recording = await self.process_recording(db, webex_rec)
                processed_recordings.append(recording)
                logger.info(f"Successfully processed recording: {recording_id}")
            except Exception as e:
                logger.error(f"Failed to process recording {recording_id}: {e}")
                continue

        logger.info(f"Processed {len(processed_recordings)} new recordings")
        return processed_recordings

    async def process_recording(
        self,
        db: AsyncSession,
        webex_recording: Dict
    ) -> Recording:
        """
        Process a single recording through the complete pipeline

        Args:
            db: Database session
            webex_recording: Recording data from Webex API

        Returns:
            Processed Recording object
        """
        recording_id = webex_recording.get("id")
        logger.info(f"Processing recording: {recording_id}")

        # Create initial recording entry
        recording = Recording(
            recording_id=recording_id,
            timestamp=self._parse_datetime(webex_recording.get("createTime")),
            processing_status=ProcessingStatus.PENDING,
            processing_started_at=datetime.utcnow(),
            source="webex_calling"
        )

        # Extract basic info from Webex response
        self._extract_basic_info(recording, webex_recording)

        # Save initial state
        db.add(recording)
        await db.commit()

        completed_steps = []
        errors = []

        try:
            # Step 1: Get detailed information
            recording.processing_status = ProcessingStatus.DOWNLOADING
            await db.commit()

            details = await self.recordings_service.get_recording_details(recording_id)
            self._extract_detailed_info(recording, details)
            completed_steps.append("fetch_details")

            # Step 2: Get metadata
            try:
                metadata = await self.recordings_service.get_recording_metadata(recording_id)
                recording.webex_metadata = metadata
                completed_steps.append("fetch_metadata")
            except Exception as e:
                logger.warning(f"Could not fetch metadata: {e}")
                errors.append({"step": "fetch_metadata", "error": str(e)})

            # Step 3: Download audio file
            download_url = details.get("downloadUrl") or details.get("temporaryDirectDownloadLinks", {}).get("audioDownloadLink")

            if download_url:
                try:
                    audio_path = await self.recordings_service.get_recording_storage_path(recording_id)
                    await self.recordings_service.download_recording_file(download_url, audio_path)

                    recording.audio_local_path = audio_path
                    recording.audio_size_bytes = os.path.getsize(audio_path)
                    recording.audio_format = "mp3"  # Usually MP3 for Webex

                    completed_steps.append("download_audio")
                except Exception as e:
                    logger.error(f"Failed to download audio: {e}")
                    errors.append({"step": "download_audio", "error": str(e)})
            else:
                errors.append({"step": "download_audio", "error": "No download URL available"})

            # Step 4: Process transcript
            recording.processing_status = ProcessingStatus.TRANSCRIBING
            await db.commit()

            transcript_url = details.get("transcriptDownloadLink")

            if transcript_url:
                # Webex provides transcript
                try:
                    transcript_path = await self.recordings_service.get_transcript_storage_path(recording_id)
                    await self.recordings_service.download_transcript(transcript_url, transcript_path)

                    recording.transcript_vtt_path = transcript_path
                    recording.transcript_text = self.recordings_service.parse_vtt_transcript(transcript_path)
                    recording.has_webex_transcript = True
                    recording.transcript_source = "webex"

                    completed_steps.append("download_transcript")
                except Exception as e:
                    logger.error(f"Failed to download transcript: {e}")
                    errors.append({"step": "download_transcript", "error": str(e)})
            else:
                # No transcript from Webex - try Whisper if audio available
                logger.info(f"No transcript available from Webex for {recording_id}")
                recording.has_webex_transcript = False

                # Try Whisper transcription if we have audio file
                if recording.audio_local_path and os.path.exists(recording.audio_local_path):
                    try:
                        logger.info(f"Attempting Whisper transcription for {recording_id}")
                        from .whisper_transcription import whisper_service

                        if whisper_service.is_available():
                            # Transcribe using Whisper
                            whisper_result = await whisper_service.transcribe_audio(
                                recording.audio_local_path,
                                language=None  # Auto-detect language
                            )

                            recording.transcript_text = whisper_result["text"]
                            recording.transcript_source = "whisper"
                            recording.detected_language = whisper_result.get("language")
                            recording.audio_duration_seconds = whisper_result.get("duration")

                            # Store segments as JSON if available
                            if whisper_result.get("segments"):
                                recording.transcript_segments = whisper_result["segments"]

                            completed_steps.append("whisper_transcription")
                            logger.info(f"Whisper transcription successful: {len(recording.transcript_text)} chars")
                        else:
                            logger.warning("Whisper service not available (OPENAI_API_KEY not configured)")
                            errors.append({"step": "transcript", "error": "No Webex transcript, Whisper not configured"})
                    except Exception as e:
                        logger.error(f"Whisper transcription failed: {e}")
                        errors.append({"step": "whisper_transcription", "error": str(e)})
                else:
                    # No audio file available either
                    errors.append({"step": "transcript", "error": "No Webex transcript and no audio file available"})

            # Step 5: Generate summary
            recording.processing_status = ProcessingStatus.SUMMARIZING
            await db.commit()

            if recording.transcript_text:
                try:
                    summary_data = await self._generate_summary(recording.transcript_text)

                    recording.summary_text = summary_data.get("summary")
                    recording.summary_bullet_points = summary_data.get("bullet_points")
                    recording.key_topics = summary_data.get("topics")
                    recording.action_items = summary_data.get("action_items")
                    recording.sentiment_score = summary_data.get("sentiment_score")
                    recording.sentiment_label = summary_data.get("sentiment_label")
                    recording.summary_source = "openrouter"

                    completed_steps.append("generate_summary")
                except Exception as e:
                    logger.error(f"Failed to generate summary: {e}")
                    errors.append({"step": "generate_summary", "error": str(e)})

            # Step 6: Detect language
            if recording.transcript_text:
                try:
                    language = await self._detect_language(recording.transcript_text)
                    recording.detected_language = language.get("code")
                    recording.language_confidence = language.get("confidence")
                    completed_steps.append("detect_language")
                except Exception as e:
                    logger.error(f"Failed to detect language: {e}")
                    errors.append({"step": "detect_language", "error": str(e)})

            # Mark as completed or partial
            if len(errors) == 0:
                recording.processing_status = ProcessingStatus.COMPLETED
            elif len(completed_steps) > 0:
                recording.processing_status = ProcessingStatus.PARTIAL
            else:
                recording.processing_status = ProcessingStatus.FAILED

            recording.processing_completed_at = datetime.utcnow()
            recording.processing_duration_seconds = (
                recording.processing_completed_at - recording.processing_started_at
            ).total_seconds()

            recording.processing_steps_completed = completed_steps
            recording.processing_errors = errors

            # Calculate quality score
            recording.quality_score = len(completed_steps) / 6.0  # 6 total steps

            await db.commit()

            logger.info(f"Recording processing completed: {recording_id} - Status: {recording.processing_status}")

            return recording

        except Exception as e:
            logger.error(f"Fatal error processing recording {recording_id}: {e}")

            recording.processing_status = ProcessingStatus.FAILED
            recording.processing_completed_at = datetime.utcnow()
            recording.processing_errors = errors + [{"step": "fatal", "error": str(e)}]

            await db.commit()
            raise

    def _extract_basic_info(self, recording: Recording, webex_data: Dict):
        """Extract basic info from Webex list response"""
        recording.duration = webex_data.get("durationSeconds")
        recording.recording_type = RecordingType.CALL
        recording.service_type = webex_data.get("serviceType", "calling")

        # Try to extract caller/callee from topic or other fields
        topic = webex_data.get("topic", "")
        recording.caller = topic  # Placeholder, will be refined in details

        recording.location = webex_data.get("siteUrl", "")
        recording.organization_id = webex_data.get("orgId", "")

    def _extract_detailed_info(self, recording: Recording, details: Dict):
        """Extract detailed info from full recording response"""
        recording.audio_url = details.get("temporaryDirectDownloadLinks", {}).get("audioDownloadLink")

        # Participants
        participants = []
        if "participants" in details:
            participants = details["participants"]
            recording.participants = participants

            # Try to identify caller/callee
            if len(participants) >= 2:
                recording.caller = participants[0].get("email", participants[0].get("name", "Unknown"))
                recording.callee = participants[1].get("email", participants[1].get("name", "Unknown"))

        # Provider info
        recording.provider_type = details.get("providerType", "Webex")

    def _parse_datetime(self, dt_string: Optional[str]) -> Optional[datetime]:
        """Parse datetime string from Webex"""
        if not dt_string:
            return None

        try:
            # Webex uses ISO 8601 format
            return datetime.fromisoformat(dt_string.replace("Z", "+00:00"))
        except Exception as e:
            logger.warning(f"Failed to parse datetime: {dt_string} - {e}")
            return None

    async def _generate_summary(self, transcript: str) -> Dict:
        """
        Generate summary, action items, and sentiment from transcript

        Args:
            transcript: Transcript text

        Returns:
            Dictionary with summary data
        """
        prompt = f"""Analyze this call recording transcript and provide:

1. A concise summary (2-3 sentences)
2. Key bullet points (3-5 main points)
3. Topics discussed
4. Action items identified
5. Sentiment analysis (score from -1.0 to 1.0 and label)

Transcript:
{transcript[:4000]}  # Limit to avoid token limits

Respond in JSON format:
{{
  "summary": "...",
  "bullet_points": ["...", "..."],
  "topics": ["...", "..."],
  "action_items": ["...", "..."],
  "sentiment_score": 0.5,
  "sentiment_label": "positive"
}}
"""

        try:
            # Use OpenRouter via AnomalyDetector
            import httpx
            import json
            import re
            import os

            api_key = os.getenv("OPENROUTER_API_KEY")
            if not api_key:
                raise ValueError("OPENROUTER_API_KEY not configured")

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "openai/gpt-4o-mini",
                        "messages": [{"role": "user", "content": prompt}]
                    },
                    timeout=60.0
                )

                result = response.json()
                response_text = result["choices"][0]["message"]["content"]

            # Try to parse JSON from response
            # Extract JSON from markdown code blocks if present
            json_match = re.search(r'```json\n(.*?)\n```', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to find JSON object in response
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                json_str = json_match.group(0) if json_match else response_text

            summary_data = json.loads(json_str)
            return summary_data

        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            # Return default structure
            return {
                "summary": transcript[:500] if transcript else "",
                "bullet_points": [],
                "topics": [],
                "action_items": [],
                "sentiment_score": 0.0,
                "sentiment_label": "neutral"
            }

    async def _detect_language(self, text: str) -> Dict:
        """
        Detect language of text

        Args:
            text: Text to analyze

        Returns:
            Dictionary with language code and confidence
        """
        # Simple heuristic based on common words
        # TODO: Implement proper language detection (langdetect, Google Cloud, etc.)

        text_lower = text.lower()

        spanish_words = ["el", "la", "de", "que", "y", "a", "en", "un", "ser", "para"]
        english_words = ["the", "be", "to", "of", "and", "a", "in", "that", "have", "i"]

        spanish_count = sum(1 for word in spanish_words if word in text_lower)
        english_count = sum(1 for word in english_words if word in text_lower)

        if spanish_count > english_count:
            return {"code": "es", "confidence": min(spanish_count / 10.0, 1.0)}
        else:
            return {"code": "en", "confidence": min(english_count / 10.0, 1.0)}


# Import timedelta
from datetime import timedelta

# Global instance
recording_processor = RecordingProcessor()
