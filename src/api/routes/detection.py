"""
Anomaly Detection Routes
AI-powered security analysis endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from src.services.webex_client import webex_client
from src.services.anomaly_detector import anomaly_detector
from src.services.alert_service import alert_service
from src.services.scheduler import analysis_scheduler

logger = logging.getLogger(__name__)

router = APIRouter()


class AnalysisRequest(BaseModel):
    """Analysis request model"""
    analysis_type: str = "security"  # security, fraud, quality
    hours: int = 24  # Look back hours
    limit: Optional[int] = 100  # Max CDRs to analyze


class AnomalyResponse(BaseModel):
    """Anomaly detection response"""
    risk_level: str
    overall_assessment: str
    anomalies: List[dict]
    insights: Optional[List[str]] = []
    recommendations: List[str]
    analyzed_cdrs: int
    analysis_time: str


@router.post("/analyze", response_model=AnomalyResponse)
async def analyze_cdrs(request: AnalysisRequest = None):
    """
    Analyze recent CDRs for security anomalies using AI

    This endpoint:
    1. Fetches recent CDRs from Webex
    2. Analyzes them using OpenRouter AI (GPT OSS Safeguard)
    3. Returns detected anomalies, risk assessment, and recommendations

    Args:
        request: Analysis configuration (type, time range, limit)

    Returns:
        Detailed security analysis with anomalies and recommendations
    """
    try:
        if request is None:
            request = AnalysisRequest()

        logger.info(f"Starting {request.analysis_type} analysis for last {request.hours} hours...")

        # Fetch CDRs from Webex
        end_time = datetime.utcnow() - timedelta(minutes=5)  # 5 min buffer
        start_time = end_time - timedelta(hours=request.hours)

        logger.info(f"Fetching CDRs from {start_time} to {end_time}...")

        cdrs = await webex_client.get_cdrs(
            start_time=start_time,
            end_time=end_time,
            limit=request.limit or 100
        )

        if not cdrs:
            return AnomalyResponse(
                risk_level="UNKNOWN",
                overall_assessment="No CDR data available for analysis",
                anomalies=[],
                recommendations=["Wait for call activity to generate CDRs"],
                analyzed_cdrs=0,
                analysis_time=datetime.utcnow().isoformat()
            )

        logger.info(f"Analyzing {len(cdrs)} CDRs...")

        # Analyze CDRs with AI
        analysis = await anomaly_detector.analyze_cdrs(
            cdrs=cdrs,
            analysis_type=request.analysis_type
        )

        # Add metadata
        analysis["analyzed_cdrs"] = len(cdrs)
        analysis["analysis_time"] = datetime.utcnow().isoformat()

        logger.info(f"Analysis complete. Risk level: {analysis.get('risk_level')}")

        # Send alert if necessary
        await alert_service.send_alert(
            risk_level=analysis.get('risk_level', 'UNKNOWN'),
            assessment=analysis.get('overall_assessment', ''),
            anomalies=analysis.get('anomalies', []),
            analyzed_cdrs=len(cdrs)
        )

        return AnomalyResponse(**analysis)

    except Exception as e:
        logger.error(f"Failed to analyze CDRs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/analyze/quick")
async def quick_analysis(
    hours: int = Query(24, ge=1, le=48, description="Hours to analyze"),
    limit: int = Query(50, ge=10, le=200, description="Max CDRs to analyze")
):
    """
    Quick security analysis of recent calls

    Simplified endpoint for quick checks. Uses default security analysis.

    Query parameters:
        hours: Hours to look back (1-48)
        limit: Maximum CDRs to analyze (10-200)
    """
    request = AnalysisRequest(
        analysis_type="security",
        hours=hours,
        limit=limit
    )

    return await analyze_cdrs(request)


@router.get("/stats")
async def get_detection_stats():
    """
    Get detection system statistics

    Returns metadata about the detection system
    """
    return {
        "status": "operational",
        "ai_model": anomaly_detector.model,
        "ai_provider": "OpenRouter",
        "analysis_types": ["security", "fraud", "quality"],
        "max_cdrs_per_analysis": 200,
        "available_hours": 48
    }


# Scheduled Analysis Endpoints

class ScheduleConfig(BaseModel):
    """Schedule configuration"""
    schedule_type: str  # hourly, daily, custom
    hours: int = 1  # Hours of data to analyze
    limit: int = 100  # Max CDRs
    # For daily
    hour: int = 8  # Hour of day (0-23)
    minute: int = 0  # Minute (0-59)
    # For custom
    interval_minutes: Optional[int] = None


@router.post("/schedule/enable")
async def enable_scheduled_analysis(config: ScheduleConfig):
    """
    Enable scheduled security analysis

    Args:
        config: Schedule configuration

    Returns:
        Scheduled job information
    """
    # Start scheduler if not running
    if not analysis_scheduler.is_running:
        analysis_scheduler.start()

    # Schedule based on type
    if config.schedule_type == "hourly":
        job = analysis_scheduler.schedule_hourly_analysis(
            hours=config.hours,
            limit=config.limit
        )
    elif config.schedule_type == "daily":
        job = analysis_scheduler.schedule_daily_analysis(
            hour=config.hour,
            minute=config.minute,
            hours=config.hours,
            limit=config.limit
        )
    elif config.schedule_type == "custom" and config.interval_minutes:
        job = analysis_scheduler.schedule_custom_interval(
            interval_minutes=config.interval_minutes,
            hours=config.hours,
            limit=config.limit
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid schedule type")

    return {
        "status": "scheduled",
        "job_id": job.id,
        "job_name": job.name,
        "next_run": job.next_run_time.isoformat() if job.next_run_time else None
    }


@router.post("/schedule/disable/{job_id}")
async def disable_scheduled_analysis(job_id: str):
    """
    Disable a scheduled analysis job

    Args:
        job_id: ID of the scheduled job to remove

    Returns:
        Status of the operation
    """
    success = analysis_scheduler.remove_scheduled_job(job_id)

    if success:
        return {"status": "disabled", "job_id": job_id}
    else:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")


@router.get("/schedule/jobs")
async def get_scheduled_jobs():
    """
    Get list of all scheduled analysis jobs

    Returns:
        List of scheduled jobs with their details
    """
    jobs = analysis_scheduler.get_scheduled_jobs()

    return {
        "total": len(jobs),
        "scheduler_running": analysis_scheduler.is_running,
        "last_analysis": analysis_scheduler.last_analysis_time.isoformat() if analysis_scheduler.last_analysis_time else None,
        "jobs": jobs
    }


@router.get("/schedule/history")
async def get_schedule_history(
    limit: int = Query(50, ge=1, le=200)
):
    """
    Get history of scheduled analyses

    Args:
        limit: Maximum number of history records to return

    Returns:
        List of past scheduled analyses
    """
    history = analysis_scheduler.get_analysis_history(limit=limit)

    return {
        "total": len(history),
        "analyses": history
    }
