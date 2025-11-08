"""
Anomaly detection modules for Webex Calling security
"""
from .international_calls import detect_unusual_international_calls
from .after_hours import detect_after_hours_activity
from .mass_dialing import detect_mass_dialing
from .call_forwarding import detect_suspicious_call_forwarding

__all__ = [
    "detect_unusual_international_calls",
    "detect_after_hours_activity",
    "detect_mass_dialing",
    "detect_suspicious_call_forwarding",
]
