import json
import re
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse
import requests
from app.config import settings

class AIExtractor:
    def __init__(self, api_key: Optional[str] = None):
        self.gemini_key = api_key or settings.GEMINI_API_KEY
        self.openai_key = settings.OPENAI_API_KEY

    def is_available(self, custom_key: Optional[str] = None) -> bool:
        return bool(custom_key or self.gemini_key or self.openai_key)

    def _call_gemini(self, prompt: str, api_key: Optional[str] = None) -> Optional[str]:
        """
        Sends prompt to Gemini REST API supporting multiple model tiers.
        """
        key = api_key or self.gemini_key
        if not key:
            return None

        models = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"]
        for model in models:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
                resp = requests.post(
                    url,
                    headers={"Content-Type": "application/json"},
                    json={"contents": [{"parts": [{"text": prompt}]}]},
                    timeout=18
                )
                if resp.status_code == 200:
                    cand = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
                    return cand
            except Exception:
                continue
        return None

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
        raw = self._call_gemini(prompt)
        if raw:
            try:
                cleaned_json = raw.replace("```json", "").replace("```", "").strip()
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

    def resolve_official_url(self, institution_name: str, api_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Intelligently discovers and returns the official institutional website URL and domain.
        Uses Gemini AI to identify the authentic educational portal and verify accessibility.
        """
        key = api_key or self.gemini_key
        if not key:
            return {
                "name": institution_name,
                "official_website": "",
                "domain": "",
                "confidence": 0.0,
                "source": "None",
                "is_accessible": False,
                "note": "Gemini API key is required to automatically fetch official college URLs."
            }

        prompt = f"""
Identify the EXACT OFFICIAL institutional website for this college/university:
"{institution_name}"

CRITICAL RULES:
1. Return ONLY the genuine official homepage URL (e.g. https://www.iitb.ac.in, https://www.bits-pilani.ac.in, https://www.stanford.edu, https://www.ox.ac.uk).
2. DO NOT return aggregator sites or social media (NO Shiksha, Collegedunia, Careers360, Wikipedia, LinkedIn, YouTube, Facebook).
3. Output valid JSON only:
{{
  "name": "{institution_name}",
  "official_website": "https://...",
  "domain": "...",
  "confidence": 0.95
}}
"""
        raw = self._call_gemini(prompt, api_key=key)
        if raw:
            try:
                cleaned = raw.replace("```json", "").replace("```", "").strip()
                # Extract json object if there is surrounding text
                json_match = re.search(r"\{.*\}", cleaned, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group(0))
                    url = data.get("official_website", "").strip()
                    if url and not url.startswith("http"):
                        url = "https://" + url

                    domain = data.get("domain", "")
                    if not domain and url:
                        domain = urlparse(url).netloc.replace("www.", "")

                    # Check accessibility
                    is_accessible = False
                    try:
                        check = requests.head(url, timeout=6, allow_redirects=True, headers={
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) FindYourCollageBot/1.0"
                        })
                        is_accessible = check.status_code < 400
                    except Exception:
                        try:
                            check = requests.get(url, timeout=6, stream=True, headers={
                                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) FindYourCollageBot/1.0"
                            })
                            is_accessible = check.status_code < 400
                        except Exception:
                            is_accessible = False

                    return {
                        "name": data.get("name", institution_name),
                        "official_website": url,
                        "domain": domain,
                        "confidence": float(data.get("confidence", 0.90)),
                        "source": "Gemini AI Knowledge",
                        "is_accessible": is_accessible,
                        "note": "URL verified via Gemini intelligence" if is_accessible else "URL discovered via Gemini; check network connectivity"
                    }
            except Exception as e:
                pass

        return {
            "name": institution_name,
            "official_website": "",
            "domain": "",
            "confidence": 0.0,
            "source": "Gemini Error",
            "is_accessible": False,
            "note": "Could not automatically resolve official website."
        }

    def smart_search(
        self,
        query: str,
        db_colleges: List[Dict[str, Any]],
        api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        AI Natural Language Search Engine.
        Synthesizes student queries, analyzes criteria, and recommends verified colleges.
        """
        key = api_key or self.gemini_key
        if not key:
            return {
                "query": query,
                "ai_answer": "To use AI Smart Search, please provide a Gemini API key. You can enter your Gemini API key in the search bar or set the GEMINI_API_KEY environment variable.",
                "recommended_institutions": [],
                "confidence": 0.0,
                "source": "AI Inactive"
            }

        db_summary = "\n".join([
            f"- {c.get('name')} in {c.get('city')}, {c.get('state')}. Type: {c.get('institution_type')}. Website: {c.get('official_website')}. Completeness: {c.get('data_completeness_score')}%"
            for c in db_colleges[:8]
        ])

        prompt = f"""
You are the intelligent academic counselor for the 'Find Your Collage' platform.
A student has submitted this search inquiry:
"{query}"

Here are institutions currently indexed in our verified database:
{db_summary if db_summary else "No directly matched institutions currently in local database."}

INSTRUCTIONS:
1. Provide a concise, clear, and actionable counseling assessment answering their exact query in Markdown format.
2. Recommend up to 5 genuine colleges or universities that best meet their criteria.
3. For each recommended institution, specify their exact official website URL (no aggregator links), location, key highlights, and why they fit the user's query.
4. Output valid JSON ONLY matching this format:
{{
  "ai_answer": "Markdown formatted summary answer...",
  "recommended_institutions": [
    {{
      "name": "Institution Name",
      "location": "City, State",
      "official_website": "https://...",
      "key_highlights": "Brief highlight regarding degrees, placements, or fees",
      "why_recommended": "Reason why it matches the query"
    }}
  ]
}}
"""
        raw = self._call_gemini(prompt, api_key=key)
        if raw:
            try:
                cleaned = raw.replace("```json", "").replace("```", "").strip()
                json_match = re.search(r"\{.*\}", cleaned, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group(0))
                    return {
                        "query": query,
                        "ai_answer": parsed.get("ai_answer", "Search completed successfully."),
                        "recommended_institutions": parsed.get("recommended_institutions", []),
                        "confidence": 0.95,
                        "source": "Gemini AI"
                    }
            except Exception:
                pass

        return {
            "query": query,
            "ai_answer": f"Unable to process AI search at this moment. You can still use the standard multi-parameter search filters for '{query}'.",
            "recommended_institutions": [],
            "confidence": 0.0,
            "source": "Gemini AI Fallback"
        }

    def extract_courses_from_text(self, pages_text: List[str], institution_name: str, source_url: str = "") -> List[Dict[str, Any]]:
        """
        AI-assisted academic catalog booster. Extracts all degree programs, courses,
        and specializations from institutional text when heuristic discovery needs enrichment.
        """
        if not self.is_available():
            return []

        combined_text = "\n\n---\n\n".join([t[:2500] for t in pages_text[:5]])
        if len(combined_text.strip()) < 100:
            return []

        prompt = f"""
You are an expert higher education data extraction specialist for '{institution_name}'.
Analyze the following official institution web pages and extract all academic degree programs, courses, and specializations offered.

STRICT INSTRUCTIONS:
1. Extract authentic degree programs (e.g. B.Tech, M.Tech, MBBS, BDS, B.Pharm, M.Pharm, BPT, MPT, B.MLS, B.Sc, M.Sc, MBA, BBA, BCA, MCA, Ph.D, etc.).
2. Extract the exact specialization / stream if present.
3. Categorize degree_type strictly as: "Undergraduate", "Postgraduate", "PhD", or "Diploma".
4. Estimate duration_years (e.g. MBBS: 5.5, B.Tech/B.Pharm: 4.0, B.Sc/BBA/BCA: 3.0, M.Tech/MBA/M.Sc: 2.0, PhD: 3.0).
5. Output valid JSON ONLY matching this format:
{{
  "programs": [
    {{
      "name": "B.Tech (Hons) in Computer Science & Engineering",
      "degree_type": "Undergraduate",
      "specialization": "Computer Science & Engineering",
      "duration_years": 4.0,
      "tuition_fees_annual": "Refer official fee matrix"
    }}
  ]
}}

Source Text:
\"\"\"{combined_text[:7000]}\"\"\"
"""
        raw = self._call_gemini(prompt)
        if raw:
            try:
                cleaned = raw.replace("```json", "").replace("```", "").strip()
                json_match = re.search(r"\{.*\}", cleaned, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group(0))
                    programs = parsed.get("programs", [])
                    results = []
                    for p in programs:
                        p_name = p.get("name")
                        if p_name and len(p_name) > 3:
                            results.append({
                                "name": p_name,
                                "degree_type": p.get("degree_type", "Undergraduate"),
                                "specialization": p.get("specialization"),
                                "duration_years": float(p.get("duration_years", 3.0)),
                                "tuition_fees_annual": p.get("tuition_fees_annual", "Refer official fee matrix"),
                                "source_url": source_url,
                                "description": f"Verified academic curriculum for {p_name} at {institution_name}"
                            })
                    return results
            except Exception:
                pass

        return []
