"""
Detector for unusual international calling patterns
"""
import pandas as pd
from sklearn.ensemble import IsolationForest
from typing import Dict, Any, Optional

from src.utils.logger import setup_logger
from src.config import settings

logger = setup_logger(__name__)


def get_historical_data(db_connection, user_id: str, days_lookback: int = 30) -> pd.DataFrame:
    """
    Retrieve historical international calling data for a user

    Args:
        db_connection: Database connection object
        user_id: User identifier
        days_lookback: Number of days to look back

    Returns:
        DataFrame with historical calling patterns
    """
    query = f"""
        SELECT
            DATE(startTime) as date,
            COUNT(*) as intl_calls,
            SUM(duration) as total_minutes
        FROM fact_calls
        WHERE callingUserId = '{user_id}'
        AND callType = 'International'
        AND startTime >= NOW() - INTERVAL '{days_lookback} days'
        GROUP BY DATE(startTime)
    """

    # TODO: Execute query with db_connection
    # For now, return empty DataFrame
    return pd.DataFrame(columns=['date', 'intl_calls', 'total_minutes'])


def get_today_activity(db_connection, user_id: str) -> Dict[str, Any]:
    """
    Get today's calling activity for a user

    Args:
        db_connection: Database connection object
        user_id: User identifier

    Returns:
        Dictionary with today's activity metrics
    """
    query = f"""
        SELECT
            COUNT(*) as intl_calls,
            SUM(duration) as total_minutes,
            ARRAY_AGG(DISTINCT calledNumber) as destinations
        FROM fact_calls
        WHERE callingUserId = '{user_id}'
        AND callType = 'International'
        AND DATE(startTime) = CURRENT_DATE
    """

    # TODO: Execute query with db_connection
    # For now, return sample data
    return {
        'intl_calls': 0,
        'total_minutes': 0,
        'destinations': []
    }


def detect_unusual_international_calls(
    db_connection,
    user_id: str,
    days_lookback: int = 30,
    contamination: float = 0.1
) -> Optional[Dict[str, Any]]:
    """
    Detect unusual international calling patterns using Isolation Forest

    Args:
        db_connection: Database connection object
        user_id: User identifier to analyze
        days_lookback: Number of days to analyze for baseline
        contamination: Expected proportion of outliers in the dataset

    Returns:
        Dictionary with detection results if anomaly found, None otherwise
    """
    logger.info(f"Analyzing international calls for user {user_id}")

    # Get historical data
    historical = get_historical_data(db_connection, user_id, days_lookback)

    if historical.empty or len(historical) < 7:
        logger.warning(f"Insufficient historical data for user {user_id}")
        return None

    # Train anomaly detection model
    model = IsolationForest(contamination=contamination, random_state=42)
    features = historical[['intl_calls', 'total_minutes']].values
    model.fit(features)

    # Get today's activity
    today_activity = get_today_activity(db_connection, user_id)

    if today_activity['intl_calls'] == 0:
        logger.debug(f"No international calls today for user {user_id}")
        return None

    # Predict anomaly
    today_features = [[today_activity['intl_calls'], today_activity['total_minutes']]]
    prediction = model.predict(today_features)
    is_anomaly = prediction[0] == -1

    if is_anomaly:
        logger.warning(f"Anomaly detected for user {user_id}")

        result = {
            'user_id': user_id,
            'anomaly_type': 'unusual_international_calls',
            'severity': 'MEDIUM',
            'today_calls': today_activity['intl_calls'],
            'today_minutes': today_activity['total_minutes'],
            'average_calls': float(historical['intl_calls'].mean()),
            'average_minutes': float(historical['total_minutes'].mean()),
            'std_calls': float(historical['intl_calls'].std()),
            'destinations': today_activity.get('destinations', []),
            'recommendation': 'Verify if this calling pattern is authorized',
        }

        return result

    logger.debug(f"No anomaly detected for user {user_id}")
    return None
