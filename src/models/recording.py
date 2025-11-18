"""
Recording model for Webex Calling recordings
"""
from sqlalchemy import Column, String, Integer, DateTime, JSON, Text, Boolean, Float, Enum
from sqlalchemy.sql import func
import enum

from src.models.base import Base


class ProcessingStatus(str, enum.Enum):
    """Recording processing status"""
    PENDING = "pending"
    DOWNLOADING = "downloading"
    TRANSCRIBING = "transcribing"
    SUMMARIZING = "summarizing"
    TRANSLATING = "translating"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"  # Some steps completed, others failed


class RecordingType(str, enum.Enum):
    """Type of recording"""
    CALL = "call"
    VOICEMAIL = "voicemail"
    MEETING = "meeting"
    OTHER = "other"


class Recording(Base):
    """
    Model for Webex Calling recordings with full processing pipeline.

    Stores:
    - Original recording metadata from Webex
    - Downloaded audio file location
    - Transcription (from Webex or generated)
    - Summary (from Webex or generated)
    - Translation (optional)
    - Processing status and errors
    """
    __tablename__ = "recordings"

    # Primary identification
    id = Column(Integer, primary_key=True, index=True)
    recording_id = Column(String(255), unique=True, index=True, nullable=False)  # Webex recordingId

    # Temporal information
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Call participants
    caller = Column(String(255), index=True)  # Calling party
    callee = Column(String(255), index=True)  # Called party
    caller_name = Column(String(255))
    callee_name = Column(String(255))

    # Call details
    duration = Column(Float)  # Duration in seconds
    recording_type = Column(Enum(RecordingType), default=RecordingType.CALL)
    service_type = Column(String(50))  # e.g., "calling"

    # Recording provider information
    provider_type = Column(String(100))  # e.g., "Webex", "BroadWorks"
    location = Column(String(255))
    organization_id = Column(String(255))

    # Metadata from Webex API
    webex_metadata = Column(JSON)  # Full metadata from /metadata endpoint
    participants = Column(JSON)  # List of all participants
    network_info = Column(JSON)  # Network/technical details
    privacy_flags = Column(JSON)  # Privacy markers

    # Audio file
    audio_url = Column(String(1024))  # Original Webex download URL
    audio_local_path = Column(String(512))  # Local storage path
    audio_format = Column(String(20))  # e.g., "mp3", "wav"
    audio_size_bytes = Column(Integer)
    audio_duration_seconds = Column(Float)  # Audio duration in seconds

    # Language detection
    detected_language = Column(String(10))  # ISO 639-1 code (e.g., "es", "en")
    language_confidence = Column(Float)  # 0.0 to 1.0

    # Transcription
    has_webex_transcript = Column(Boolean, default=False)
    transcript_text = Column(Text)  # Final transcript text
    transcript_original = Column(Text)  # Original transcript if translated
    transcript_vtt_path = Column(String(512))  # Path to VTT file if available
    transcript_source = Column(String(50))  # "webex", "whisper", "google_stt", etc.
    transcript_confidence = Column(Float)  # Average confidence score
    transcript_segments = Column(JSON)  # Timestamped segments from Whisper

    # Summary
    has_webex_summary = Column(Boolean, default=False)
    summary_text = Column(Text)  # Final summary
    summary_original = Column(Text)  # Original summary if translated
    summary_source = Column(String(50))  # "webex", "claude", "openrouter", etc.
    summary_bullet_points = Column(JSON)  # Structured summary points

    # Translation
    is_translated = Column(Boolean, default=False)
    translation_target_language = Column(String(10))  # Target language code
    translation_service = Column(String(50))  # "deepl", "google", "claude", etc.

    # AI Analysis (additional insights)
    sentiment_score = Column(Float)  # -1.0 (negative) to 1.0 (positive)
    sentiment_label = Column(String(20))  # "positive", "neutral", "negative"
    key_topics = Column(JSON)  # List of detected topics
    action_items = Column(JSON)  # Extracted action items

    # Processing status
    processing_status = Column(
        Enum(ProcessingStatus),
        default=ProcessingStatus.PENDING,
        index=True
    )
    processing_steps_completed = Column(JSON)  # List of completed steps
    processing_errors = Column(JSON)  # List of errors encountered
    processing_started_at = Column(DateTime(timezone=True))
    processing_completed_at = Column(DateTime(timezone=True))
    processing_duration_seconds = Column(Float)

    # Correlation and quality
    call_correlation_id = Column(String(255), index=True)  # Link to CDR if available
    quality_score = Column(Float)  # Overall processing quality (0.0 to 1.0)

    # Flags
    is_deleted = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    requires_reprocessing = Column(Boolean, default=False)

    # Source
    source = Column(String(50), default="webex_calling")

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "recordingId": self.recording_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "caller": self.caller,
            "callee": self.callee,
            "caller_name": self.caller_name,
            "callee_name": self.callee_name,
            "duration": self.duration,
            "metadata": self.webex_metadata,
            "audio_url": self.audio_local_path or self.audio_url,
            "transcript_text": self.transcript_text,
            "transcript_original": self.transcript_original,
            "transcript_translation": self.transcript_text if self.is_translated else None,
            "summary_text": self.summary_text,
            "summary_original": self.summary_original,
            "source": self.source,
            "processing_status": self.processing_status.value if self.processing_status else None,
            "detected_language": self.detected_language,
            "is_translated": self.is_translated,
            "sentiment": {
                "score": self.sentiment_score,
                "label": self.sentiment_label
            } if self.sentiment_score is not None else None,
            "key_topics": self.key_topics,
            "action_items": self.action_items,
            "quality_score": self.quality_score,
        }

    def __repr__(self):
        return f"<Recording {self.recording_id} - {self.caller} → {self.callee}>"
