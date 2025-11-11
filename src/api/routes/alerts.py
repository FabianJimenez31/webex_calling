"""Alert endpoints"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from uuid import UUID
from pydantic import BaseModel

from src.database import get_async_db
from src.models.alert import Alert, AlertType, AlertSeverity
from src.api.schemas import AlertResponse, AlertList, AlertCreate, AlertUpdate
from src.utils.logger import setup_logger
from src.services.alert_service import alert_service

logger = setup_logger(__name__)

router = APIRouter()


class WebhookConfig(BaseModel):
    """Webhook configuration"""
    webhook_urls: List[str]


class EmailConfig(BaseModel):
    """Email configuration"""
    email_recipients: List[str]


@router.get("/", response_model=AlertList)
async def list_alerts(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    severity: Optional[str] = None,
    status: Optional[str] = None,
    user_id: Optional[str] = None,
    db: AsyncSession = Depends(get_async_db),
):
    """
    List all alerts with pagination and filters
    """
    # Build query
    query = select(Alert)

    if severity:
        query = query.where(Alert.severity == severity)
    if status:
        query = query.where(Alert.status == status)
    if user_id:
        query = query.where(Alert.user_id == user_id)

    # Get total count
    count_query = select(func.count()).select_from(Alert)
    if severity:
        count_query = count_query.where(Alert.severity == severity)
    if status:
        count_query = count_query.where(Alert.status == status)
    if user_id:
        count_query = count_query.where(Alert.user_id == user_id)

    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size).order_by(Alert.created_at.desc())

    # Execute query
    result = await db.execute(query)
    alerts = result.scalars().all()

    return AlertList(
        total=total,
        items=[AlertResponse.model_validate(alert) for alert in alerts],
        page=page,
        page_size=page_size,
    )


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: UUID,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Get a specific alert by ID
    """
    query = select(Alert).where(Alert.id == alert_id)
    result = await db.execute(query)
    alert = result.scalar_one_or_none()

    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert {alert_id} not found",
        )

    return AlertResponse.model_validate(alert)


@router.post("/", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
async def create_alert(
    alert_data: AlertCreate,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Create a new alert
    """
    alert = Alert(
        alert_type=AlertType(alert_data.alert_type),
        severity=AlertSeverity(alert_data.severity),
        title=alert_data.title,
        description=alert_data.description,
        user_id=alert_data.user_id,
        user_name=alert_data.user_name,
        detection_data=alert_data.detection_data,
        ai_analysis=alert_data.ai_analysis,
    )

    db.add(alert)
    await db.commit()
    await db.refresh(alert)

    logger.info(f"Created alert: {alert.id} - {alert.alert_type.value}")

    return AlertResponse.model_validate(alert)


@router.patch("/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: UUID,
    alert_update: AlertUpdate,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Update an alert (e.g., change status, add resolution notes)
    """
    query = select(Alert).where(Alert.id == alert_id)
    result = await db.execute(query)
    alert = result.scalar_one_or_none()

    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert {alert_id} not found",
        )

    # Update fields
    if alert_update.status:
        alert.status = alert_update.status
    if alert_update.resolution_notes:
        alert.resolution_notes = alert_update.resolution_notes

    await db.commit()
    await db.refresh(alert)

    logger.info(f"Updated alert: {alert.id} - status: {alert.status}")

    return AlertResponse.model_validate(alert)


@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert(
    alert_id: UUID,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Delete an alert
    """
    query = select(Alert).where(Alert.id == alert_id)
    result = await db.execute(query)
    alert = result.scalar_one_or_none()

    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert {alert_id} not found",
        )

    await db.delete(alert)
    await db.commit()

    logger.info(f"Deleted alert: {alert_id}")

    return None


@router.get("/stats/summary")
async def get_alert_stats(
    db: AsyncSession = Depends(get_async_db),
):
    """
    Get alert statistics
    """
    # Total alerts
    total_query = select(func.count()).select_from(Alert)
    total_result = await db.execute(total_query)
    total = total_result.scalar_one()

    # Open alerts
    open_query = select(func.count()).select_from(Alert).where(Alert.status == "open")
    open_result = await db.execute(open_query)
    open_count = open_result.scalar_one()

    # Critical alerts
    critical_query = (
        select(func.count())
        .select_from(Alert)
        .where(Alert.severity == AlertSeverity.CRITICAL)
    )
    critical_result = await db.execute(critical_query)
    critical_count = critical_result.scalar_one()

    # By type
    type_query = select(
        Alert.alert_type, func.count(Alert.id).label("count")
    ).group_by(Alert.alert_type)
    type_result = await db.execute(type_query)
    by_type = {row[0].value: row[1] for row in type_result.all()}

    return {
        "total_alerts": total,
        "open_alerts": open_count,
        "critical_alerts": critical_count,
        "by_type": by_type,
    }


# Alert Service Configuration Endpoints

@router.post("/config/webhooks")
async def configure_webhooks(config: WebhookConfig):
    """
    Configure webhook URLs for alert notifications

    Supports Slack and Microsoft Teams webhooks.

    Args:
        config: Webhook configuration with list of URLs

    Returns:
        Configuration status
    """
    alert_service.configure_webhooks(config.webhook_urls)

    return {
        "status": "success",
        "message": f"Configured {len(config.webhook_urls)} webhook(s)",
        "webhooks": config.webhook_urls
    }


@router.post("/config/emails")
async def configure_emails(config: EmailConfig):
    """
    Configure email recipients for alert notifications

    Args:
        config: Email configuration with list of recipients

    Returns:
        Configuration status
    """
    alert_service.configure_emails(config.email_recipients)

    return {
        "status": "success",
        "message": f"Configured {len(config.email_recipients)} email recipient(s)",
        "recipients": config.email_recipients
    }


@router.get("/config/status")
async def get_alert_config_status():
    """
    Get current alert configuration status

    Returns:
        Current webhook and email configuration
    """
    return {
        "webhooks_configured": len(alert_service.webhook_urls),
        "email_recipients_configured": len(alert_service.email_recipients),
        "alert_history_count": len(alert_service.alert_history)
    }


@router.get("/history")
async def get_alert_history(
    limit: int = Query(50, ge=1, le=200, description="Number of alerts to return")
):
    """
    Get recent alert history from the alert service

    This shows alerts that were actually sent (MEDIUM or higher severity).

    Args:
        limit: Maximum number of alerts to return

    Returns:
        List of recent alerts
    """
    history = alert_service.get_alert_history(limit=limit)

    return {
        "total": len(history),
        "alerts": history
    }
