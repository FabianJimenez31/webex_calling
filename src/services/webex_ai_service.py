"""
Webex AI Service
Servicio de análisis IA para módulos Operativo, Comercial y Estratégico
"""
import os
import json
import logging
import random
from typing import Dict, List, Optional
from datetime import datetime
import httpx

from src.config import settings

logger = logging.getLogger(__name__)


class WebexAIService:
    """Servicio de IA para análisis de módulos de negocio de Davivienda"""

    def __init__(self):
        self.api_key = settings.openrouter_api_key
        self.model = settings.openrouter_model
        self.base_url = "https://openrouter.ai/api/v1"

        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY must be set")

    async def analyze_module(
        self,
        module_type: str,
        num_recordings: int = 100,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Analiza grabaciones simuladas para un módulo específico

        Args:
            module_type: Tipo de módulo (operativo, comercial, estrategico)
            num_recordings: Número de grabaciones simuladas a analizar
            context: Contexto adicional opcional

        Returns:
            Resultados del análisis con insights de IA
        """
        logger.info(f"Analyzing {num_recordings} recordings for module: {module_type}")

        # Generar datos simulados de grabaciones
        simulated_data = self._generate_simulated_recordings_data(module_type, num_recordings)

        # Generar prompt específico para el módulo
        system_prompt = self._get_system_prompt(module_type)
        user_prompt = self._create_module_prompt(module_type, simulated_data)

        try:
            # Llamar a la API de IA
            response = await self._call_ai_api(system_prompt, user_prompt)

            # Parsear respuesta
            result = self._parse_ai_response(response, module_type, num_recordings)

            logger.info(f"Module analysis completed successfully for {module_type}")

            return result

        except Exception as e:
            logger.error(f"Failed to analyze module {module_type}: {str(e)}")
            raise

    def _generate_simulated_recordings_data(self, module_type: str, num_recordings: int) -> Dict:
        """Genera datos simulados de grabaciones basados en patrones reales de Davivienda"""

        # Patrones específicos de Davivienda (banco colombiano)
        common_issues = [
            "problemas con tarjetas de crédito",
            "consultas sobre créditos hipotecarios",
            "bloqueo de cuentas",
            "problemas con la app móvil",
            "transferencias internacionales",
            "actualización de datos personales",
            "problemas con cajeros automáticos",
            "consultas sobre inversiones",
            "seguros y pólizas",
            "reclamos por transacciones"
        ]

        products_mentioned = [
            "DaviPlata",
            "Tarjeta de Crédito Mastercard",
            "Cuenta de Ahorros",
            "CDT (Certificado de Depósito a Término)",
            "Crédito Hipotecario",
            "Crédito de Libre Inversión",
            "App Móvil Davivienda",
            "Banca en Línea"
        ]

        # Distribución por día de la semana
        day_distribution = {
            "Lunes": random.randint(12, 18),
            "Martes": random.randint(14, 20),
            "Miércoles": random.randint(15, 22),
            "Jueves": random.randint(13, 19),
            "Viernes": random.randint(16, 24),
            "Sábado": random.randint(8, 12),
            "Domingo": random.randint(5, 10)
        }

        # Distribución por hora
        hour_distribution = {
            "8-10 AM": random.randint(8, 15),
            "10-12 PM": random.randint(15, 25),
            "12-2 PM": random.randint(10, 18),
            "2-4 PM": random.randint(18, 28),
            "4-6 PM": random.randint(12, 20),
            "6-8 PM": random.randint(6, 12)
        }

        # Métricas de calidad
        avg_duration = random.randint(180, 420)  # 3-7 minutos
        avg_satisfaction = round(random.uniform(3.5, 4.5), 1)
        first_call_resolution = round(random.uniform(65, 85), 1)

        return {
            "total_recordings": num_recordings,
            "date_range": "últimos 7 días",
            "common_issues": random.sample(common_issues, k=min(6, len(common_issues))),
            "products_mentioned": random.sample(products_mentioned, k=min(5, len(products_mentioned))),
            "day_distribution": day_distribution,
            "hour_distribution": hour_distribution,
            "avg_call_duration_seconds": avg_duration,
            "avg_customer_satisfaction": avg_satisfaction,
            "first_call_resolution_rate": first_call_resolution,
            "peak_day": max(day_distribution, key=day_distribution.get),
            "peak_hour": max(hour_distribution, key=hour_distribution.get)
        }

    def _get_system_prompt(self, module_type: str) -> str:
        """Obtiene el prompt del sistema según el tipo de módulo"""

        base_prompt = """Eres un experto consultor de IA especializado en análisis de call centers bancarios, específicamente para Davivienda, uno de los bancos más grandes de Colombia.

Tu rol es analizar grabaciones de llamadas y proporcionar insights accionables y estratégicos que ayuden a mejorar las operaciones del banco.

IMPORTANTE: SIEMPRE responde en ESPAÑOL colombiano profesional."""

        module_prompts = {
            "operativo": """
MÓDULO OPERATIVO - Enfoque en eficiencia operacional y resolución de problemas

Analiza los datos enfocándote en:
- Identificar problemas operativos recurrentes
- Detectar patrones de fallas en sistemas o procesos
- Proponer mejoras en la eficiencia del servicio
- Identificar necesidades de capacitación para agentes
- Optimizar tiempos de resolución
- Detectar cuellos de botella en procesos

Proporciona insights específicos, datos cuantitativos y recomendaciones accionables.""",

            "comercial": """
MÓDULO COMERCIAL - Enfoque en oportunidades de negocio y ventas

Analiza los datos enfocándote en:
- Identificar oportunidades de venta cruzada (cross-selling)
- Detectar productos con mayor demanda
- Analizar momentos óptimos para ofrecer productos
- Identificar necesidades no satisfechas de clientes
- Proponer estrategias para aumentar conversión
- Detectar patrones de clientes con alto potencial

Proporciona insights comerciales con datos específicos y estrategias de acción.""",

            "estrategico": """
MÓDULO ESTRATÉGICO - Enfoque en decisiones de alto nivel y tendencias

Analiza los datos enfocándote en:
- Identificar tendencias a largo plazo
- Detectar cambios en comportamiento de clientes
- Proponer iniciativas estratégicas
- Analizar riesgos y oportunidades del mercado
- Sugerir inversiones en tecnología o recursos
- Identificar áreas de innovación

Proporciona insights estratégicos con visión de negocio y recomendaciones de alto impacto."""
        }

        return base_prompt + "\n" + module_prompts.get(module_type, module_prompts["operativo"])

    def _create_module_prompt(self, module_type: str, simulated_data: Dict) -> str:
        """Crea el prompt específico para el análisis del módulo"""

        prompt = f"""He analizado {simulated_data['total_recordings']} grabaciones de llamadas del call center de Davivienda de los {simulated_data['date_range']}.

DATOS ENCONTRADOS:

📊 Distribución Temporal:
- Día con más llamadas: {simulated_data['peak_day']} ({simulated_data['day_distribution'][simulated_data['peak_day']]}% del volumen)
- Horario pico: {simulated_data['peak_hour']} ({simulated_data['hour_distribution'][simulated_data['peak_hour']]}% del volumen)

📞 Métricas de Calidad:
- Duración promedio: {simulated_data['avg_call_duration_seconds']} segundos ({simulated_data['avg_call_duration_seconds']//60} minutos)
- Satisfacción promedio: {simulated_data['avg_customer_satisfaction']}/5.0
- Resolución en primera llamada: {simulated_data['first_call_resolution_rate']}%

🔍 Temas Principales Identificados:
{chr(10).join(f"- {issue}" for issue in simulated_data['common_issues'])}

💳 Productos Más Mencionados:
{chr(10).join(f"- {product}" for product in simulated_data['products_mentioned'])}

Por favor, proporciona un análisis detallado en formato JSON con la siguiente estructura:

{{
  "resumen_ejecutivo": "Resumen de 2-3 líneas del análisis",
  "hallazgos_principales": [
    {{
      "titulo": "Título del hallazgo",
      "descripcion": "Descripción detallada",
      "impacto": "Alto/Medio/Bajo",
      "datos_soporte": "Estadística o dato que lo respalda"
    }}
  ],
  "insight_destacado": {{
    "titulo": "Insight más importante",
    "descripcion": "Explicación detallada con datos específicos",
    "ejemplo": "Ejemplo concreto basado en los datos"
  }},
  "recomendaciones": [
    {{
      "titulo": "Título de la recomendación",
      "descripcion": "Descripción de la acción recomendada",
      "impacto_esperado": "Impacto esperado de implementar esta recomendación",
      "prioridad": "Alta/Media/Baja"
    }}
  ],
  "metricas_clave": {{
    "metrica_1": "valor y descripción",
    "metrica_2": "valor y descripción",
    "metrica_3": "valor y descripción"
  }}
}}

IMPORTANTE:
- Sé específico con los datos proporcionados
- Menciona porcentajes y números exactos
- Las recomendaciones deben ser accionables e inmediatas
- Enfócate en el contexto de un banco colombiano (Davivienda)
- Usa terminología bancaria apropiada
"""

        return prompt

    async def _call_ai_api(self, system_prompt: str, user_prompt: str) -> str:
        """Llama a la API de IA (OpenRouter)"""

        url = f"{self.base_url}/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://webex-calling-security.ai",
            "X-Title": "Webex AI Module - Davivienda"
        }

        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7,  # Un poco más creativo para insights
            "max_tokens": 2000
        }

        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(url, headers=headers, json=data)

            if response.status_code != 200:
                logger.error(f"AI API error: {response.status_code} - {response.text}")
                raise Exception(f"AI API error: {response.status_code}")

            result = response.json()
            logger.info(f"OpenRouter full response: {result}")

            # Check if we have choices
            if not result.get("choices") or len(result["choices"]) == 0:
                logger.error(f"No choices in response: {result}")
                return ""

            content = result["choices"][0]["message"]["content"]
            logger.info(f"AI response content length: {len(content) if content else 0}")

            return content

    def _parse_ai_response(self, response: str, module_type: str, num_recordings: int) -> Dict:
        """Parsea la respuesta de la IA"""

        try:
            # Extraer JSON de la respuesta
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            elif "```" in response:
                json_start = response.find("```") + 3
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            else:
                json_str = response.strip()

            parsed = json.loads(json_str)

            return {
                "module_type": module_type,
                "num_recordings_analyzed": num_recordings,
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "status": "completed",
                "results": parsed
            }

        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON response: {e}")

            # Fallback: crear respuesta estructurada básica
            return {
                "module_type": module_type,
                "num_recordings_analyzed": num_recordings,
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "status": "completed",
                "results": {
                    "resumen_ejecutivo": response[:200],
                    "hallazgos_principales": [],
                    "recomendaciones": [],
                    "raw_response": response
                }
            }


# Instancia global
webex_ai_service = WebexAIService()
