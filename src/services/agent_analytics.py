"""
Agent Analytics Service
Tracks agent performance, SLA compliance, and productivity metrics
"""
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import statistics

logger = logging.getLogger(__name__)


class AgentAnalyticsService:
    """Service for tracking agent performance and productivity"""

    def __init__(self):
        # Configuración de SLA
        self.sla_config = {
            "answer_time_target": 20,  # segundos
            "answer_rate_target": 80,  # porcentaje
            "service_level_target": 80,  # % contestadas en X segundos
            "abandonment_rate_target": 10,  # porcentaje máximo
            "avg_handle_time_target": 180,  # segundos (3 minutos)
        }

    async def analyze_agent_performance(self, cdrs: List[Dict]) -> Dict[str, any]:
        """
        Analiza el rendimiento de agentes

        Args:
            cdrs: Lista de CDRs

        Returns:
            Análisis completo de rendimiento de agentes
        """
        # Agrupar por agente/usuario
        agent_calls = defaultdict(list)

        for cdr in cdrs:
            # Identificar agente (puede ser User o el que contestó)
            agent = cdr.get("User") or cdr.get("calling_user_name")

            if agent and agent != "Unknown":
                agent_calls[agent].append(cdr)

        # Analizar cada agente
        agent_metrics = []

        for agent, calls in agent_calls.items():
            metrics = self._calculate_agent_metrics(agent, calls)
            agent_metrics.append(metrics)

        # Ordenar por llamadas atendidas
        agent_metrics.sort(key=lambda x: x["calls_answered"], reverse=True)

        # Calcular métricas generales
        overall_metrics = self._calculate_overall_metrics(agent_metrics, cdrs)

        # Identificar top performers y áreas de mejora
        insights = self._generate_insights(agent_metrics)

        return {
            "agents": agent_metrics[:20],  # Top 20 agentes
            "overall": overall_metrics,
            "insights": insights,
            "sla_compliance": self._check_sla_compliance(overall_metrics),
            "timestamp": datetime.utcnow().isoformat()
        }

    def _calculate_agent_metrics(self, agent: str, calls: List[Dict]) -> Dict:
        """Calcula métricas para un agente específico"""

        total_calls = len(calls)
        answered_calls = [c for c in calls if c.get("Answered") == "true" or c.get("answered") is True]
        failed_calls = [c for c in calls if c.get("Answered") == "false" or c.get("answered") is False]

        # Duración de llamadas
        durations = [c.get("Duration", 0) for c in answered_calls if c.get("Duration")]
        avg_duration = statistics.mean(durations) if durations else 0
        total_duration = sum(durations)

        # Llamadas por dirección
        inbound = sum(1 for c in calls if c.get("Direction") == "TERMINATING")
        outbound = sum(1 for c in calls if c.get("Direction") == "ORIGINATING")

        # Tasa de contestación
        answer_rate = (len(answered_calls) / total_calls * 100) if total_calls > 0 else 0

        # Distribución por hora del día
        hour_distribution = self._get_hour_distribution(calls)

        # Productivity score (0-100)
        productivity_score = self._calculate_productivity_score(
            answer_rate, avg_duration, total_calls
        )

        return {
            "agent": agent,
            "total_calls": total_calls,
            "calls_answered": len(answered_calls),
            "calls_failed": len(failed_calls),
            "answer_rate": round(answer_rate, 2),
            "inbound_calls": inbound,
            "outbound_calls": outbound,
            "total_duration_seconds": total_duration,
            "total_duration_minutes": round(total_duration / 60, 2),
            "avg_handle_time": round(avg_duration, 2),
            "min_duration": min(durations) if durations else 0,
            "max_duration": max(durations) if durations else 0,
            "hour_distribution": hour_distribution,
            "productivity_score": round(productivity_score, 2),
            "sla_compliant": answer_rate >= self.sla_config["answer_rate_target"]
        }

    def _calculate_overall_metrics(self, agent_metrics: List[Dict], cdrs: List[Dict]) -> Dict:
        """Calcula métricas generales del equipo"""

        total_agents = len(agent_metrics)
        total_calls = sum(a["total_calls"] for a in agent_metrics)
        total_answered = sum(a["calls_answered"] for a in agent_metrics)
        total_failed = sum(a["calls_failed"] for a in agent_metrics)

        overall_answer_rate = (total_answered / total_calls * 100) if total_calls > 0 else 0

        # Promedio de handle time del equipo
        all_durations = [a["avg_handle_time"] for a in agent_metrics if a["avg_handle_time"] > 0]
        avg_team_handle_time = statistics.mean(all_durations) if all_durations else 0

        # Distribución de productividad
        productivity_scores = [a["productivity_score"] for a in agent_metrics]
        avg_productivity = statistics.mean(productivity_scores) if productivity_scores else 0

        # Agentes con problemas de SLA
        sla_violations = sum(1 for a in agent_metrics if not a["sla_compliant"])

        return {
            "total_agents": total_agents,
            "total_calls": total_calls,
            "total_answered": total_answered,
            "total_failed": total_failed,
            "overall_answer_rate": round(overall_answer_rate, 2),
            "avg_handle_time": round(avg_team_handle_time, 2),
            "avg_productivity_score": round(avg_productivity, 2),
            "sla_violations": sla_violations,
            "sla_compliance_rate": round((total_agents - sla_violations) / total_agents * 100, 2) if total_agents > 0 else 100
        }

    def _calculate_productivity_score(self, answer_rate: float, avg_duration: float, total_calls: int) -> float:
        """
        Calcula un score de productividad (0-100)

        Factores:
        - Tasa de contestación (40%)
        - Eficiencia en manejo de tiempo (30%)
        - Volumen de llamadas (30%)
        """
        # Score por tasa de contestación
        answer_score = min(answer_rate, 100) * 0.4

        # Score por eficiencia (duración óptima ~3 minutos)
        target_duration = self.sla_config["avg_handle_time_target"]
        if avg_duration == 0:
            duration_score = 0
        elif avg_duration <= target_duration:
            duration_score = 100 * 0.3
        else:
            # Penalizar llamadas muy largas
            duration_score = max(0, (target_duration / avg_duration) * 100) * 0.3

        # Score por volumen (normalizado)
        # Asumiendo 50 llamadas como muy bueno
        volume_score = min(total_calls / 50, 1) * 100 * 0.3

        return answer_score + duration_score + volume_score

    def _get_hour_distribution(self, calls: List[Dict]) -> Dict[int, int]:
        """Obtiene distribución de llamadas por hora del día"""
        hour_counts = defaultdict(int)

        for call in calls:
            start_time = call.get("Start time")
            if start_time:
                try:
                    dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    hour_counts[dt.hour] += 1
                except:
                    pass

        return dict(hour_counts)

    def _generate_insights(self, agent_metrics: List[Dict]) -> List[str]:
        """Genera insights basados en las métricas de agentes"""
        insights = []

        if not agent_metrics:
            return ["No hay datos suficientes para generar insights."]

        # Top performer
        top_agent = agent_metrics[0]
        insights.append(
            f"🏆 Mejor agente: {top_agent['agent']} con {top_agent['calls_answered']} "
            f"llamadas contestadas y {top_agent['answer_rate']}% de tasa de respuesta."
        )

        # Agentes con baja performance
        low_performers = [a for a in agent_metrics if a["answer_rate"] < 60]
        if low_performers:
            insights.append(
                f"⚠️ {len(low_performers)} agente(s) tienen tasa de respuesta inferior al 60%. "
                f"Se recomienda capacitación adicional."
            )

        # Análisis de handle time
        handle_times = [a["avg_handle_time"] for a in agent_metrics if a["avg_handle_time"] > 0]
        if handle_times:
            avg_ht = statistics.mean(handle_times)
            target = self.sla_config["avg_handle_time_target"]

            if avg_ht > target * 1.5:
                insights.append(
                    f"📞 El tiempo promedio de manejo ({avg_ht:.0f}s) está 50% por encima del objetivo ({target}s). "
                    f"Revisar procesos para optimizar eficiencia."
                )
            elif avg_ht < target * 0.5:
                insights.append(
                    f"⚡ El tiempo promedio de manejo ({avg_ht:.0f}s) es muy bajo. "
                    f"Verificar que se está dando atención adecuada a los clientes."
                )

        # Balance de carga
        call_counts = [a["total_calls"] for a in agent_metrics]
        if call_counts:
            max_calls = max(call_counts)
            min_calls = min(call_counts)

            if max_calls > min_calls * 3:
                insights.append(
                    f"⚖️ Desbalance de carga detectado: el agente más ocupado tiene "
                    f"3x más llamadas que el menos ocupado. Considerar redistribución."
                )

        return insights

    def _check_sla_compliance(self, overall_metrics: Dict) -> Dict:
        """Verifica cumplimiento de SLA"""

        answer_rate = overall_metrics.get("overall_answer_rate", 0)
        avg_handle_time = overall_metrics.get("avg_handle_time", 0)
        sla_compliance_rate = overall_metrics.get("sla_compliance_rate", 0)

        sla_status = {
            "answer_rate": {
                "value": answer_rate,
                "target": self.sla_config["answer_rate_target"],
                "compliant": answer_rate >= self.sla_config["answer_rate_target"],
                "status": "✅ Cumplido" if answer_rate >= self.sla_config["answer_rate_target"] else "❌ No cumplido"
            },
            "avg_handle_time": {
                "value": avg_handle_time,
                "target": self.sla_config["avg_handle_time_target"],
                "compliant": avg_handle_time <= self.sla_config["avg_handle_time_target"],
                "status": "✅ Cumplido" if avg_handle_time <= self.sla_config["avg_handle_time_target"] else "❌ No cumplido"
            },
            "team_compliance": {
                "value": sla_compliance_rate,
                "target": 90.0,
                "compliant": sla_compliance_rate >= 90,
                "status": "✅ Cumplido" if sla_compliance_rate >= 90 else "⚠️ Mejorable"
            }
        }

        # Score general de SLA (0-100)
        compliant_count = sum(1 for v in sla_status.values() if v["compliant"])
        overall_sla_score = (compliant_count / len(sla_status)) * 100

        sla_status["overall_score"] = round(overall_sla_score, 2)
        sla_status["overall_status"] = "✅ CUMPLIDO" if overall_sla_score >= 80 else "❌ NO CUMPLIDO"

        return sla_status

    def get_staffing_recommendations(self, agent_metrics: List[Dict], cdrs: List[Dict]) -> Dict:
        """
        Genera recomendaciones de staffing basadas en patrones de llamadas

        Returns:
            Recomendaciones de asignación de personal por hora
        """
        # Analizar volumen por hora
        hour_volumes = defaultdict(int)

        for cdr in cdrs:
            start_time = cdr.get("Start time")
            if start_time:
                try:
                    dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    hour_volumes[dt.hour] += 1
                except:
                    pass

        if not hour_volumes:
            return {"recommendations": [], "message": "No hay datos suficientes"}

        # Calcular agentes necesarios por hora (asumiendo 10 llamadas por agente por hora)
        calls_per_agent_per_hour = 10

        recommendations = []
        for hour in range(24):
            volume = hour_volumes.get(hour, 0)
            recommended_agents = max(1, round(volume / calls_per_agent_per_hour))

            if volume > 0:
                recommendations.append({
                    "hour": hour,
                    "hour_label": f"{hour:02d}:00 - {hour+1:02d}:00",
                    "call_volume": volume,
                    "recommended_agents": recommended_agents,
                    "priority": "ALTA" if volume > 15 else "MEDIA" if volume > 5 else "BAJA"
                })

        # Ordenar por volumen
        recommendations.sort(key=lambda x: x["call_volume"], reverse=True)

        # Identificar horas pico
        peak_hours = [r for r in recommendations if r["priority"] == "ALTA"]

        return {
            "recommendations": recommendations,
            "peak_hours": peak_hours,
            "total_hours_coverage": len(recommendations),
            "summary": f"Se identificaron {len(peak_hours)} horas pico que requieren mayor cobertura de personal."
        }


# Instancia global
agent_analytics_service = AgentAnalyticsService()
