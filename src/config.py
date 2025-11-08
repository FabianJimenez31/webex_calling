"""
Configuration module for Webex Calling Security AI
"""
import os
from pathlib import Path
from typing import Dict, Tuple

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load environment variables
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = DATA_DIR / "models"


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Webex Configuration
    webex_access_token: str
    webex_org_id: str
    webex_bot_token: str = ""
    webex_bot_email: str = ""

    # Claude AI Configuration
    anthropic_api_key: str

    # Database Configuration
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "webex_calling_security"
    db_user: str = "postgres"
    db_password: str

    # Application Configuration
    environment: str = "development"
    log_level: str = "INFO"
    timezone: str = "America/Bogota"

    # Alerting Configuration
    slack_webhook_url: str = ""
    alert_email: str = ""

    # Detection Thresholds
    international_calls_threshold: int = 5
    after_hours_calls_threshold: int = 3
    mass_dialing_threshold: int = 50
    mass_dialing_time_window_minutes: int = 60

    # Business Hours (per location)
    business_hours_bogota_start: int = 8
    business_hours_bogota_end: int = 18
    business_hours_mexico_start: int = 9
    business_hours_mexico_end: int = 19
    business_hours_madrid_start: int = 9
    business_hours_madrid_end: int = 18

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def database_url(self) -> str:
        """Construct database URL"""
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def business_hours(self) -> Dict[str, Tuple[int, int]]:
        """Get business hours configuration by location"""
        return {
            "Bogota": (self.business_hours_bogota_start, self.business_hours_bogota_end),
            "Mexico": (self.business_hours_mexico_start, self.business_hours_mexico_end),
            "Madrid": (self.business_hours_madrid_start, self.business_hours_madrid_end),
        }


# Global settings instance
settings = Settings()
