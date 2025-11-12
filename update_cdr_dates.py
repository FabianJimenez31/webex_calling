#!/usr/bin/env python3
"""Update CDR dates to today"""

import asyncio
from datetime import datetime, timedelta
from src.database import AsyncSessionLocal
from src.models.cdr import CallDetailRecord
from sqlalchemy import select

async def update_dates():
    """Update all CDR dates to today"""
    async with AsyncSessionLocal() as session:
        # Get all CDRs
        result = await session.execute(select(CallDetailRecord))
        cdrs = result.scalars().all()

        print(f"Updating {len(cdrs)} CDRs...")

        # Calculate offset (from Nov 11 to today)
        today = datetime.now().date()
        offset_days = 1  # Move forward 1 day

        for cdr in cdrs:
            if cdr.start_time:
                # Keep the time, just update the date
                cdr.start_time = cdr.start_time + timedelta(days=offset_days)
            if cdr.answer_time:
                cdr.answer_time = cdr.answer_time + timedelta(days=offset_days)
            if cdr.release_time:
                cdr.release_time = cdr.release_time + timedelta(days=offset_days)

        await session.commit()
        print(f"✅ Updated all CDR dates to {today}")

if __name__ == "__main__":
    asyncio.run(update_dates())
