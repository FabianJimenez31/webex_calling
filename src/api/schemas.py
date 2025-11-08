"""Pydantic schemas for API requests/responses"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID


# ============================================================================
# CDR Schemas
# ============================================================================

class CDRBase(BaseModel):
    """Base schema for CDR"""

    call_id: str
    start_time: datetime
    duration: Optional[int] = None
    calling_number: Optional[str] = None
    called_number: Optional[str] = None
    call_type: Optional[str] = None
    location: Optional[str] = None


class CDRCreate(CDRBase):
    """Schema for creating a CDR"""

    correlation_id: Optional[str] = None
    calling_user_id: Optional[str] = None
    answered: bool = False
    metadata: Optional[Dict[str, Any]] = None


class CDRResponse(CDRBase):
    """Schema for CDR response"""

    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CDRList(BaseModel):
    """Schema for list of CDRs"""

    total: int
    items: List[CDRResponse]
    page: int
    page_size: int


# ============================================================================
# Alert Schemas
# ============================================================================

class AlertBase(BaseModel):
    """Base schema for Alert"""

    alert_type: str
    severity: str
    title: str
    description: Optional[str] = None


class AlertCreate(AlertBase):
    """Schema for creating an alert"""

    user_id: Optional[str] = None
    user_name: Optional[str] = None
    detection_data: Optional[Dict[str, Any]] = None
    ai_analysis: Optional[str] = None


class AlertResponse(AlertBase):
    """Schema for alert response"""

    id: UUID
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    status: str
    created_at: datetime
    ai_analysis: Optional[str] = None
    recommended_action: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AlertList(BaseModel):
    """Schema for list of alerts"""

    total: int
    items: List[AlertResponse]
    page: int
    page_size: int


class AlertUpdate(BaseModel):
    """Schema for updating an alert"""

    status: Optional[str] = None
    resolution_notes: Optional[str] = None


# ============================================================================
# User Schemas
# ============================================================================

class UserBase(BaseModel):
    """Base schema for User"""

    user_id: str
    user_name: Optional[str] = None
    extension: Optional[str] = None
    location: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a user"""

    email: Optional[str] = None
    department: Optional[str] = None


class UserResponse(UserBase):
    """Schema for user response"""

    id: UUID
    total_calls_outbound: int = 0
    total_calls_inbound: int = 0
    risk_score: float = 0.0
    is_active: bool = True
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Detection Schemas
# ============================================================================

class DetectionRequest(BaseModel):
    """Schema for requesting anomaly detection"""

    user_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    detection_types: Optional[List[str]] = None


class DetectionResult(BaseModel):
    """Schema for detection result"""

    detection_type: str
    anomaly_detected: bool
    confidence: str
    details: Dict[str, Any]
    recommended_action: Optional[str] = None


class DetectionResponse(BaseModel):
    """Schema for detection response"""

    total_detections: int
    results: List[DetectionResult]
    execution_time_ms: float


# ============================================================================
# Stats Schemas
# ============================================================================

class StatsResponse(BaseModel):
    """Schema for statistics response"""

    total_calls: int
    total_users: int
    total_alerts: int
    open_alerts: int
    critical_alerts: int
    stats_by_type: Dict[str, int]
    stats_by_location: Dict[str, int]
