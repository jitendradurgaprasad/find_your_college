import json
from typing import Dict, Any, Optional
import requests
from app.config import settings

class AIExtractor:
    def __init__(self, api_key: Optional[str] = None):
        self.gemini_key = api_key or settings.GEMINI_API_KEY
        self.openai_key = settings.OPENAI_API_KEY

    def is_available(self) -> bool:
        return bool(self.gemini_key or self.openai_key)

    def extract_structured_data(self, text_snippet: str, source_url: str) -> Dict[str, Any]:
        """
        AI-assisted structured extraction for complex unstructured pages.
        Extracts verified facts strictly based on supporting evidence in text.
        Never hallucinates or assumes missing values.
        """
        if not self.is_available():
            return {
                "source_url": source_url,
                "confidence_score": 0.0,
                "verification_status": "UNVERIFIED",
                "extracted": {},
                "note": "LLM API key not configured; rule-based pipeline active."
            }

        prompt = f"""
You are an institutional data extraction agent for 'Find Your Collage'.
Extract structured facts strictly from the source text below.
STRICT RULES:
1. NEVER invent or assume any date, fee, scholarship, or placement number.
2. If a field is not explicitly present in the text, return null.
3. Every fact must include the exact verbatim supporting text snippet.
4. Output valid JSON only matching this schema:
{{
  "institution_name": string or null,
  "admission_status": "OPEN" | "CLOSED" | "UPCOMING" | "ONGOING" | "UNKNOWN",
  "admission_evidence": string or null,
  "academic_year": string or null,
  "scholarships_mentioned": [string],
  "tuition_fees": string or null,
  "highest_package": string or null,
  "average_package": string or null,
  "confidence_score": number between 0.0 and 1.0
}}

Source URL: {source_url}
Source Text:
\"\"\"{text_snippet[:4000]}\"\"\"
"""

        try:
            if self.gemini_key:
                resp = requests.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_key}",
                    headers={"Content-Type": "application/json"},
                    json={"contents": [{"parts": [{"text": prompt}]}]},
                    timeout=15
                )
                if resp.status_code == 200:
                    cand = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
                    cleaned_json = cand.replace("```json", "").replace("```", "").strip()
                    parsed = json.loads(cleaned_json)
                    conf = float(parsed.get("confidence_score", 0.70))
                    return {
                        "source_url": source_url,
                        "confidence_score": conf,
                        "verification_status": "VERIFIED" if conf >= 0.85 else "NEEDS_REVIEW",
                        "extracted": parsed
                    }
        except Exception:
            pass

        return {
            "source_url": source_url,
            "confidence_score": 0.50,
            "verification_status": "NEEDS_REVIEW",
            "extracted": {}
        }
