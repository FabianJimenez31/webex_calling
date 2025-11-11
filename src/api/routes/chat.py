"""
Chat Assistant Routes
Conversational interface for querying call data
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from src.services.webex_client import webex_client
from src.services.chat_assistant import chat_assistant
from src.services.cdr_service import cdr_service

logger = logging.getLogger(__name__)

router = APIRouter()


class ChatRequest(BaseModel):
    """Chat request model"""
    question: str
    hours: Optional[int] = 24  # Look back hours for data
    limit: Optional[int] = 200  # Max CDRs to analyze
    context: Optional[dict] = None  # Optional context


class ChatResponse(BaseModel):
    """Chat response model"""
    question: str
    answer: str
    details: dict
    visualization_data: Optional[dict] = None
    timestamp: str


@router.post("/ask", response_model=ChatResponse)
async def ask_question(request: ChatRequest):
    """
    Ask a question about your call data in natural language

    Examples:
    - "¿Cuál es la cola que más llamadas tiene?"
    - "¿Cuántas llamadas fallidas hubo hoy?"
    - "¿Qué usuario hizo más llamadas?"
    - "¿Cuál es el porcentaje de respuesta de las colas?"
    - "¿En qué horario hay más llamadas?"

    Args:
        request: Question and optional filters

    Returns:
        Natural language answer with relevant data
    """
    try:
        logger.info(f"Received question: {request.question}")

        # Get CDRs from database cache (fast) and trigger background sync
        logger.info(f"Getting CDRs from database cache for last {request.hours} hours...")

        cdrs = await cdr_service.get_cdrs_with_background_sync(
            hours=request.hours,
            limit=request.limit
        )

        # If no CDRs in cache, try fetching directly from API once
        if not cdrs:
            logger.warning("No CDRs in cache, fetching from API...")
            try:
                end_time = datetime.utcnow() - timedelta(minutes=5)
                start_time = end_time - timedelta(hours=request.hours)

                cdrs = await webex_client.get_cdrs(
                    start_time=start_time,
                    end_time=end_time,
                    limit=request.limit
                )

                # Save to cache for next time
                if cdrs:
                    await cdr_service.save_cdrs_to_db(cdrs)
                    logger.info(f"Saved {len(cdrs)} CDRs to cache")

            except Exception as api_error:
                logger.error(f"Failed to fetch from API: {str(api_error)}")

        if not cdrs:
            return ChatResponse(
                question=request.question,
                answer="No hay datos de llamadas disponibles para el período seleccionado. Por favor, intenta con un rango de tiempo diferente o espera a que se sincronicen los datos.",
                details={},
                timestamp=datetime.utcnow().isoformat()
            )

        logger.info(f"Asking AI about {len(cdrs)} CDRs from cache...")

        # Ask the AI assistant
        response = await chat_assistant.ask(
            question=request.question,
            cdrs=cdrs,
            context=request.context
        )

        return ChatResponse(**response)

    except Exception as e:
        logger.error(f"Failed to process question: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process question: {str(e)}")


@router.get("/examples")
async def get_example_questions():
    """
    Get example questions you can ask

    Returns:
        List of example questions in different categories
    """
    return {
        "categories": {
            "Colas de Llamadas": [
                "¿Cuál es la cola que más llamadas tiene?",
                "¿Cuál es el porcentaje de respuesta de cada cola?",
                "¿Qué cola tiene más llamadas abandonadas?",
                "¿Cuál es el tiempo promedio de espera por cola?"
            ],
            "Usuarios y Agentes": [
                "¿Qué usuario hizo más llamadas?",
                "¿Cuántas llamadas atendió cada agente?",
                "¿Qué agentes tienen mejor tasa de respuesta?",
                "¿Quién tiene el mayor tiempo promedio de llamada?"
            ],
            "Análisis Temporal": [
                "¿En qué horario hay más llamadas?",
                "¿Cuántas llamadas hubo hoy?",
                "¿Cuál es la distribución de llamadas por hora?",
                "¿Hay picos de llamadas en algún momento?"
            ],
            "Métricas de Calidad": [
                "¿Cuál es la tasa de respuesta general?",
                "¿Cuántas llamadas fallaron?",
                "¿Cuál es la duración promedio de las llamadas?",
                "¿Qué porcentaje de llamadas fueron exitosas?"
            ],
            "Ubicaciones": [
                "¿Desde qué ubicaciones hay más llamadas?",
                "¿Cuántas llamadas hay por país?",
                "¿Qué sitio tiene más actividad?",
                "¿Hay llamadas internacionales?"
            ],
            "Infraestructura": [
                "¿Qué trunks están más utilizados?",
                "¿Cuántas llamadas entraron por cada gateway?",
                "¿Qué tipo de llamadas son más comunes?",
                "¿Hay problemas con algún trunk específico?"
            ]
        },
        "quick_questions": [
            "Dame un resumen de las llamadas de hoy",
            "¿Cuáles son las principales métricas?",
            "¿Hay algún problema que deba atender?",
            "Muéstrame las estadísticas más importantes"
        ]
    }


@router.post("/ask/quick")
async def quick_question(
    q: str = Query(..., description="Your question", min_length=5),
    hours: int = Query(24, ge=1, le=48, description="Hours of data to analyze")
):
    """
    Quick question endpoint (simpler interface)

    Query parameters:
        q: Your question (e.g., "¿Cuál es la cola que más llamadas tiene?")
        hours: Hours of data to analyze (default: 24)

    Example:
        GET /chat/ask/quick?q=¿Cuál es la cola que más llamadas tiene?&hours=24
    """
    request = ChatRequest(
        question=q,
        hours=hours
    )

    return await ask_question(request)


@router.get("/stats")
async def get_chat_stats():
    """Get chat assistant statistics"""

    sync_status = await cdr_service.get_sync_status()

    return {
        "status": "operational",
        "ai_model": chat_assistant.model,
        "ai_provider": "OpenRouter",
        "supported_languages": ["Español", "English"],
        "max_cdrs_analyzed": 200,
        "available_hours": 48,
        "example_questions_count": 25,
        "cdr_cache": {
            "enabled": True,
            "sync_status": sync_status["status"],
            "is_syncing": sync_status["is_syncing"]
        }
    }


@router.post("/sync")
async def trigger_cdr_sync(
    hours: int = Query(24, ge=1, le=168, description="Hours of data to sync")
):
    """
    Manually trigger CDR sync from Webex API to database

    Args:
        hours: Hours of data to sync (default: 24, max: 168 = 1 week)

    Returns:
        Sync result
    """
    result = await cdr_service.sync_cdrs_from_api(hours=hours)
    return result
