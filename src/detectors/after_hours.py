"""
Detector for after-hours calling activity
"""
from typing import List, Dict, Any
from datetime import datetime

from src.utils.logger import setup_logger
from src.config import settings

logger = setup_logger(__name__)


def is_after_hours(timestamp: datetime, location: str) -> bool:
    """
    Check if a timestamp is outside business hours for a location

    Args:
        timestamp: Call timestamp
        location: Location name (Bogota, Mexico, Madrid)

    Returns:
        True if timestamp is after hours, False otherwise
    """
    business_hours = settings.business_hours.get(location)
    if not business_hours:
        logger.warning(f"Unknown location: {location}, using default hours")
        business_hours = (8, 18)

    start_hour, end_hour = business_hours
    call_hour = timestamp.hour

    return call_hour < start_hour or call_hour >= end_hour


def detect_after_hours_activity(
    db_connection,
    threshold_calls: int = None
) -> List[Dict[str, Any]]:
    """
    Detect suspicious after-hours calling activity

    Args:
        db_connection: Database connection object
        threshold_calls: Minimum number of calls to trigger alert (default from settings)

    Returns:
        List of users with suspicious after-hours activity
    """
    if threshold_calls is None:
        threshold_calls = settings.after_hours_calls_threshold

    logger.info("Detecting after-hours activity")

    query = f"""
        SELECT
            callingUserId,
            userName,
            location,
            COUNT(*) as suspicious_calls,
            ARRAY_AGG(calledNumber) as destinations,
            ARRAY_AGG(startTime) as call_times,
            AVG(duration) as avg_duration
        FROM fact_calls
        WHERE
            DATE(startTime) = CURRENT_DATE
            AND (
                EXTRACT(HOUR FROM startTime) < 8
                OR EXTRACT(HOUR FROM startTime) >= 20
            )
        GROUP BY callingUserId, userName, location
        HAVING COUNT(*) > {threshold_calls}
    """

    # TODO: Execute query with db_connection
    # For now, return empty list
    after_hours_calls = []

    suspicious_users = []

    for user in after_hours_calls:
        user_data = {
            'user_id': user.get('callingUserId'),
            'user_name': user.get('userName'),
            'location': user.get('location'),
            'anomaly_type': 'after_hours_activity',
            'suspicious_calls': user.get('suspicious_calls'),
            'destinations': user.get('destinations', []),
            'call_times': user.get('call_times', []),
            'avg_duration': float(user.get('avg_duration', 0)),
            'business_hours': settings.business_hours.get(user.get('location'), (8, 18)),
        }

        # Determine severity based on number of calls and patterns
        if user_data['suspicious_calls'] > threshold_calls * 3:
            user_data['severity'] = 'HIGH'
        elif user_data['suspicious_calls'] > threshold_calls * 2:
            user_data['severity'] = 'MEDIUM'
        else:
            user_data['severity'] = 'LOW'

        suspicious_users.append(user_data)

        logger.warning(
            f"After-hours activity detected: {user_data['user_name']} "
            f"({user_data['suspicious_calls']} calls, severity: {user_data['severity']})"
        )

    logger.info(f"Found {len(suspicious_users)} users with after-hours activity")
    return suspicious_users
