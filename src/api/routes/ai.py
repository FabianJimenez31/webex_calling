"""
AI Module Routes
Endpoints para módulos de IA: Operativo, Comercial, Estratégico
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime
import logging

from src.services.webex_ai_service import webex_ai_service

logger = logging.getLogger(__name__)

router = APIRouter()


class ModuleAnalysisRequest(BaseModel):
    """Request model para análisis de módulo"""
    module_type: Literal["operativo", "comercial", "estrategico"]
    num_recordings: Optional[int] = 100
    context: Optional[dict] = None


class ModuleAnalysisResponse(BaseModel):
    """Response model para análisis de módulo"""
    module_type: str
    num_recordings_analyzed: int
    analysis_timestamp: str
    status: str
    results: dict


@router.post("/analyze-module", response_model=ModuleAnalysisResponse)
async def analyze_module(request: ModuleAnalysisRequest):
    """
    Analiza grabaciones simuladas para un módulo específico de IA

    Módulos disponibles:
    - **operativo**: Análisis de eficiencia operacional y problemas recurrentes
    - **comercial**: Análisis de oportunidades de negocio y ventas
    - **estrategico**: Análisis de tendencias y decisiones de alto nivel

    Args:
        request: Configuración del análisis

    Returns:
        Resultados del análisis con insights generados por IA real

    Example:
        ```json
        {
          "module_type": "operativo",
          "num_recordings": 100,
          "context": {}
        }
        ```
    """
    try:
        logger.info(f"Starting module analysis: {request.module_type}")

        # Validar número de grabaciones
        if request.num_recordings < 10 or request.num_recordings > 500:
            raise HTTPException(
                status_code=400,
                detail="num_recordings debe estar entre 10 y 500"
            )

        # Realizar análisis
        result = await webex_ai_service.analyze_module(
            module_type=request.module_type,
            num_recordings=request.num_recordings,
            context=request.context
        )

        return ModuleAnalysisResponse(**result)

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to analyze module: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al analizar módulo: {str(e)}"
        )


@router.get("/modules")
async def get_available_modules():
    """
    Obtiene información sobre los módulos de IA disponibles

    Returns:
        Lista de módulos con sus descripciones
    """
    return {
        "modules": [
            {
                "id": "operativo",
                "name": "Módulo Operativo",
                "description": "Análisis de eficiencia operacional, problemas recurrentes y optimización de procesos",
                "icon": "Settings",
                "color": "#4CAF50",
                "focus_areas": [
                    "Identificación de problemas operativos",
                    "Optimización de tiempos de resolución",
                    "Detección de cuellos de botella",
                    "Necesidades de capacitación"
                ]
            },
            {
                "id": "comercial",
                "name": "Módulo Comercial",
                "description": "Análisis de oportunidades de negocio, ventas cruzadas y satisfacción del cliente",
                "icon": "TrendingUp",
                "color": "#2196F3",
                "focus_areas": [
                    "Oportunidades de venta cruzada",
                    "Productos con mayor demanda",
                    "Momentos óptimos para ofertas",
                    "Análisis de conversión"
                ]
            },
            {
                "id": "estrategico",
                "name": "Módulo Estratégico",
                "description": "Análisis de tendencias, decisiones de alto nivel e iniciativas estratégicas",
                "icon": "Target",
                "color": "#9C27B0",
                "focus_areas": [
                    "Tendencias a largo plazo",
                    "Cambios en comportamiento",
                    "Iniciativas estratégicas",
                    "Oportunidades de innovación"
                ]
            }
        ],
        "total_modules": 3,
        "ai_provider": "OpenRouter",
        "ai_model": webex_ai_service.model
    }


@router.get("/module-examples/{module_type}")
async def get_module_examples(
    module_type: Literal["operativo", "comercial", "estrategico"]
):
    """
    Obtiene ejemplos de insights para un módulo específico

    Args:
        module_type: Tipo de módulo

    Returns:
        Ejemplos de análisis para el módulo
    """
    examples = {
        "operativo": {
            "module_type": "operativo",
            "example_insights": [
                {
                    "titulo": "Picos de volumen los miércoles",
                    "descripcion": "El 40% de las llamadas sobre problemas técnicos con la app móvil ocurren los miércoles entre 2-4 PM",
                    "recomendacion": "Considera programar actualizaciones de sistemas para días de menor volumen (sábado/domingo) y asignar personal adicional los miércoles en horario pico"
                },
                {
                    "titulo": "Tiempo de resolución elevado",
                    "descripcion": "Las consultas sobre bloqueo de tarjetas toman en promedio 8 minutos, 65% más que otras consultas",
                    "recomendacion": "Implementar script automatizado de verificación de identidad para reducir tiempo de validación de seguridad"
                }
            ]
        },
        "comercial": {
            "module_type": "comercial",
            "example_insights": [
                {
                    "titulo": "Oportunidad de cross-selling en créditos",
                    "descripcion": "35% de clientes que consultan sobre cuentas de ahorro tienen perfil crediticio apto para créditos hipotecarios",
                    "recomendacion": "Entrenar agentes para identificar este perfil y ofrecer pre-aprobación de crédito hipotecario durante la llamada"
                },
                {
                    "titulo": "DaviPlata con alta demanda",
                    "descripcion": "DaviPlata aparece en 28% de las conversaciones, principalmente consultas sobre límites y transferencias",
                    "recomendacion": "Crear campaña para actualización de plan DaviPlata Plus durante estas interacciones"
                }
            ]
        },
        "estrategico": {
            "module_type": "estrategico",
            "example_insights": [
                {
                    "titulo": "Migración digital acelerada",
                    "descripcion": "45% de las llamadas son consultas sobre cómo usar servicios digitales, indicando adopción tecnológica en crecimiento",
                    "recomendacion": "Invertir en programa de alfabetización digital y tutoriales in-app para reducir dependencia del call center"
                },
                {
                    "titulo": "Segmento joven con necesidades específicas",
                    "descripcion": "Clientes menores de 30 años consultan principalmente sobre inversiones (CDT, fondos) y criptomonedas",
                    "recomendacion": "Desarrollar línea de productos de inversión para millennials y gen-Z, incluyendo educación financiera integrada"
                }
            ]
        }
    }

    if module_type not in examples:
        raise HTTPException(status_code=404, detail="Módulo no encontrado")

    return examples[module_type]


@router.get("/stats")
async def get_ai_stats():
    """
    Obtiene estadísticas del módulo de IA

    Returns:
        Estadísticas de uso y configuración
    """
    return {
        "status": "operational",
        "ai_provider": "OpenRouter",
        "ai_model": webex_ai_service.model,
        "modules_available": 3,
        "languages": ["Español (Colombia)"],
        "max_recordings_per_analysis": 500,
        "min_recordings_per_analysis": 10,
        "default_recordings": 100,
        "features": [
            "Análisis en tiempo real con IA",
            "Insights accionables específicos por módulo",
            "Simulación de análisis de grabaciones",
            "Recomendaciones basadas en datos",
            "Métricas cuantificables"
        ]
    }
