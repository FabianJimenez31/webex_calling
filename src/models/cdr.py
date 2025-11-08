"""
Call Detail Record (CDR) models based on Webex Calling API
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    Float,
    Text,
    Index,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
import uuid

from .base import Base, TimestampMixin


class CallDetailRecord(Base, TimestampMixin):
    """
    Call Detail Record from Webex Calling API
    Based on: https://developer.webex.com/docs/api/v1/reports-detailed-call-history
    """

    __tablename__ = "call_detail_records"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Call Identifiers
    call_id = Column(String(255), unique=True, nullable=False, index=True)
    correlation_id = Column(String(255), index=True)
    call_leg_id = Column(String(255))
    related_call_id = Column(String(255), index=True)

    # Time Information
    start_time = Column(DateTime(timezone=True), nullable=False, index=True)
    answer_time = Column(DateTime(timezone=True))
    release_time = Column(DateTime(timezone=True))
    duration = Column(Integer)  # seconds
    ring_duration = Column(Integer)  # seconds

    # Calling Party
    calling_line_id = Column(String(100))
    calling_number = Column(String(50), index=True)
    calling_user_id = Column(String(255), index=True)
    calling_user_name = Column(String(255))
    calling_user_type = Column(String(50))

    # Called Party
    called_line_id = Column(String(100))
    called_number = Column(String(50), index=True)
    answered_line_id = Column(String(100))
    answered_number = Column(String(50))

    # Redirection
    redirecting_number = Column(String(50))
    original_reason = Column(String(100))
    redirect_reason = Column(String(100))

    # Call Type & Direction
    call_type = Column(String(50), index=True)  # International, National, Local, etc.
    direction = Column(String(20))  # ORIGINATING, TERMINATING
    call_transfer_time = Column(DateTime(timezone=True))

    # Location
    location = Column(String(255), index=True)
    site_uuid = Column(String(255))
    site_timezone = Column(String(50))

    # Device & Client
    device_mac = Column(String(50))
    model = Column(String(100))
    client_type = Column(String(50))
    client_version = Column(String(50))

    # Call Routing
    trunk_name = Column(String(255))
    related_reason = Column(String(255))  # Trunk information
    queue_id = Column(String(255))
    queue_name = Column(String(255), index=True)
    hunt_group_id = Column(String(255))
    hunt_group_name = Column(String(255))

    # Call Outcome
    answered = Column(Boolean, default=False)
    releasing_party = Column(String(50))
    release_reason = Column(String(100))

    # Media & Quality
    local_session_id = Column(String(255))
    remote_session_id = Column(String(255))
    network_call_id = Column(String(255))

    # Authorization Code (if used)
    authorization_code = Column(String(50))

    # Sub Call Type
    sub_call_type = Column(String(100))

    # User Agent
    user_agent = Column(String(255))

    # International Dialing
    international_country = Column(String(3))  # ISO country code

    # Additional metadata (flexible JSONB field)
    metadata = Column(JSONB)

    # Indexes
    __table_args__ = (
        Index("idx_cdr_start_time", "start_time"),
        Index("idx_cdr_calling_user", "calling_user_id", "start_time"),
        Index("idx_cdr_location_time", "location", "start_time"),
        Index("idx_cdr_call_type", "call_type", "start_time"),
        Index("idx_cdr_queue", "queue_name", "start_time"),
    )

    def __repr__(self):
        return f"<CDR {self.call_id} - {self.start_time}>"


class CallJourney(Base, TimestampMixin):
    """
    Reconstructed call journey showing the complete path of a call
    """

    __tablename__ = "call_journeys"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Journey Identifier (groups multiple legs)
    journey_id = Column(String(255), unique=True, nullable=False, index=True)
    related_call_id = Column(String(255), index=True)

    # Time Information
    call_date = Column(DateTime(timezone=True), nullable=False, index=True)
    total_duration = Column(Integer)  # Total seconds

    # Entry Point
    trunk_entrada = Column(String(255))
    original_caller = Column(String(50))

    # Route (serialized as array or text)
    route = Column(Text)  # e.g., "SIP-Bogotá → AA-Principal → Cola-Comercial → Ext.203"
    route_stages = Column(JSONB)  # Detailed stages array

    # Time spent in each stage
    t_trunk_to_aa = Column(Integer)  # seconds
    t_aa = Column(Integer)  # Time in Auto Attendant
    t_queue_1 = Column(Integer)  # Time in first queue
    t_queue_2 = Column(Integer)  # Time in second queue (if applicable)
    t_queue_total = Column(Integer)  # Total queue time
    t_agent = Column(Integer)  # Time with agent

    # Final Destination
    agente_final = Column(String(100))  # Extension or agent
    agent_user_id = Column(String(255))
    agent_name = Column(String(255))

    # Call Outcome
    resultado = Column(String(50), index=True)  # atendida, abandonada, desviada
    abandono_stage = Column(String(100))  # Where was the call abandoned

    # Quality Metrics
    calidad_media = Column(Float)  # Average MOS score
    packet_loss = Column(Float)
    jitter = Column(Float)
    latency = Column(Float)

    # Location
    location = Column(String(255), index=True)

    # Reference to CDRs
    cdr_ids = Column(ARRAY(String))  # Array of CDR call_ids that form this journey

    # Indexes
    __table_args__ = (
        Index("idx_journey_date", "call_date"),
        Index("idx_journey_resultado", "resultado", "call_date"),
        Index("idx_journey_location", "location", "call_date"),
    )

    def __repr__(self):
        return f"<CallJourney {self.journey_id} - {self.route}>"
