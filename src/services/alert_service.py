"""
Alert Service
Sends notifications when security anomalies are detected
"""
import logging
import json
from typing import List, Dict, Optional
from datetime import datetime
import httpx
import aiosmtplib
from email.message import EmailMessage

from src.config import settings

logger = logging.getLogger(__name__)


class AlertService:
    """Service for sending security alerts"""

    def __init__(self):
        self.alert_history = []  # In-memory storage (use DB in production)
        self.webhook_urls = []  # Can be configured
        self.email_recipients = []  # Can be configured

    async def send_alert(
        self,
        risk_level: str,
        assessment: str,
        anomalies: List[Dict],
        analyzed_cdrs: int
    ):
        """
        Send alert for detected anomalies

        Args:
            risk_level: Risk level (LOW, MEDIUM, HIGH, CRITICAL)
            assessment: Overall security assessment
            anomalies: List of detected anomalies
            analyzed_cdrs: Number of CDRs analyzed
        """
        # Only send alerts for MEDIUM or higher
        if risk_level in ['MEDIUM', 'HIGH', 'CRITICAL']:
            logger.info(f"Sending {risk_level} alert for {len(anomalies)} anomalies")

            alert_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "risk_level": risk_level,
                "assessment": assessment,
                "anomalies": anomalies,
                "analyzed_cdrs": analyzed_cdrs
            }

            # Store in history
            self.alert_history.append(alert_data)

            # Send to configured channels
            if self.webhook_urls:
                await self._send_webhook_alerts(alert_data)

            if self.email_recipients:
                await self._send_email_alerts(alert_data)

            # Log alert
            logger.warning(
                f"SECURITY ALERT: {risk_level} - {assessment}. "
                f"{len(anomalies)} anomalies detected in {analyzed_cdrs} CDRs"
            )

            return alert_data
        else:
            logger.info(f"Risk level {risk_level} - no alert sent")
            return None

    async def _send_webhook_alerts(self, alert_data: Dict):
        """Send alerts via webhooks (Slack, Teams, etc.)"""
        for webhook_url in self.webhook_urls:
            try:
                await self._send_to_webhook(webhook_url, alert_data)
            except Exception as e:
                logger.error(f"Failed to send webhook alert: {str(e)}")

    async def _send_to_webhook(self, webhook_url: str, alert_data: Dict):
        """
        Send alert to webhook URL
        Supports Slack and Microsoft Teams formatting
        """
        risk_color = self._get_risk_color(alert_data['risk_level'])

        # Format for Slack/Teams
        if 'slack' in webhook_url.lower():
            payload = self._format_slack_message(alert_data, risk_color)
        elif 'office' in webhook_url.lower() or 'teams' in webhook_url.lower():
            payload = self._format_teams_message(alert_data, risk_color)
        else:
            # Generic JSON payload
            payload = alert_data

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(webhook_url, json=payload)
            response.raise_for_status()
            logger.info(f"Webhook alert sent successfully to {webhook_url}")

    def _format_slack_message(self, alert_data: Dict, color: str) -> Dict:
        """Format message for Slack"""
        anomalies_text = "\n".join([
            f"• *{a.get('type')}* ({a.get('severity')}): {a.get('description')}"
            for a in alert_data['anomalies'][:5]  # First 5 anomalies
        ])

        return {
            "attachments": [{
                "color": color,
                "title": f"🚨 Webex Calling Security Alert - {alert_data['risk_level']}",
                "text": alert_data['assessment'],
                "fields": [
                    {
                        "title": "Anomalies Detected",
                        "value": str(len(alert_data['anomalies'])),
                        "short": True
                    },
                    {
                        "title": "CDRs Analyzed",
                        "value": str(alert_data['analyzed_cdrs']),
                        "short": True
                    },
                    {
                        "title": "Details",
                        "value": anomalies_text,
                        "short": False
                    }
                ],
                "footer": "Webex Calling Security AI",
                "ts": int(datetime.utcnow().timestamp())
            }]
        }

    def _format_teams_message(self, alert_data: Dict, color: str) -> Dict:
        """Format message for Microsoft Teams"""
        anomalies_text = "\n\n".join([
            f"**{a.get('type')}** ({a.get('severity')})\n\n{a.get('description')}"
            for a in alert_data['anomalies'][:5]
        ])

        return {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": color.replace('#', ''),
            "summary": f"Security Alert - {alert_data['risk_level']}",
            "sections": [{
                "activityTitle": f"🚨 Webex Calling Security Alert",
                "activitySubtitle": f"Risk Level: {alert_data['risk_level']}",
                "facts": [
                    {
                        "name": "Assessment",
                        "value": alert_data['assessment']
                    },
                    {
                        "name": "Anomalies Detected",
                        "value": str(len(alert_data['anomalies']))
                    },
                    {
                        "name": "CDRs Analyzed",
                        "value": str(alert_data['analyzed_cdrs'])
                    }
                ],
                "text": anomalies_text
            }]
        }

    async def _send_email_alerts(self, alert_data: Dict):
        """Send email alerts"""
        # Email sending would require SMTP configuration
        # This is a placeholder implementation
        logger.info(f"Would send email to {len(self.email_recipients)} recipients")

        # Actual implementation would use aiosmtplib:
        # message = EmailMessage()
        # message["From"] = settings.smtp_from_email
        # message["To"] = ", ".join(self.email_recipients)
        # message["Subject"] = f"Security Alert: {alert_data['risk_level']}"
        # message.set_content(self._format_email_body(alert_data))
        #
        # async with aiosmtplib.SMTP(hostname=settings.smtp_host, port=settings.smtp_port) as smtp:
        #     await smtp.send_message(message)

    def _format_email_body(self, alert_data: Dict) -> str:
        """Format email body"""
        body = f"""
Webex Calling Security Alert
=============================

Risk Level: {alert_data['risk_level']}
Time: {alert_data['timestamp']}

Assessment:
{alert_data['assessment']}

Anomalies Detected: {len(alert_data['anomalies'])}
CDRs Analyzed: {alert_data['analyzed_cdrs']}

Details:
"""
        for anomaly in alert_data['anomalies']:
            body += f"\n\n{anomaly.get('type')} ({anomaly.get('severity')})\n"
            body += f"{anomaly.get('description')}\n"
            body += f"Recommendation: {anomaly.get('recommendation')}\n"

        return body

    def _get_risk_color(self, risk_level: str) -> str:
        """Get color code for risk level"""
        colors = {
            'LOW': '#36a64f',  # Green
            'MEDIUM': '#ff9900',  # Orange
            'HIGH': '#ff0000',  # Red
            'CRITICAL': '#8b0000'  # Dark red
        }
        return colors.get(risk_level, '#808080')

    def configure_webhooks(self, webhook_urls: List[str]):
        """Configure webhook URLs for alerts"""
        self.webhook_urls = webhook_urls
        logger.info(f"Configured {len(webhook_urls)} webhook(s)")

    def configure_emails(self, email_recipients: List[str]):
        """Configure email recipients for alerts"""
        self.email_recipients = email_recipients
        logger.info(f"Configured {len(email_recipients)} email recipient(s)")

    def get_alert_history(self, limit: int = 50) -> List[Dict]:
        """Get recent alert history"""
        return self.alert_history[-limit:]


# Global instance
alert_service = AlertService()
