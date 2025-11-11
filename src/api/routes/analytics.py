"""
Analytics and Reports Routes
Endpoints for Webex Analytics and Reports API
Includes fraud detection, agent performance, and SLA analytics
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from src.services.webex_client import webex_client
from src.services.fraud_detection import fraud_detection_service
from src.services.agent_analytics import agent_analytics_service
from src.services.cdr_service import cdr_service

logger = logging.getLogger(__name__)

router = APIRouter()


class ReportTemplate(BaseModel):
    """Report template model"""
    id: int
    title: str
    service: Optional[str] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None


class ReportCreate(BaseModel):
    """Create report request"""
    templateId: int
    startDate: Optional[str] = None
    endDate: Optional[str] = None


class Report(BaseModel):
    """Report model"""
    id: str
    title: str
    service: str
    startDate: str
    endDate: str
    created: str
    status: str
    downloadURL: Optional[str] = None


@router.get("/templates")
async def list_report_templates():
    """
    List all available report templates

    Returns templates for Calling Quality, Engagement, Media Quality, etc.
    """
    try:
        logger.info("Fetching available report templates...")

        templates = await webex_client.get_report_templates()

        return {
            "total": len(templates),
            "items": templates
        }

    except Exception as e:
        logger.error(f"Failed to fetch report templates: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch templates: {str(e)}")


@router.post("/reports")
async def create_report(report_data: ReportCreate):
    """
    Create a new analytics report

    Args:
        report_data: Report configuration (templateId, date range)

    Returns:
        Report ID for the newly created report
    """
    try:
        logger.info(f"Creating report with template ID: {report_data.templateId}")

        # Default to last 7 days if not specified
        if not report_data.startDate:
            start = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")
            report_data.startDate = start

        if not report_data.endDate:
            # End date should be at least 1 day ago to ensure data availability
            end = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
            report_data.endDate = end

        report = await webex_client.create_report(
            template_id=report_data.templateId,
            start_date=report_data.startDate,
            end_date=report_data.endDate
        )

        return report

    except Exception as e:
        logger.error(f"Failed to create report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create report: {str(e)}")


@router.get("/reports")
async def list_reports(
    service: Optional[str] = Query(None, description="Filter by service type"),
    from_date: Optional[str] = Query(None, description="Filter by creation date (from)"),
    to_date: Optional[str] = Query(None, description="Filter by creation date (to)")
):
    """
    List all generated reports

    Query parameters:
        service: Filter by service type (e.g., 'webex-calling')
        from_date: Filter from creation date
        to_date: Filter to creation date
    """
    try:
        logger.info("Fetching generated reports...")

        reports = await webex_client.get_reports(
            service=service,
            from_date=from_date,
            to_date=to_date
        )

        return {
            "total": len(reports),
            "items": reports
        }

    except Exception as e:
        logger.error(f"Failed to fetch reports: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch reports: {str(e)}")


@router.get("/reports/{report_id}")
async def get_report(report_id: str):
    """
    Get details of a specific report including download URL

    Args:
        report_id: Report ID

    Returns:
        Report metadata including download URL
    """
    try:
        logger.info(f"Fetching report details: {report_id}")

        report = await webex_client.get_report(report_id)

        return report

    except Exception as e:
        logger.error(f"Failed to fetch report {report_id}: {str(e)}")
        raise HTTPException(status_code=404, detail=f"Report not found: {str(e)}")


@router.get("/calling-stats")
async def get_calling_stats():
    """
    Get aggregated calling statistics

    This endpoint creates a Calling Engagement report and returns aggregated stats
    """
    try:
        logger.info("Generating calling statistics...")

        # Get available templates to find Calling Engagement template
        templates = await webex_client.get_report_templates()

        # Find Calling Engagement template (usually templateId around 1-10)
        engagement_template = None
        for template in templates:
            if "calling" in template.get("title", "").lower() and "engagement" in template.get("title", "").lower():
                engagement_template = template
                break

        if not engagement_template:
            # Return mock data if template not found
            return {
                "message": "Calling Engagement template not found",
                "available_templates": [t.get("title") for t in templates[:5]]
            }

        # Create report for last 7 days
        start_date = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")
        end_date = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")

        report = await webex_client.create_report(
            template_id=engagement_template["id"],
            start_date=start_date,
            end_date=end_date
        )

        return {
            "status": "Report created",
            "report_id": report.get("id"),
            "template": engagement_template.get("title"),
            "period": f"{start_date} to {end_date}",
            "message": "Report is being generated. Use GET /analytics/reports/{id} to check status and download."
        }

    except Exception as e:
        logger.error(f"Failed to generate calling stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate stats: {str(e)}")


# ===========================
# FRAUD DETECTION & SECURITY
# ===========================

@router.get("/security/scan")
async def security_scan(
    hours: int = Query(24, description="Hours to analyze", ge=1, le=168),
    limit: int = Query(1000, description="Maximum CDRs to analyze", ge=1, le=5000)
):
    """
    🔒 Analiza CDRs en busca de patrones de fraude y actividad sospechosa

    Detecta:
    - Llamadas internacionales sospechosas
    - Actividad fuera de horario laboral
    - Mass dialing (posibles ataques)
    - Llamadas rápidas secuenciales (bots)
    - Destinos de alto costo

    Args:
        hours: Horas hacia atrás para analizar (default: 24, max: 168)
        limit: Máximo de CDRs a analizar (default: 1000)

    Returns:
        Alertas de seguridad, estadísticas y score de seguridad
    """
    try:
        logger.info(f"Starting security scan for last {hours} hours...")

        # Get CDRs from database
        cdrs = await cdr_service.get_cdrs_from_db(hours=hours, limit=limit)

        if not cdrs:
            return {
                "status": "no_data",
                "message": "No hay CDRs disponibles para analizar",
                "alerts": [],
                "stats": {
                    "total_cdrs": 0,
                    "suspicious_patterns": 0,
                    "high_risk_calls": 0,
                    "medium_risk_calls": 0,
                    "low_risk_calls": 0
                }
            }

        # Run fraud detection analysis
        result = await fraud_detection_service.analyze_cdrs(cdrs)

        # Calculate security score
        security_score, risk_level = fraud_detection_service.get_security_score(result["alerts"])

        result["security_score"] = security_score
        result["risk_level"] = risk_level
        result["analysis_period_hours"] = hours

        logger.info(f"Security scan complete. Found {len(result['alerts'])} alerts. Score: {security_score}")

        return result

    except Exception as e:
        logger.error(f"Security scan failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Security scan failed: {str(e)}")


# ===========================
# AGENT PERFORMANCE ANALYTICS
# ===========================

@router.get("/agents/performance")
async def agent_performance(
    hours: int = Query(24, description="Hours to analyze", ge=1, le=168),
    limit: int = Query(1000, description="Maximum CDRs to analyze", ge=1, le=5000)
):
    """
    👥 Análisis completo de rendimiento de agentes

    Métricas incluidas:
    - Llamadas atendidas vs fallidas
    - Tasa de contestación (answer rate)
    - Tiempo promedio de manejo (handle time)
    - Distribución por hora del día
    - Score de productividad (0-100)
    - Cumplimiento de SLA por agente

    Args:
        hours: Horas hacia atrás para analizar
        limit: Máximo de CDRs a analizar

    Returns:
        Métricas por agente, métricas generales del equipo, insights y SLA compliance
    """
    try:
        logger.info(f"Analyzing agent performance for last {hours} hours...")

        # Get CDRs from database
        cdrs = await cdr_service.get_cdrs_from_db(hours=hours, limit=limit)

        if not cdrs:
            return {
                "status": "no_data",
                "message": "No hay CDRs disponibles para analizar",
                "agents": [],
                "overall": {},
                "insights": []
            }

        # Analyze agent performance
        result = await agent_analytics_service.analyze_agent_performance(cdrs)
        result["analysis_period_hours"] = hours

        logger.info(f"Agent performance analysis complete. Analyzed {result['overall']['total_agents']} agents")

        return result

    except Exception as e:
        logger.error(f"Agent performance analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/sla/compliance")
async def sla_compliance(
    hours: int = Query(24, description="Hours to analyze", ge=1, le=168),
    limit: int = Query(1000, description="Maximum CDRs to analyze", ge=1, le=5000)
):
    """
    📊 Verificación de cumplimiento de SLA

    Verifica:
    - Tasa de contestación vs objetivo (80%)
    - Tiempo promedio de manejo vs objetivo (180s)
    - Compliance rate del equipo (90%)
    - Score general de SLA (0-100)

    Args:
        hours: Horas hacia atrás para analizar
        limit: Máximo de CDRs a analizar

    Returns:
        Estado de cumplimiento de SLA con métricas detalladas
    """
    try:
        logger.info(f"Checking SLA compliance for last {hours} hours...")

        # Get CDRs from database
        cdrs = await cdr_service.get_cdrs_from_db(hours=hours, limit=limit)

        if not cdrs:
            return {
                "status": "no_data",
                "message": "No hay CDRs disponibles para analizar",
                "sla_compliance": {}
            }

        # Analyze agent performance to get SLA metrics
        result = await agent_analytics_service.analyze_agent_performance(cdrs)

        # Extract SLA compliance
        sla_data = result.get("sla_compliance", {})
        sla_data["analysis_period_hours"] = hours
        sla_data["total_agents_analyzed"] = result["overall"]["total_agents"]
        sla_data["total_calls_analyzed"] = result["overall"]["total_calls"]

        logger.info(f"SLA compliance check complete. Overall score: {sla_data.get('overall_score', 0)}")

        return sla_data

    except Exception as e:
        logger.error(f"SLA compliance check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"SLA check failed: {str(e)}")


@router.get("/staffing/recommendations")
async def staffing_recommendations(
    hours: int = Query(168, description="Hours to analyze for patterns (default: 7 days)", ge=24, le=720),
    limit: int = Query(5000, description="Maximum CDRs to analyze", ge=100, le=10000)
):
    """
    ⏱️ Recomendaciones de asignación de personal

    Analiza patrones de volumen de llamadas por hora del día
    para recomendar staffing óptimo

    Incluye:
    - Agentes recomendados por hora
    - Horas pico identificadas
    - Prioridad por hora (ALTA/MEDIA/BAJA)
    - Volumen de llamadas por hora

    Args:
        hours: Horas hacia atrás para analizar (recomendado: 168 = 7 días)
        limit: Máximo de CDRs a analizar

    Returns:
        Recomendaciones de staffing por hora del día
    """
    try:
        logger.info(f"Generating staffing recommendations based on last {hours} hours...")

        # Get CDRs from database
        cdrs = await cdr_service.get_cdrs_from_db(hours=hours, limit=limit)

        if not cdrs:
            return {
                "status": "no_data",
                "message": "No hay CDRs disponibles para analizar",
                "recommendations": []
            }

        # Analyze agent performance first to get agent metrics
        agent_result = await agent_analytics_service.analyze_agent_performance(cdrs)

        # Get staffing recommendations
        staffing = agent_analytics_service.get_staffing_recommendations(
            agent_result["agents"],
            cdrs
        )

        staffing["analysis_period_hours"] = hours
        staffing["total_calls_analyzed"] = len(cdrs)

        logger.info(f"Staffing recommendations generated. Peak hours: {len(staffing.get('peak_hours', []))}")

        return staffing

    except Exception as e:
        logger.error(f"Staffing recommendations failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Recommendations failed: {str(e)}")


@router.get("/dashboard/summary")
async def dashboard_summary(
    hours: int = Query(24, description="Hours to analyze", ge=1, le=168)
):
    """
    📈 Dashboard completo con todas las métricas

    Combina:
    - Análisis de seguridad y fraude
    - Rendimiento de agentes
    - Cumplimiento de SLA
    - Estado general del sistema

    Perfecto para dashboards principales y vistas ejecutivas

    Args:
        hours: Horas hacia atrás para analizar

    Returns:
        Resumen completo con todas las métricas principales
    """
    try:
        logger.info(f"Generating dashboard summary for last {hours} hours...")

        # Get CDRs from database
        cdrs = await cdr_service.get_cdrs_from_db(hours=hours, limit=2000)

        if not cdrs:
            return {
                "status": "no_data",
                "message": "No hay CDRs disponibles",
                "timestamp": datetime.utcnow().isoformat(),
                "analysis_period_hours": hours
            }

        # Run all analyses in parallel (concurrent execution)
        import asyncio

        security_task = fraud_detection_service.analyze_cdrs(cdrs)
        performance_task = agent_analytics_service.analyze_agent_performance(cdrs)

        security_result, performance_result = await asyncio.gather(
            security_task,
            performance_task
        )

        # Calculate security score
        security_score, risk_level = fraud_detection_service.get_security_score(
            security_result["alerts"]
        )

        # Build comprehensive summary
        summary = {
            "timestamp": datetime.utcnow().isoformat(),
            "analysis_period_hours": hours,
            "total_cdrs_analyzed": len(cdrs),

            # Security overview
            "security": {
                "score": security_score,
                "risk_level": risk_level,
                "total_alerts": len(security_result["alerts"]),
                "critical_alerts": security_result["stats"]["high_risk_calls"],
                "top_alerts": security_result["alerts"][:5]  # Top 5 alerts
            },

            # Agent performance overview
            "performance": {
                "total_agents": performance_result["overall"]["total_agents"],
                "total_calls": performance_result["overall"]["total_calls"],
                "answer_rate": performance_result["overall"]["overall_answer_rate"],
                "avg_handle_time": performance_result["overall"]["avg_handle_time"],
                "avg_productivity": performance_result["overall"]["avg_productivity_score"],
                "top_performers": performance_result["agents"][:5]  # Top 5 agents
            },

            # SLA overview
            "sla": {
                "overall_score": performance_result["sla_compliance"]["overall_score"],
                "status": performance_result["sla_compliance"]["overall_status"],
                "compliance_details": {
                    "answer_rate": performance_result["sla_compliance"]["answer_rate"],
                    "avg_handle_time": performance_result["sla_compliance"]["avg_handle_time"],
                    "team_compliance": performance_result["sla_compliance"]["team_compliance"]
                }
            },

            # Key insights
            "insights": performance_result["insights"],

            # System status
            "status": "healthy" if security_score >= 80 and performance_result["sla_compliance"]["overall_score"] >= 80 else "warning"
        }

        logger.info(f"Dashboard summary generated. Status: {summary['status']}")

        return summary

    except Exception as e:
        logger.error(f"Dashboard summary failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Dashboard generation failed: {str(e)}")
