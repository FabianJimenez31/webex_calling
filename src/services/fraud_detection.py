"""
Fraud Detection Service
Detects suspicious calling patterns and potential toll fraud
"""
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from src.models.alert import Alert, AlertType, AlertSeverity

logger = logging.getLogger(__name__)


class FraudDetectionService:
    """Service for detecting fraudulent calling patterns"""

    def __init__(self):
        # Configuración de umbrales
        self.config = {
            "international_calls_threshold": 5,  # Llamadas internacionales en 1 hora
            "after_hours_threshold": 3,  # Llamadas fuera de horario en 1 día
            "rapid_calls_threshold": 10,  # Llamadas en 5 minutos
            "high_cost_countries": ["900", "888", "809", "876"],  # Códigos de alto costo
            "business_hours_start": 7,  # 7 AM
            "business_hours_end": 19,  # 7 PM
            "suspicious_duration_min": 300,  # 5 minutos (posible fraude)
            "mass_dialing_threshold": 20,  # Llamadas únicas en 1 hora
        }

    async def analyze_cdrs(self, cdrs: List[Dict]) -> Dict[str, any]:
        """
        Analiza CDRs en busca de patrones sospechosos

        Args:
            cdrs: Lista de CDRs a analizar

        Returns:
            Diccionario con alertas y estadísticas de seguridad
        """
        alerts = []
        stats = {
            "total_cdrs": len(cdrs),
            "suspicious_patterns": 0,
            "high_risk_calls": 0,
            "medium_risk_calls": 0,
            "low_risk_calls": 0,
        }

        # Agrupar por usuario para análisis
        user_calls = defaultdict(list)
        for cdr in cdrs:
            user = cdr.get("User") or cdr.get("calling_user_name") or "Unknown"
            user_calls[user].append(cdr)

        # Analizar cada usuario
        for user, user_cdrs in user_calls.items():
            if user == "Unknown" or not user:
                continue

            # Detectar patrones sospechosos
            fraud_alerts = self._detect_fraud_patterns(user, user_cdrs)
            alerts.extend(fraud_alerts)

        # Clasificar alertas por severidad
        for alert in alerts:
            if alert["severity"] == "critical":
                stats["high_risk_calls"] += 1
            elif alert["severity"] == "high":
                stats["medium_risk_calls"] += 1
            else:
                stats["low_risk_calls"] += 1

        stats["suspicious_patterns"] = len(alerts)

        return {
            "alerts": alerts,
            "stats": stats,
            "analyzed_users": len(user_calls),
            "timestamp": datetime.utcnow().isoformat()
        }

    def _detect_fraud_patterns(self, user: str, cdrs: List[Dict]) -> List[Dict]:
        """Detecta patrones de fraude para un usuario específico"""
        alerts = []

        # 1. Llamadas internacionales sospechosas
        intl_alert = self._detect_suspicious_international(user, cdrs)
        if intl_alert:
            alerts.append(intl_alert)

        # 2. Llamadas fuera de horario
        after_hours_alert = self._detect_after_hours_activity(user, cdrs)
        if after_hours_alert:
            alerts.append(after_hours_alert)

        # 3. Mass dialing (posible ataque)
        mass_dial_alert = self._detect_mass_dialing(user, cdrs)
        if mass_dial_alert:
            alerts.append(mass_dial_alert)

        # 4. Llamadas rápidas secuenciales
        rapid_alert = self._detect_rapid_sequential_calls(user, cdrs)
        if rapid_alert:
            alerts.append(rapid_alert)

        # 5. Destinos de alto costo
        high_cost_alert = self._detect_high_cost_destinations(user, cdrs)
        if high_cost_alert:
            alerts.append(high_cost_alert)

        return alerts

    def _detect_suspicious_international(self, user: str, cdrs: List[Dict]) -> Optional[Dict]:
        """Detecta llamadas internacionales sospechosas"""
        # Filtrar llamadas internacionales
        intl_calls = [
            cdr for cdr in cdrs
            if cdr.get("Call type") == "International"
        ]

        if len(intl_calls) < self.config["international_calls_threshold"]:
            return None

        # Analizar patrón temporal
        times = []
        for cdr in intl_calls:
            start_time = cdr.get("Start time")
            if start_time:
                try:
                    dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    times.append(dt)
                except:
                    pass

        if not times:
            return None

        # Verificar si hay muchas llamadas en corto tiempo
        times.sort()
        time_window = timedelta(hours=1)

        for i in range(len(times)):
            window_calls = [t for t in times if times[i] <= t < times[i] + time_window]

            if len(window_calls) >= self.config["international_calls_threshold"]:
                total_duration = sum(
                    cdr.get("Duration", 0) for cdr in intl_calls
                    if self._get_call_time(cdr) in window_calls
                )

                return {
                    "alert_type": "unusual_international_calls",
                    "severity": "high",
                    "user": user,
                    "title": f"Patrón sospechoso de llamadas internacionales",
                    "description": f"Usuario {user} realizó {len(window_calls)} llamadas internacionales en 1 hora",
                    "details": {
                        "call_count": len(window_calls),
                        "total_duration": total_duration,
                        "time_window": times[i].isoformat(),
                        "destinations": list(set(
                            cdr.get("Called number") for cdr in intl_calls
                        ))
                    },
                    "recommended_action": "Verificar con el usuario si estas llamadas son legítimas. Considerar bloqueo temporal de llamadas internacionales.",
                    "timestamp": datetime.utcnow().isoformat()
                }

        return None

    def _detect_after_hours_activity(self, user: str, cdrs: List[Dict]) -> Optional[Dict]:
        """Detecta actividad fuera de horario laboral"""
        after_hours_calls = []

        for cdr in cdrs:
            start_time = self._get_call_time(cdr)
            if not start_time:
                continue

            hour = start_time.hour

            # Fuera de horario laboral (7 AM - 7 PM)
            if hour < self.config["business_hours_start"] or hour >= self.config["business_hours_end"]:
                after_hours_calls.append(cdr)

        if len(after_hours_calls) >= self.config["after_hours_threshold"]:
            # Verificar si son llamadas salientes
            outbound_count = sum(
                1 for cdr in after_hours_calls
                if cdr.get("Direction") == "ORIGINATING"
            )

            if outbound_count >= 2:
                return {
                    "alert_type": "after_hours_activity",
                    "severity": "medium",
                    "user": user,
                    "title": f"Actividad sospechosa fuera de horario",
                    "description": f"Usuario {user} realizó {len(after_hours_calls)} llamadas fuera de horario laboral ({outbound_count} salientes)",
                    "details": {
                        "total_calls": len(after_hours_calls),
                        "outbound_calls": outbound_count,
                        "times": [
                            self._get_call_time(cdr).strftime("%Y-%m-%d %H:%M")
                            for cdr in after_hours_calls[:5]
                        ]
                    },
                    "recommended_action": "Verificar si el usuario tiene autorización para llamadas fuera de horario.",
                    "timestamp": datetime.utcnow().isoformat()
                }

        return None

    def _detect_mass_dialing(self, user: str, cdrs: List[Dict]) -> Optional[Dict]:
        """Detecta mass dialing (muchos destinos diferentes)"""
        # Obtener destinos únicos
        destinations = set()
        outbound_calls = []

        for cdr in cdrs:
            if cdr.get("Direction") == "ORIGINATING":
                called = cdr.get("Called number")
                if called:
                    destinations.add(called)
                    outbound_calls.append(cdr)

        if len(destinations) >= self.config["mass_dialing_threshold"]:
            # Verificar ventana temporal
            times = [self._get_call_time(cdr) for cdr in outbound_calls if self._get_call_time(cdr)]

            if times:
                times.sort()
                time_span = (times[-1] - times[0]).total_seconds() / 3600  # horas

                if time_span <= 2:  # 2 horas
                    return {
                        "alert_type": "mass_dialing",
                        "severity": "critical",
                        "user": user,
                        "title": f"Posible ataque de mass dialing",
                        "description": f"Usuario {user} marcó {len(destinations)} números diferentes en {time_span:.1f} horas",
                        "details": {
                            "unique_destinations": len(destinations),
                            "total_calls": len(outbound_calls),
                            "time_span_hours": round(time_span, 2),
                            "sample_destinations": list(destinations)[:10]
                        },
                        "recommended_action": "ACCIÓN URGENTE: Bloquear extensión inmediatamente y contactar al usuario. Posible compromiso de cuenta.",
                        "timestamp": datetime.utcnow().isoformat()
                    }

        return None

    def _detect_rapid_sequential_calls(self, user: str, cdrs: List[Dict]) -> Optional[Dict]:
        """Detecta llamadas rápidas secuenciales (posible bot)"""
        times = []
        for cdr in cdrs:
            t = self._get_call_time(cdr)
            if t and cdr.get("Direction") == "ORIGINATING":
                times.append(t)

        if len(times) < self.config["rapid_calls_threshold"]:
            return None

        times.sort()

        # Buscar 10 llamadas en 5 minutos
        for i in range(len(times) - self.config["rapid_calls_threshold"] + 1):
            window_end = times[i] + timedelta(minutes=5)
            window_calls = sum(1 for t in times[i:] if t < window_end)

            if window_calls >= self.config["rapid_calls_threshold"]:
                return {
                    "alert_type": "rapid_sequential_calls",
                    "severity": "high",
                    "user": user,
                    "title": f"Llamadas secuenciales sospechosamente rápidas",
                    "description": f"Usuario {user} realizó {window_calls} llamadas en 5 minutos",
                    "details": {
                        "calls_count": window_calls,
                        "time_window": "5 minutos",
                        "start_time": times[i].isoformat()
                    },
                    "recommended_action": "Verificar si es un proceso automatizado legítimo o posible compromiso.",
                    "timestamp": datetime.utcnow().isoformat()
                }

        return None

    def _detect_high_cost_destinations(self, user: str, cdrs: List[Dict]) -> Optional[Dict]:
        """Detecta llamadas a destinos de alto costo"""
        high_cost_calls = []

        for cdr in cdrs:
            called = cdr.get("Called number", "")

            # Verificar si empieza con código de alto costo
            for code in self.config["high_cost_countries"]:
                if called.startswith(code) or called.startswith(f"+{code}"):
                    high_cost_calls.append(cdr)
                    break

        if len(high_cost_calls) >= 2:
            total_duration = sum(cdr.get("Duration", 0) for cdr in high_cost_calls)

            return {
                "alert_type": "suspicious_call_forwarding",
                "severity": "high",
                "user": user,
                "title": f"Llamadas a destinos de alto costo",
                "description": f"Usuario {user} realizó {len(high_cost_calls)} llamadas a números de alto costo",
                "details": {
                    "call_count": len(high_cost_calls),
                    "total_duration_seconds": total_duration,
                    "destinations": [cdr.get("Called number") for cdr in high_cost_calls],
                    "estimated_cost": "ALTO"
                },
                "recommended_action": "URGENTE: Revisar facturación. Bloquear llamadas a estos destinos si no son autorizadas.",
                "timestamp": datetime.utcnow().isoformat()
            }

        return None

    def _get_call_time(self, cdr: Dict) -> Optional[datetime]:
        """Obtiene el tiempo de inicio de una llamada"""
        start_time = cdr.get("Start time")
        if not start_time:
            return None

        try:
            return datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        except:
            return None

    def get_security_score(self, alerts: List[Dict]) -> Tuple[int, str]:
        """
        Calcula un score de seguridad basado en las alertas

        Returns:
            Tupla de (score 0-100, nivel de riesgo)
        """
        if not alerts:
            return 100, "SEGURO"

        # Ponderación por severidad
        severity_weights = {
            "critical": 30,
            "high": 15,
            "medium": 7,
            "low": 3
        }

        penalty = 0
        for alert in alerts:
            severity = alert.get("severity", "low")
            penalty += severity_weights.get(severity, 0)

        score = max(0, 100 - penalty)

        # Clasificar nivel de riesgo
        if score >= 80:
            risk_level = "BAJO"
        elif score >= 60:
            risk_level = "MEDIO"
        elif score >= 40:
            risk_level = "ALTO"
        else:
            risk_level = "CRÍTICO"

        return score, risk_level


# Instancia global
fraud_detection_service = FraudDetectionService()
