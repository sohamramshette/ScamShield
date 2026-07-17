import asyncio
import time

import httpx

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
            "Explanation unavailable at this time due to AI service disruption.",
            "Default to highest caution.",
        )
