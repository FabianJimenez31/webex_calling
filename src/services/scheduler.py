"""
Scheduler Service
Runs scheduled security analysis and monitoring tasks
"""
import logging
import asyncio
from typing import Optional
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from src.services.webex_client import webex_client
from src.services.anomaly_detector import anomaly_detector
from src.services.alert_service import alert_service

logger = logging.getLogger(__name__)


class AnalysisScheduler:
    """Scheduler for automated security analysis"""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
        self.last_analysis_time = None
        self.analysis_history = []

    def start(self):
        """Start the scheduler"""
        if not self.is_running:
            self.scheduler.start()
            self.is_running = True
            logger.info("Analysis scheduler started")

    def stop(self):
        """Stop the scheduler"""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("Analysis scheduler stopped")

    async def run_scheduled_analysis(self, hours: int = 24, limit: int = 100):
        """
        Run scheduled security analysis

        Args:
            hours: Hours of data to analyze
            limit: Maximum CDRs to analyze
        """
        try:
            logger.info(f"Starting scheduled security analysis (last {hours} hours)...")

            # Fetch CDRs
            end_time = datetime.utcnow() - timedelta(minutes=5)
            start_time = end_time - timedelta(hours=hours)

            cdrs = await webex_client.get_cdrs(
                start_time=start_time,
                end_time=end_time,
                limit=limit
            )

            if not cdrs:
                logger.warning("No CDR data available for scheduled analysis")
                return

            logger.info(f"Analyzing {len(cdrs)} CDRs in scheduled analysis...")

            # Run AI analysis
            analysis = await anomaly_detector.analyze_cdrs(
                cdrs=cdrs,
                analysis_type="security"
            )

            # Send alerts if necessary
            await alert_service.send_alert(
                risk_level=analysis.get('risk_level', 'UNKNOWN'),
                assessment=analysis.get('overall_assessment', ''),
                anomalies=analysis.get('anomalies', []),
                analyzed_cdrs=len(cdrs)
            )

            # Store in history
            analysis_record = {
                "timestamp": datetime.utcnow().isoformat(),
                "cdrs_analyzed": len(cdrs),
                "risk_level": analysis.get('risk_level'),
                "anomalies_count": len(analysis.get('anomalies', [])),
                "overall_assessment": analysis.get('overall_assessment', '')[:200]  # First 200 chars
            }
            self.analysis_history.append(analysis_record)

            # Keep only last 100 analyses
            if len(self.analysis_history) > 100:
                self.analysis_history = self.analysis_history[-100:]

            self.last_analysis_time = datetime.utcnow()

            logger.info(
                f"Scheduled analysis complete. Risk level: {analysis.get('risk_level')}, "
                f"Anomalies: {len(analysis.get('anomalies', []))}"
            )

        except Exception as e:
            logger.error(f"Scheduled analysis failed: {str(e)}")

    def schedule_hourly_analysis(self, hours: int = 1, limit: int = 100):
        """
        Schedule analysis to run every hour

        Args:
            hours: Hours of data to analyze in each run
            limit: Maximum CDRs per analysis
        """
        job = self.scheduler.add_job(
            self.run_scheduled_analysis,
            trigger=IntervalTrigger(hours=1),
            args=[hours, limit],
            id='hourly_analysis',
            replace_existing=True,
            name='Hourly Security Analysis'
        )

        logger.info(f"Scheduled hourly analysis (analyzing last {hours} hour(s), max {limit} CDRs)")
        return job

    def schedule_daily_analysis(self, hour: int = 8, minute: int = 0, hours: int = 24, limit: int = 200):
        """
        Schedule analysis to run daily at a specific time

        Args:
            hour: Hour of day to run (0-23)
            minute: Minute of hour to run (0-59)
            hours: Hours of data to analyze
            limit: Maximum CDRs per analysis
        """
        job = self.scheduler.add_job(
            self.run_scheduled_analysis,
            trigger=CronTrigger(hour=hour, minute=minute),
            args=[hours, limit],
            id='daily_analysis',
            replace_existing=True,
            name=f'Daily Security Analysis ({hour:02d}:{minute:02d})'
        )

        logger.info(f"Scheduled daily analysis at {hour:02d}:{minute:02d} UTC (analyzing last {hours} hours, max {limit} CDRs)")
        return job

    def schedule_custom_interval(
        self,
        interval_minutes: int,
        hours: int = 1,
        limit: int = 50
    ):
        """
        Schedule analysis at custom interval

        Args:
            interval_minutes: Minutes between analyses
            hours: Hours of data to analyze
            limit: Maximum CDRs per analysis
        """
        job = self.scheduler.add_job(
            self.run_scheduled_analysis,
            trigger=IntervalTrigger(minutes=interval_minutes),
            args=[hours, limit],
            id=f'custom_{interval_minutes}min_analysis',
            replace_existing=True,
            name=f'Custom Analysis (every {interval_minutes} min)'
        )

        logger.info(f"Scheduled analysis every {interval_minutes} minutes (analyzing last {hours} hour(s), max {limit} CDRs)")
        return job

    def remove_scheduled_job(self, job_id: str):
        """Remove a scheduled job"""
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"Removed scheduled job: {job_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to remove job {job_id}: {str(e)}")
            return False

    def get_scheduled_jobs(self):
        """Get list of all scheduled jobs"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger)
            })
        return jobs

    def get_analysis_history(self, limit: int = 50):
        """Get recent analysis history"""
        return self.analysis_history[-limit:]


# Global scheduler instance
analysis_scheduler = AnalysisScheduler()
