"""User model for tracking users and their calling patterns"""
from sqlalchemy import Column, String, Integer, Float, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

from .base import Base, TimestampMixin


class User(Base, TimestampMixin):
    """
    User/Extension in Webex Calling
    """

    __tablename__ = "users"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # User Identifiers
    user_id = Column(String(255), unique=True, nullable=False, index=True)
    user_name = Column(String(255))
    extension = Column(String(50), index=True)
    email = Column(String(255))

    # Location
    location = Column(String(255), index=True)
    site_id = Column(String(255))
    department = Column(String(255))

    # License & Status
    license_type = Column(String(100))
    is_active = Column(Boolean, default=True)

    # Calling Statistics (updated periodically)
    total_calls_outbound = Column(Integer, default=0)
    total_calls_inbound = Column(Integer, default=0)
    total_international_calls = Column(Integer, default=0)
    avg_call_duration = Column(Float)  # seconds

    # Risk Scoring
    risk_score = Column(Float, default=0.0)  # 0.0 - 1.0
    anomaly_count = Column(Integer, default=0)
    last_anomaly_date = Column(String(50))

    # Baseline Patterns (for ML)
    baseline_data = Column(JSONB)  # Stores normal behavior patterns

    def __repr__(self):
        return f"<User {self.user_name} ({self.extension})>"
