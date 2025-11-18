"""
Whisper Transcription Service
OpenAI Whisper API integration for audio transcription
"""
import os
import logging
from typing import Dict, Optional
from pathlib import Path
import httpx
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


class WhisperTranscriptionService:
    """Service for transcribing audio files using OpenAI Whisper API"""

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not configured - Whisper transcription will not be available")
        self.client = AsyncOpenAI(api_key=self.api_key) if self.api_key else None

    async def transcribe_audio(
        self,
        audio_file_path: str,
        language: Optional[str] = None,
        prompt: Optional[str] = None
    ) -> Dict:
        """
        Transcribe audio file using Whisper API

        Args:
            audio_file_path: Path to audio file (mp3, mp4, mpeg, mpga, m4a, wav, webm)
            language: ISO-639-1 language code (e.g., 'en', 'es') - optional, Whisper will auto-detect
            prompt: Optional text to guide the model's style

        Returns:
            Dictionary with:
            {
                "text": "Full transcription text",
                "language": "detected_language",
                "duration": audio_duration_seconds,
                "segments": [...] (if available)
            }

        Raises:
            ValueError: If OPENAI_API_KEY not configured
            FileNotFoundError: If audio file doesn't exist
            Exception: For API errors
        """
        if not self.client:
            raise ValueError("OPENAI_API_KEY not configured - cannot transcribe")

        # Verify file exists
        if not Path(audio_file_path).exists():
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

        file_size = Path(audio_file_path).stat().st_size
        logger.info(f"Transcribing audio file: {audio_file_path} ({file_size} bytes)")

        try:
            # Open audio file
            with open(audio_file_path, "rb") as audio_file:
                # Call Whisper API
                transcript = await self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language,
                    prompt=prompt,
                    response_format="verbose_json"  # Get detailed response with segments
                )

            # Extract response data
            result = {
                "text": transcript.text,
                "language": transcript.language if hasattr(transcript, 'language') else None,
                "duration": transcript.duration if hasattr(transcript, 'duration') else None,
                "segments": []
            }

            # Add segments if available (timestamps for each part)
            if hasattr(transcript, 'segments'):
                result["segments"] = [
                    {
                        "id": seg.get("id"),
                        "start": seg.get("start"),
                        "end": seg.get("end"),
                        "text": seg.get("text"),
                    }
                    for seg in transcript.segments
                ]

            logger.info(f"Transcription successful: {len(result['text'])} characters, language: {result['language']}")

            return result

        except Exception as e:
            logger.error(f"Whisper transcription failed: {e}")
            raise Exception(f"Failed to transcribe audio: {str(e)}")

    async def transcribe_with_translation(
        self,
        audio_file_path: str,
        target_language: str = "en"
    ) -> Dict:
        """
        Transcribe audio and translate to target language

        Args:
            audio_file_path: Path to audio file
            target_language: Target language code (default: 'en')

        Returns:
            Dictionary with original and translated text
        """
        if not self.client:
            raise ValueError("OPENAI_API_KEY not configured")

        if not Path(audio_file_path).exists():
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

        logger.info(f"Transcribing and translating audio: {audio_file_path}")

        try:
            # First, transcribe to get original language
            transcription = await self.transcribe_audio(audio_file_path)

            # If original is not target language, translate using Whisper translate endpoint
            if transcription["language"] != target_language:
                with open(audio_file_path, "rb") as audio_file:
                    translation = await self.client.audio.translations.create(
                        model="whisper-1",
                        file=audio_file
                    )

                result = {
                    "original_text": transcription["text"],
                    "original_language": transcription["language"],
                    "translated_text": translation.text,
                    "target_language": target_language,
                    "duration": transcription["duration"],
                    "segments": transcription["segments"]
                }
            else:
                # Already in target language
                result = {
                    "original_text": transcription["text"],
                    "original_language": transcription["language"],
                    "translated_text": transcription["text"],
                    "target_language": target_language,
                    "duration": transcription["duration"],
                    "segments": transcription["segments"]
                }

            logger.info(f"Transcription and translation successful")
            return result

        except Exception as e:
            logger.error(f"Transcription with translation failed: {e}")
            raise Exception(f"Failed to transcribe and translate: {str(e)}")

    async def estimate_cost(self, audio_file_path: str) -> Dict:
        """
        Estimate transcription cost

        OpenAI Whisper pricing: $0.006 per minute

        Args:
            audio_file_path: Path to audio file

        Returns:
            Dictionary with estimated cost and duration
        """
        if not Path(audio_file_path).exists():
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

        # For accurate estimation, we'd need audio duration
        # This is a rough estimate based on file size
        file_size_mb = Path(audio_file_path).stat().st_size / (1024 * 1024)

        # Rough estimate: 1 MB ≈ 1 minute of audio (varies by quality)
        estimated_minutes = file_size_mb

        # Whisper pricing: $0.006 per minute
        estimated_cost = estimated_minutes * 0.006

        return {
            "file_size_mb": round(file_size_mb, 2),
            "estimated_minutes": round(estimated_minutes, 2),
            "estimated_cost_usd": round(estimated_cost, 4),
            "note": "Actual cost may vary based on audio duration"
        }

    def is_available(self) -> bool:
        """Check if Whisper service is available (API key configured)"""
        return self.client is not None


# Global instance
whisper_service = WhisperTranscriptionService()
