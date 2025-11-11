"""
Report Export Routes
PDF and CSV downloads for analysis and chat responses
"""
from fastapi import APIRouter, HTTPException, Query, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import logging
import io

from src.services.webex_client import webex_client
from src.services.anomaly_detector import anomaly_detector
from src.services.chat_assistant import chat_assistant
from src.services.report_generator import report_generator

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/security/pdf")
async def export_security_pdf(
    hours: int = Query(24, ge=1, le=48, description="Hours to analyze"),
    limit: int = Query(100, ge=10, le=200, description="Max CDRs")
):
    """
    Generate and download PDF security report

    Query parameters:
        hours: Hours of data to analyze (1-48)
        limit: Maximum CDRs to analyze (10-200)

    Returns:
        PDF file download
    """
    try:
        logger.info(f"Generating security PDF report for last {hours} hours...")

        # Fetch CDRs
        end_time = datetime.utcnow() - timedelta(minutes=5)
        start_time = end_time - timedelta(hours=hours)

        cdrs = await webex_client.get_cdrs(
            start_time=start_time,
            end_time=end_time,
            limit=limit
        )

        if not cdrs:
            raise HTTPException(status_code=404, detail="No CDR data available")

        # Run security analysis
        analysis = await anomaly_detector.analyze_cdrs(
            cdrs=cdrs,
            analysis_type="security"
        )

        # Generate PDF
        pdf_bytes = report_generator.generate_security_report_pdf(
            analysis=analysis,
            cdrs_count=len(cdrs)
        )

        # Return as downloadable file
        filename = f"security_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )

    except Exception as e:
        logger.error(f"Failed to generate security PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")


@router.get("/security/csv")
async def export_security_csv(
    hours: int = Query(24, ge=1, le=48),
    limit: int = Query(100, ge=10, le=200)
):
    """
    Generate and download CSV security analysis report

    Returns CSV with security analysis details
    """
    try:
        logger.info(f"Generating security CSV report...")

        # Fetch CDRs
        end_time = datetime.utcnow() - timedelta(minutes=5)
        start_time = end_time - timedelta(hours=hours)

        cdrs = await webex_client.get_cdrs(
            start_time=start_time,
            end_time=end_time,
            limit=limit
        )

        if not cdrs:
            raise HTTPException(status_code=404, detail="No CDR data available")

        # Run security analysis
        analysis = await anomaly_detector.analyze_cdrs(
            cdrs=cdrs,
            analysis_type="security"
        )

        # Generate CSV
        csv_content = report_generator.generate_analysis_csv(analysis)

        filename = f"security_analysis_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"

        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )

    except Exception as e:
        logger.error(f"Failed to generate security CSV: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")


@router.get("/cdrs/csv")
async def export_cdrs_csv(
    hours: int = Query(24, ge=1, le=48),
    limit: int = Query(200, ge=10, le=500)
):
    """
    Export raw CDRs to CSV

    Query parameters:
        hours: Hours of data to export (1-48)
        limit: Maximum CDRs to export (10-500)

    Returns:
        CSV file with raw CDR data
    """
    try:
        logger.info(f"Exporting CDRs to CSV...")

        # Fetch CDRs
        end_time = datetime.utcnow() - timedelta(minutes=5)
        start_time = end_time - timedelta(hours=hours)

        cdrs = await webex_client.get_cdrs(
            start_time=start_time,
            end_time=end_time,
            limit=limit
        )

        if not cdrs:
            raise HTTPException(status_code=404, detail="No CDR data available")

        # Generate CSV
        csv_content = report_generator.generate_cdrs_csv(cdrs)

        filename = f"cdrs_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"

        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )

    except Exception as e:
        logger.error(f"Failed to export CDRs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to export CDRs: {str(e)}")


class ChatReportRequest(BaseModel):
    """Request for chat report generation"""
    question: str
    hours: Optional[int] = 24
    limit: Optional[int] = 200


@router.post("/chat/pdf")
async def export_chat_pdf(request: ChatReportRequest):
    """
    Generate PDF report from a chat query

    Args:
        request: Chat question and parameters

    Returns:
        PDF report with chat response
    """
    try:
        logger.info(f"Generating chat PDF report for: {request.question}")

        # Fetch CDRs
        end_time = datetime.utcnow() - timedelta(minutes=5)
        start_time = end_time - timedelta(hours=request.hours)

        cdrs = await webex_client.get_cdrs(
            start_time=start_time,
            end_time=end_time,
            limit=request.limit
        )

        if not cdrs:
            raise HTTPException(status_code=404, detail="No CDR data available")

        # Ask AI
        chat_response = await chat_assistant.ask(
            question=request.question,
            cdrs=cdrs
        )

        # Generate PDF
        pdf_bytes = report_generator.generate_chat_report_pdf(chat_response)

        filename = f"chat_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )

    except Exception as e:
        logger.error(f"Failed to generate chat PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")


@router.get("/stats")
async def get_report_stats():
    """Get reporting system statistics"""
    return {
        "status": "operational",
        "available_formats": ["PDF", "CSV"],
        "report_types": [
            "Security Analysis (PDF/CSV)",
            "Raw CDRs (CSV)",
            "Chat Responses (PDF)"
        ],
        "max_hours": 48,
        "max_cdrs": 500
    }
