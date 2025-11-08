"""
Detector for suspicious call forwarding configuration changes
"""
from typing import List, Dict, Any
from datetime import datetime, timedelta

from src.utils.logger import setup_logger
from src.config import settings

logger = setup_logger(__name__)


def is_internal_number(phone_number: str) -> bool:
    """
    Check if a phone number is internal to the organization

    Args:
        phone_number: Phone number to check

    Returns:
        True if internal, False if external
    """
    # TODO: Implement actual logic based on organization's numbering plan
    # For now, assume extensions < 5 digits are internal
    if not phone_number:
        return False

    # Remove common prefixes and formatting
    cleaned = phone_number.replace('+', '').replace('-', '').replace(' ', '')

    # Simple heuristic: less than 5 digits = internal extension
    return len(cleaned) < 5


def is_business_hours_now(location: str) -> bool:
    """
    Check if current time is within business hours for a location

    Args:
        location: Location name

    Returns:
        True if within business hours, False otherwise
    """
    now = datetime.now()
    business_hours = settings.business_hours.get(location, (8, 18))
    start_hour, end_hour = business_hours

    return start_hour <= now.hour < end_hour


def detect_suspicious_call_forwarding(
    webex_api,
    lookback_hours: int = 24
) -> List[Dict[str, Any]]:
    """
    Detect suspicious call forwarding configuration changes

    Args:
        webex_api: Webex API client instance
        lookback_hours: Hours to look back for configuration changes

    Returns:
        List of suspicious call forwarding changes
    """
    logger.info(f"Detecting suspicious call forwarding changes (last {lookback_hours} hours)")

    # Calculate time range
    now = datetime.now()
    start_time = now - timedelta(hours=lookback_hours)

    # Get admin audit events for call forwarding changes
    # TODO: Implement actual API call
    # config_changes = webex_api.get_admin_audit_events(
    #     eventType='USER_CALL_FORWARDING_CHANGED',
    #     startTime=start_time
    # )
    config_changes = []

    suspicious_changes = []

    for change in config_changes:
        user_id = change.get('targetUserId')
        new_forward = change.get('newForwardingNumber')
        timestamp = change.get('timestamp')
        source_ip = change.get('sourceIP')
        user_location = change.get('userLocation', 'Unknown')

        # Check suspicious conditions
        is_suspicious = False
        risk_factors = []

        # Risk factor 1: Forwarding to external number
        if not is_internal_number(new_forward):
            is_suspicious = True
            risk_factors.append('external_destination')

        # Risk factor 2: Change made after hours
        change_time = datetime.fromisoformat(timestamp) if isinstance(timestamp, str) else timestamp
        if not is_business_hours_now(user_location):
            is_suspicious = True
            risk_factors.append('after_hours_change')

        # Risk factor 3: Change from unusual IP
        # TODO: Implement IP reputation check
        # if is_unusual_ip(source_ip, user_id):
        #     is_suspicious = True
        #     risk_factors.append('unusual_source_ip')

        if is_suspicious:
            alert = {
                'user_id': user_id,
                'anomaly_type': 'suspicious_call_forwarding',
                'forwarding_number': new_forward,
                'is_external': not is_internal_number(new_forward),
                'change_timestamp': timestamp,
                'source_ip': source_ip,
                'location': user_location,
                'risk_factors': risk_factors,
            }

            # Determine severity
            if len(risk_factors) >= 2:
                alert['severity'] = 'HIGH'
                alert['recommended_action'] = 'IMMEDIATE INVESTIGATION REQUIRED'
                alert['possible_threats'] = [
                    'SIM swapping attack',
                    'Account compromise',
                    'Call forwarding fraud',
                ]
            else:
                alert['severity'] = 'MEDIUM'
                alert['recommended_action'] = 'Verify with user if change is legitimate'
                alert['possible_threats'] = [
                    'Unauthorized configuration change',
                    'Social engineering',
                ]

            suspicious_changes.append(alert)

            logger.warning(
                f"Suspicious call forwarding detected: User {user_id} forwarded to "
                f"{new_forward} ({', '.join(risk_factors)})"
            )

    logger.info(f"Found {len(suspicious_changes)} suspicious call forwarding changes")
    return suspicious_changes
