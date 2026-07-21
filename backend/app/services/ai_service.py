import asyncio
import time

import httpx
import json

from app.config.settings import settings
from app.core.logging import log_ai_response, logger
from app.services.risk_engine import get_risk_level


async def generate_explanation(
    scan_type: str, target: str, risk_score: int, threat_indicators: list[dict]
) -> tuple[str, str]:
    """
    Calls IBM Granite API to explain the risk. If AI_MODE=mock, returns a mock explanation.
    Returns (explanation, recommendations).
    """
    start_time = time.time()

    if settings.AI_MODE.lower() == "mock":
        await asyncio.sleep(1)  # simulate delay
        log_ai_response(int((time.time() - start_time) * 1000), "success (mock)")

        risk_level = get_risk_level(risk_score)
        indicator_list = (
            "\n".join([f"- {i['indicator']}" for i in threat_indicators])
            if threat_indicators
            else "- No major threats detected"
        )

        explanation = f"Based on the analysis, this {scan_type} ({target}) presents a {risk_level} (Score: {risk_score}).\n\nEvidence:\n{indicator_list}"

        if risk_score > 60:
            recommendation = "Immediate Action Required: Do not proceed. Avoid entering any credentials or personal information."
        elif risk_score > 40:
            recommendation = (
                "Exercise Caution: Proceed only if you trust the source completely."
            )
        else:
            recommendation = "Appears Safe: No significant threats detected, but always remain vigilant."

        return explanation, recommendation

    # --- PRODUCTION MODE: IBM WatsonX API Integration ---
    try:
        url = f"{settings.IBM_URL}/ml/v1/text/generation?version=2023-05-29"
        headers = {
            "Authorization": f"Bearer {settings.IBM_API_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        prompt = f"Analyze this {scan_type} scan for {target}. Risk score: {risk_score}/100. Threats: {threat_indicators}. Explain why it is suspicious and provide a recommendation."

        payload = {
            "input": prompt,
            "parameters": {"max_new_tokens": 250, "decoding_method": "greedy"},
            "model_id": "ibm/granite-13b-chat-v2",
            "project_id": settings.IBM_PROJECT_ID,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url, json=payload, headers=headers, timeout=10.0
            )
            response.raise_for_status()
            data = response.json()

            result_text = data["results"][0]["generated_text"]

            # Simple parsing (in reality you might instruct the LLM to output JSON)
            explanation = result_text
            recommendation = "Review the explanation above and proceed with caution."

            log_ai_response(int((time.time() - start_time) * 1000), "success")
            return explanation, recommendation

    except Exception as e:
        logger.error(f"Failed to connect to IBM Granite: {e}")
        log_ai_response(int((time.time() - start_time) * 1000), "failed")
        return (
            "Analysis Mode = LIMITED. IBM Granite AI is unavailable.",
            "Default to highest caution.",
        )

async def generate_apk_investigation(
    target: str, risk_score: int, threat_indicators: dict
) -> dict:
    """
    Calls IBM Granite API to generate a structured JSON investigation for an APK.
    """
    start_time = time.time()

    # Mock response for local development
    if settings.AI_MODE.lower() == "mock":
        await asyncio.sleep(1)
        log_ai_response(int((time.time() - start_time) * 1000), "success (mock)")
        
        family = threat_indicators.get("family", "Unknown")
        return {
            "family": family,
            "summary": f"This APK presents a risk score of {risk_score}/100 based on its static properties.",
            "behaviour": "The application requests several dangerous permissions that could allow access to sensitive user data or system resources.",
            "risk": f"The primary risk stems from {threat_indicators.get('iocs', 0)} extracted IOCs and {threat_indicators.get('dangerous_perms', 0)} dangerous permissions.",
            "impact": "Potential data exfiltration or unauthorized system access.",
            "actions": "Do not install this application. Delete the APK file from your device immediately."
        }

    try:
        url = f"{settings.IBM_URL}/ml/v1/text/generation?version=2023-05-29"
        headers = {
            "Authorization": f"Bearer {settings.IBM_API_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        prompt = f"""Analyze this Android APK for potential malware.
Package: {target}
Risk Score: {risk_score}/100
Threat Context: {json.dumps(threat_indicators)}

Output ONLY valid JSON matching this schema, with no markdown formatting or extra text:
{{
  "family": "Detected malware family or 'Unknown'",
  "summary": "High-level summary of the threat",
  "behaviour": "Analysis of the app's capabilities based on permissions and IOCs",
  "risk": "Detailed explanation of why this risk score was assigned",
  "impact": "What happens if a user installs this",
  "actions": "Recommended actions for the user"
}}
"""
        payload = {
            "input": prompt,
            "parameters": {"max_new_tokens": 500, "decoding_method": "greedy"},
            "model_id": "ibm/granite-13b-chat-v2",
            "project_id": settings.IBM_PROJECT_ID,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers, timeout=15.0)
            response.raise_for_status()
            data = response.json()
            result_text = data["results"][0]["generated_text"].strip()
            
            # Clean up markdown if AI includes it
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
                
            parsed = json.loads(result_text)
            log_ai_response(int((time.time() - start_time) * 1000), "success")
            return parsed

    except Exception as e:
        logger.error(f"Failed to connect to IBM Granite for APK: {e}")
        log_ai_response(int((time.time() - start_time) * 1000), "failed")
        return {
            "family": "Unknown",
            "summary": "Analysis Mode = LIMITED. IBM Granite AI is unavailable.",
            "behaviour": "Unable to analyze behaviour dynamically.",
            "risk": "Risk calculation is based purely on static rules engine.",
            "impact": "Unknown. Treat with caution.",
            "actions": "Do not install unless absolutely necessary and verified."
        }
