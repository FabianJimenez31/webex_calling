"""
Chat Assistant Service
AI-powered conversational interface for querying Webex Calling data
"""
import os
import json
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import httpx

from src.config import settings

logger = logging.getLogger(__name__)


class ChatAssistant:
    """AI assistant for conversational queries about call data"""

    def __init__(self):
        self.api_key = settings.openrouter_api_key
        self.model = settings.openrouter_model
        self.base_url = "https://openrouter.ai/api/v1"
        self.conversation_history = []

        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY must be set")

    async def ask(self, question: str, cdrs: List[Dict], context: Optional[Dict] = None) -> Dict:
        """
        Ask a question about call data

        Args:
            question: User's question in natural language
            cdrs: Call Detail Records to query
            context: Optional context (previous messages, filters, etc.)

        Returns:
            AI response with answer and relevant data
        """
        logger.info(f"Processing question: {question}")

        # Prepare data context
        data_context = self._prepare_data_context(cdrs)

        # Create prompt
        system_prompt = self._get_system_prompt()
        user_prompt = self._create_query_prompt(question, data_context, context)

        try:
            # Call AI
            response = await self._call_openrouter(system_prompt, user_prompt)

            # Parse response
            result = self._parse_response(response, question)

            logger.info(f"Question answered successfully")

            return result

        except Exception as e:
            logger.error(f"Failed to process question: {str(e)}")
            raise

    def _prepare_data_context(self, cdrs: List[Dict]) -> Dict:
        """Prepare comprehensive data context from CDRs"""

        if not cdrs:
            return {"summary": "No call data available"}

        total_calls = len(cdrs)

        # Call patterns by queue
        queues = {}
        for cdr in cdrs:
            queue = cdr.get("Called line ID") or cdr.get("User", "Unknown")
            if queue not in queues:
                queues[queue] = {
                    "total_calls": 0,
                    "answered": 0,
                    "failed": 0,
                    "total_duration": 0,
                    "avg_duration": 0
                }
            queues[queue]["total_calls"] += 1
            if cdr.get("Answered") == "true":
                queues[queue]["answered"] += 1
            else:
                queues[queue]["failed"] += 1
            queues[queue]["total_duration"] += cdr.get("Duration", 0)

        # Calculate averages
        for queue in queues:
            if queues[queue]["total_calls"] > 0:
                queues[queue]["avg_duration"] = round(
                    queues[queue]["total_duration"] / queues[queue]["total_calls"], 2
                )
                queues[queue]["answer_rate"] = round(
                    (queues[queue]["answered"] / queues[queue]["total_calls"]) * 100, 2
                )

        # Location analysis
        locations = {}
        for cdr in cdrs:
            loc = cdr.get("Location", "Unknown")
            if loc not in locations:
                locations[loc] = 0
            locations[loc] += 1

        # User analysis
        users = {}
        for cdr in cdrs:
            user = cdr.get("User", "Unknown")
            if user != "Unknown" and user:
                if user not in users:
                    users[user] = 0
                users[user] += 1

        # Time analysis
        hours = {}
        for cdr in cdrs:
            start = cdr.get("Start time")
            if start:
                try:
                    dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                    hour = dt.hour
                    if hour not in hours:
                        hours[hour] = 0
                    hours[hour] += 1
                except:
                    pass

        # Call types
        call_types = {}
        for cdr in cdrs:
            ct = cdr.get("Call type", "Unknown")
            if ct not in call_types:
                call_types[ct] = 0
            call_types[ct] += 1

        # Direction analysis
        directions = {}
        for cdr in cdrs:
            direction = cdr.get("Direction", "Unknown")
            if direction not in directions:
                directions[direction] = 0
            directions[direction] += 1

        # Answered vs Failed
        answered = sum(1 for cdr in cdrs if cdr.get("Answered") == "true")
        failed = total_calls - answered

        # Trunks
        trunks = {}
        for cdr in cdrs:
            trunk = cdr.get("Inbound trunk") or cdr.get("Outbound trunk")
            if trunk:
                if trunk not in trunks:
                    trunks[trunk] = 0
                trunks[trunk] += 1

        return {
            "total_calls": total_calls,
            "answered_calls": answered,
            "failed_calls": failed,
            "answer_rate": round((answered / total_calls * 100) if total_calls > 0 else 0, 2),
            "queues": queues,
            "locations": locations,
            "users": dict(sorted(users.items(), key=lambda x: x[1], reverse=True)[:20]),
            "hours_distribution": hours,
            "call_types": call_types,
            "directions": directions,
            "trunks": trunks,
            "sample_calls": cdrs[:5]  # Sample for reference
        }

    def _get_system_prompt(self) -> str:
        """Get system prompt for the chat assistant"""

        return """Eres un asistente experto en análisis de datos de Webex Calling. Tu función es ayudar a los usuarios a comprender sus datos de llamadas respondiendo preguntas de manera clara, concisa y accionable.

IMPORTANTE: SIEMPRE debes responder en ESPAÑOL. Todas tus respuestas, métricas, observaciones y recomendaciones deben estar en español.

Tienes acceso a datos completos de registros de llamadas (CDRs) que incluyen:
- Colas de llamadas y sus estadísticas
- Ubicaciones y distribución geográfica
- Usuarios y sus patrones de llamadas
- Resultados de llamadas (contestadas/fallidas)
- Patrones basados en tiempo
- Tipos y direcciones de llamadas
- Troncales e infraestructura

Al responder preguntas:
1. Sé específico y usa números exactos de los datos
2. Proporciona contexto y perspectivas, no solo números crudos
3. Resalta patrones o anomalías importantes
4. Sugiere acciones de seguimiento cuando sea relevante
5. Usa lenguaje claro y profesional en español
6. Formatea tu respuesta de manera estructurada

Si el usuario pregunta sobre colas, usuarios, ubicaciones o períodos de tiempo específicos, enfoca tu análisis en esos aspectos.

Siempre proporciona tu respuesta en formato JSON:
{
  "answer": "Respuesta directa a la pregunta en español",
  "details": {
    "key_metrics": {},
    "insights": [],
    "recommendations": []
  },
  "visualization_data": {}  // Opcional: datos para gráficos
}
"""

    def _create_query_prompt(self, question: str, data_context: Dict, context: Optional[Dict] = None) -> str:
        """Create query prompt with question and data"""

        prompt = f"""Pregunta del usuario: {question}

Resumen de datos de llamadas disponibles:
{json.dumps(data_context, indent=2, ensure_ascii=False)}

Por favor analiza estos datos y responde la pregunta del usuario EN ESPAÑOL. Sé específico y proporciona insights accionables.

Formatea tu respuesta como JSON con la estructura especificada en el prompt del sistema. Recuerda: TODO debe estar en español."""

        return prompt

    async def _call_openrouter(self, system_prompt: str, user_prompt: str) -> str:
        """Call OpenRouter API"""

        url = f"{self.base_url}/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://webex-calling-security.ai",
            "X-Title": "Webex Calling Chat Assistant"
        }

        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 1500
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=headers, json=data)

            if response.status_code != 200:
                logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
                raise Exception(f"OpenRouter API error: {response.status_code}")

            result = response.json()
            content = result["choices"][0]["message"]["content"]

            return content

    def _parse_response(self, response: str, question: str) -> Dict:
        """Parse AI response"""

        try:
            # Extract JSON from response
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
                "question": question,
                "answer": parsed.get("answer", response),
                "details": parsed.get("details", {}),
                "visualization_data": parsed.get("visualization_data"),
                "timestamp": datetime.utcnow().isoformat()
            }

        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON response: {e}")

            # Return plain text response
            return {
                "question": question,
                "answer": response,
                "details": {},
                "timestamp": datetime.utcnow().isoformat()
            }


# Global assistant instance
chat_assistant = ChatAssistant()
