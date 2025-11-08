"""
Detector for mass dialing patterns (potential fraud/spam)
"""
from typing import List, Dict, Any

from src.utils.logger import setup_logger
from src.config import settings

logger = setup_logger(__name__)


def detect_mass_dialing(
    db_connection,
    threshold_calls: int = None,
    time_window_minutes: int = None,
    short_call_threshold: int = 10
) -> List[Dict[str, Any]]:
    """
    Detect mass dialing patterns that could indicate fraud or compromised extensions

    Args:
        db_connection: Database connection object
        threshold_calls: Minimum calls to trigger detection
        time_window_minutes: Time window to analyze
        short_call_threshold: Duration threshold for "short calls" in seconds

    Returns:
        List of suspicious mass dialing activities
    """
    if threshold_calls is None:
        threshold_calls = settings.mass_dialing_threshold
    if time_window_minutes is None:
        time_window_minutes = settings.mass_dialing_time_window_minutes

    logger.info(
        f"Detecting mass dialing (threshold: {threshold_calls} calls "
        f"in {time_window_minutes} minutes)"
    )

    query = f"""
        SELECT
            callingUserId,
            userName,
            COUNT(DISTINCT calledNumber) as unique_destinations,
            COUNT(*) as total_calls,
            AVG(duration) as avg_duration,
            MIN(duration) as min_duration,
            MAX(duration) as max_duration,
            location,
            ARRAY_AGG(calledNumber) as destinations,
            relatedReason as trunk_used
        FROM fact_calls
        WHERE
            startTime >= NOW() - INTERVAL '{time_window_minutes} minutes'
        GROUP BY callingUserId, userName, location, relatedReason
        HAVING COUNT(*) > {threshold_calls}
    """

    # TODO: Execute query with db_connection
    suspicious_patterns = []

    suspicious_activities = []

    for pattern in suspicious_patterns:
        activity = {
            'user_id': pattern.get('callingUserId'),
            'user_name': pattern.get('userName'),
            'location': pattern.get('location'),
            'anomaly_type': 'mass_dialing',
            'total_calls': pattern.get('total_calls'),
            'unique_destinations': pattern.get('unique_destinations'),
            'avg_duration': float(pattern.get('avg_duration', 0)),
            'min_duration': float(pattern.get('min_duration', 0)),
            'max_duration': float(pattern.get('max_duration', 0)),
            'trunk_used': pattern.get('trunk_used'),
            'time_window_minutes': time_window_minutes,
        }

        # Determine severity
        avg_duration = activity['avg_duration']
        total_calls = activity['total_calls']

        if avg_duration < short_call_threshold and total_calls > threshold_calls * 2:
            # Critical: Many very short calls = likely autodialer or fraud
            activity['severity'] = 'CRITICAL'
            activity['fraud_likelihood'] = 'HIGH'
            activity['recommended_action'] = 'BLOCK EXTENSION IMMEDIATELY'
            activity['reason'] = (
                f"Possible PBX fraud: {total_calls} calls in {time_window_minutes} minutes "
                f"with average duration of only {avg_duration:.1f} seconds"
            )
        elif total_calls > threshold_calls * 3:
            # High: Excessive calling volume
            activity['severity'] = 'HIGH'
            activity['fraud_likelihood'] = 'MEDIUM'
            activity['recommended_action'] = 'Investigate and consider temporary restriction'
            activity['reason'] = f"Excessive call volume: {total_calls} calls in {time_window_minutes} minutes"
        else:
            # Medium: Unusual but not necessarily malicious
            activity['severity'] = 'MEDIUM'
            activity['fraud_likelihood'] = 'LOW'
            activity['recommended_action'] = 'Monitor closely'
            activity['reason'] = f"Elevated call volume: {total_calls} calls in {time_window_minutes} minutes"

        suspicious_activities.append(activity)

        logger.warning(
            f"Mass dialing detected: {activity['user_name']} - "
            f"{activity['total_calls']} calls, severity: {activity['severity']}"
        )

    logger.info(f"Found {len(suspicious_activities)} mass dialing patterns")
    return suspicious_activities
