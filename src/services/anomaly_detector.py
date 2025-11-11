"""
Anomaly Detection Service using OpenRouter AI
Analyzes Webex Calling CDRs for security threats and suspicious patterns
"""
import os
import json
import logging
from typing import List, Dict, Optional
import httpx

from src.config import settings

logger = logging.getLogger(__name__)


class AnomalyDetector:
    """AI-powered anomaly detection for Webex Calling CDRs"""

    def __init__(self):
        self.api_key = settings.openrouter_api_key
        self.model = settings.openrouter_model
        self.base_url = "https://openrouter.ai/api/v1"

        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY must be set")

    async def analyze_cdrs(self, cdrs: List[Dict], analysis_type: str = "security") -> Dict:
        """
        Analyze CDRs for anomalies using AI

        Args:
            cdrs: List of CDR records
            analysis_type: Type of analysis ('security', 'fraud', 'quality')

        Returns:
            Analysis results with detected anomalies and recommendations
        """
        if not cdrs:
            return {
                "status": "no_data",
                "message": "No CDRs provided for analysis",
                "anomalies": []
            }

        logger.info(f"Analyzing {len(cdrs)} CDRs for {analysis_type} anomalies...")

        # Prepare CDR summary for AI analysis
        cdr_summary = self._prepare_cdr_summary(cdrs)

        # Create analysis prompt based on type
        system_prompt = self._get_system_prompt(analysis_type)
        user_prompt = self._create_analysis_prompt(cdr_summary, analysis_type)

        try:
            # Call OpenRouter API
            response = await self._call_openrouter(system_prompt, user_prompt)

            # Parse AI response
            analysis = self._parse_ai_response(response)

            logger.info(f"Analysis complete. Found {len(analysis.get('anomalies', []))} potential threats")

            return analysis

        except Exception as e:
            logger.error(f"Failed to analyze CDRs: {str(e)}")
            raise

    def _prepare_cdr_summary(self, cdrs: List[Dict]) -> Dict:
        """Prepare a summary of CDRs for AI analysis"""

        # Extract key metrics
        total_calls = len(cdrs)
        answered_calls = sum(1 for cdr in cdrs if cdr.get("Answered") == "true")

        # Call patterns by location
        locations = {}
        for cdr in cdrs:
            loc = cdr.get("Location", "Unknown")
            if loc not in locations:
                locations[loc] = 0
            locations[loc] += 1

        # Call patterns by user
        users = {}
        for cdr in cdrs:
            user = cdr.get("User", "Unknown")
            if user not in users:
                users[user] = 0
            users[user] += 1

        # International calls
        international_calls = sum(1 for cdr in cdrs if cdr.get("International country"))

        # Failed calls
        failed_calls = total_calls - answered_calls

        # Call durations
        durations = [cdr.get("Duration", 0) for cdr in cdrs if cdr.get("Duration")]
        avg_duration = sum(durations) / len(durations) if durations else 0

        # Call types
        call_types = {}
        for cdr in cdrs:
            ct = cdr.get("Call type", "Unknown")
            if ct not in call_types:
                call_types[ct] = 0
            call_types[ct] += 1

        # Sample detailed records (first 10)
        sample_records = cdrs[:10]

        return {
            "summary": {
                "total_calls": total_calls,
                "answered_calls": answered_calls,
                "failed_calls": failed_calls,
                "answer_rate": round((answered_calls / total_calls * 100) if total_calls > 0 else 0, 2),
                "international_calls": international_calls,
                "average_duration": round(avg_duration, 2),
                "locations": locations,
                "top_users": dict(sorted(users.items(), key=lambda x: x[1], reverse=True)[:10]),
                "call_types": call_types
            },
            "sample_records": sample_records
        }

    def _get_system_prompt(self, analysis_type: str) -> str:
        """Get system prompt based on analysis type"""

        base_prompt = """You are an expert cybersecurity analyst specializing in telecommunications fraud detection and security for Webex Calling systems.

Your task is to analyze Call Detail Records (CDRs) and identify potential security threats, fraud patterns, and anomalies.

Focus on detecting:
- Unusual call patterns (high volume, odd hours)
- International fraud (unexpected international calls)
- Toll fraud (calls to premium numbers)
- Account compromise (unusual user behavior)
- Call flooding/DoS attacks
- Unauthorized access patterns
- PBX hacking attempts
- Suspicious geographic patterns
"""

        if analysis_type == "fraud":
            base_prompt += "\n\nPay special attention to financial fraud indicators like premium rate calls, international anomalies, and cost abuse patterns."
        elif analysis_type == "quality":
            base_prompt += "\n\nPay special attention to call quality issues like high failure rates, short call durations, and technical problems."

        return base_prompt

    def _create_analysis_prompt(self, cdr_summary: Dict, analysis_type: str) -> str:
        """Create analysis prompt with CDR data"""

        prompt = f"""Analyze the following Webex Calling data for security threats and anomalies:

## Call Summary Statistics:
{json.dumps(cdr_summary['summary'], indent=2)}

## Sample Call Records (first 10):
{json.dumps(cdr_summary['sample_records'], indent=2)}

Please provide a detailed security analysis in the following JSON format:

{{
  "risk_level": "LOW|MEDIUM|HIGH|CRITICAL",
  "overall_assessment": "Brief overall security assessment",
  "anomalies": [
    {{
      "type": "Type of anomaly (e.g., 'International Fraud', 'Call Flooding', 'Account Compromise')",
      "severity": "LOW|MEDIUM|HIGH|CRITICAL",
      "description": "Detailed description of the anomaly",
      "affected_entities": ["List of affected users, numbers, or locations"],
      "indicators": ["Specific indicators that triggered this detection"],
      "recommendation": "Specific action to take"
    }}
  ],
  "insights": [
    "Key insight 1",
    "Key insight 2"
  ],
  "recommendations": [
    "Security recommendation 1",
    "Security recommendation 2"
  ]
}}

Be thorough and specific. Only report actual anomalies with evidence from the data."""

        return prompt

    async def _call_openrouter(self, system_prompt: str, user_prompt: str) -> str:
        """Call OpenRouter API"""

        url = f"{self.base_url}/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://webex-calling-security.ai",
            "X-Title": "Webex Calling Security AI"
        }

        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.3,  # Lower temperature for more consistent analysis
            "max_tokens": 2000
        }

        logger.info(f"Calling OpenRouter API with model: {self.model}")

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=headers, json=data)

            if response.status_code != 200:
                logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
                raise Exception(f"OpenRouter API error: {response.status_code} - {response.text}")

            result = response.json()
            content = result["choices"][0]["message"]["content"]

            logger.info(f"OpenRouter API call successful. Tokens used: {result.get('usage', {}).get('total_tokens', 'unknown')}")

            return content

    def _parse_ai_response(self, response: str) -> Dict:
        """Parse AI response into structured format"""

        try:
            # Try to extract JSON from response
            # Sometimes AI wraps JSON in markdown code blocks
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            elif "```" in response:
                json_start = response.find("```") + 3
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            else:
                json_str = response.strip()

            analysis = json.loads(json_str)

            # Validate required fields
            if "risk_level" not in analysis:
                analysis["risk_level"] = "MEDIUM"
            if "anomalies" not in analysis:
                analysis["anomalies"] = []
            if "recommendations" not in analysis:
                analysis["recommendations"] = []

            return analysis

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            logger.debug(f"Response: {response}")

            # Return fallback response
            return {
                "risk_level": "UNKNOWN",
                "overall_assessment": "Failed to parse AI analysis",
                "anomalies": [],
                "insights": [response[:500]],  # First 500 chars as insight
                "recommendations": ["Review analysis manually"],
                "raw_response": response
            }


# Global detector instance
anomaly_detector = AnomalyDetector()
