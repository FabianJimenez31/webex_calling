#!/usr/bin/env python3
"""Generate test data for Webex Calling Security AI"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
import random
from uuid import uuid4

# Add the project directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database import async_engine, AsyncSessionLocal
from src.models.cdr import CallDetailRecord
from src.models.alert import Alert
from src.models.user import User
import json

async def generate_test_data():
    """Generate test CDRs, users, and alerts"""
    async with AsyncSessionLocal() as session:
        print("Generating test data...")

        # Create test users
        users = []
        for i in range(10):
            user = User(
                id=str(uuid4()),
                user_id=f"user_{i:03d}",
                user_name=f"Test User {i}",
                extension=f"1{i:03d}",
                email=f"user{i}@example.com",
                location=random.choice(["Bogota", "Mexico", "Madrid"]),
                department=random.choice(["Sales", "Support", "Engineering"]),
                is_active=True,
                total_calls_outbound=random.randint(10, 100),
                total_calls_inbound=random.randint(10, 100),
                total_international_calls=random.randint(0, 20),
                avg_call_duration=random.uniform(60, 300)
            )
            users.append(user)
            session.add(user)

        # Generate CDRs for the last 24 hours (using utcnow to match API queries)
        cdrs = []
        now = datetime.utcnow()
        for i in range(200):
            hours_ago = random.randint(0, 23)
            start_time = now - timedelta(hours=hours_ago, minutes=random.randint(0, 59))
            duration = random.randint(10, 600)  # 10 seconds to 10 minutes

            calling_user = random.choice(users)

            cdr = CallDetailRecord(
                id=str(uuid4()),
                call_id=f"call_{uuid4().hex[:12]}",
                start_time=start_time,
                answer_time=start_time + timedelta(seconds=random.randint(2, 10)),
                release_time=start_time + timedelta(seconds=duration),
                duration=duration,
                calling_number=calling_user.extension,
                calling_user_id=calling_user.user_id,
                calling_user_name=calling_user.user_name,
                called_number=f"+1{random.randint(1000000000, 9999999999)}",
                call_type=random.choice(["Outbound", "Inbound", "Internal", "International"]),
                direction=random.choice(["Incoming", "Outgoing"]),
                location=calling_user.location,
                answered=random.choice([True, True, True, False]),  # 75% answered
                releasing_party=random.choice(["Local", "Remote"]),
                international_country="US" if random.random() > 0.8 else None
            )
            cdrs.append(cdr)
            session.add(cdr)

        # Generate some alerts
        alerts = []
        alert_types = ["unusual_international_calls", "after_hours_activity", "mass_dialing", "suspicious_forwarding"]
        severities = ["low", "medium", "high", "critical"]

        for i in range(30):
            hours_ago = random.randint(0, 72)
            alert = Alert(
                id=str(uuid4()),
                alert_type=random.choice(alert_types),
                severity=random.choice(severities),
                user_id=random.choice(users).user_id,
                user_name=random.choice(users).user_name,
                location=random.choice(["Bogota", "Mexico", "Madrid"]),
                title=f"Test Alert {i}: Suspicious Activity Detected",
                description=f"This is a test alert generated for demonstration purposes. Alert number {i}.",
                status="open" if random.random() > 0.3 else "resolved",
                created_at=datetime.now() - timedelta(hours=hours_ago),
                detection_data={"test": True, "alert_id": i}
            )
            alerts.append(alert)
            session.add(alert)

        # Commit all data
        await session.commit()

        print(f"✅ Generated:")
        print(f"  - {len(users)} users")
        print(f"  - {len(cdrs)} CDRs")
        print(f"  - {len(alerts)} alerts")
        print("\nTest data generated successfully!")

if __name__ == "__main__":
    asyncio.run(generate_test_data())