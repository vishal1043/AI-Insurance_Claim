import os
import logging
import json
from typing import List, Dict, Any

import requests

logger = logging.getLogger(__name__)

# Read config from environment (similar to official SDK initialization)
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY","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")

# Default model similar to official snippet: 'openai/gpt-4o'
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "openai/gpt-4.1-nano")

# Optional: used for rankings/metadata on openrouter.ai
OPENROUTER_SITE_URL = os.environ.get("OPENROUTER_SITE_URL", "http://localhost/8000")
OPENROUTER_SITE_NAME = os.environ.get("OPENROUTER_SITE_NAME", "AI Insurance Claim System")

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


async def analyze_claim_with_ai(claim_data: Dict[str, Any], extracted_texts: List[str]) -> Dict[str, Any]:
    """
    Analyze insurance claim using OpenRouter (OpenAI-compatible API).

    This follows the same structure as the official JS snippet:

    const completion = await openRouter.chat.send({
      model: 'openai/gpt-4o',
      messages: [{ role: 'user', content: '...' }],
      stream: false,
    });

    console.log(completion.choices[0].message.content);
    """

    print("\n🔍 [AI] Starting OpenRouter analysis for claim:", claim_data.get("id"))
    logger.info("Starting OpenRouter analysis for claim_id=%s", claim_data.get("id"))

    if not OPENROUTER_API_KEY:
        msg = "OPENROUTER_API_KEY is not set in environment variables"
        logger.error(msg)
        print("⚠ [AI]", msg)
        # Fallback default response
        return {
            "consistency_score": 50,
            "issues": ["AI key not configured. Using default analysis."],
            "summary": "AI analysis could not be performed due to missing API key.",
            "recommendation": "REVIEW",
        }

    try:
        combined_text = "\n\n".join(extracted_texts)

        prompt = f"""
You are an insurance claim analyst. Analyze the following insurance claim:

**Claim Details:**
- Hospital Name: {claim_data.get('hospital_name')}
- Date of Admission: {claim_data.get('date_of_admission')}
- Disease/Condition: {claim_data.get('disease_description')}
- Total Claim Amount: Rs. {claim_data.get('total_claim_amount')}
- Aadhar Number: {claim_data.get('aadhar_no')}

**Extracted Text from Bills and Reports:**
{combined_text[:3000]}

**Task:**
1. Check if the claim details match the information in the documents.
2. Identify any suspicious or inconsistent information.
3. Verify if the disease description matches medical reports.
4. Check if dates and amounts are consistent.
5. List any red flags or concerns.

**Provide a JSON response with:**
- "consistency_score": (0-100) how consistent is the claim with documents on the basis of details match if the key details are mismitched then consistency score should be less than 50
- "issues": list of specific issues found (empty list if none)
- "summary": brief analysis (2-3 sentences)
- "recommendation": "APPROVE" or "REVIEW" or "REJECT"

Respond ONLY with valid JSON, no other text.

{
  "summary": "<short human-readable summary>",
  "identity_match": true | false,
  "timeline_valid": true | false,
  "diagnosis_supported": true | false,
  "amount_verifiable": true | false
}

Rules:
- identity_match = false if ANY mismatch in claimant name or hospital name between claim and documents.
- timeline_valid = false if report date is after discharge or before admission in an impossible way.
- diagnosis_supported = false if reports do not clearly support the claimed disease/condition.
- amount_verifiable = false if you cannot reasonably map the total claim amount to items in the documents.
""".strip()

        # Headers matching official OpenRouter snippet semantics
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": OPENROUTER_SITE_URL,  # like <YOUR_SITE_URL>
            "X-Title": OPENROUTER_SITE_NAME,      # like <YOUR_SITE_NAME>
        }

        # Payload equivalent to openRouter.chat.send({...})
        payload = {
            "model": OPENROUTER_MODEL,  # 'openai/gpt-4o' or from env
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert insurance claim analyst. Respond only with valid JSON.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            "stream": False,
            "temperature": 0.2,
        }

        print(f"📡 [AI] Sending request to OpenRouter model='{OPENROUTER_MODEL}'")
        logger.info("Sending request to OpenRouter model=%s", OPENROUTER_MODEL)

        # Sync HTTP call inside async function (ok for now)
        response = requests.post(
            OPENROUTER_URL,
            headers=headers,
            json=payload,
            timeout=60,
        )

        print("📨 [AI] OpenRouter HTTP status:", response.status_code)
        logger.info("OpenRouter HTTP status: %s", response.status_code)

        if response.status_code != 200:
            logger.error("OpenRouter API error: %s %s", response.status_code, response.text)
            print("❌ [AI] OpenRouter API error:", response.status_code)
            return {
                "consistency_score": 50,
                "issues": [f"AI API error: {response.status_code}"],
                "summary": "The AI analysis could not be completed. Manual review recommended.",
                "recommendation": "REVIEW",
            }

        data = response.json()

        # This matches: completion.choices[0].message.content
        response_text = data["choices"][0]["message"]["content"].strip()

        print("🧾 [AI] Raw model response (truncated):", response_text[:200], "...")
        logger.debug("Raw AI response: %s", response_text)

        # Clean possible markdown fences
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]

        try:
            ai_analysis = json.loads(response_text.strip())
            print("✅ [AI] Parsed AI JSON successfully.")
            logger.info("Parsed AI JSON successfully")
            return ai_analysis

        except json.JSONDecodeError as e:
            logger.error("Failed to parse AI response as JSON: %s", str(e))
            logger.error("Response was: %s", response_text)
            print("⚠ [AI] JSON parse error, using fallback. Error:", e)
            return {
                "consistency_score": 50,
                "issues": ["Unable to perform complete AI analysis"],
                "summary": "The AI analysis could not be completed. Manual review recommended.",
                "recommendation": "REVIEW",
            }

    except Exception as e:
        logger.error("Error in AI analysis: %s", str(e))
        print("🔥 [AI] Exception during AI analysis:", e)
        return {
            "consistency_score": 50,
            "issues": [f"AI analysis error: {str(e)}"],
            "summary": "Error occurred during AI analysis. Manual review required.",
            "recommendation": "REVIEW",
        }
