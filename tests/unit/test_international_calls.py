"""
Unit tests for international calls detection
"""
import pytest
import pandas as pd
from unittest.mock import Mock, MagicMock

from src.detectors.international_calls import (
    detect_unusual_international_calls,
    get_historical_data,
    get_today_activity,
)


class TestInternationalCallsDetector:
    """Test suite for international calls anomaly detection"""

    def test_get_historical_data_returns_dataframe(self):
        """Test that historical data returns a DataFrame with correct columns"""
        db_mock = Mock()
        result = get_historical_data(db_mock, "user123", days_lookback=30)

        assert isinstance(result, pd.DataFrame)
        assert 'date' in result.columns
        assert 'intl_calls' in result.columns
        assert 'total_minutes' in result.columns

    def test_get_today_activity_returns_dict(self):
        """Test that today's activity returns a dictionary"""
        db_mock = Mock()
        result = get_today_activity(db_mock, "user123")

        assert isinstance(result, dict)
        assert 'intl_calls' in result
        assert 'total_minutes' in result
        assert 'destinations' in result

    def test_detect_unusual_calls_no_historical_data(self):
        """Test that detection returns None when no historical data"""
        db_mock = Mock()

        result = detect_unusual_international_calls(db_mock, "user123")

        # Should return None due to insufficient historical data
        assert result is None

    @pytest.mark.skip(reason="Requires mocked data - implement when DB layer is ready")
    def test_detect_unusual_calls_with_anomaly(self):
        """Test detection when an anomaly is present"""
        # TODO: Implement when we have proper DB mocking
        pass

    @pytest.mark.skip(reason="Requires mocked data - implement when DB layer is ready")
    def test_detect_unusual_calls_normal_activity(self):
        """Test detection when activity is normal"""
        # TODO: Implement when we have proper DB mocking
        pass
